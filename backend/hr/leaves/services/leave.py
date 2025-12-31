from typing import Optional, Iterable
from uuid import UUID
from django.db import transaction
from django.db.models import Q, Count, F, Sum
from django.utils import timezone
from django.db.models import QuerySet

from hr.utils.fn import update_instance
from hr.leaves.models import Leave, LeaveEmployee
from hr.leaves.choices import LeaveStatus
from hr.employees.models import Employee
from hr.leaves.schemas import LeaveFilterIn
from hr.leaves.exceptions import (
    LeaveOverlapError, 
    LeaveValidationError,
    LeaveWorkflowError
)

from .base import LeaveOverlapService



class LeaveReaderService:
    """Read-only service for leave data."""

    @staticmethod
    def base_queryset() -> QuerySet[Leave]:
        return (
            Leave.objects
            .select_related("approved_by")
            .prefetch_related("leaves_employees__employee")
        )

    # ---- Single reads ----
    @staticmethod
    def get_leave(leave_id: UUID) -> Leave:
        return LeaveReaderService.base_queryset().get(id=leave_id)

    # ---- Lists ----
    @staticmethod
    def get_globals_leaves() -> QuerySet[Leave]:
        return LeaveReaderService.base_queryset().filter(everyone=True)

    @staticmethod
    def get_leaves_for_employee(employee_id: UUID) -> QuerySet[Leave]:
        Employee.objects.get(id=employee_id)  # ensure exists
        return LeaveReaderService.base_queryset().filter(
            Q(everyone=True) | Q(leaves_employees__employee_id=employee_id)
        ).distinct()

    # ---- Filtered / search ----
    @staticmethod
    def get_leaves(*, filters: LeaveFilterIn) -> QuerySet[Leave]:
        """
        Search leaves using FilterSchema logic.
        """
        qs = LeaveReaderService.base_queryset()
        return filters.filter(qs)

    # ---- Aggregations ----
    @staticmethod
    def total_days_for_employee(employee_id: UUID) -> int:
        qs = LeaveReaderService.get_leaves_for_employee(employee_id)
        qs = qs.filter(status=LeaveStatus.APPROVED.value)
        total = qs.aggregate(total_days=Sum(F("end_date") - F("start_date")))["total_days"]
        return total.days if total else 0

    @classmethod
    def stats_by_status(cls) -> QuerySet:
        return cls.base_queryset().values("status").annotate(total=Count("id"))


class LeaveWriterService:
    """Write and workflow service for leave management."""

    # ---- Overlap validation ----
    @staticmethod
    def _validate_overlap_for_employees(
        *, 
        employees: Iterable[Employee], 
        start_date, 
        end_date, 
        exclude_leave: Optional[Leave] = None
    ):
        has_overlapped = LeaveOverlapService.has_overlap_bulk(
            employees=employees,
            start_date=start_date,
            end_date=end_date,
            exclude_leave=exclude_leave,
        )   
        
        if has_overlapped:
            raise LeaveOverlapError(
                f"Overlap detected for one or more employees between {start_date} and {end_date}"
            )

    # ---- Creation ----
    @staticmethod
    @transaction.atomic
    def add_global_leave(*, start_date, end_date, leave_type, paid, reason: Optional[str] = None) -> Leave:
        employees = Employee.objects.all()
        LeaveWriterService._validate_overlap_for_employees(
            employees=employees, 
            start_date=start_date, 
            end_date=end_date
        )

        leave = Leave(
            start_date=start_date, 
            end_date=end_date, 
            leave_type=leave_type, 
            paid=paid, 
            everyone=True, 
            reason=reason
        )
        leave.full_clean()
        leave.save()
        return leave

    @staticmethod
    @transaction.atomic
    def add_leave_for_employees(
        *, 
        start_date, 
        end_date, 
        leave_type, 
        paid, 
        employees: Iterable[Employee], 
        reason: Optional[str] = None, 
        created_by=None
    ) -> Leave:
        if not employees:
            raise LeaveValidationError("No employees provided")

        LeaveWriterService._validate_overlap_for_employees(
            employees=employees, 
            start_date=start_date, 
            end_date=end_date
        )

        leave = Leave(
            start_date=start_date, 
            end_date=end_date, 
            leave_type=leave_type, 
            paid=paid, 
            everyone=False, 
            reason=reason
        )
        leave.full_clean()
        leave.save()

        # bulk assignment
        LeaveEmployee.objects.bulk_create([
            LeaveEmployee(leave=leave, employee=emp, created_by=created_by)
            for emp in employees
        ])
        return leave

    # ---- Update ----
    @staticmethod
    @transaction.atomic
    def update_leave(leave_id: UUID, **kwargs) -> Leave:
        """
        Updates allowed fields of a leave record.
        Validates overlap for employees before saving.
        """
        # Retrieve the leave instance
        leave = Leave.objects.get(id=leave_id)

        # Allowed fields for update
        allowed_fields = {
            "start_date",
            "end_date",
            "leave_type",
            "paid",
            "reason",
        }

        # Prepare the updated values for validation
        updated_data = {field: kwargs.get(field, getattr(leave, field)) for field in allowed_fields}

        # Check overlaps if dates are updated
        if "start_date" in kwargs or "end_date" in kwargs:
            if leave.everyone:
                employees = Employee.objects.all()
            else:
                employees = Employee.objects.filter(leaves__id=leave.id)

            LeaveWriterService._validate_overlap_for_employees(
                employees=employees,
                start_date=updated_data["start_date"],
                end_date=updated_data["end_date"],
                exclude_leave=leave,
            )

        # Apply updates using the helper
        return update_instance(
            instance=leave,
            allowed_fields=allowed_fields,
            data=kwargs,
        )

    # ---- Assignment ----
    @staticmethod
    @transaction.atomic
    def assign_employee(leave_id: UUID, employee: Employee, created_by=None) -> LeaveEmployee:
        leave = LeaveReaderService.get_leave(leave_id)

        if leave.everyone:
            raise LeaveValidationError("Cannot assign employees to a global leave")

        LeaveWriterService._validate_overlap_for_employees(
            employees=[employee], 
            start_date=leave.start_date, 
            end_date=leave.end_date
        )

        return LeaveEmployee.objects.create(
            leave=leave, 
            employee=employee, 
            created_by=created_by
        )

    @staticmethod
    @transaction.atomic
    def assign_employees_bulk(
        leave_id: UUID, 
        employees: Iterable[Employee], 
        created_by=None
    ):
        leave = LeaveReaderService.get_leave(leave_id)
        
        if leave.everyone:
            raise LeaveValidationError("Cannot assign employees to a global leave")

        LeaveWriterService._validate_overlap_for_employees(
            employees=employees, 
            start_date=leave.start_date, 
            end_date=leave.end_date
        )
        LeaveEmployee.objects.bulk_create([
            LeaveEmployee(leave=leave, employee=emp, created_by=created_by)
            for emp in employees
        ])

    @staticmethod
    @transaction.atomic
    def sync_employees(leave_id: UUID, employees: Iterable[Employee], created_by=None):
        leave = LeaveReaderService.get_leave(leave_id)
        
        if leave.everyone:
            raise LeaveValidationError("Cannot sync employees on a global leave")

        # remove employees not in the new list
        LeaveEmployee.objects.filter(leave=leave).exclude(employee__in=employees).delete()

        existing = set(LeaveEmployee.objects.filter(leave=leave).values_list("employee_id", flat=True))
        new_assignments = []
        for emp in employees:
            if emp.id not in existing:
                new_assignments.append(
                    LeaveEmployee(
                        leave=leave, 
                        employee=emp, 
                        created_by=created_by
                    )
                )

        LeaveEmployee.objects.bulk_create(new_assignments)

    # ---- Workflow ----
    @staticmethod
    @transaction.atomic
    def approve(leave_id: UUID, approver: Employee) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)

        if leave.status != LeaveStatus.PENDING.value:
            raise LeaveWorkflowError("Leave cannot be approved")

        if leave.everyone:
            employees = Employee.objects.all()
        else:
            employees = Employee.objects.filter(leaves__id=leave.id)  # ensure at least one employee assigned

        LeaveWriterService._validate_overlap_for_employees(
            employees=employees, 
            start_date=leave.start_date, 
            end_date=leave.end_date, 
            exclude_leave=leave
        )

        leave.status = LeaveStatus.APPROVED.value
        leave.approved_by = approver
        leave.approved_at = timezone.now()
        leave.full_clean()
        leave.save()
        return leave

    @staticmethod
    @transaction.atomic
    def reject(leave_id: UUID) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)
        
        if leave.status != LeaveStatus.PENDING.value:
            raise LeaveWorkflowError("Leave cannot be rejected")

        leave.status = LeaveStatus.REJECTED.value
        leave.full_clean()
        leave.save()
        return leave

    @staticmethod
    @transaction.atomic
    def cancel(leave_id: UUID) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)
        
        if leave.status != LeaveStatus.APPROVED.value:
            raise LeaveWorkflowError("Leave cannot be cancelled")

        leave.status = LeaveStatus.CANCELLED.value
        leave.full_clean()
        leave.save()
        return leave

    @staticmethod
    @transaction.atomic
    def reset_to_pending(leave_id: UUID) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)
        leave.status = LeaveStatus.PENDING.value
        leave.approved_by = None
        leave.approved_at = None
        leave.full_clean()
        leave.save()
        return leave

    # ---- Removals ----
    @staticmethod
    @transaction.atomic
    def remove_employee(leave_id: UUID, employee: Employee):
        leave = LeaveReaderService.get_leave(leave_id)
        LeaveEmployee.objects.filter(leave=leave, employee=employee).delete()

    @staticmethod
    @transaction.atomic
    def remove_leave(leave_id: UUID):
        leave = LeaveReaderService.get_leave(leave_id)
        leave.delete()
