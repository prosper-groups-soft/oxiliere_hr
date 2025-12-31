from django.db import transaction
from django.db.models import Count
from hr.employees.models import Employee
from hr.leaves.models import Leave, LeaveEmployee
from hr.leaves.exceptions import (
    LeaveValidationError,
    LeaveOverlapError,
    LeaveWorkflowError
)
from hr.leaves.choices import LeaveStatus
from .base import LeaveOverlapService


class LeaveEmployeeReaderService:
    """Read-only access layer for LeaveEmployee relations."""

    @staticmethod
    def base_queryset():
        """Base queryset with required joins for read operations."""
        return LeaveEmployee.objects.select_related("leave", "employee")

    @classmethod
    def get_by_id(cls, pk):
        """Return a single LeaveEmployee by primary key."""
        return cls.base_queryset().get(id=pk)

    @classmethod
    def list_by_employee(cls, employee: Employee):
        """List all leave assignments for a given employee."""
        return cls.base_queryset().filter(employee=employee)

    @classmethod
    def list_by_leave(cls, leave: Leave):
        """List all employees assigned to a given leave."""
        return cls.base_queryset().filter(leave=leave)

    @classmethod
    def list_by_period(cls, start_date, end_date):
        """List assignments whose leave overlaps a given period."""
        return cls.base_queryset().filter(
            leave__start_date__lte=end_date,
            leave__end_date__gte=start_date,
        )

    @classmethod
    def search(cls, *, employee=None, leave_status=None):
        """Search assignments using optional employee or leave status filters."""
        qs = cls.base_queryset()
        if employee:
            qs = qs.filter(employee=employee)
        if leave_status:
            qs = qs.filter(leave__status=leave_status)
        return qs

    @classmethod
    def stats_by_employee(cls):
        """Return assignment count grouped by employee."""
        return (
            cls.base_queryset()
            .values("employee_id")
            .annotate(total=Count("id"))
        )


class LeaveEmployeeWriterService:
    """Write layer handling mutations and business rules for LeaveEmployee."""

    @classmethod
    @transaction.atomic
    def assign(cls, leave: Leave, employee: Employee, created_by=None):
        """Assign an employee to a leave after business validations."""
        if leave.everyone:
            raise LeaveValidationError("Impossible d'affecter un congé global")

        # Prevent overlapping leaves for the same employee
        if LeaveOverlapService.has_overlap(
            employee=employee,
            start_date=leave.start_date,
            end_date=leave.end_date,
            exclude_leave=leave,
        ):
            raise LeaveOverlapError(f"Chevauchement pour {employee}")

        return LeaveEmployee.objects.create(
            leave=leave,
            employee=employee,
            created_by=created_by,
        )

    @classmethod
    @transaction.atomic
    def bulk_assign(cls, leave: Leave, employees, created_by=None):
        """Assign multiple employees to the same leave."""
        for employee in employees:
            cls.assign(leave, employee, created_by)

    @classmethod
    @transaction.atomic
    def unassign(cls, leave: Leave, employee: Employee):
        """Remove an employee from a leave if workflow allows it."""
        if leave.status == LeaveStatus.APPROVED.value:
            raise LeaveWorkflowError(
                "Impossible de modifier un congé approuvé"
            )
        LeaveEmployee.objects.filter(
            leave=leave, 
            employee=employee
        ).delete()

    @classmethod
    @transaction.atomic
    def reassign(
        cls,
        leave: Leave,
        old_employee: Employee,
        new_employee: Employee,
        created_by=None,
    ):
        """Replace one employee assignment with another."""
        cls.unassign(leave, old_employee)
        return cls.assign(leave, new_employee, created_by)

    @classmethod
    @transaction.atomic
    def cleanup_orphans(cls):
        """Remove orphan LeaveEmployee records."""
        LeaveEmployee.objects.filter(leave__isnull=True).delete()

