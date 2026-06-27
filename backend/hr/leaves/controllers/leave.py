import logging
from injector import inject
from datetime import date, timedelta    
from uuid     import UUID
from typing   import List
from collections import OrderedDict
from django.utils import timezone

from django.core.exceptions import ValidationError
from django.shortcuts       import get_object_or_404
from ninja                  import File, Query
from ninja.files            import UploadedFile
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_put,
    ControllerBase,
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
)

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
from hr.attendance.services import SchedulingService
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
    LeaveBalanceSummary,
    WorkingDaysCountOut,
    OverlappingLeavesCheckOut,
    PendingCountOut,
    TeamPlannerEmployeeOut,
)
from hr.leaves.enums import LeaveCategory, LeaveStatus

# Cache integration
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

        request_obj = self.request_service.create_request(
            employee=employee,
            data=payload,
            creator=actor,
        )

        # Invalidate balance cache so reserved (pending) days reflect immediately
        LeaveCacheService.clear_employee_balances_cache(str(employee.id))

        return 201, request_obj

    @http_get('/requests', response=PaginatedResponseSchema[LeaveRequestOut], permissions=[ScopePermission('leaves:r')])
    @paginate(PageNumberPaginationExtra)
    def list_requests(
        self,
        filters: LeaveRequestFilter = Query(...),
        ordering: str = Query(None, description="Sort by: employee_name, -employee_name, start_date, -start_date, requested_days, -requested_days, created_at, -created_at"),
    ):
        """ Lists and filters leave requests across the organization. """
        qs = LeaveRequest.objects.select_related('employee', 'employee__user') \
            .prefetch_related('employee__position_history').all()

        # Apply filters from the schema
        qs = filters.filter(qs)

        # Apply ordering/sorting
        qs = filters.apply_ordering(qs, ordering)

        return qs

    @http_get('/requests/pending-count', response=PendingCountOut, permissions=[ScopePermission('leaves:r')])
    def get_pending_count(self):
        """ Returns the total number of pending leave requests. """
        qs = LeaveRequest.objects.filter(status=LeaveStatus.PENDING)
        return {'count': qs.count()}

    @http_get('/team-planner', response=List[TeamPlannerEmployeeOut], permissions=[ScopePermission('leaves:r')])
    def get_team_planner(
        self,
        year: int = Query(None),
        month: int = Query(None),
    ):
        """ Returns all non-rejected leave requests for a given month (team Gantt view),
            expanded per-day and grouped by employee. """
        now = timezone.now()
        y = year or now.year
        m = month or now.month

        month_start = date(y, m, 1)
        if m == 12:
            month_end = date(y + 1, 1, 1)
        else:
            month_end = date(y, m + 1, 1)

        qs = LeaveRequest.objects\
            .select_related('employee', 'employee__user')\
            .prefetch_related('employee__position_history')\
            .exclude(status=LeaveStatus.REJECTED)\
            .filter(start_date__lt=month_end, end_date__gte=month_start)

        # Expand days and group by employee
        employees_map: dict[UUID, dict] = OrderedDict()

        for req in qs:
            emp = req.employee
            emp_id = emp.id

            if emp_id not in employees_map:
                from hr.employees.schemas import _get_current_pos
                pos = _get_current_pos(emp)
                employees_map[emp_id] = {
                    'employee_id': emp_id,
                    'employee_name': ' '.join(p for p in [emp.last_name, emp.middle_name, emp.first_name] if p),
                    'org_unit': pos.org_unit.name if pos and pos.org_unit else None,
                    'avatar_url': emp.profile_photo.url if emp.profile_photo else None,
                    'days': [],
                }

            # Expand date range into individual days within this month
            day_start = max(req.start_date, month_start)
            day_end = min(req.end_date, month_end - timedelta(days=1))
            d = day_start
            while d <= day_end:
                employees_map[emp_id]['days'].append({
                    'date': d.isoformat(),
                    'type': req.category,
                    'status': req.status,
                })
                d += timedelta(days=1)

        return list(employees_map.values())

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
    @paginate(PageNumberPaginationExtra)
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
    def update_request_by_hr(
        self,
        request_id: UUID,
        data: LeaveRequestUpdate,
        attachment: File[UploadedFile] = None,
    ):
        """ Allows HR to adjust the parameters of an existing leave request. """
        leave_request = get_object_or_404(LeaveRequest, id=request_id)
        hr_user = self.context.request.user
        dump = data.model_dump(exclude_unset=True)
        if attachment:
            dump['attachment'] = attachment
        return self.request_service.update_request_by_hr(
            leave_request,
            dump,
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

    @http_get('/working-days-count', response=WorkingDaysCountOut, permissions=[ScopePermission('leaves:r')])
    def count_working_days(
        self,
        employee_id: UUID,
        start_date: date,
        end_date: date,
    ):
        """
        Returns a detailed day-by-day working status breakdown for a date range.
        Used by the LeaveRequestSheet frontend to preview working days.
        Delegates to SchedulingService.get_working_days_breakdown().
        """
        employee = get_object_or_404(Employee, id=employee_id)
        return SchedulingService.get_working_days_breakdown(employee, start_date, end_date)

    @http_get('/overlap-check', response=OverlappingLeavesCheckOut, permissions=[ScopePermission('leaves:r')])
    def check_overlapping_leaves(
        self,
        employee_id: UUID,
        start_date: date,
        end_date: date,
        excluded_categories: str = None,
    ):
        """
        Checks for any leave requests that overlap with the given period.

        Used by the LeaveRequestSheet frontend to warn about conflicts in real time.

        Accepts an optional comma-separated `excluded_categories` parameter to
        exclude specific categories from the overlap check. For example, when
        creating a sick leave, pass `excluded_categories=ANNUAL,CIRCUMSTANCE,UNPAID`
        to only check conflicts with other sick leaves (per business rules:
        illness can overlap with planned leave, but two sick leaves cannot).
        """
        employee = get_object_or_404(Employee, id=employee_id)

        qs = LeaveRequest.objects.filter(
            employee=employee,
            status__in=[LeaveStatus.PENDING, LeaveStatus.APPROVED],
            start_date__lte=end_date,
            end_date__gte=start_date,
        )

        if excluded_categories:
            exclude_list = [c.strip() for c in excluded_categories.split(',')]
            qs = qs.exclude(category__in=exclude_list)

        leaves = []
        for req in qs:
            leaves.append({
                'id': req.id,
                'category': req.category,
                'start_date': req.start_date,
                'end_date': req.end_date,
                'requested_days': int(req.requested_days),
                'status': req.status,
            })

        return {
            'hasOverlap': len(leaves) > 0,
            'leaves': leaves,
        }

    # Leave Transactions

    @http_get('/transactions', response=List[LeaveTransactionOut])
    @paginate(PageNumberPaginationExtra)
    def list_transactions(self, filters: LeaveTransactionFilter = Query(...)):
        """ Views the audit trail of all manual and automatic leave balance movements. """
        qs = LeaveTransaction.objects.select_related('employee', 'leave_request').all()
        return filters.filter(qs)

