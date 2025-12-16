from typing import Optional
from django.db import transaction
from django.db import models
from django.core.exceptions import ValidationError
from hr.jobs.models import (
    EmployeePositionHistory, 
    Position, 
    Department
)
from hr.employees.models import Employee


# -------------------------------------------------------------------
# EmployeePositionHistory Reader / Writer Services
# -------------------------------------------------------------------
class EmployeePositionHistoryWriter:
    """
    Writer for EmployeePositionHistory: create, update, close current position, 
    promote/demote helper.
    Business rules implemented here:
      - Prevent overlapping active periods for the same employee unless explicitly 
        allowed.
      - When creating a new active position (end_date is None), optionally close 
        previous active period.
      - Promotion helper: create new history entry with a higher-level position 
        while closing previous.
    """

    @staticmethod
    def _has_overlap(
        employee: Employee, 
        start_date, 
        end_date, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Checks whether a given period overlaps existing history records for the employee.
        """
        qs = EmployeePositionHistory.objects.filter(employee=employee)
        if exclude_id:
            qs = qs.exclude(id=exclude_id)
        if end_date:
            return qs.filter(
                models.Q(start_date__lte=end_date) & models.Q(end_date__gte=start_date)
            ).exists()
        else:
            # new open-ended period overlaps if any history intersects start_date OR has no end_date
            return qs.filter(models.Q(end_date__isnull=True) | models.Q(end_date__gte=start_date)).exists()

    @staticmethod
    @transaction.atomic
    def create(
        employee: Employee, 
        position: Position, 
        department: Optional[Department] = None,
               start_date = None, end_date = None, description: Optional[str] = None,
               close_previous: bool = True) -> EmployeePositionHistory:
        """
        Create a career history record. If close_previous=True and start_date provided,
        the current active record (end_date is None) will be closed the day before new start_date.
        Throws ValidationError if overlap detected.
        """
        # Validate overlap
        if start_date and EmployeePositionHistoryWriter._has_overlap(employee, start_date, end_date):
            raise ValidationError("The provided period overlaps an existing EmployeePositionHistory.")

        # Optionally close previous active history
        if close_previous:
            current = EmployeePositionHistory.objects.filter(employee=employee, end_date__isnull=True).first()
            if current:
                # close the current to the day before new start_date or today if no start_date
                if start_date:
                    current.end_date = start_date
                else:
                    from django.utils import timezone
                    current.end_date = timezone.now().date()
                current.save()

        eph = EmployeePositionHistory(
            employee=employee,
            position=position,
            department=department,
            start_date=start_date,
            end_date=end_date,
            description=description
        )
        eph.full_clean()
        eph.save()
        return eph

    @staticmethod
    @transaction.atomic
    def update(history_id: int, **kwargs) -> EmployeePositionHistory:
        """
        Update an EmployeePositionHistory record. Validates overlap when changing dates.
        """
        eph = EmployeePositionHistory.objects.get(id=history_id)

        start_date = kwargs.get("start_date", eph.start_date)
        end_date = kwargs.get("end_date", eph.end_date)

        if EmployeePositionHistoryWriter._has_overlap(eph.employee, start_date, end_date, exclude_id=eph.id):
            raise ValidationError("The updated period would overlap an existing EmployeePositionHistory.")

        for field, value in kwargs.items():
            if hasattr(eph, field):
                setattr(eph, field, value)
        eph.full_clean()
        eph.save()
        return eph

    @staticmethod
    @transaction.atomic
    def close_current(employee: Employee, end_date = None) -> Optional[EmployeePositionHistory]:
        """
        Closes the current active position (end_date is null) for the employee by setting end_date.
        Returns the closed record or None if none active.
        """
        current = EmployeePositionHistory.objects.filter(employee=employee, end_date__isnull=True).first()
        if not current:
            return None
        if end_date is None:
            from django.utils import timezone
            end_date = timezone.now().date()
        current.end_date = end_date
        current.save()
        return current

    @staticmethod
    @transaction.atomic
    def promote(employee: Employee, new_position: Position, start_date = None, department: Optional[Department] = None, description: Optional[str] = None) -> EmployeePositionHistory:
        """
        Promote an employee by closing current active record and creating a new one with new_position.
        Ensures the level difference or business validations should be applied in caller or extended here.
        """
        # close current
        EmployeePositionHistoryWriter.close_current(employee, end_date=(start_date or None))
        # create new
        return EmployeePositionHistoryWriter.create(
            employee=employee,
            position=new_position,
            department=department,
            start_date=start_date,
            end_date=None,
            description=description,
            close_previous=False
        )

    @staticmethod
    @transaction.atomic
    def delete(history_id: int) -> None:
        eph = EmployeePositionHistory.objects.get(id=history_id)
        eph.delete()


class EmployeePositionHistoryReader:
    """
    Reader for EmployeePositionHistory: retrieval, listing and simple analytics helpers.
    """

    @staticmethod
    def get(history_id: int) -> Optional[EmployeePositionHistory]:
        return EmployeePositionHistory.objects.filter(id=history_id).select_related("position", "department", "employee").first()

    @staticmethod
    def list_for_employee(employee_id: int):
        return EmployeePositionHistory.objects.filter(employee_id=employee_id).select_related("position", "department").order_by("-start_date")

    @staticmethod
    def current_for_employee(employee_id: int) -> Optional[EmployeePositionHistory]:
        return EmployeePositionHistory.objects.filter(employee_id=employee_id, end_date__isnull=True).select_related("position", "department").first()

    @staticmethod
    def list_by_position(position_id: int):
        return EmployeePositionHistory.objects.filter(position_id=position_id).select_related("employee", "department")

