import logging 
from typing   import Optional, List
from uuid     import UUID
from datetime import date
from injector import inject

from django.shortcuts import get_object_or_404
from django.utils     import timezone
from django.db.models import Q, Prefetch
from ninja            import Query
from ninja_extra      import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_delete,
    ControllerBase,
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
)
from oxutils.pagination.cursor import CursorPagination
from oxutils.permissions.perms import ScopePermission

from hr.employees.models    import Employee, StatusHistory
from hr.jobs.models         import EmployeePositionHistory
from hr.attendance.services import SchedulingService
from hr.attendance.models   import ShiftPolicy, EmploymentScheme
from hr.attendance.schemas  import (
    ShiftPolicyOut,
    ShiftPolicyCreateIn,
    ShiftPolicyUpdateIn,
    EmploymentSchemeAssignIn,
    EmploymentSchemeUpdateIn,
    AssignmentFilterIn,
    WeeklyPlanningOut,
    RotationCreateIn,
    RotationBackfillIn,
    WorkingDaysPreviewOut,
    WorkingDayCheckOut,
    EmploymentSchemeOut,
)
# Cache integration
from hr.services.cache_helpers import cache_api_response
from hr.attendance.services    import AttendanceCacheService


logger = logging.getLogger(__name__)


@api_controller('/scheduling', tags=['Schedules & Rotations'])
class SchedulingController(ControllerBase):
    """ API controller for shift policy management, employee scheduling, and rotation setup. """

    @inject
    def __init__(self, scheduling_service: SchedulingService):
        self.scheduling_service = scheduling_service

    @http_post('/shifts', response={201: ShiftPolicyOut}, permissions=[ScopePermission('attendance:w')])
    def create_policy(self, data: ShiftPolicyCreateIn):
        """ Creates a new shift policy with a complete weekly configuration. """
        logger.info(
            "Shift policy creation requested",
            extra={
                "policy_name": data.name,
                "weekly_target_hours": data.weekly_target_hours,
            },
        )

        try:
            policy = self.scheduling_service.create_full_policy(
                name=data.name,
                description=data.description,
                weekly_target_hours=data.weekly_target_hours,
                daily_configs=data.daily_configs,
            )

            logger.info(
                "Shift policy successfully created",
                extra={
                    "policy_id": str(policy.id),
                    "policy_name": policy.name,
                },
            )

            return 201, policy

        except Exception:
            logger.exception(
                "Error while creating shift policy",
                extra={"policy_name": data.name},
            )
            return self.create_response(
                {"detail": "Unable to create shift policy"},
                status_code=400,
            )

    @http_get('/shifts', response=PaginatedResponseSchema[ShiftPolicyOut], permissions=[ScopePermission('attendance:r')])
    @paginate(func_or_pgn_class= PageNumberPaginationExtra, page_size=200)
    @cache_api_response(timeout=60*60, key_prefix="policy_list", user_specific=False)
    def list_policies(self):
        """ Retrieves a list of all available shift policies. """
        return ShiftPolicy.objects.all()
    
    @http_patch('/policies/{policy_id}', response={200: ShiftPolicyOut}, permissions=[ScopePermission('attendance:u')])
    def update_policy(self, policy_id: UUID, data: ShiftPolicyUpdateIn):
        """ Updates core shift policy information and daily schedule configuration. """
        policy = get_object_or_404(ShiftPolicy, id=policy_id)
        logger.info(f"Updating shift policy {policy.name} (ID: {policy_id})")

        update_data = data.model_dump(exclude_unset=True)
        daily_configs = update_data.pop('daily_configs', None)

        # Update scalar model fields (name, description, weekly_target_hours)
        for attr, value in update_data.items():
            setattr(policy, attr, value)
        policy.save()

        # Update the 7-day ShiftDetail + ShiftPeriod configuration if provided
        if daily_configs is not None:
            self.scheduling_service.update_policy_details(policy, daily_configs)

        # Refresh from DB to include updated relations
        policy.refresh_from_db()

        logger.info(f"Shift policy {policy.name} (ID: {policy_id}) updated successfully")
        
        return 200, policy

    @http_get('/assignments', response=PaginatedResponseSchema[EmploymentSchemeOut], permissions=[ScopePermission('attendance:r')])
    @paginate(func_or_pgn_class= PageNumberPaginationExtra, page_size=10)
    def list_assignments(self, filters: AssignmentFilterIn = Query(...)):
        """ Lists all active policy assignments with employee and policy info. """

        qs = EmploymentScheme.objects.all().select_related(
            'employee', 'policy', 'override_policy'
        ).prefetch_related(
            Prefetch(
                'employee__status_history',
                queryset=StatusHistory.objects.order_by('-created_at'),
                to_attr='prefetched_current_status',
            ),
            Prefetch(
                'employee__position_history',
                queryset=EmployeePositionHistory.objects.filter(
                    is_current=True
                ).select_related('position', 'org_unit', 'seniority_level'),
                to_attr='prefetched_current_position',
            ),
        )

        # Apply filters (search, org_unit, recurrence) + ordering
        if filters:
            qs = filters.filter(qs)
            qs = filters.apply_ordering(qs, None)

        return qs

    @http_post('/assignments', response={201: EmploymentSchemeOut}, permissions=[ScopePermission('attendance:w')])
    def create_assignment(self, data: EmploymentSchemeAssignIn):
        """ Assigns a shift policy to an employee for a specific period. """
        employee = get_object_or_404(Employee, id=data.employee_id)
        policy = get_object_or_404(ShiftPolicy, id=data.policy_id)

        override_policy = None
        if data.override_policy_id:
            override_policy = get_object_or_404(ShiftPolicy, id=data.override_policy_id)

        scheme = self.scheduling_service.assign_policy_to_employee(
            employee=employee,
            policy=policy,
            start_date=data.start_date,
            end_date=data.end_date,
            recurrence=data.recurrence or "NONE",
            override_policy=override_policy,
            override_valid_from=data.override_valid_from,
            override_valid_until=data.override_valid_until,
            override_recurrence=data.override_recurrence or "NONE",
            override_recurrence_count=data.override_recurrence_count,
        )

        logger.info(
            "Employee scheme assignment created",
            extra={
                "employee_id": str(employee.id),
                "policy_id": str(policy.id),
                "override_policy_id": str(override_policy.id) if override_policy else None,
            },
        )
        return 201, scheme

    @http_patch('/assignments/{assignment_id}', response={200: EmploymentSchemeOut}, permissions=[ScopePermission('attendance:u')])
    def update_assignment(self, assignment_id: UUID, data: EmploymentSchemeUpdateIn):
        """ Updates an existing assignment. Delegates to the service for correct field mapping. """
        scheme = get_object_or_404(EmploymentScheme, id=assignment_id)
        update_data = data.model_dump(exclude_unset=True)
        scheme = self.scheduling_service.update_assignment(scheme, **update_data)

        logger.info(
            "Employee scheme updated",
            extra={
                "scheme_id": str(scheme.id),
                "employee_id": str(scheme.employee_id),
            },
        )
        return 200, scheme

    @http_delete('/assignments/{assignment_id}', response={204: None}, permissions=[ScopePermission('attendance:w')])
    def delete_assignment(self, assignment_id: UUID):
        """ Deletes a policy assignment. """
        scheme = get_object_or_404(EmploymentScheme, id=assignment_id)
        logger.info(
            "Deleting employee scheme assignment",
            extra={
                "scheme_id": str(scheme.id),
                "employee_id": str(scheme.employee_id),
                "policy_id": str(scheme.policy_id),
            },
        )
        scheme.delete()
        return 204, None

    @http_get('/planning/{employee_id}', response=WeeklyPlanningOut, permissions=[ScopePermission('attendance:r')])
    @cache_api_response(timeout=60*30, key_prefix="planning", user_specific=True)
    def get_employee_weekly_planning(
        self,
        employee_id: UUID,
        start_date: Optional[date] = None,
    ):
        """ Retrieves the expected weekly work schedule for an employee. """
        if not start_date:
            start_date = timezone.now().date()

        logger.debug(
            "Weekly planning requested",
            extra={
                "employee_id": str(employee_id),
                "start_date": start_date,
            },
        )

        employee = get_object_or_404(Employee, id=employee_id)
        planning_days = self.scheduling_service.get_weekly_planning(
            employee,
            start_date,
        )

        logger.info(
            "Weekly planning successfully generated",
            extra={
                "employee_id": employee.id,
                "start_date": start_date,
            },
        )

        return {
            "employee_id": employee.id,
            "days": planning_days,
        }

    @http_post('/rotations', response={201: dict}, permissions=[ScopePermission('attendance:w')])
    def setup_rotation(self, data: RotationCreateIn):
        """ Configures and applies a recurring shift rotation for an employee. """
        logger.warning(
            "Rotation setup requested",
            extra={
                "employee_id": str(data.employee_id),
                "start_date": data.start_date,
                "num_weeks": data.num_weeks,
                "policy_ids": data.policy_ids,
            },
        )

        employee = get_object_or_404(Employee, id=data.employee_id)
        policy_map = {p.id: p for p in ShiftPolicy.objects.filter(id__in=data.policy_ids)}
        policies = [policy_map[p_id] for p_id in data.policy_ids if p_id in policy_map]

        self.scheduling_service.apply_rotation(
            employee=employee,
            start_date=data.start_date,
            num_weeks=data.num_weeks,
            weekly_patterns=policies,
        )

        logger.warning(
            "Rotation successfully applied",
            extra={
                "employee_id": employee.id,
                "num_weeks": data.num_weeks,
            },
        )

        return 201, {"message": "Rotation created and backfilled"}

    @http_post('/rotations/backfill', response={200: dict}, permissions=[ScopePermission('attendance:a')])
    def trigger_backfill(self, data: RotationBackfillIn):
        """ Triggers a system-wide backfill of future planning entries for active rotations. """
        logger.info(
            "Rotation backfill triggered",
            extra={"look_ahead_days": data.look_ahead_days},
        )

        self.scheduling_service.backfill_rotations(
            look_ahead_days=data.look_ahead_days
        )

        logger.info("Rotation backfill completed")
        AttendanceCacheService.clear_api_cache_prefix("planning")

        return {"message": "Backfill process triggered"}

    @http_get('/check-working-day', response=WorkingDayCheckOut, permissions=[ScopePermission('attendance:r')])
    @cache_api_response(timeout=60*30, key_prefix="working_day_check", user_specific=False)
    def check_working_day(self, employee_id: UUID, target_date: date):
        """ Checks if an employee is scheduled to work on a specific date. """
        logger.debug(
            "Working day check requested",
            extra={
                "employee_id": str(employee_id),
                "date": target_date
            }
        )

        employee = get_object_or_404(Employee, id=employee_id)
        is_working = self.scheduling_service.is_working_day(employee, target_date)
        
        shift = None
        if is_working:
            shift = self.scheduling_service.get_expected_schedule(employee, target_date)
        
        logger.info(
            "Working day check completed",
            extra={
                "employee_id": str(employee_id),
                "date": target_date,
                "is_working": is_working
            }
        )

        return {
            "is_working": is_working,
            "date": target_date,
            "employee_id": employee_id,
            "shift": shift
        }

    @http_get('/preview-working-days', response=WorkingDaysPreviewOut, permissions=[ScopePermission('attendance:r')])
    def preview_working_days(self, employee_id: UUID, start_date: date, end_date: date):
        """ Previews working day calculation for a full period to assist in leave planning. """
        employee = get_object_or_404(Employee, id=employee_id)

        total = self.scheduling_service.count_working_days_for_employee(
            employee, start_date, end_date
        )
        breakdown = self.scheduling_service.get_working_days_by_year(
            employee, start_date, end_date
        )

        return WorkingDaysPreviewOut(
            total_working_days=total,
            breakdown=breakdown
        )
