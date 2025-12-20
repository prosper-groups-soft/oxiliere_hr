from django.db import transaction
from django.db.models import Sum
from django.core.exceptions import ValidationError
from decimal import Decimal
from hr.payroll.models import SalaryAdvance, RepaymentLog


class RepaymentLogReaderService:
    """
    Service to read repayment logs.
    """

    @staticmethod
    def get_repayments_for_advance(salary_advance_id):
        """Return all repayment logs for a specific salary advance."""
        return RepaymentLog.objects.filter(
            salary_advance_id=salary_advance_id
        ).order_by('-date')

    @staticmethod
    def get_latest_repayment(salary_advance_id):
        """Return the latest repayment log for a salary advance."""
        return RepaymentLog.objects.filter(
            salary_advance_id=salary_advance_id
        ).order_by('-date').first()

    @staticmethod
    def get_total_repaid(salary_advance_id):
        """Calculate the total amount repaid for a salary advance."""
        total = RepaymentLog.objects.filter(
            salary_advance_id=salary_advance_id
        ).aggregate(total=Sum('amount'))['total']
        return total or Decimal('0.00')

    @staticmethod
    def get_remaining_amount(salary_advance_id):
        """Get the remaining amount to repay for a salary advance."""
        latest = RepaymentLogReaderService.get_latest_repayment(salary_advance_id)
        if latest:
            return latest.sold
        advance = SalaryAdvance.objects.filter(id=salary_advance_id).first()
        return advance.amount if advance else Decimal('0.00')


class RepaymentLogWriterService:
    """
    Service to create repayment logs and manage salary advance repayment logic.
    """

    @staticmethod
    @transaction.atomic
    def create_repayment(salary_advance: SalaryAdvance, amount: Decimal):
        """
        Create a repayment log for a salary advance.
        This will automatically update the remaining amount 
        and the advance status.
        """

        if salary_advance.is_repaid:
            raise ValidationError("This salary advance is already fully repaid.")

        # Determine last remaining amount
        last_log = RepaymentLogReaderService.get_latest_repayment(salary_advance.id)
        remaining = last_log.sold if last_log else salary_advance.amount

        if amount <= 0:
            raise ValidationError("Repayment amount must be greater than zero.")

        if amount > remaining:
            raise ValidationError(
                f"Repayment amount {amount} exceeds remaining amount {remaining}."
            )

        new_sold = remaining - amount

        # Create the repayment log
        repayment = RepaymentLog.objects.create(
            salary_advance=salary_advance,
            amount=amount,
            sold=new_sold
        )

        # Update advance status if fully repaid
        if new_sold <= 0:
            salary_advance.is_repaid = True
            salary_advance.save(update_fields=['is_repaid'])

        return repayment

    @staticmethod
    @transaction.atomic
    def rollback_repayment(repayment_log: RepaymentLog):
        """
        Rollback a repayment log. Updates the remaining amount and advance status.
        """
        advance = repayment_log.salary_advance

        # Delete repayment
        repayment_log.delete()

        # Recalculate the last remaining amount
        last_log = RepaymentLogReaderService.get_latest_repayment(advance.id)
        remaining = last_log.sold if last_log else advance.amount

        # Update advance status
        advance.is_repaid = remaining <= 0
        advance.save(update_fields=['is_repaid'])

        return remaining

