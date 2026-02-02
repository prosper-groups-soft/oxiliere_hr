from decimal             import Decimal
from django.db           import transaction
from django.utils        import timezone
from hr.employees.models import Employee
from hr.payroll.models   import (
    EmployeeContract, 
    PayrollRun, 
    EmployeePayslip, 
    PayslipLine, 
    PayrollConfiguration,
    OvertimeRule,
    WorkedDaysRecord
)
from hr.payroll.enums    import (
    PayrollStatus, 
    RemunerationType, 
    OvertimeRuleType,
    SalaryBaseType,
    SocialContributionType
)
from hr.enums import Currency

from .adjustments        import AdjustmentResolverService
from .advances.advances              import AdvanceService
from .calculations.calculators       import PayrollCalculatorService
from .calculations.taxes             import TaxCalculationService
from .calculations.contributions     import SocialContributionService
from .calculations.legal_allowances  import LegalAllowanceService
from hr.payroll.services.integration import PayrollIntegrationService
from hr.payroll.services.calculations.brutage import GrossUpService
from hr.payroll.services.integration.exchange import ExchangeRateService


class PayrollOrchestrator:
    """ Main engine that coordinates the entire payroll processing run. """

    @classmethod
    @transaction.atomic
    def process_run(cls, payroll_run: PayrollRun):
        """ Processes all active contracts for a specific payroll run. """
        if payroll_run.status != PayrollStatus.DRAFT:
            raise ValueError("Only draft payroll runs can be processed.")

        config = PayrollConfiguration.objects.first() # Global settings
        active_contracts = EmployeeContract.objects.filter(is_active=True)

        for contract in active_contracts:
            cls._generate_single_payslip(payroll_run, contract, config)

        payroll_run.status = PayrollStatus.VALIDATED
        payroll_run.save()

    @classmethod
    def _generate_single_payslip(cls, run, contract, config):
        """ Generates a complete payslip for an employee following DRC legal standards. """
        # === PREVENT DUPLICATES ===
        existing = EmployeePayslip.objects.filter(payroll_run=run, contract=contract).first()
        if existing:
            return existing
        
        # === STAGE 1: Data Retrieval ===
        employee_data = cls._retrieve_employee_data(contract, run, config)
        
        # === STAGE 2: Gross Salary Calculation ===
        gross_data = cls._calculate_gross_salary(
            contract, 
            employee_data, 
            config
        )
        
        # === STAGE 3: Legal Deductions (Absences) ===
        gross_data = cls._apply_absence_deductions(
            gross_data, 
            contract, 
            employee_data, 
            config
        )
        
        # === STAGE 4: Social Contributions & Tax ===
        social_data = cls._calculate_social_contributions(
            gross_data['gross_salary'],
            employee_data['company_size']
        )
        
        tax_data = cls._calculate_tax_and_allowances(
            gross_data['gross_salary'],
            gross_data['base_amount'],
            social_data['cnss_employee'],
            employee_data,
            config
        )
        
        # === STAGE 5: Process Salary Advances ===
        advance_data = cls._process_advances(
            contract, 
            gross_data['gross_salary'],
            social_data['cnss_employee'],
            tax_data['ipr_tax'],
            tax_data['total_allowances'],
            gross_data['total_other_deductions'],
            employee_data,
            run
        )
        
        # === STAGE 6: Create Payslip ===
        payslip = cls._create_payslip(
            run, 
            contract, 
            config,
            gross_data,
            social_data,
            tax_data,
            advance_data,
            employee_data
        )
        
        # === STAGE 7: Record Detail Lines ===
        cls._record_payslip_lines(
            payslip,
            gross_data,
            social_data,
            tax_data,
            advance_data,
            employee_data
        )
        
        return payslip

    @classmethod
    def _retrieve_employee_data(cls, contract, run, config):
        """ Retrieves employee data (attendance, family, leaves) for the period. """
        attendance = PayrollIntegrationService.get_worked_days_data(
            contract.employee_id, 
            run.start_date, 
            run.end_date
        )
        family = PayrollIntegrationService.get_employee_family_data(contract.employee_id)
        
        # Leave data (configurable)
        leave = {
            'paid_leave_days': Decimal('0.00'),
            'unpaid_leave_days': Decimal('0.00')
        }
        if config.include_leaves_in_payroll:
            leave = PayrollIntegrationService.get_employee_leave_data(
                contract.employee_id, 
                run.start_date, 
                run.end_date
            )
        
        # Company size for INPP calculation
        company_size = Employee.objects.filter(is_active=True).count()
        
        # Use Run's specific exchange rate if defined, otherwise fetch current
        conversion_rate = run.exchange_rate_applied or Decimal('1.0')
        if not run.exchange_rate_applied and contract.currency != Currency.CDF:
             conversion_rate = ExchangeRateService.get_exchange_rate(contract.currency, Currency.CDF)
        
        # PERSISTENCE - DRC Rule: 6 hours for the first tier (130%)
        # Ref: Arrêté ministériel n° 68/11
        standard_ot = Decimal(str(attendance['overtime_hours_standard']))
        tier_limit = Decimal('6.0') 
        
        WorkedDaysRecord.objects.update_or_create(
            employee=contract.employee,
            payroll_run=run,
            defaults={
                'regular_days': attendance['regular_days'],
                'overtime_hours_first_tier': min(standard_ot, tier_limit),
                'overtime_hours_second_tier': max(0, standard_ot - tier_limit),
                'overtime_hours_holiday': attendance['overtime_hours_holiday'],
                'absence_days': attendance['absence_days']
            }
        )
        
        return {
            'attendance': attendance,
            'family': family,
            'leave': leave,
            'company_size': company_size,
            'contract_currency': contract.currency,
            'conversion_rate': conversion_rate,
        }

    @classmethod
    def _calculate_gross_salary(cls, contract, employee_data, config):
        """ Calculates base salary, overtime, and bonuses. Handles multi-currency and net-to-gross. """
        attendance = employee_data['attendance']
        family = employee_data['family']
        leave = employee_data['leave']
        company_size = employee_data['company_size']
        conversion_rate = employee_data['conversion_rate']
        
        payroll_config = PayrollConfiguration.objects.first()
        std_monthly_hours = Decimal(str(payroll_config.work_hours_per_month if payroll_config else 195))
        
        # === Base Salary Calculation ===
        if contract.remuneration_type == RemunerationType.FIXED:
            target_amount = contract.base_salary
            
            # Apply currency conversion
            if employee_data['contract_currency'] != Currency.CDF:
                target_amount = (target_amount * conversion_rate).quantize(Decimal('0.01'))
            
            # Brutage if base is Net
            if contract.salary_base_type == SalaryBaseType.NET:
                base_amount = GrossUpService.calculate_base_from_net(
                    target_net=target_amount,
                    company_size=company_size,
                    worked_days=attendance['regular_days'],
                    child_count=family['child_count'],
                    is_hourly=False
                )
            else:
                base_amount = target_amount
            
            hourly_rate = base_amount / std_monthly_hours
        
        else:  # HOURLY
            target_rate = contract.hourly_rate
            
            # Apply currency conversion
            if employee_data['contract_currency'] != Currency.CDF:
                target_rate = (target_rate * conversion_rate).quantize(Decimal('0.01'))
            
            # Brutage if rate is Net
            if contract.salary_base_type == SalaryBaseType.NET:
                hourly_rate = GrossUpService.calculate_base_from_net(
                    target_net=target_rate,
                    company_size=company_size,
                    worked_days=attendance['regular_days'] + int(leave['paid_leave_days']),
                    child_count=family['child_count'],
                    is_hourly=True,
                    std_monthly_hours=std_monthly_hours
                )
            else:
                hourly_rate = target_rate
            
            # Total hours: worked + paid leave hours
            paid_leave_hours = float(leave['paid_leave_days']) * 8.0
            total_remunerable_hours = float(attendance['total_worked_hours']) + paid_leave_hours
            base_amount = (hourly_rate * Decimal(str(total_remunerable_hours))).quantize(Decimal('0.01'))
            
        # === Overtime Calculation - Updated for DRC (6-hour tier) ===
        rules_qs = OvertimeRule.objects.filter(is_active=True)
        multipliers = {
            # Change 'first_two' to a generic name like 'first_period'
            'first_period': rules_qs.filter(rule_type=OvertimeRuleType.FIRST_TWO_HOURS).values_list('multiplier', flat=True).first() or Decimal('1.30'),
            'subsequent': rules_qs.filter(rule_type=OvertimeRuleType.SUBSEQUENT_HOURS).values_list('multiplier', flat=True).first() or Decimal('1.60'),
            'holiday': rules_qs.filter(rule_type=OvertimeRuleType.HOLIDAY).values_list('multiplier', flat=True).first() or Decimal('2.00')
        }
        
        # This service now correctly uses the 6-hour rule for RDC
        overtime_pay = PayrollCalculatorService.calculate_overtime_pay(
            hourly_rate=hourly_rate,
            std_hours=attendance['overtime_hours_standard'],
            hol_hours=attendance['overtime_hours_holiday'],
            multipliers=multipliers
        )
        
        # === Adjustments (Bonuses) ===
        # Use end_date to fetch active adjustments for the period
        ref_date = attendance.get('end_date') or timezone.now().date()
        applicable_adjs = AdjustmentResolverService.get_applicable_adjustments(
            contract.employee_id, 
            ref_date
        )
        
        total_bonuses = Decimal('0.00')
        total_other_deductions = Decimal('0.00')
        adjustment_lines = []
        
        for adj in applicable_adjs:
            val = PayrollCalculatorService.calculate_adjustment_value(
                adj['mode'], 
                base_amount, 
                adj['amount'], 
                adj['percentage']
            )
            if adj['type'] == 'BONUS':
                total_bonuses += val
                adjustment_lines.append({
                    'label': adj['label'],
                    'amount': val,
                    'type': 'BONUS'
                })
            else:  # CONTRIBUTION
                total_other_deductions += val
                adjustment_lines.append({
                    'label': adj['label'],
                    'amount': val,
                    'type': 'CONTRIBUTION'
                })
        
        # Important: total_other_deductions are calculated here but 
        # should be subtracted from Gross or Net depending on their nature
        gross_salary = base_amount + total_bonuses + overtime_pay
        
        return {
            'base_amount': base_amount,
            'hourly_rate': hourly_rate,
            'overtime_pay': overtime_pay,
            'total_bonuses': total_bonuses,
            'total_other_deductions': total_other_deductions,
            'gross_salary': gross_salary,
            'adjustment_lines': adjustment_lines,
        }

    @classmethod
    def _apply_absence_deductions(cls, gross_data, contract, employee_data, config):
        """ Applies deductions for unpaid absences based on company policy. """
        if contract.remuneration_type != RemunerationType.FIXED:
            return gross_data
        
        attendance = employee_data['attendance']
        leave = employee_data['leave']
        base_amount = gross_data['base_amount']
        
        unpaid_days = Decimal(str(attendance['absence_days'])) + leave['unpaid_leave_days']
        
        if unpaid_days <= 0:
            return gross_data
        
        # Determine deduction amount
        if config.fixed_deduction_per_absent_day:
            deduction = config.fixed_deduction_per_absent_day * unpaid_days
        else:
            # Use theoretical days or configured divisor
            divisor = config.leave_deduction_divisor or Decimal('26.0')
            
            if config.use_theoretical_days_from_attendance:
                theoretical_days = PayrollIntegrationService.get_theoretical_working_days(
                    contract.employee_id,
                    attendance['start_date'],
                    attendance['end_date']
                )
                if theoretical_days > 0:
                    divisor = theoretical_days
            
            deduction = (base_amount / divisor) * unpaid_days
        
        # Apply deduction
        gross_data['base_amount'] -= deduction
        gross_data['gross_salary'] -= deduction
        gross_data['adjustment_lines'].append({
            'label': f"Absence non payée ({unpaid_days} jrs)",
            'amount': -deduction.quantize(Decimal('0.01')),
            'type': 'CONTRIBUTION'
        })
        
        return gross_data

    @classmethod
    def _calculate_social_contributions(cls, gross_salary, company_size):
        """ Calculates statutory social security contributions (CNSS, ONEM, INPP). """
        social_data = SocialContributionService.calculate_contributions(
            gross_amount=gross_salary,
            company_size=company_size
        )
        
        cnss_employee = Decimal('0.00')
        onem_amount = Decimal('0.00')
        inpp_amount = Decimal('0.00')
        employer_charges = Decimal('0.00')
        
        for detail in social_data['details']:
            if detail['type'] == SocialContributionType.CNSS:
                cnss_employee = detail['employee_amount']
            elif detail['type'] == SocialContributionType.ONEM:
                # 100% Employer charge in DRC
                onem_amount = detail['employer_amount']
            elif detail['type'] == SocialContributionType.INPP:
                # 100% Employer charge in DRC
                inpp_amount = detail['employer_amount']
            
            employer_charges += detail['employer_amount']
        
        return {
            'cnss_employee': cnss_employee,
            'onem_amount': onem_amount,
            'inpp_amount': inpp_amount,
            'employer_charges': employer_charges,
            'contribution_details': social_data['details'],
        }

    @classmethod
    def _calculate_tax_and_allowances(cls, gross_salary, base_salary, cnss_employee, employee_data, config):
        """ Calculates IPR tax and legal allowances (Housing, Transport, Family). """
        attendance = employee_data['attendance']
        family = employee_data['family']
        leave = employee_data['leave']
        
        # 1. Calculate Allowances first
        # Critical: Use base_salary for housing threshold (30% rule)
        allowances = LegalAllowanceService.calculate_allowances(
            worked_days=attendance['regular_days'] + int(leave['paid_leave_days']),
            child_count=family['child_count'],
            base_salary=base_salary
        )
        
        # 2. Taxable base calculation for IPR (DRC Rule)
        # Base = (Gross - Allowances) + Taxable Housing Excess - CNSS Employee
        # Simplified here as: (Gross - CNSS) + Housing Excess
        # We ensure the non-taxable part of allowances is excluded
        taxable_base = (gross_salary - cnss_employee) + allowances['taxable_housing_excess']
        
        # 3. Calculate IPR tax using progressive brackets
        ipr_tax = TaxCalculationService.calculate_progressive_tax(taxable_base)
        
        return {
            'taxable_base': taxable_base,
            'ipr_tax': ipr_tax,
            'family_allowance': allowances['family_allowance'],
            'housing_allowance': allowances['housing_allowance'],
            'transport_allowance': allowances['transport_allowance'],
            'total_allowances': allowances['total_allowances'],
            'allowance_details': allowances.get('details', []),
        }

    @classmethod
    def _process_advances(cls, contract, gross_salary, cnss_employee, ipr_tax, 
                         total_allowances, total_other_deductions, employee_data, run):
        """ Processes outstanding salary advances in priority order. """
        # Calculate net salary before advances
        net_before_advances = (
            (gross_salary + total_allowances) - 
            (cnss_employee + ipr_tax + total_other_deductions)
        )
        
        # Process all advances
        advance_deductions, total_advance_deduction = AdvanceService.process_advances_for_payslip(
            employee_id=contract.employee.id,
            gross_salary=gross_salary,
            net_salary_before_advances=net_before_advances,
            payroll_date=run.end_date
        )
        
        return {
            'advance_deductions': advance_deductions,
            'total_advance_deduction': total_advance_deduction,
        }

    @classmethod
    def _create_payslip(cls, run, contract, config, gross_data, social_data, 
                       tax_data, advance_data, employee_data):
        """ Persists the employee payslip summary. """
        # Calculate final net amount
        net_amount = (
            (gross_data['gross_salary'] + tax_data['total_allowances']) -
            (social_data['cnss_employee'] + tax_data['ipr_tax'] + 
             gross_data['total_other_deductions'] + advance_data['total_advance_deduction'])
        )
        
        # FIX: Corrected total_adjustments logic (should be positive bonuses/allowances)
        total_adjustments = (
            tax_data['total_allowances'] + 
            gross_data['total_bonuses']
        ) - (
            social_data['cnss_employee'] + 
            tax_data['ipr_tax'] + 
            advance_data['total_advance_deduction'] + 
            gross_data['total_other_deductions']
        )
        
        payslip = EmployeePayslip.objects.create(
            payroll_run=run,
            contract=contract,
            base_salary_snapshot=gross_data['base_amount'],
            gross_amount=gross_data['gross_salary'],
            taxable_base=tax_data['taxable_base'],
            
            cnss_amount=social_data['cnss_employee'],
            onem_amount=social_data['onem_amount'],
            inpp_amount=social_data['inpp_amount'],
            ipr_amount=tax_data['ipr_tax'],
            
            family_allowance=tax_data['family_allowance'],
            housing_allowance=tax_data['housing_allowance'],
            transport_allowance=tax_data['transport_allowance'],
            
            total_adjustments=total_adjustments,
            net_amount=net_amount,
            
            worked_days=employee_data['attendance']['regular_days'],
            worked_hours=employee_data['attendance']['total_worked_hours'],
            paid_leave_days=float(employee_data['leave']['paid_leave_days']),
            unpaid_leave_days=float(employee_data['leave']['unpaid_leave_days']),
            
            contract_currency=employee_data['contract_currency'],
            exchange_rate_used=employee_data['conversion_rate'],
            
            currency=config.currency,
            payment_method=contract.employee.preferred_payment_method or config.default_payment_method
        )
        
        # Record advance repayments
        if advance_data['advance_deductions']:
            AdvanceService.record_batch_repayments(payslip, advance_data['advance_deductions'])
        
        return payslip

    @classmethod
    def _record_payslip_lines(cls, payslip, gross_data, social_data, tax_data, 
                             advance_data, employee_data):
        """ Records detailed line items (earnings and deductions) on the payslip. """
        # Base salary
        PayslipLine.objects.create(
            payslip=payslip,
            label="Salaire de Base",
            amount=gross_data['base_amount'],
            adjustment_type='BONUS'
        )
        
        # Overtime
        if gross_data['overtime_pay'] > 0:
            PayslipLine.objects.create(
                payslip=payslip,
                label="Heures Supplémentaires",
                amount=gross_data['overtime_pay'],
                adjustment_type='BONUS'
            )
        
        # Adjustments
        for adj in gross_data['adjustment_lines']:
            PayslipLine.objects.create(
                payslip=payslip,
                label=adj['label'],
                amount=adj['amount'],
                adjustment_type=adj['type']
            )
        
        # Legal allowances
        for detail in tax_data['allowance_details']:
            PayslipLine.objects.create(
                payslip=payslip,
                label=detail['label'],
                amount=detail['amount'],
                adjustment_type='BONUS'
            )
        
        # Leaves
        if employee_data['leave']['paid_leave_days'] > 0:
            PayslipLine.objects.create(
                payslip=payslip,
                label=f"Maintien de salaire - Congés Payés ({employee_data['leave']['paid_leave_days']} jrs)",
                amount=Decimal('0.00'),
                adjustment_type='BONUS'
            )
        
        # Exchange rate info
        if employee_data['contract_currency'] != Currency.CDF:
            PayslipLine.objects.create(
                payslip=payslip,
                label=f"Taux de change appliqué (1 {employee_data['contract_currency']} = {employee_data['conversion_rate']} CDF)",
                amount=Decimal('0.00'),
                adjustment_type='BONUS'
            )
        
        # Worker deductions
        PayslipLine.objects.create(
            payslip=payslip,
            label="CNSS (5%)",
            amount=social_data['cnss_employee'],
            adjustment_type='CONTRIBUTION'
        )
        PayslipLine.objects.create(
            payslip=payslip,
            label="IPR",
            amount=tax_data['ipr_tax'],
            adjustment_type='CONTRIBUTION'
        )
        
        if tax_data.get('taxable_housing_excess', 0) > 0:
            PayslipLine.objects.create(
                payslip=payslip,
                label=f"Dont excédent logement imposable: {tax_data['taxable_housing_excess']} CDF",
                amount=Decimal('0.00'),
                adjustment_type='BONUS' 
            )

        
        # Advance repayments as detail lines
        for advance, amount in advance_data['advance_deductions']:
            PayslipLine.objects.create(
                payslip=payslip,
                label=f"Retenue Avance sur Salaire #{advance.id}",
                amount=amount,
                adjustment_type='CONTRIBUTION'
            )

