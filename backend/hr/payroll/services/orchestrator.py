from decimal import Decimal
from django.db import transaction
from hr.payroll.models import (
    EmployeeContract, 
    PayrollRun, 
    EmployeePayslip, 
    PayslipLine, 
    PayrollConfiguration,
    SalaryAdvance
)
from hr.payroll.enums import PayrollStatus, RemunerationType

from .calculators import PayrollCalculatorService
from .adjustments import AdjustmentResolverService
from .advances import AdvanceService


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
        Internal logic to calculate and save one employee's payslip.
        """
        # 1. Base Salary Calculation
        if contract.remuneration_type == RemunerationType.FIXED:
            base_amount = contract.base_salary
        else:
            # For hourly: this would require integration with a timesheet service
            # Here we use work_hours_per_month from config as a default
            base_amount = PayrollCalculatorService.calculate_hourly_gross(
                contract.hourly_rate, config.work_hours_per_month, 0, config.overtime_multiplier
            )

        # 2. Resolve Adjustments (Bonuses & Deductions)
        applicable_adjs = AdjustmentResolverService.get_applicable_adjustments(
            contract.employee_id, run.end_date
        )

        # 3. Create Payslip Snapshot (initial save to get ID)
        payslip = EmployeePayslip.objects.create(
            payroll_run=run,
            contract=contract,
            base_salary_snapshot=base_amount,
            gross_amount=base_amount, # Will be updated below
            total_adjustments=0,
            net_amount=0,
            currency=config.currency,
            payment_method=contract.employee.preferred_payment_method or config.default_payment_method
        )

        # 4. Process Lines & Calculate Totals
        total_bonus = Decimal('0.00')
        total_deduction = Decimal('0.00')

        for adj_data in applicable_adjs:
            val = PayrollCalculatorService.calculate_adjustment_value(
                adj_data['mode'], base_amount, adj_data['amount'], adj_data['percentage']
            )
            
            PayslipLine.objects.create(
                payslip=payslip,
                adjustment=adj_data['source'],
                label=adj_data['label'],
                amount=val,
                adjustment_type=adj_data['type']
            )

            if adj_data['type'] == 'BONUS':
                total_bonus += val
            else:
                total_deduction += val

        # 5. Handle Salary Advances
        active_advance = SalaryAdvance.objects.filter(
            employee=contract.employee, is_closed=False
        ).first()
        
        advance_deduction = Decimal('0.00')
        if active_advance:
            current_net = base_amount + total_bonus - total_deduction
            advance_deduction = AdvanceService.calculate_monthly_repayment(
                active_advance, 
                current_net
            )
            
            if advance_deduction > 0:
                AdvanceService.record_repayment(active_advance, payslip, advance_deduction)
                # Add advance as a negative line
                PayslipLine.objects.create(
                    payslip=payslip,
                    label=f"Repayment: Advance {active_advance.id}",
                    amount=advance_deduction,
                    adjustment_type='CONTRIBUTION'
                )

        # 6. Final Updates
        payslip.gross_amount = base_amount + total_bonus
        payslip.total_adjustments = total_bonus - total_deduction - advance_deduction
        payslip.net_amount = payslip.gross_amount - total_deduction - advance_deduction
        payslip.save()

