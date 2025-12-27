from django.db import transaction
from django.db.models import Q, Sum, Count, F
from django.utils import timezone
from hr.leaves.models import Leave, LeaveEmployee
from hr.leaves.enums import LeaveStatus
from hr.employees.models import Employee
from hr.leaves.exceptions import (
    LeaveOverlapError,
    LeaveValidationError,
    LeaveWorkflowError,
)
from .base import LeaveOverlapService


class LeaveReaderService:
    """Read-only service for leave data (no side effects)."""

    @staticmethod
    def base_queryset():
        """Return an optimized queryset for read operations."""
        return (
            Leave.objects
            .select_related("approved_by")
            .prefetch_related("leaves_employees__employee")
        )

    # ---- Single reads ----
    @classmethod
    def get_by_id(cls, leave_id):
        """Retrieve a leave by its database ID."""
        return cls.base_queryset().get(id=leave_id)

    @classmethod
    def get_by_uuid(cls, uuid):
        """Retrieve a leave by its UUID."""
        return cls.base_queryset().get(uuid=uuid)

    # ---- Lists ----
    @classmethod
    def list_all(cls):
        """Return all leaves."""
        return cls.base_queryset()

    @classmethod
    def list_globals(cls):
        """Return leaves applied to everyone."""
        return cls.base_queryset().filter(everyone=True)

    @classmethod
    def list_for_employee(cls, employee: Employee):
        """Return leaves visible for a given employee."""
        return cls.base_queryset().filter(
            Q(everyone=True) |
            Q(leaves_employees__employee=employee)
        ).distinct()

    # ---- Filters / search ----
    @classmethod
    def filter(
        cls,
        *,
        status=None,
        leave_type=None,
        paid=None,
        approver=None,
        employee=None,
        start_date=None,
        end_date=None,
        search=None,
    ):
        """Multi-criteria search over leaves."""
        qs = cls.base_queryset()

        if status:
            qs = qs.filter(status=status)
        if leave_type:
            qs = qs.filter(leave_type=leave_type)
        if paid is not None:
            qs = qs.filter(paid=paid)
        if approver:
            qs = qs.filter(approved_by=approver)
        if employee:
            qs = qs.filter(leaves_employees__employee=employee)
        if start_date and end_date:
            qs = qs.filter(start_date__lte=end_date, end_date__gte=start_date)
        if search:
            qs = qs.filter(reason__icontains=search)

        return qs.distinct()

    # ---- Aggregations ----
    @classmethod
    def total_days_for_employee(cls, employee: Employee):
        """Prepare approved leave day calculations for an employee."""
        return (
            cls.list_for_employee(employee)
            .filter(status=LeaveStatus.APPROVED.value)
            .annotate(days=F("end_date") - F("start_date"))
        )

    @classmethod
    def stats_by_status(cls):
        """Return global leave statistics grouped by status."""
        return cls.base_queryset().values("status").annotate(total=Count("id"))


class LeaveWriterService:
    """Write and workflow service for leave management."""

    # ---- Creation ----
    @classmethod
    @transaction.atomic
    def create_global_leave(
        cls,
        *,
        start_date,
        end_date,
        leave_type,
        paid,
        reason=None,
    ):
        """Create a global leave applied to all employees."""
        leave = Leave(
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            paid=paid,
            everyone=True,
            reason=reason,
        )
        leave.full_clean()
        leave.save()
        return leave

    @classmethod
    @transaction.atomic
    def create_leave_for_employees(
        cls,
        *,
        start_date,
        end_date,
        leave_type,
        paid,
        employees,
        reason=None,
        created_by=None,
    ):
        """Create a leave and assign it to specific employees."""
        if not employees:
            raise LeaveValidationError("No employees provided")

        leave = Leave(
            start_date=start_date,
            end_date=end_date,
            leave_type=leave_type,
            paid=paid,
            everyone=False,
            reason=reason,
        )
        leave.full_clean()
        leave.save()

        for employee in employees:
            if LeaveOverlapService.has_overlap(
                employee=employee,
                start_date=start_date,
                end_date=end_date,
            ):
                raise LeaveOverlapError(f"Overlap detected for {employee}")

            LeaveEmployee.objects.create(
                leave=leave,
                employee=employee,
                created_by=created_by,
            )

        return leave

    # ---- Assignment ----
    @classmethod
    @transaction.atomic
    def assign_employee(
        cls, 
        leave: Leave, 
        employee: Employee, 
        created_by=None
    ):
        """Assign an employee to an existing leave."""
        if leave.everyone:
            raise LeaveValidationError(
                "Cannot assign employees to a global leave"
            )

        if LeaveOverlapService.has_overlap(
            employee=employee,
            start_date=leave.start_date,
            end_date=leave.end_date,
        ):
            raise LeaveOverlapError(f"Overlap detected for {employee}")

        return LeaveEmployee.objects.create(
            leave=leave,
            employee=employee,
            created_by=created_by,
        )

    @classmethod
    @transaction.atomic
    def assign_employees_bulk(cls, leave: Leave, employees, created_by=None):
        """Assign multiple employees to a leave."""
        for employee in employees:
            cls.assign_employee(leave, employee, created_by)

    @classmethod
    @transaction.atomic
    def remove_employee(cls, leave: Leave, employee: Employee):
        """Remove an employee from a leave."""
        LeaveEmployee.objects.filter(leave=leave, employee=employee).delete()

    @classmethod
    @transaction.atomic
    def sync_employees(cls, leave: Leave, employees, created_by=None):
        """Synchronize the exact list of employees assigned to a leave."""
        if leave.everyone:
            raise LeaveValidationError("Cannot sync employees on a global leave")

        LeaveEmployee.objects.filter(
            leave=leave
        ).exclude(employee__in=employees).delete()
        existing = set(
            LeaveEmployee.objects.filter(
                leave=leave
            ).values_list("employee_id", flat=True)
        )

        for employee in employees:
            if employee.id not in existing:
                cls.assign_employee(leave, employee, created_by)

    # ---- Workflow ----
    @classmethod
    @transaction.atomic
    def approve(cls, leave: Leave, approver):
        """Approve a leave after all business validations."""
        if leave.status != LeaveStatus.PENDING.value:
            raise LeaveWorkflowError("Leave cannot be approved")

        employees = (
            Employee.objects.all()
            if leave.everyone
            else Employee.objects.filter(leaves__id=leave.id)
        )

        for emp in employees:
            if LeaveOverlapService.has_overlap(
                employee=emp,
                start_date=leave.start_date,
                end_date=leave.end_date,
                exclude_leave=leave,
            ):
                raise LeaveOverlapError(f"Overlap detected for {emp}")

        leave.status = LeaveStatus.APPROVED.value
        leave.approved_by = approver
        leave.approved_at = timezone.now()
        leave.full_clean()
        leave.save()
        return leave

    @classmethod
    @transaction.atomic
    def reject(cls, leave: Leave):
        """Reject a pending leave."""
        if leave.status != LeaveStatus.PENDING.value:
            raise LeaveWorkflowError("Leave cannot be rejected")

        leave.status = LeaveStatus.REJECTED.value
        leave.full_clean()
        leave.save()
        return leave

    @classmethod
    @transaction.atomic
    def cancel(cls, leave: Leave):
        """Cancel an already approved leave."""
        if leave.status != LeaveStatus.APPROVED.value:
            raise LeaveWorkflowError("Leave cannot be cancelled")

        leave.status = LeaveStatus.CANCELLED.value
        leave.full_clean()
        leave.save()
        return leave

    @classmethod
    @transaction.atomic
    def reset_to_pending(cls, leave: Leave):
        """Reset a leave back to the pending state."""
        leave.status = LeaveStatus.PENDING.value
        leave.approved_by = None
        leave.approved_at = None
        leave.full_clean()
        leave.save()
        return leave
