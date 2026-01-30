import logging
from typing   import List
from uuid     import UUID
from ninja    import Query
from injector import inject

from django.core.exceptions import ValidationError
from django.shortcuts       import get_object_or_404
from ninja.pagination       import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_delete,
    ControllerBase,
)

from oxutils.pagination.cursor import CursorPagination

from hr.attendance.models  import TimeSheet, TimePunch
from hr.attendance.schemas import (
    PunchCreateIn,
    PunchAdjustIn,
    PunchOut,
    TimeSheetOut,
    TimeSheetFilter,
    CanModifyOut,
    AttendanceSettingsOut,
    AttendanceSettingsUpdateIn
)

from hr.attendance.services import (
    AttendanceService, 
    ValidationService,
    PunchService
)
# Cache integration
from hr.services.cache_helpers import cache_api_response
from hr.attendance.services    import AttendanceCacheService


logger = logging.getLogger(__name__)


@api_controller('/attendance', tags=['Attendance & Timesheets'])
class AttendanceController(ControllerBase):
    """
    API controller responsible for attendance operations:
    - Punch in / punch out
    - Timesheet listing
    - Timesheet modification eligibility checks
    """

    @inject
    def __init__(
        self,
        attendance_service: AttendanceService,
        validation_service: ValidationService,
        punch_service: PunchService
    ):
        # Inject domain services (business logic stays outside the controller)
        self.attendance_service = attendance_service
        self.validation_service = validation_service
        self.punch_service = punch_service
        
    # Punch creation (clock-in / clock-out)
    # -------------------------------------
    @http_post('/punch', response={201: PunchOut})
    def create_punch(self, data: PunchCreateIn):
        """
        Record a punch with geofencing validation.
        """
        actor = self.context.request.user

        logger.debug(
            "Incoming punch request",
            extra={
                "user_id": actor.id,
                "lat": data.latitude,
                "lon": data.longitude,
                "is_manual": data.is_manual,
            },
        )

        try:
            # We use the PunchService now
            # Note: We pass latitude and longitude directly from data
            punch = self.punch_service.record_punch(
                actor_user=actor,
                timestamp=data.timestamp,
                punch_type=data.punch_type,
                is_manual=data.is_manual,
                employee_id=getattr(data, 'employee_id', None),
                latitude=data.latitude,
                longitude=data.longitude
            )

            return 201, punch

        except ValidationError as e:
            # We catch geofencing or locking errors here
            return self.create_response(
                {"detail": str(e.message)},
                status_code=400,
            )
        except Exception as e:
            logger.exception("Critical error in Punch API")
            raise

    @http_patch('/punch/{punch_id}', response={200: PunchOut})
    def adjust_existing_punch(self, punch_id: UUID, data: PunchAdjustIn):
        """
        Endpoint for HR to adjust an existing punch segment.
        """
        actor = self.context.request.user

        # 1. Get the punch to adjust
        punch = get_object_or_404(TimePunch, id=punch_id)

        try:
            # 2. Delegate adjustment logic to the PunchService
            updated_punch = self.punch_service.adjust_punch(
                punch=punch,
                start_at=data.start_at,
                end_at=data.end_at,
                punch_type=data.punch_type
            )
            
            logger.info(
                "Punch manually adjusted by HR",
                extra={
                    "punch_id": str(punch_id),
                    "actor_id": actor.id,
                    "employee_id": punch.timesheet.employee.id
                }
            )
            return 200, updated_punch

        except ValidationError as e:
            return self.create_response(
                {"detail": str(e.message)},
                status_code=400,
            )

    @http_delete('/punch/{punch_id}', response={204: None})
    def delete_existing_punch(self, punch_id: UUID):
        """
        HR Endpoint to permanently remove a punch segment.
        """
        actor = self.context.request.user

        # 1. Get the punch to delete
        punch = get_object_or_404(TimePunch, id=punch_id)

        try:
            # 2. Check if the punch is eligible for deletion (i.e., not locked)
            self.punch_service.delete_punch(punch)
            
            logger.info(
                "Punch deleted by HR",
                extra={
                    "punch_id": str(punch_id),
                    "actor_id": actor.id,
                    "employee_id": punch.timesheet.employee.id
                }
            )
            
            return 204, None

        except ValidationError as e:
            return self.create_response(
                {"detail": str(e.message)},
                status_code=400,
            )
            

    # Timesheet listing (paginated)
    # -----------------------------
    @http_get('/timesheets', response=List[TimeSheetOut])
    @paginate(CursorPagination)
    @cache_api_response(key_prefix="ts_list", user_specific=False)
    def list_timesheets(self, filters: TimeSheetFilter = Query(...)):
        qs = TimeSheet.objects.select_related(
            'employee',
            'employee__work_site',
            'register',
        ).all()

        return filters.filter(qs)

    # Timesheet modification eligibility
    # ----------------------------------
    @http_get('/timesheets/{timesheet_id}/can-modify', response=CanModifyOut)
    def check_modification_status(self, timesheet_id: UUID):
        """
        Determine whether a timesheet can still be modified according
        to business rules (period closure, validation state, etc.).
        """
        # Trace access to modification check endpoint
        logger.debug(
            "Checking timesheet modification rights",
            extra={"timesheet_id": str(timesheet_id)},
        )

        # Load the target timesheet
        timesheet = get_object_or_404(TimeSheet, id=timesheet_id)

        # Delegate decision logic to the validation service
        can_modify = self.validation_service.can_modify_attendance(timesheet)
        
        # If can_modify is False, we set a generic or specific reason
        reason = "Period locked or finalized" if not can_modify else "Editable"

        # Log the outcome for audit and traceability
        logger.info(
            "Timesheet modification check completed",
            extra={
                "timesheet_id": str(timesheet_id),
                "employee_id": timesheet.employee.id,
                "can_modify": can_modify,
                "reason": reason,
            },
        )

        return {
            "can_modify": can_modify,
            "reason": reason,
        }

    # Global attendance settings
    # --------------------------
    @http_get('/settings', response=AttendanceSettingsOut)
    def get_settings(self):
        """
        Retrieve global attendance configuration
        (grace periods, rounding rules, tolerances, etc.).
        """
        logger.debug("Attendance settings requested")

        # AttendanceSettings is a singleton
        return AttendanceCacheService.get_settings()

    @http_patch('/settings', response=AttendanceSettingsOut)
    def update_settings(self, data: AttendanceSettingsUpdateIn):
        """
        Update global attendance calculation rules.
        """
        logger.info(
            "Attendance settings update requested",
            extra={"payload": data.model_dump(exclude_unset=True)},
        )

        settings = AttendanceCacheService.get_settings()

        # Apply only provided fields to the settings instance
        for attr, value in data.model_dump(exclude_unset=True).items():
            setattr(settings, attr, value)

        settings.save()
        
        AttendanceCacheService.clear_global_attendance_cache()

        logger.info(
            "Attendance settings successfully updated",
            extra={"settings_id": settings.id},
        )

        return settings

