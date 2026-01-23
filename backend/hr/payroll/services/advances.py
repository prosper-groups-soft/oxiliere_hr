from decimal import Decimal
from django.db.models import Sum
from hr.payroll.models import (
    SalaryAdvance, 
    RepaymentRecord
)


class AdvanceService:
    """
    Service to manage salary advances and their repayment lifecycle.
    """

    @classmethod
    def get_remaining_balance(cls, advance: SalaryAdvance) -> Decimal:
        """
        Calculates the remaining balance of a specific advance.
        """
        total_repaid = advance.repayments.aggregate(
            total=Sum('amount')
        )['total'] or Decimal('0.00')
        
        return advance.amount - total_repaid

    @classmethod
    def calculate_monthly_repayment(cls, advance: SalaryAdvance, net_salary: Decimal) -> Decimal:
        """
        Calculates how much should be deducted from the current payslip.
        Logic: Use repayment_percentage of net salary, but never exceed the remaining balance.
        """
        balance = cls.get_remaining_balance(advance)
        if balance <= 0:
            return Decimal('0.00')

        # Suggested deduction based on percentage
        suggested_deduction = (net_salary * (advance.repayment_percentage / Decimal('100'))).quantize(Decimal('0.01'))

        # Return the smaller of the two (don't overcharge if balance is low)
        return min(suggested_deduction, balance)

    @classmethod
    def record_repayment(cls, advance: SalaryAdvance, payslip, amount: Decimal):
        """
        Creates a repayment record and checks if the advance is fully paid.
        """
        if amount <= 0:
            return

        RepaymentRecord.objects.create(
            salary_advance=advance,
            payslip=payslip,
            amount=amount
        )

        # Re-check balance to close the advance if necessary
        if cls.get_remaining_balance(advance) <= 0:
            advance.is_closed = True
            advance.save()
