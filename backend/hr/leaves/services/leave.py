from typing import Optional, Iterable
from uuid import UUID
from django.db import transaction
from django.db.models import Q, Count, F, Sum
from django.utils import timezone
from django.db.models import QuerySet

from hr.leaves.models import Leave, LeaveEmployee
from hr.leaves.enums import LeaveStatus
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
    @classmethod
    def get_leave(cls, leave_id: UUID) -> Leave:
        return cls.base_queryset().get(id=leave_id)

    # ---- Lists ----
    @classmethod
    def get_globals_leaves(cls) -> QuerySet[Leave]:
        return cls.base_queryset().filter(everyone=True)

    @classmethod
    def get_leaves_for_employee(cls, employee_id: UUID) -> QuerySet[Leave]:
        Employee.objects.get(id=employee_id)  # ensure exists
        return cls.base_queryset().filter(
            Q(everyone=True) | Q(leaves_employees__employee_id=employee_id)
        ).distinct()

    # ---- Filtered / search ----
    @classmethod
    def get_leaves(cls, *, filters: LeaveFilterIn) -> QuerySet[Leave]:
        qs = cls.base_queryset()

        if filters.status:
            qs = qs.filter(status=filters.status)
        if filters.leave_type:
            qs = qs.filter(leave_type=filters.leave_type)
        if filters.paid is not None:
            qs = qs.filter(paid=filters.paid)
        if filters.approver_id:
            qs = qs.filter(approved_by_id=filters.approver_id)
        if filters.employee_id:
            qs = qs.filter(leaves_employees__employee_id=filters.employee_id)
        if filters.start_date and filters.end_date:
            qs = qs.filter(start_date__lte=filters.end_date, end_date__gte=filters.start_date)
        if filters.search:
            qs = qs.filter(reason__icontains=filters.search)
        if filters.everyone is not None:
            qs = qs.filter(everyone=filters.everyone)

        return qs.distinct()

    # ---- Aggregations ----
    @classmethod
    def total_days_for_employee(cls, employee_id: UUID) -> int:
        qs = cls.get_leaves_for_employee(employee_id).filter(status=LeaveStatus.APPROVED.value)
        total = qs.aggregate(total_days=Sum(F("end_date") - F("start_date")))["total_days"]
        return total.days if total else 0

    @classmethod
    def stats_by_status(cls) -> QuerySet:
        return cls.base_queryset().values("status").annotate(total=Count("id"))


class LeaveWriterService:
    """Write and workflow service for leave management."""

    # ---- Overlap validation ----
    @classmethod
    def _validate_overlap_for_employees(
        cls,
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
    @classmethod
    @transaction.atomic
    def add_global_leave(
        cls, 
        *, 
        start_date, 
        end_date, 
        leave_type,
        paid, 
        reason: Optional[str] = None
    ) -> Leave:
        employees = Employee.objects.all()
        cls._validate_overlap_for_employees(
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

    @classmethod
    @transaction.atomic
    def add_leave_for_employees(
        cls, 
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

        cls._validate_overlap_for_employees(
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
    @classmethod
    @transaction.atomic
    def update_leave(
        cls, 
        leave_id: UUID, 
        *, 
        start_date=None, 
        end_date=None, 
        leave_type=None, 
        paid=None, 
        reason=None
    ) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)

        if start_date:
            leave.start_date = start_date
        if end_date:
            leave.end_date = end_date
        if leave_type:
            leave.leave_type = leave_type
        if paid is not None:
            leave.paid = paid
        if reason:
            leave.reason = reason

        if start_date or end_date:
            if leave.everyone:
                employees = Employee.objects.all()
            else:
                employees = Employee.objects.filter(leaves__id=leave.id)

            cls._validate_overlap_for_employees(
                employees=employees, 
                start_date=leave.start_date, 
                end_date=leave.end_date, 
                exclude_leave=leave
            )

        leave.full_clean()
        leave.save()
        return leave

    # ---- Assignment ----
    @classmethod
    @transaction.atomic
    def assign_employee(cls, leave_id: UUID, employee: Employee, created_by=None) -> LeaveEmployee:
        leave = LeaveReaderService.get_leave(leave_id)

        if leave.everyone:
            raise LeaveValidationError("Cannot assign employees to a global leave")

        cls._validate_overlap_for_employees(
            employees=[employee], 
            start_date=leave.start_date, 
            end_date=leave.end_date
        )

        return LeaveEmployee.objects.create(
            leave=leave, 
            employee=employee, 
            created_by=created_by
        )

    @classmethod
    @transaction.atomic
    def assign_employees_bulk(
        cls, 
        leave_id: UUID, 
        employees: Iterable[Employee], 
        created_by=None
    ):
        leave = LeaveReaderService.get_leave(leave_id)
        
        if leave.everyone:
            raise LeaveValidationError("Cannot assign employees to a global leave")

        cls._validate_overlap_for_employees(
            employees=employees, 
            start_date=leave.start_date, 
            end_date=leave.end_date
        )
        LeaveEmployee.objects.bulk_create([
            LeaveEmployee(leave=leave, employee=emp, created_by=created_by)
            for emp in employees
        ])

    @classmethod
    @transaction.atomic
    def sync_employees(cls, leave_id: UUID, employees: Iterable[Employee], created_by=None):
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
    @classmethod
    @transaction.atomic
    def approve(cls, leave_id: UUID, approver: Employee) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)

        if leave.status != LeaveStatus.PENDING.value:
            raise LeaveWorkflowError("Leave cannot be approved")

        if leave.everyone:
            employees = Employee.objects.all()
        else:
            employees = Employee.objects.filter(leaves__id=leave.id)  # ensure at least one employee assigned

        cls._validate_overlap_for_employees(
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

    @classmethod
    @transaction.atomic
    def reject(cls, leave_id: UUID) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)
        
        if leave.status != LeaveStatus.PENDING.value:
            raise LeaveWorkflowError("Leave cannot be rejected")

        leave.status = LeaveStatus.REJECTED.value
        leave.full_clean()
        leave.save()
        return leave

    @classmethod
    @transaction.atomic
    def cancel(cls, leave_id: UUID) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)
        
        if leave.status != LeaveStatus.APPROVED.value:
            raise LeaveWorkflowError("Leave cannot be cancelled")

        leave.status = LeaveStatus.CANCELLED.value
        leave.full_clean()
        leave.save()
        return leave

    @classmethod
    @transaction.atomic
    def reset_to_pending(cls, leave_id: UUID) -> Leave:
        leave = LeaveReaderService.get_leave(leave_id)
        leave.status = LeaveStatus.PENDING.value
        leave.approved_by = None
        leave.approved_at = None
        leave.full_clean()
        leave.save()
        return leave

    # ---- Removals ----
    @classmethod
    @transaction.atomic
    def remove_employee(cls, leave_id: UUID, employee: Employee):
        leave = LeaveReaderService.get_leave(leave_id)
        LeaveEmployee.objects.filter(leave=leave, employee=employee).delete()

    @classmethod
    @transaction.atomic
    def remove_leave(cls, leave_id: UUID):
        leave = LeaveReaderService.get_leave(leave_id)
        leave.delete()
