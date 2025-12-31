from uuid import UUID
from ninja import Query
from ninja.pagination import paginate
from ninja.errors import HttpError
from ninja_extra import api_controller, route
from django.core.exceptions import ObjectDoesNotExist

from hr.employees.models import Employee
from hr.leaves.services import (
    LeaveReaderService,
    LeaveWriterService,
)
from hr.leaves.schemas import (
    LeaveDetailOut,
    LeaveCreateIn,
    LeaveUpdateIn,
    LeaveFilterIn,
    LeaveCreateEmployeesIn,
)
from hr.leaves.exceptions import (
    LeaveOverlapError,
    LeaveValidationError,
    LeaveWorkflowError,
)
from oxutils.pagination.cursor import CursorPagination




@api_controller("/leaves", tags=["Leaves"])
class LeaveAPI:
    """
    Leave API Controller
    - Thin layer
    - Zero business logic
    """

    # ---------- Reads ----------

    @route.get("/{leave_id}", response=LeaveDetailOut)
    def get_leave(self, request, leave_id: UUID):
        try:
            leave = LeaveReaderService.get_leave(leave_id)
            return {
                **leave.__dict__,
                "total_days": leave.total_days,
            }
        except ObjectDoesNotExist:
            raise HttpError(404, "Leave not found")

    @route.get("/", response=list[LeaveDetailOut])
    @paginate(CursorPagination)
    def get_leaves(self, request, filters: LeaveFilterIn = Query(...)):
        # The service now returns the filtered queryset directly
        qs = LeaveReaderService.get_leaves(filters=filters)
        
        # Note: If your LeaveDetailOut has a 'total_days' field, 
        # Ninja can often call the model method automatically.
        return qs

    # ---------- Creation ----------

    @route.post("/global", response=LeaveDetailOut)
    def add_global_leave(self, request, payload: LeaveCreateIn):
        try:
            leave = LeaveWriterService.add_global_leave(**payload.dict())
            return {
                **leave.__dict__,
                "total_days": leave.total_days,    
            }
        except LeaveOverlapError as e:
            raise HttpError(409, str(e))

    @route.post("/employees", response=LeaveDetailOut)
    def add_leave_for_employees(self, request, payload: LeaveCreateEmployeesIn):
        try:
            employees = Employee.objects.filter(id__in=payload.employee_ids)
            leave = LeaveWriterService.add_leave_for_employees(
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
                "total_days": leave.total_days,
            }
        except LeaveOverlapError as e:
            raise HttpError(409, str(e))
        except LeaveValidationError as e:
            raise HttpError(400, str(e))

    # ---------- Update ----------

    @route.patch("/{leave_id}", response=LeaveDetailOut) 
    def update_leave(request, leave_id: UUID, payload: LeaveUpdateIn):
        """
        Update a leave record. Validates overlaps before saving.
        """
        try:
            leave = LeaveWriterService.update_leave(
                leave_id=leave_id,
                **payload.dict(exclude_unset=True),  # only fields provided in the request
            )

            # Return the leave with computed total_days
            return {
                **leave.__dict__,
                "total_days": leave.total_days,
            }

        except ObjectDoesNotExist:
            raise HttpError(404, "Leave not found")
        except LeaveOverlapError as e:
            raise HttpError(409, str(e))    

    # ---------- Workflow ----------

    @route.post("/{leave_id}/approve", response=LeaveDetailOut)
    def approve_leave(self, request, leave_id: UUID):
        try:
            leave = LeaveWriterService.approve(leave_id, request.user)
            return {
                **leave.__dict__,
                "total_days": leave.total_days(),
            }
        except ObjectDoesNotExist:
            raise HttpError(404, "Leave not found")
        except LeaveWorkflowError as e:
            raise HttpError(400, str(e))
        except LeaveOverlapError as e:
            raise HttpError(409, str(e))

    @route.post("/{leave_id}/reject", response=LeaveDetailOut)
    def reject_leave(self, request, leave_id: UUID):
        try:
            leave = LeaveWriterService.reject(leave_id)
            return {
                **leave.__dict__,
                "total_days": leave.total_days(),
            }
        except ObjectDoesNotExist:
            raise HttpError(404, "Leave not found")
        except LeaveWorkflowError as e:
            raise HttpError(400, str(e))

    @route.post("/{leave_id}/cancel", response=LeaveDetailOut)
    def cancel_leave(self, request, leave_id: UUID):
        try:
            leave = LeaveWriterService.cancel(leave_id)
            return {
                **leave.__dict__,
                "total_days": leave.total_days(),
            }
        except ObjectDoesNotExist:
            raise HttpError(404, "Leave not found")
        except LeaveWorkflowError as e:
            raise HttpError(400, str(e))

    # ---------- Deletion ----------

    @route.delete("/{leave_id}")
    def delete_leave(self, request, leave_id: UUID):
        try:
            LeaveWriterService.remove_leave(leave_id)
            return {"success": True, "id": leave_id}
        except ObjectDoesNotExist:
            raise HttpError(404, "Leave not found")
