from typing import Optional, List
from datetime import date
from uuid import UUID
import logging
from injector import inject

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from ninja_extra import (
    api_controller, 
    ControllerBase, 
    http_post
)

from hr.employees.models import Employee
from hr.leaves.models import LeaveRequest
from hr.leaves.services import LeaveRequestService
from hr.leaves.schemas import (
    BatchLeaveRequestCreate,
    BatchLeaveRequestResult, 
    BatchLeaveRequestReport,
    BatchActionSchema
)


logger = logging.getLogger(__name__)


@api_controller("/leaves/batch", tags=["Leave Management - Batch"])
class LeaveBatchController(ControllerBase):
    """
    Controller dedicated to batch operations on leave requests.
    """

    @inject
    def __init__(self, leave_request_service: LeaveRequestService):
        self.leave_request_service = leave_request_service    
    
    @http_post("/requests/batch", response=BatchLeaveRequestReport)
    def create_leave_requests_batch(self, data: BatchLeaveRequestCreate):
        """
        HR/Admin: create multiple leave requests at once.
        Returns a report indicating success or failure for each request.
        """
        user = self.context.request.user
        report = []

        for item in data.requests:
            try:
                employee = get_object_or_404(Employee, id=item.employee_id)
                payload = item.model_dump(exclude={"employee_id"})
                leave_request = self.leave_request_service.create_request(
                    employee=employee,
                    data=payload,
                    creator=user
                )
                report.append(BatchLeaveRequestResult(
                    employee_id=item.employee_id,
                    success=True,
                    leave_request_id=leave_request.id
                ))
            except ValidationError as e:
                report.append(BatchLeaveRequestResult(
                    employee_id=item.employee_id,
                    success=False,
                    error=str(e)
                ))
            except Exception as e:
                report.append(BatchLeaveRequestResult(
                    employee_id=item.employee_id,
                    success=False,
                    error=str(e)
                ))

        return {"results": report}

    # --- Internal helper for DRY ---
    def _process_batch(
        self,
        request_ids: List[UUID],
        action: str,
        reason: Optional[str] = None,
        recall_date: Optional[date] = None
    ) -> BatchLeaveRequestReport:
        """
        Internal method to perform batch actions on leave requests.
        Supported actions: approve, reject, cancel, recall.
        """
        report = []

        for request_id in request_ids:
            try:
                leave_request = get_object_or_404(LeaveRequest, id=request_id)
                user = self.context.request.user

                if action == "approve":
                    self.leave_request_service.approve_request(leave_request, user=user)
                elif action == "reject":
                    self.leave_request_service.reject_request(leave_request, user=user, reason=reason)
                elif action == "cancel":
                    self.leave_request_service.cancel_request(leave_request, user=user)
                elif action == "recall":
                    if not recall_date:
                        raise ValidationError("recall_date is required for recall action")
                    self.leave_request_service.recall_employee(
                        leave_request=leave_request,
                        recall_date=recall_date,
                        reason=reason or "Batch recall",
                        recalled_by=user
                    )
                else:
                    raise ValidationError(f"Unknown batch action: {action}")

                report.append(BatchLeaveRequestResult(
                    employee_id=leave_request.employee.id,
                    success=True,
                    leave_request_id=leave_request.id
                ))

            except ValidationError as e:
                report.append(BatchLeaveRequestResult(
                    employee_id=getattr(leave_request, "employee", None).id if 'leave_request' in locals() else None,
                    success=False,
                    error=str(e)
                ))
            except Exception as e:
                report.append(BatchLeaveRequestResult(
                    employee_id=getattr(leave_request, "employee", None).id if 'leave_request' in locals() else None,
                    success=False,
                    error=str(e)
                ))

        return {"results": report}

    # --- Batch endpoints ---
    @http_post("/approve", response=BatchLeaveRequestReport)
    def approve_batch(self, data: BatchActionSchema):
        """
        Approve multiple leave requests in a single operation.
        """
        return self._process_batch(data.request_ids, action="approve")

    @http_post("/reject", response=BatchLeaveRequestReport)
    def reject_batch(self, data: BatchActionSchema):
        """
        Reject multiple leave requests in a single operation.
        """
        return self._process_batch(data.request_ids, action="reject", reason=data.reason)

    @http_post("/cancel", response=BatchLeaveRequestReport)
    def cancel_batch(self, data: BatchActionSchema):
        """
        Cancel multiple leave requests in a single operation.
        """
        return self._process_batch(data.request_ids, action="cancel")

    @http_post("/recall", response=BatchLeaveRequestReport)
    def recall_batch(self, data: BatchActionSchema):
        """
        Recall multiple employees from leave in a single operation.
        """
        return self._process_batch(
            data.request_ids,
            action="recall",
            reason=data.reason,
            recall_date=data.recall_date
        )

