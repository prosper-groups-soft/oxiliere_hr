"""
Service for managing salary advances and their flexible repayment lifecycle.

Supports:
- Multiple deduction bases (Gross/Net)
- Tax timing flexibility (Before/After)
- Configurable deduction windows
- Priority-based advance selection
"""

from decimal import Decimal
from datetime import date
from django.db.models import Sum
from typing import List, Tuple

from hr.payroll.models import (
    SalaryAdvance,
    AdvanceDeductionConfiguration,
    RepaymentRecord,
)
from hr.payroll.enums import (
    AdvanceDeductionBase,
    AdvanceDeductionWindow,
)


class AdvanceService:
    """
    Manages salary advances with full flexibility in deduction configuration.
    
    Key features:
    - Get remaining balance for any advance
    - Calculate monthly repayments with priority ordering
    - Record repayments and auto-close advances
    - Retrieve active advances in priority order
    """

    @classmethod
    def get_remaining_balance(cls, advance: SalaryAdvance) -> Decimal:
        """
        Calculates the remaining unpaid balance for a specific advance.
        
        Args:
            advance: The SalaryAdvance instance
            
        Returns:
            Decimal: Remaining balance (principal - total repaid)
        """
        total_repaid = advance.repayments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        return advance.amount - total_repaid

    @classmethod
    def is_advance_deductible_on_date(
        cls,
        advance: SalaryAdvance,
        payroll_date: date
    ) -> bool:
        """
        Determines if an advance should be deducted during the specified payroll period.
        
        Respects the deduction_window configuration:
        - ALL_MONTHS: Always deductible until closed
        - CUSTOM_PERIOD: Only between deduction_start_date and deduction_end_date
        
        Args:
            advance: The SalaryAdvance instance
            payroll_date: The date of the payroll (typically month-end)
            
        Returns:
            bool: True if advance should be deducted, False otherwise
        """
        if advance.is_closed:
            return False

        if advance.deduction_window == AdvanceDeductionWindow.ALL_MONTHS:
            return True

        # CUSTOM_PERIOD: Check if payroll_date falls within the window
        if advance.deduction_window == AdvanceDeductionWindow.CUSTOM_PERIOD:
            if advance.deduction_start_date is None or advance.deduction_end_date is None:
                return False
            
            return advance.deduction_start_date <= payroll_date <= advance.deduction_end_date

        return False

    @classmethod
    def get_active_advances_ordered(
        cls,
        employee_id: int,
        payroll_date: date
    ) -> List[SalaryAdvance]:
        """
        Retrieves all active advances for an employee, ordered by priority.
        
        Only returns advances that:
        1. Are not closed
        2. Have an active AdvanceDeductionConfiguration (is_active=True)
        3. Are currently deductible (within their deduction_window)
        
        Results are ordered by priority_order (lower number = higher priority).
        
        Args:
            employee_id: The ID of the employee
            payroll_date: The current payroll date
            
        Returns:
            List[SalaryAdvance]: Ordered list of active advances ready for deduction
        """
        # Get configurations for this employee, ordered by priority
        configs = AdvanceDeductionConfiguration.objects.filter(
            employee_id=employee_id,
            is_active=True
        ).select_related('advance').order_by('priority_order')

        # Filter advances that are deductible on the given date
        active_advances = [
            config.advance
            for config in configs
            if cls.is_advance_deductible_on_date(config.advance, payroll_date)
        ]

        return active_advances

    @classmethod
    def calculate_advance_deduction(
        cls,
        advance: SalaryAdvance,
        gross_salary: Decimal,
        net_salary: Decimal
    ) -> Decimal:
        """
        Calculates the deduction amount for a single advance, respecting its configuration.
        
        Logic:
        1. Determines deduction base (Gross or Net) based on advance config
        2. Calculates repayment_percentage of that base
        3. Never deducts more than the remaining balance
        
        Args:
            advance: The SalaryAdvance instance
            gross_salary: Gross salary amount (before deductions)
            net_salary: Net salary amount (before advance deductions)
            
        Returns:
            Decimal: Amount to deduct (0 if balance is zero)
        """
        balance = cls.get_remaining_balance(advance)
        
        if balance <= 0:
            return Decimal('0.00')

        # Select the appropriate salary base
        if advance.salary_base_for_deduction == AdvanceDeductionBase.GROSS:
            salary_base = gross_salary
        else:  # AdvanceDeductionBase.NET
            salary_base = net_salary

        # Calculate suggested deduction
        suggested_deduction = (
            salary_base * (advance.repayment_percentage / Decimal('100'))
        ).quantize(Decimal('0.01'))

        # Never exceed remaining balance
        return min(suggested_deduction, balance)

    @classmethod
    def process_advances_for_payslip(
        cls,
        employee_id: int,
        gross_salary: Decimal,
        net_salary_before_advances: Decimal,
        payroll_date: date
    ) -> Tuple[List[Tuple[SalaryAdvance, Decimal]], Decimal]:
        """
        Processes all advances for an employee in priority order and returns deductions.
        
        This method:
        1. Retrieves active advances in priority order
        2. Calculates deduction for each advance
        3. Returns ordered list of (advance, amount) tuples and total deduction
        
        Args:
            employee_id: Employee ID
            gross_salary: Gross salary amount
            net_salary_before_advances: Net salary before any advance deductions
            payroll_date: Current payroll date
            
        Returns:
            Tuple of:
            - List[(SalaryAdvance, Decimal)]: Advances with their deduction amounts
            - Decimal: Total deduction amount across all advances
            
        Example:
            advances, total = AdvanceService.process_advances_for_payslip(
                employee_id=1,
                gross_salary=2000,
                net_salary_before_advances=1800,
                payroll_date=date(2026, 1, 31)
            )
            # advances = [(AdvanceA, 180), (AdvanceB, 90)]
            # total = 270
        """
        active_advances = cls.get_active_advances_ordered(employee_id, payroll_date)
        
        advance_deductions = []
        total_deduction = Decimal('0.00')

        for advance in active_advances:
            deduction = cls.calculate_advance_deduction(
                advance,
                gross_salary,
                net_salary_before_advances
            )
            
            if deduction > 0:
                advance_deductions.append((advance, deduction))
                total_deduction += deduction

        return advance_deductions, total_deduction

    @classmethod
    def record_repayment(
        cls,
        advance: SalaryAdvance,
        payslip,
        amount: Decimal
    ) -> bool:
        """
        Records a repayment transaction and auto-closes advance if fully repaid.
        
        Args:
            advance: The SalaryAdvance instance
            payslip: The EmployeePayslip instance
            amount: The repayment amount
            
        Returns:
            bool: True if advance was closed, False otherwise
        """
        if amount <= 0:
            return False

        # Create repayment record
        RepaymentRecord.objects.create(
            salary_advance=advance,
            payslip=payslip,
            amount=amount
        )

        # Check if advance is fully repaid
        remaining = cls.get_remaining_balance(advance)
        
        if remaining <= 0:
            advance.is_closed = True
            advance.save(update_fields=['is_closed'])
            return True

        return False

    @classmethod
    def record_batch_repayments(
        cls,
        payslip,
        advance_deductions: List[Tuple[SalaryAdvance, Decimal]]
    ) -> dict:
        """
        Records multiple repayments at once (batch operation).
        
        Useful when processing multiple advances for a single payslip.
        
        Args:
            payslip: The EmployeePayslip instance
            advance_deductions: List of (advance, amount) tuples
            
        Returns:
            dict: Status information
            {
                'recorded': int,  # Number of repayments recorded
                'closed': int,    # Number of advances fully closed
                'total_amount': Decimal
            }
        """
        recorded_count = 0
        closed_count = 0
        total_amount = Decimal('0.00')

        for advance, amount in advance_deductions:
            if cls.record_repayment(advance, payslip, amount):
                closed_count += 1
            recorded_count += 1
            total_amount += amount

        return {
            'recorded': recorded_count,
            'closed': closed_count,
            'total_amount': total_amount,
        }

