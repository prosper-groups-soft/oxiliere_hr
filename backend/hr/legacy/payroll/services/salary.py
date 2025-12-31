from django.db import transaction
from django.core.exceptions import ValidationError
from hr.payroll.models import Salary
from hr.choices import ContractType
from sequences import get_next_value
from hr.utils import get_contract_seq_key
from utils_mixins.fn import get_rotate_value


class SalaryReaderService:
    """
    Service for reading/retrieving contracts.
    """

    @staticmethod
    def get_active_salaries(employee_id=None):
        """Return all active contracts, optionally filtered by employee."""
        qs = Salary.objects.filter(is_active=True)
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        return qs.order_by('-start_date')
    
    @staticmethod
    def get_active_salary(employee):
        """Return the first active salary for a given employee."""
        return Salary.objects.filter(
            employee=employee, 
            is_active=True
        ).order_by('-start_date').first()

    @staticmethod
    def get_salary_by_id(salary_id):
        """Return a specific contract."""
        return Salary.objects.filter(id=salary_id).first()

    @staticmethod
    def get_salaries_for_period(employee_id, start_date, end_date):
        """Retrieve contracts for an employee that overlap a given period."""
        return Salary.objects.filter(
            employee_id=employee_id,
            start_date__lt=end_date,
            end_date__gt=start_date
        )

    @staticmethod
    def get_latest_salary(employee_id):
        """Return the latest active contract of an employee."""
        return Salary.objects.filter(
            employee_id=employee_id, 
            is_active=True
        ).order_by('-start_date').first()


class SalaryWriterService:
    """
    Service to manage creation and modification of contracts.
    All business rules are enforced here.
    """

    @staticmethod
    @transaction.atomic
    def create_salary(
        employee,
        payment_type,
        payment_period,
        contract_type,
        base_salary=None,
        hourly_rate=None,
        start_date=None,
        end_date=None,
        deduct_late=False,
        pay_overtime=False,
        allow_advance=False,
        comments=None
    ):
        # Check for overlapping contracts
        overlapping = Salary.objects.filter(employee=employee, is_active=True)
        if overlapping.exists():
            raise ValidationError(
                "The employee already has an active contract during this period."
            )

        # Validate dates
        if contract_type != ContractType.CDI and end_date is None:
            raise ValidationError("End date is required for non-CDI contracts.")

        if contract_type != ContractType.CDI and start_date >= end_date:
            raise ValidationError("Start date must be before end date.")

        # Create salary object
        salary = Salary(
            employee=employee,
            payment_type=payment_type,
            payment_period=payment_period,
            contract_type=contract_type,
            base_salary=base_salary,
            hourly_rate=hourly_rate,
            start_date=start_date,
            end_date=end_date,
            deduct_late=deduct_late,
            pay_overtime=pay_overtime,
            allow_advance=allow_advance,
            comments=comments.strip() if comments else None,
            is_active=True
        )

        # Generate code
        salary.code = f"C-{get_rotate_value()}{get_next_value(get_contract_seq_key()):05d}"

        salary.save()
        return salary

    @staticmethod
    @transaction.atomic
    def update_salary(salary: Salary, **kwargs):
        """Update a contract while enforcing business rules."""
        for field, value in kwargs.items():
            setattr(salary, field, value)

        # Check for overlapping contracts
        overlapping = Salary.objects.filter(
            employee=salary.employee,
            is_active=True
        ).exclude(id=salary.id)
        if overlapping.exists():
            raise ValidationError(
                "The employee already has an active contract during this period."
            )

        # Validate dates
        if salary.contract_type != ContractType.CDI:
            if salary.end_date is None:
                raise ValidationError("End date is required for non-CDI contracts.")
            if salary.start_date >= salary.end_date:
                raise ValidationError("Start date must be before end date.")


        salary.save()
        return salary

    @staticmethod
    @transaction.atomic
    def close_salary(salary: Salary):
        """Close a contract and notify if necessary."""
        salary.is_active = False
        salary.save()
        # Here, a notification service could be called
        # NotificationService.notify_contract_closed(salary)
