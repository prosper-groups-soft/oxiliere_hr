from hr.payroll.models import SalaryAdvance
from django.db import transaction
from django.core.exceptions import ValidationError
from hr.payroll.models import SalaryAdvance, RepaymentLog
from hr.employees.models import Employee


class SalaryAdvanceWriterService:
    """
    Write service for salary advances.
    All business rules are enforced here.
    """

    @staticmethod
    @transaction.atomic
    def create_advance(
        *,
        employee: Employee,
        amount,
        repayment_percentage,
        comments=None
    ):
        """Create a new salary advance for an employee."""

        unpaid_exists = SalaryAdvance.objects.filter(
            employee=employee,
            is_repaid=False
        ).exists()

        if unpaid_exists:
            raise ValidationError(
                "This employee already has an unpaid salary advance."
            )

        advance = SalaryAdvance.objects.create(
            employee=employee,
            amount=amount,
            repayment_percentage=repayment_percentage,
            comments=comments.strip() if comments else None,
            is_repaid=False
        )

        return advance

    @staticmethod
    @transaction.atomic
    def apply_repayment(
        *,
        salary_advance: SalaryAdvance,
        available_amount
    ):
        """
        Apply a repayment based on the configured percentage.
        Returns the created RepaymentLog or None.
        """

        if salary_advance.is_repaid:
            return None

        repayment_amount = salary_advance.repayment_amount
        if not repayment_amount or available_amount < repayment_amount:
            return None

        last_log = salary_advance.repayment_logs.order_by('-created_at').first()
        current_sold = last_log.sold if last_log else salary_advance.amount

        new_sold = current_sold - repayment_amount

        repayment_log = RepaymentLog.objects.create(
            salary_advance=salary_advance,
            amount=repayment_amount,
            sold=new_sold
        )

        if new_sold <= 0:
            salary_advance.is_repaid = True
            salary_advance.save(update_fields=['is_repaid'])

        return repayment_log

    @staticmethod
    @transaction.atomic
    def force_close_advance(salary_advance: SalaryAdvance):
        """
        Force an advance to be marked as repaid.
        Intended for administrative corrections.
        """
        salary_advance.is_repaid = True
        salary_advance.save(update_fields=['is_repaid'])
        return salary_advance


class SalaryAdvanceReaderService:
    """
    Read-only service for salary advances.
    """

    @staticmethod
    def get_by_id(advance_id):
        """Return a salary advance by its ID."""
        return SalaryAdvance.objects.filter(id=advance_id).first()

    @staticmethod
    def get_active_advance_for_employee(employee):
        """Return the current unpaid salary advance for an employee."""
        return SalaryAdvance.objects.filter(
            employee=employee,
            is_repaid=False
        ).order_by('-created_at').first()

    @staticmethod
    def get_all_for_employee(employee):
        """Return all salary advances for an employee."""
        return SalaryAdvance.objects.filter(
            employee=employee
        ).order_by('-created_at')

    @staticmethod
    def has_unpaid_advance(employee):
        """Check if the employee has an unpaid salary advance."""
        return SalaryAdvance.objects.filter(
            employee=employee,
            is_repaid=False
        ).exists()

