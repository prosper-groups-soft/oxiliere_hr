from hr.payroll.models import BonusEmployee
from django.db import transaction, IntegrityError
from django.core.exceptions import ValidationError
from hr.payroll.models import BonusEmployee, Bonus
from hr.employees.models import Employee



class BonusEmployeeWriterService:
    """
    Write service for BonusEmployee relations.
    Handles all business rules.
    """

    @staticmethod
    @transaction.atomic
    def assign_bonus_to_employee(employee: Employee, bonus: Bonus, created_by):
        """
        Assign a bonus to an employee.
        """
        if bonus.everyone:
            raise ValidationError(
                "This bonus applies to everyone; manual assignment is not allowed."
            )

        try:
            return BonusEmployee.objects.create(
                employee=employee,
                bonus=bonus,
                created_by=created_by
            )
        except IntegrityError:
            raise ValidationError(
                "This employee already has this bonus."
            )

    @staticmethod
    @transaction.atomic
    def remove_bonus_from_employee(employee: Employee, bonus: Bonus):
        """
        Remove a bonus from an employee.
        """
        if bonus.everyone:
            raise ValidationError(
                "This bonus applies to everyone; manual removal is not allowed."
            )

        deleted_count, _ = BonusEmployee.objects.filter(
            employee=employee,
            bonus=bonus
        ).delete()

        return deleted_count > 0

    @staticmethod
    @transaction.atomic
    def bulk_assign(bonus: Bonus, employees: Employee, created_by):
        """
        Assign a bonus to multiple employees.
        """
        if bonus.everyone:
            raise ValidationError(
                "This bonus applies to everyone; bulk assignment is not allowed."
            )

        existing_employee_ids = BonusEmployee.objects.filter(
            bonus=bonus
        ).values_list('employee_id', flat=True)

        new_relations = [
            BonusEmployee(
                employee=employee,
                bonus=bonus,
                created_by=created_by
            )
            for employee in employees
            if employee.id not in existing_employee_ids
        ]

        BonusEmployee.objects.bulk_create(new_relations)
        return len(new_relations)

    @staticmethod
    @transaction.atomic
    def bulk_remove(bonus: Bonus, employees: Employee):
        """
        Remove a bonus from multiple employees.
        """
        if bonus.everyone:
            raise ValidationError(
                "This bonus applies to everyone; bulk removal is not allowed."
            )

        employee_ids = [employee.id for employee in employees]

        deleted_count, _ = BonusEmployee.objects.filter(
            bonus=bonus,
            employee_id__in=employee_ids
        ).delete()

        return deleted_count


class BonusEmployeeReaderService:
    """
    Read-only service for BonusEmployee relations.
    """

    @staticmethod
    def get_by_id(bonus_employee_id):
        """Return a BonusEmployee relation by its ID."""
        return BonusEmployee.objects.filter(id=bonus_employee_id).first()

    @staticmethod
    def get_by_employee(employee_id):
        """Return all bonus relations for a given employee."""
        return BonusEmployee.objects.filter(
            employee_id=employee_id
        ).select_related('employee', 'bonus')

    @staticmethod
    def get_by_bonus(bonus_id):
        """Return all employee relations for a given bonus."""
        return BonusEmployee.objects.filter(
            bonus_id=bonus_id
        ).select_related('employee', 'bonus')

    @staticmethod
    def exists(employee_id, bonus_id):
        """Check if a bonus is already assigned to an employee."""
        return BonusEmployee.objects.filter(
            employee_id=employee_id,
            bonus_id=bonus_id
        ).exists()

