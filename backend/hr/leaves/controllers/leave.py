import logging
from injector import inject
from uuid     import UUID
from typing   import List

from django.core.exceptions import ValidationError
from django.shortcuts       import get_object_or_404
from ninja                  import File, Query
from ninja.files            import UploadedFile
from ninja.pagination       import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_put,
    ControllerBase,
)
from oxutils.pagination.cursor import CursorPagination

from hr.employees.models import Employee
from oxutils.permissions.perms import ScopePermission
from hr.leaves.models    import (
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
    LeaveTransactionFilter,
    LeaveBalanceSummary
)
# Cache integration
from hr.services.cache_helpers import cache_api_response
from hr.leaves.services.cache  import LeaveCacheService



logger = logging.getLogger(__name__)


@api_controller('/leaves', tags=['Leave Management'])
class LeaveController(ControllerBase):
    """ Manages employee leave applications, entitlements, and usage history. """

    @inject
    def __init__(
        self,
        request_service: LeaveRequestService,
        balance_service: BalanceService,
    ):
        self.request_service = request_service
        self.balance_service = balance_service

    # ------------------ Leave Requests ------------------

    @http_post('/requests', response={201: LeaveRequestOut}, permissions=[ScopePermission('leaves:w')])
    def create_leave_request(
        self,
        data: LeaveRequestCreate,
        attachment: File[UploadedFile] = None,
    ):
        """ Submits a new leave request for the authenticated employee. """
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
            return 201, request_obj
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)
        
    @http_post('/requests/employee/{employee_id}', response={201: LeaveRequestOut}, permissions=[ScopePermission('leaves:w')])
    def create_leave_request_for_employee(
        self,
        employee_id: UUID,
        data: LeaveRequestCreate,
        attachment: File[UploadedFile] = None,
    ):
        """ Submits a leave request on behalf of a specific employee. """
        actor = self.context.request.user
        employee = get_object_or_404(Employee, id=employee_id)

        payload = data.model_dump()
        if attachment:
            payload["attachment"] = attachment

        return 201, self.request_service.create_request(
            employee=employee,
            data=payload,
            creator=actor,
        )

    @http_get('/requests', response=List[LeaveRequestOut], permissions=[ScopePermission('leaves:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24, key_prefix="leave_requests_list", user_specific=True)
    def list_requests(self, filters: LeaveRequestFilter = Query(...)):
        """ Lists and filters leave requests across the organization. """
        qs = LeaveRequest.objects.select_related('employee', 'employee__user').all()
        return filters.filter(qs)

    @http_get('/requests/{request_id}', response=LeaveRequestOut, permissions=[ScopePermission('leaves:r')])
    def get_leave_request(self, request_id: UUID):
        """ Retrieves the details of a specific leave request. """
        return get_object_or_404(LeaveRequest, id=request_id)

    @http_post('/requests/{request_id}/approve', response=LeaveRequestOut, permissions=[ScopePermission('leaves:u')])
    def approve_request(self, request_id: UUID):
        """ Formally approves a leave request and updates the employee's balance. """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.approve_request(leave_request, user=actor)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/requests/{request_id}/reject', response=LeaveRequestOut, permissions=[ScopePermission('leaves:u')])
    def reject_request(self, request_id: UUID, reason: str = None):
        """ Rejects a pending leave request with an optional explanation. """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.reject_request(leave_request, user=actor, reason=reason)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/requests/{request_id}/cancel', response=LeaveRequestOut, permissions=[ScopePermission('leaves:u')])
    def cancel_request(self, request_id: UUID):
        """ Rescinds a leave request and restores any deducted balance. """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.cancel_request(leave_request, user=actor)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/requests/{request_id}/mark-taken', response=LeaveRequestOut, permissions=[ScopePermission('leaves:u')])
    def mark_taken_request(self, request_id: UUID):
        """ Archives an approved leave request that has already passed. """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        try:
            return self.request_service.mark_taken_request(leave_request)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/requests/{request_id}/recall', response=LeaveRecallOut, permissions=[ScopePermission('leaves:u')])
    def recall_employee(self, request_id: UUID, data: LeaveRecallCreate):
        """ Records an employee's premature return to work from an active leave. """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.recall_employee(
                leave_request=leave_request,
                recall_date=data.recall_date,
                reason=data.reason,
                recalled_by=actor,
            )
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    # ------------------ Leave Balances ------------------

    @http_get('/balances', response=List[LeaveBalanceOut], permissions=[ScopePermission('leaves:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24, key_prefix="leave_balances_list", user_specific=True)
    def list_balances(self, filters: LeaveBalanceFilter = Query(...)):
        """ Views current leave entitlements and usage for all employees. """
        qs = LeaveBalance.objects.select_related('employee').all()
        return filters.filter(qs)

    @http_post('/balances/init/{employee_id}', response=LeaveBalanceOut, permissions=[ScopePermission('leaves:w')])
    def initialize_balance(self, employee_id: UUID, year: int = None):
        """ Sets up or resets the annual leave entitlement for a specific employee. """
        employee = get_object_or_404(Employee, id=employee_id)
        return self.balance_service.init_employee_balance(employee, year)

    @http_get('/balances/summary/{employee_id}', response=LeaveBalanceSummary)
    def get_balance_summary(self, employee_id: UUID, year: int = None):
        """ Displays a detailed breakdown of an employee's total available leave days. """
        employee = get_object_or_404(Employee, id=employee_id)
        
        if not year:
            from django.utils import timezone
            year = timezone.now().year

        balance_data = LeaveCacheService.get_leave_balance_dict(employee, year)
        
        if not balance_data:
            balance_obj = self.balance_service.init_employee_balance(employee, year)
            if balance_obj:
                 balance_data = LeaveCacheService.get_leave_balance_dict(employee, year)
        
        if not balance_data:
             return self.create_response({"detail": "Balance summary unavailable"}, status_code=400)

        return balance_data

    # ------------------ HR Updates ------------------

    @http_patch('/requests/{request_id}/hr-update', response=LeaveRequestOut)
    def update_request_by_hr(self, request_id: UUID, data: LeaveRequestUpdate):
        """ Allows HR to adjust the parameters of an existing leave request. """
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
        request_id: UUID,
        file: UploadedFile = File(...),
    ):
        """ Uploads or updates supporting documentation for a leave request. """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        actor = self.context.request.user
        try:
            return self.request_service.add_attachment(leave_request, file, actor)
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    # ------------------ Leave Transactions ------------------

    @http_get('/transactions', response=List[LeaveTransactionOut])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24, key_prefix="leave_transactions_list", user_specific=True)
    def list_transactions(self, filters: LeaveTransactionFilter = Query(...)):
        """ Views the audit trail of all manual and automatic leave balance movements. """
        qs = LeaveTransaction.objects.select_related('employee', 'leave_request').all()
        return filters.filter(qs)

