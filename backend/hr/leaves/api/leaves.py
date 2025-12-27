from uuid import UUID
from ninja_extra import api_controller, route
from django.shortcuts import get_object_or_404

from hr.leaves.models import Leave
from hr.employees.models import Employee
from hr.leaves.services import (
    LeaveReaderService,
    LeaveWriterService,
)
from hr.leaves.schemas import (
    LeaveDetailOut,
    LeaveCreateIn,
    LeaveUpdateIn,
    LeaveCreateGlobalIn,
    LeaveCreateEmployeesIn,
    LeaveFilterIn,
)


@api_controller("/leaves", tags=["Leaves"])
class LeaveController:
    """
    Leave API Controller
    - Thin layer
    - Zero business logic
    """

    # ---------- Reads ----------

    @route.get("/", response=list[LeaveDetailOut])
    def list_leaves(self, request, filters: LeaveFilterIn):
        qs = LeaveReaderService.filter(
            status=filters.status,
            leave_type=filters.leave_type,
            paid=filters.paid,
            employee=(
                Employee.objects.get(id=filters.employee_id)
                if filters.employee_id else None
            ),
            search=filters.search,
        )
        return [
            {
                **leave.__dict__,
                "total_days": leave.total_days(),
            }
            for leave in qs
        ]

    @route.get("/{leave_id}", response=LeaveDetailOut)
    def get_leave(self, request, leave_id: UUID):
        leave = LeaveReaderService.get_by_id(leave_id)
        return {
            **leave.__dict__,
            "total_days": leave.total_days(),
        }

    # ---------- Creation ----------

    @route.post("/global", response=LeaveOut)
    def create_global_leave(self, request, payload: LeaveCreateGlobalIn):
        leave = LeaveWriterService.create_global_leave(**payload.dict())
        return {
            **leave.__dict__,
            "total_days": leave.total_days(),
        }

    @route.post("/employees", response=LeaveOut)
    def create_leave_for_employees(
        self,
        request,
        payload: LeaveCreateEmployeesIn,
    ):
        employees = Employee.objects.filter(id__in=payload.employee_ids)
        leave = LeaveWriterService.create_leave_for_employees(
            start_date=payload.start_date,
            end_date=payload.end_date,
            leave_type=payload.leave_type,
            paid=payload.paid,
            employees=employees,
            reason=payload.reason,
            created_by=request.user,
        )
        return {
            **leave.__dict__,
            "total_days": leave.total_days(),
        }

    # ---------- Workflow ----------

    @route.post("/{leave_id}/approve", response=LeaveOut)
    def approve_leave(self, request, leave_id: int):
        leave = get_object_or_404(Leave, id=leave_id)
        leave = LeaveWriterService.approve(leave, request.user)
        return {
            **leave.__dict__,
            "total_days": leave.total_days(),
        }

    @route.post("/{leave_id}/reject", response=LeaveOut)
    def reject_leave(self, request, leave_id: int):
        leave = get_object_or_404(Leave, id=leave_id)
        leave = LeaveWriterService.reject(leave)
        return {
            **leave.__dict__,
            "total_days": leave.total_days(),
        }

    @route.post("/{leave_id}/cancel", response=LeaveOut)
    def cancel_leave(self, request, leave_id: int):
        leave = get_object_or_404(Leave, id=leave_id)
        leave = LeaveWriterService.cancel(leave)
        return {
            **leave.__dict__,
            "total_days": leave.total_days(),
        }
