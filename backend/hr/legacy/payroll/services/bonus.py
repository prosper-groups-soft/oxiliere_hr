from django.db import transaction
from django.core.exceptions import ValidationError
from hr.employees.models import Employee
from hr.payroll.models import Bonus, BonusEmployee


class BonusReaderService:
    """
    Service to read/retrieve bonuses.
    """

    @staticmethod
    def get_active_bonuses():
        """Return all active bonuses."""
        return Bonus.objects.filter(is_active=True).order_by('-created_at')

    @staticmethod
    def get_bonus_by_id(bonus_id):
        """Return a specific bonus by its ID."""
        return Bonus.objects.filter(id=bonus_id).first()

    @staticmethod
    def get_bonuses_for_employee(employee_id):
        """Return all bonuses applicable to a specific employee."""
        return Bonus.objects.filter(
            applicable_to__id=employee_id,
            is_active=True
        )

    @staticmethod
    def get_always_apply_bonuses():
        """Return bonuses that always apply to all eligible employees."""
        return Bonus.objects.filter(always_apply=True, is_active=True)


class BonusWriterService:
    """
    Service to manage creation, updating, and assignment of bonuses.
    All business rules are applied here.
    """

    @staticmethod
    @transaction.atomic
    def create_bonus(
        bonus_type,
        amount,
        name=None,
        always_apply=False,
        everyone=False,
        start_date=None,
        end_date=None,
        description=None
    ):
        """Create a new bonus."""
        bonus = Bonus(
            bonus_type=bonus_type,
            amount=amount,
            name=name,
            always_apply=always_apply,
            everyone=everyone,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        bonus.clean()
        bonus.save()
        return bonus

    @staticmethod
    @transaction.atomic
    def update_bonus(bonus: Bonus, **kwargs):
        """Update an existing bonus with business rules."""
        for field, value in kwargs.items():
            setattr(bonus, field, value)
        bonus.clean()
        bonus.save()
        return bonus

    @staticmethod
    @transaction.atomic
    def add_employees_to_bonus(bonus: Bonus, employee_ids, created_by_user):
        """Assign employees to a bonus, checking business rules."""
        if bonus.everyone:
            raise ValidationError(
                "This bonus applies to all employees, cannot add specific ones."
            )
        if not employee_ids:
            return []
        
        existing_employee_ids = bonus.bonus_employees.values_list('employee__id', flat=True)
        new_employee_ids = [eid for eid in employee_ids if eid not in existing_employee_ids]
        new_employees = Employee.objects.filter(id__in=new_employee_ids)
        bonus_employee_instances = [
            BonusEmployee(employee=emp, bonus=bonus, created_by=created_by_user)
            for emp in new_employees
        ]
        BonusEmployee.objects.bulk_create(bonus_employee_instances)
        return new_employee_ids

    @staticmethod
    @transaction.atomic
    def remove_employees_from_bonus(bonus: Bonus, employee_ids, created_by_user):
        """Remove employees from a bonus."""
        if bonus.everyone:
            raise ValidationError(
                "This bonus applies to all employees, cannot remove specific ones."
            )
        if not employee_ids:
            return []
        
        existing_employee_ids = bonus.bonus_employees.values_list('employee__id', flat=True)
        ids_to_remove = [eid for eid in employee_ids if eid in existing_employee_ids]
        bonus.bonus_employees.filter(employee__id__in=ids_to_remove).delete()
        return ids_to_remove

    @staticmethod
    @transaction.atomic
    def reset_bonus(bonus: Bonus, created_by_user):
        """Remove all employee assignments and reset the bonus to non-everyone."""
        bonus.everyone = False
        bonus.bonus_employees.all().delete()
        bonus.updated_by = created_by_user
        bonus.save(update_fields=['everyone', 'updated_by'])
        return bonus
