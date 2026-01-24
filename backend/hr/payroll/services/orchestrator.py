from decimal             import Decimal
from django.db           import transaction
from hr.employees.models import Employee
from hr.payroll.models   import (
    EmployeeContract, 
    PayrollRun, 
    EmployeePayslip, 
    PayslipLine, 
    PayrollConfiguration,
    SalaryAdvance,
    OvertimeRule,
    PayrollConfiguration
)
from hr.payroll.enums    import (
    PayrollStatus, 
    RemunerationType, 
    OvertimeRuleType,
    SalaryBaseType
)

from .adjustments        import AdjustmentResolverService
from .advances           import AdvanceService
from .calculators        import PayrollCalculatorService
from .taxes              import TaxCalculationService
from .contributions      import SocialContributionService
from .legal_allowances   import LegalAllowanceService
from hr.payroll.services.integration import PayrollIntegrationService
from hr.payroll.services.brutage     import GrossUpService
from hr.payroll.services.exchange    import ExchangeRateService


class PayrollOrchestrator:
    """
    The main engine that orchestrates the entire payroll process for a given run.
    """

    @classmethod
    @transaction.atomic
    def process_run(cls, payroll_run: PayrollRun):
        """
        Processes all active contracts for a specific payroll run.
        Uses atomic transaction to ensure data integrity.
        """
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
        """
        Internal logic to calculate and save one employee's payslip following DRC legal standards.
        Sequence:
        1. Worked Days Data Persistence
        2. Gross Salary (Base + Overtime + Bonuses)
        3. Social Deductions (Worker CNSS 5%)
        4. Taxable Base & IPR Tax
        5. Legal Allowances (Family, Housing, Transport)
        6. Net Pay calculation
        """
        # --- A. Data Retrieval (Integration) ---
        attendance = PayrollIntegrationService.get_worked_days_data(contract.employee_id, run.start_date, run.end_date)
        family = PayrollIntegrationService.get_employee_family_data(contract.employee_id)

        # --- B. Leave Data Retrieval (Configurable) ---
        leave = {
            'paid_leave_days': Decimal('0.00'),
            'unpaid_leave_days': Decimal('0.00')
        }
        if config.include_leaves_in_payroll:
            leave = PayrollIntegrationService.get_employee_leave_data(contract.employee_id, run.start_date, run.end_date)

        # Determine dynamic company size for INPP
        company_size = Employee.objects.filter(is_active=True).count()

        # --- B. Persistence: WorkedDaysRecord ---
        WorkedDaysRecord.objects.update_or_create(
            employee=contract.employee,
            payroll_run=run,
            defaults={
                'regular_days': attendance['regular_days'],
                'overtime_hours_first_tier': attendance['overtime_hours_standard'] if attendance['overtime_hours_standard'] <= 2 else 2.0,
                'overtime_hours_second_tier': max(0, attendance['overtime_hours_standard'] - 2.0),
                'overtime_hours_holiday': attendance['overtime_hours_holiday'],
                'absence_days': attendance['absence_days']
            }
        )

        payroll_config = PayrollConfiguration.objects.first()
        std_monthly_hours = Decimal(str(payroll_config.work_hours_per_month if payroll_config else 195))

        # --- Multi-Currency Handling ---
        # Convert contract amounts to CDF if necessary
        contract_currency = getattr(contract, 'currency', Currency.CDF) # Assuming added to model or default
        # Note: Contract model likely needs currency field, checking if it exists or default to CDF
        # Inspecting previous models.py view, EmployeeContract did not show 'currency' field explicitly in the snippet?
        # Let's assume logic: Check if we need to add field or if it exists.
        # Wait, I didn't see a currency field on EmployeeContract in step 546.
        # I must add it to the model first!
        # ABORTING changes to Orchestrator to add field to model first.
        # --- Multi-Currency Handling ---
        contract_currency = contract.currency
        conversion_rate = Decimal('1.0')
        
        if contract_currency != Currency.CDF:
            conversion_rate = ExchangeRateService.get_exchange_rate(contract_currency, Currency.CDF)
            
        # --- C. Base Salary & Overtime (Stage 1: Gross/Net Resolution) ---
        if contract.remuneration_type == RemunerationType.FIXED:
            target_amount = contract.base_salary
            
            # Apply currency conversion if needed
            if contract_currency != Currency.CDF:
                target_amount = (target_amount * conversion_rate).quantize(Decimal('0.01'))

            if contract.salary_base_type == SalaryBaseType.NET:
                # Brutage: Resolve required Gross Base from target Net à Payer
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
        else:
            target_rate = contract.hourly_rate
            
            # Apply currency conversion if needed
            if contract_currency != Currency.CDF:
                target_rate = (target_rate * conversion_rate).quantize(Decimal('0.01'))

            if contract.salary_base_type == SalaryBaseType.NET:
                # Brutage: Resolve required Gross Hourly Rate from target Net Hourly à Payer
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
            
            # Total hours for payment: Worked + Paid Leave Hours (assuming 8h/day for leave)
            paid_leave_hours = float(leave['paid_leave_days']) * 8.0
            total_remunerable_hours = float(attendance['total_worked_hours']) + paid_leave_hours
            base_amount = (hourly_rate * Decimal(str(total_remunerable_hours))).quantize(Decimal('0.01'))

        # Calculate Overtime Pay using the new calculator
        rules_qs = OvertimeRule.objects.filter(is_active=True)
        multipliers = {
            'first_two': rules_qs.filter(rule_type=OvertimeRuleType.FIRST_TWO_HOURS).values_list('multiplier', flat=True).first() or Decimal('1.30'),
            'subsequent': rules_qs.filter(rule_type=OvertimeRuleType.SUBSEQUENT_HOURS).values_list('multiplier', flat=True).first() or Decimal('1.60'),
            'holiday': rules_qs.filter(rule_type=OvertimeRuleType.HOLIDAY).values_list('multiplier', flat=True).first() or Decimal('2.00')
        }
        
        overtime_pay = PayrollCalculatorService.calculate_overtime_pay(
            hourly_rate=hourly_rate,
            std_hours=attendance['overtime_hours_standard'],
            hol_hours=attendance['overtime_hours_holiday'],
            multipliers=multipliers
        )

        # Resolved Adjustments (Bonuses & Other Deductions)
        applicable_adjs = AdjustmentResolverService.get_applicable_adjustments(
            contract.employee_id, run.end_date
        )
        total_bonuses = Decimal('0.00')
        total_other_deductions = Decimal('0.00')
        adjustment_lines = []

        for adj in applicable_adjs:
            val = PayrollCalculatorService.calculate_adjustment_value(
                adj['mode'], base_amount, adj['amount'], adj['percentage']
            )
            if adj['type'] == 'BONUS':
                total_bonuses += val
                adjustment_lines.append({'label': adj['label'], 'amount': val, 'type': 'BONUS'})
            else: # CONTRIBUTION
                total_other_deductions += val
                adjustment_lines.append({'label': adj['label'], 'amount': val, 'type': 'CONTRIBUTION'})

        gross_salary = base_amount + total_bonuses + overtime_pay

        # --- D. Pro-rating for Unpaid Absences (if Fixed Salary) ---
        if contract.remuneration_type == RemunerationType.FIXED:
            unpaid_days = Decimal(str(attendance['absence_days'])) + leave['unpaid_leave_days']
            if unpaid_days > 0:
                # Deduction logic: Fixed amount (if set) OR Pro-rata divisor
                if config.fixed_deduction_per_absent_day:
                    deduction = config.fixed_deduction_per_absent_day * unpaid_days
                else:
                    # Divisor logic: Theoretical days from Attendance OR Configured divisor
                    divisor = config.leave_deduction_divisor or Decimal('26.0')
                    
                    if config.use_theoretical_days_from_attendance:
                        theoretical_days = PayrollIntegrationService.get_theoretical_working_days(
                            contract.employee_id, run.start_date, run.end_date
                        )
                        if theoretical_days > 0:
                            divisor = theoretical_days

                    deduction = (base_amount / divisor) * unpaid_days
                
                base_amount -= deduction
                gross_salary -= deduction
                adjustment_lines.append({
                    'label': f"Absence non payée ({unpaid_days} jrs)", 
                    'amount': -deduction.quantize(Decimal('0.01')), 
                    'type': 'CONTRIBUTION'
                })

        # --- D. Retenues Obligatoires (Stage 2: Deductions) ---
        # 1. Social Contributions (Split Employee vs Employer)
        social_data = SocialContributionService.calculate_contributions(
            gross_amount=gross_salary, 
            base_salary=base_amount, 
            company_size=company_size
        )
        
        cnss_employee = Decimal('0.00')
        onem_amount = Decimal('0.00')
        inpp_amount = Decimal('0.00')
        employer_charges = Decimal('0.00')
        contribution_details = []

        for detail in social_data['details']:
            if detail['type'] == 'CNSS':
                cnss_employee = detail['employee_amount']
            elif detail['type'] == 'ONEM':
                onem_amount = detail['employee_amount'] or detail['employer_amount'] # ONEM is usually employer-only but captured here
            elif detail['type'] == 'INPP':
                inpp_amount = detail['employer_amount']
            
            # Employer total charges (for audit/payslip visibility)
            employer_charges += detail['employer_amount']
            contribution_details.append(detail)

        # 2. Taxable Base & IPR
        initial_taxable_base = gross_salary - cnss_employee
        
        allowances = LegalAllowanceService.calculate_allowances(
            worked_days=attendance['regular_days'] + int(leave['paid_leave_days']), 
            child_count=family['child_count'], 
            gross_salary=gross_salary,
            base_salary=base_amount
        )
        
        taxable_base = initial_taxable_base + allowances['taxable_housing_excess']
        ipr_tax = TaxCalculationService.calculate_progressive_tax(taxable_base)

        # --- E. Final Calculation (Stage 3: Net) ---
        active_advance = SalaryAdvance.objects.filter(
            employee=contract.employee, is_closed=False
        ).first()
        advance_deduction = Decimal('0.00')
        if active_advance:
            # Pre-advance net is (Gross + Allowances) - Deductions
            pre_advance_net = (gross_salary + allowances['total_allowances']) - (cnss_employee + ipr_tax)
            advance_deduction = AdvanceService.calculate_monthly_repayment(active_advance, pre_advance_net)

        # SOLDE NET = (Gains Totaux) - (Retenues Travailleur)
        net_amount = (gross_salary + allowances['total_allowances']) - (cnss_employee + ipr_tax + advance_deduction + total_other_deductions)

        # --- F. Persistence ---
        payslip = EmployeePayslip.objects.create(
            payroll_run=run,
            contract=contract,
            base_salary_snapshot=base_amount,
            gross_amount=gross_salary,
            taxable_base=taxable_base,
            
            cnss_amount=cnss_employee,
            onem_amount=onem_amount,
            inpp_amount=inpp_amount,
            ipr_amount=ipr_tax,
            
            family_allowance=allowances['family_allowance'],
            housing_allowance=allowances['housing_allowance'],
            transport_allowance=allowances['transport_allowance'],
            
            total_adjustments=allowances['total_allowances'] - cnss_employee - ipr_tax - advance_deduction - total_other_deductions,
            net_amount=net_amount,
            
            worked_days=attendance['regular_days'],
            worked_hours=attendance['total_worked_hours'],
            paid_leave_days=float(leave['paid_leave_days']),
            unpaid_leave_days=float(leave['unpaid_leave_days']),
            
            # Currency persistence
            contract_currency=contract_currency,
            exchange_rate_used=conversion_rate,
            
            currency=config.currency,
            payment_method=contract.employee.preferred_payment_method or config.default_payment_method
        )

        # Record detail lines
        PayslipLine.objects.create(payslip=payslip, label="Salaire de Base", amount=base_amount, adjustment_type='BONUS')
        
        if overtime_pay > 0:
            PayslipLine.objects.create(payslip=payslip, label="Heures Supplémentaires", amount=overtime_pay, adjustment_type='BONUS')

        for adj in adjustment_lines:
             PayslipLine.objects.create(payslip=payslip, label=adj['label'], amount=adj['amount'], adjustment_type=adj['type'])

        for detail in allowances['details']:
            PayslipLine.objects.create(payslip=payslip, label=detail['label'], amount=detail['amount'], adjustment_type='BONUS')

        # Record leaves if any
        if leave['paid_leave_days'] > 0:
            PayslipLine.objects.create(payslip=payslip, label=f"Maintien de salaire - Congés Payés ({leave['paid_leave_days']} jrs)", amount=Decimal('0.00'), adjustment_type='BONUS')

        # Record exchange rate if applied
        if contract_currency != Currency.CDF:
             PayslipLine.objects.create(
                 payslip=payslip, 
                 label=f"Taux de change appliqué (1 {contract_currency} = {conversion_rate} CDF)", 
                 amount=Decimal('0.00'), 
                 adjustment_type='BONUS'
             )

        # worker deductions
        PayslipLine.objects.create(payslip=payslip, label="CNSS (5%)", amount=cnss_employee, adjustment_type='CONTRIBUTION')
        PayslipLine.objects.create(payslip=payslip, label="IPR", amount=ipr_tax, adjustment_type='CONTRIBUTION')
            
        if advance_deduction > 0:
            AdvanceService.record_repayment(active_advance, payslip, advance_deduction)
            PayslipLine.objects.create(
                payslip=payslip, 
                label=f"Retenue Avance sur Salaire", 
                amount=advance_deduction, 
                adjustment_type='CONTRIBUTION'
            )

        return payslip

