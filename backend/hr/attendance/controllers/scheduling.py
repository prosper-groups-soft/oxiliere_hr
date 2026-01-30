import logging 
from typing   import Optional, List
from uuid     import UUID
from datetime import date
from injector import inject

from ninja.pagination import paginate
from django.shortcuts import get_object_or_404
from django.utils     import timezone
from ninja_extra      import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from oxutils.pagination.cursor import CursorPagination

from hr.employees.models    import Employee
from hr.attendance.services import SchedulingService
from hr.attendance.models   import ShiftPolicy
from hr.attendance.schemas  import (
    ShiftPolicyOut,
    ShiftPolicyCreateIn,
    ShiftPolicyUpdateIn,
    WeeklyPlanningOut,
    RotationCreateIn,
    RotationBackfillIn,
    WorkingDaysPreviewOut,
)
# Cache integration
from hr.services.cache_helpers import cache_api_response
from hr.attendance.services    import AttendanceCacheService


logger = logging.getLogger(__name__)


@api_controller('/scheduling', tags=['Schedules & Rotations'])
class SchedulingController(ControllerBase):
    """
    API controller responsible for:
    - Shift policy management
    - Weekly employee planning
    - Rotation setup and backfill
    """

    @inject
    def __init__(self, scheduling_service: SchedulingService):
        # Inject scheduling service to keep business logic out of the controller
        self.scheduling_service = scheduling_service

    # Shift policies
    # --------------
    @http_post('/policies', response={201: ShiftPolicyOut})
    def create_policy(self, data: ShiftPolicyCreateIn):
        """
        Create a shift policy with its complete weekly configuration.
        """
        logger.info(
            "Shift policy creation requested",
            extra={
                "name": data.name,
                "weekly_target_hours": data.weekly_target_hours,
            },
        )

        try:
            # Delegate policy creation to the scheduling service
            policy = self.scheduling_service.create_full_policy(
                name=data.name,
                weekly_target=data.weekly_target_hours,
                daily_configs=data.daily_configs,
            )

            logger.info(
                "Shift policy successfully created",
                extra={
                    "policy_id": policy.id,
                    "name": policy.name,
                },
            )

            return 201, policy

        except Exception:
            # Unexpected error during policy creation
            logger.exception(
                "Error while creating shift policy",
                extra={"policy_name": data.name},
            )
            return self.create_response(
                {"detail": "Unable to create shift policy"},
                status_code=400,
            )

    @http_get('/policies', response=List[ShiftPolicyOut])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60, key_prefix="policy_list", user_specific=False)
    def list_policies(self):
        """
        Get all shift policies.
        Uses shared cache as the list is the same for all managers.
        """
        return ShiftPolicy.objects.all()
    
    @http_patch('/policies/{policy_id}', response={200: ShiftPolicyOut})
    def update_policy(self, policy_id: UUID, data: ShiftPolicyUpdateIn):
        """
        Update a shift policy's basic information.
        Note: Changing the target hours will affect future overtime calculations.
        """
        policy = get_object_or_404(ShiftPolicy, id=policy_id)
        
        logger.info(f"Updating shift policy {policy.name} (ID: {policy_id})")

        # Extract provided data
        update_data = data.model_dump(exclude_unset=True)
        
        for attr, value in update_data.items():
            setattr(policy, attr, value)
            
        policy.save()

        # Invalidate cache for policy list is handled automatically by your signals
        # sender=ShiftPolicy is in your @receiver decorator!
        logger.info(f"Shift policy {policy.name} (ID: {policy_id}) updated successfully")
        
        return 200, policy

    # Weekly planning
    # ---------------
    @http_get('/planning/{employee_id}', response=WeeklyPlanningOut)
    @cache_api_response(timeout=60*30, key_prefix="planning", user_specific=True)
    def get_employee_weekly_planning(
        self,
        employee_id: UUID,
        start_date: Optional[date] = None,
    ):
        """
        Retrieve the theoretical weekly planning for an employee.
        Defaults to the current date when not provided.
        """
        # Default to today's date if no start date is provided
        if not start_date:
            start_date = timezone.now().date()

        logger.debug(
            "Weekly planning requested",
            extra={
                "employee_id": str(employee_id),
                "start_date": start_date,
            },
        )

        # Ensure the employee exists before computing planning
        employee = get_object_or_404(Employee, id=employee_id)

        # Compute planning via the scheduling service
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

    # Rotations
    # ---------
    @http_post('/rotations', response={201: dict})
    def setup_rotation(self, data: RotationCreateIn):
        """
        Configure a rotation pattern for an employee and optionally
        backfill past and future planning slots.
        """
        logger.warning(
            "Rotation setup requested",
            extra={
                "employee_id": str(data.employee_id),
                "start_date": data.start_date,
                "num_weeks": data.num_weeks,
                "policy_ids": data.policy_ids,
            },
        )

        # Resolve employee
        employee = get_object_or_404(Employee, id=data.employee_id)

        # Load shift policies referenced by the rotation
        policy_map = {p.id: p for p in ShiftPolicy.objects.filter(id__in=data.policy_ids)}
        policies = [policy_map[p_id] for p_id in data.policy_ids if p_id in policy_map]

        # Apply rotation via the scheduling service
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

    @http_post('/rotations/backfill', response={200: dict})
    def trigger_backfill(self, data: RotationBackfillIn):
        """
        Trigger the rotation backfill process to generate
        future planning entries for all active rotations.
        """
        logger.info(
            "Rotation backfill triggered",
            extra={"look_ahead_days": data.look_ahead_days},
        )

        # Delegate backfill execution to the scheduling service
        self.scheduling_service.backfill_rotations(
            look_ahead_days=data.look_ahead_days
        )

        logger.info("Rotation backfill completed")
        
        AttendanceCacheService.clear_api_cache_prefix("planning")

        return {"message": "Backfill process triggered"}

    @http_get('/preview-working-days', response=WorkingDaysPreviewOut)
    def preview_working_days(self, employee_id: UUID, start_date: date, end_date: date):
        """
        Preview working days calculation for a given period.
        Useful for previewing leave consumption.
        """
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

