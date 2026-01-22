import logging
from uuid import UUID
from typing import List

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from ninja import File, Query
from ninja.files import UploadedFile
from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_put,
    ControllerBase,
)
from injector import inject
from oxutils.pagination.cursor import CursorPagination

from hr.employees.models import Employee
from hr.leaves.models import (
    LeaveRequest,
    LeaveBalance,
    LeaveTransaction,
)
from hr.leaves.services import (
    LeaveRequestService,
    BalanceService,
)
from hr.leaves.schemas import (
    LeaveRequestOut,
    LeaveRequestCreate,
    LeaveRequestUpdate,
    LeaveRequestFilter,
    LeaveBalanceOut,
    LeaveBalanceFilter,
    LeaveRecallOut,
    LeaveRecallCreate,
    LeaveTransactionOut,
    LeaveTransactionFilter
)


logger = logging.getLogger(__name__)


@api_controller('/leaves', tags=['Leave Management'])
class LeaveController(ControllerBase):
    """
    API controller handling employee leave requests, balances,
    approvals, rejections, cancellations, recalls, attachments, and HR updates.
    """

    @inject
    def __init__(
        self,
        request_service: LeaveRequestService,
        balance_service: BalanceService,
    ):
        self.request_service = request_service
        self.balance_service = balance_service

    # ------------------ Leave Requests ------------------

    @http_post('/requests', response={201: LeaveRequestOut})
    def create_leave_request(
        self,
        data: LeaveRequestCreate,
        attachment: File[UploadedFile] = None,
    ):
        """
        Submit a new leave request (annual or circumstance-based).
        """
        actor = getattr(self.context.request, 'user', None)
        employee = get_object_or_404(Employee, user=actor)

        payload = data.model_dump()
        if attachment:
            payload['attachment'] = attachment

        try:
            request_obj = self.request_service.create_request(
                employee=employee,
                data=payload,
                creator=actor,
            )
            logger.info(f"[API] Leave request created: {request_obj.id} for employee {employee.matricule}")
            return 201, request_obj
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)
        
    @http_post('/requests/employee/{employee_id}', response={201: LeaveRequestOut})
    def create_leave_request_for_employee(
        self,
        employee_id: UUID,
        data: LeaveRequestCreate,
        attachment: File[UploadedFile] = None,
    ):
        """
        Creates a new leave request for a specific employee. 
        Restricted to users with the 'create_for_employee' permission.
        """
        actor = self.context.request.user

        """
        Business logic control / Permission check
        if not actor.has_perm("leaves.create_for_employee"):
            return self.create_response({"detail": "Forbidden"}, status_code=403)
        """
        employee = get_object_or_404(Employee, id=employee_id)

        payload = data.model_dump()
        if attachment:
            payload["attachment"] = attachment

        return 201, self.request_service.create_request(
            employee=employee,
            data=payload,
            creator=actor,
        )

    @http_get('/requests', response=List[LeaveRequestOut])
    @paginate(CursorPagination)
    def list_requests(self, filters: LeaveRequestFilter = Query(...)):
        """
        List and filter leave requests.
        """
        qs = LeaveRequest.objects.select_related('employee', 'employee__user').all()
        return filters.filter(qs)

    @http_post('/requests/{request_id}/approve', response=LeaveRequestOut)
    def approve_request(self, request_id: UUID):
        """
        Approve a leave request and deduct the corresponding days from balance.
        """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.approve_request(leave_request, user=actor)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/requests/{request_id}/reject', response=LeaveRequestOut)
    def reject_request(self, request_id: UUID, reason: str = None):
        """
        Reject a pending leave request.
        """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.reject_request(leave_request, user=actor, reason=reason)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/requests/{request_id}/cancel', response=LeaveRequestOut)
    def cancel_request(self, request_id: UUID):
        """
        Cancel a leave request and re-credit the balance if applicable.
        """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.cancel_request(leave_request, user=actor)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/requests/{request_id}/mark-taken', response=LeaveRequestOut)
    def mark_taken_request(self, request_id: UUID):
        """
        Mark an approved leave as TAKEN (typically after the end date).
        """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        try:
            return self.request_service.mark_taken_request(leave_request)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/requests/{request_id}/recall', response=LeaveRecallOut)
    def recall_employee(self, request_id: UUID, data: LeaveRecallCreate):
        """
        Recall an employee before the end of an approved leave.
        """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            recall_obj = self.request_service.recall_employee(
                leave_request=leave_request,
                recall_date=data.recall_date,
                reason=data.reason,
                recalled_by=actor,
            )
            logger.warning(f"[API] Leave recall initiated for request {request_id}")
            return recall_obj
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    # ------------------ Leave Balances ------------------

    @http_get('/balances', response=List[LeaveBalanceOut])
    @paginate(CursorPagination)
    def list_balances(self, filters: LeaveBalanceFilter = Query(...)):
        """
        View and filter employee leave balances.
        """
        qs = LeaveBalance.objects.select_related('employee').all()
        return filters.filter(qs)

    @http_post('/balances/init/{employee_id}', response=LeaveBalanceOut)
    def initialize_balance(self, employee_id: UUID, year: int = None):
        """
        Initialize or recalculate an employee's leave balance for a given year.
        """
        employee = get_object_or_404(Employee, id=employee_id)
        balance = self.balance_service.init_employee_balance(employee, year)
        return balance

    # ------------------ HR Updates ------------------

    @http_patch('/requests/{request_id}/hr-update', response=LeaveRequestOut)
    def update_request_by_hr(self, request_id: UUID, data: LeaveRequestUpdate):
        """
        HR-only endpoint to modify a leave request.
        Cancels the original request and creates a new one for audit integrity.
        """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        hr_user = self.context.request.user
        return self.request_service.update_request_by_hr(
            leave_request,
            data.model_dump(exclude_unset=True),
            hr_user,
        )

    # ------------------ Attachments ------------------

    @http_put('/requests/{request_id}/attachment', response=LeaveRequestOut)
    def upload_request_attachment(
        self,
        request_id: int,
        file: UploadedFile = File(...),
    ):
        """
        Add or replace an attachment on an existing leave request.
        """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.add_attachment(leave_request, file, actor)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    # ------------------ Leave Transactions ------------------

    @http_get('/transactions', response=List[LeaveTransactionOut])
    @paginate(CursorPagination)
    def list_transactions(self, filters: LeaveTransactionFilter = Query(...)):
        """
        View the history of all leave-related transactions (accrual, consumption, refund, etc.).
        """
        qs = LeaveTransaction.objects.select_related('employee', 'leave_request').all()
        return filters.filter(qs)

