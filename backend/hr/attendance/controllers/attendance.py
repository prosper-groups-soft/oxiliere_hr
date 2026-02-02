import logging
from typing import List
from uuid   import UUID
from ninja  import Query
from injector import inject
from oxutils.permissions.perms import ScopePermission

from django.core.exceptions import ValidationError
from django.shortcuts       import get_object_or_404
from ninja.pagination       import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_delete,
    ControllerBase
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
    AttendanceSettingsUpdateIn,
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
    """ API controller for attendance operations, including punches and timesheet management. """

    @inject
    def __init__(
        self,
        attendance_service: AttendanceService,
        validation_service: ValidationService,
        punch_service: PunchService
    ):
        self.attendance_service = attendance_service
        self.validation_service = validation_service
        self.punch_service = punch_service
        
    @http_post('/punches/clock-in', response={201: PunchOut}, permissions=[ScopePermission('attendance:w')])
    def clock_in(self, employee_id: UUID, data: PunchCreateIn):
        """ Records a clock-in punch with location validation. """
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
            return self.create_response(
                {"detail": str(e.message)},
                status_code=400,
            )
        except Exception as e:
            logger.exception("Critical error in Punch API")
            raise

    @http_post('/punches/clock-out', response={200: PunchOut}, permissions=[ScopePermission('attendance:w')])
    def clock_out(self, employee_id: UUID, data: PunchCreateIn):
        """ Records a clock-out punch with location validation. """
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
            punch = self.punch_service.record_punch(
                actor_user=actor,
                timestamp=data.timestamp,
                punch_type=data.punch_type,
                is_manual=data.is_manual,
                employee_id=getattr(data, 'employee_id', None),
                latitude=data.latitude,
                longitude=data.longitude
            )

            return 200, punch

        except ValidationError as e:
            return self.create_response(
                {"detail": str(e.message)},
                status_code=400,
            )
        except Exception as e:
            logger.exception("Critical error in Punch API")
            raise

    @http_patch('/punch/{punch_id}', response={200: PunchOut}, permissions=[ScopePermission('attendance:w')])
    def adjust_existing_punch(self, punch_id: UUID, data: PunchAdjustIn):
        """ Endpoint for HR to adjust an existing punch segment. """
        actor = self.context.request.user
        punch = get_object_or_404(TimePunch, id=punch_id)

        try:
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

    @http_delete('/punch/{punch_id}', response={204: None}, permissions=[ScopePermission('attendance:d')])
    def delete_existing_punch(self, punch_id: UUID):
        """ Endpoint for HR to permanently remove a punch segment. """
        actor = self.context.request.user
        punch = get_object_or_404(TimePunch, id=punch_id)

        try:
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
            
    @http_get('/entries', response=List[TimeSheetOut], permissions=[ScopePermission('attendance:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*15, key_prefix="registry_entries", user_specific=False)
    def list_timesheets(self, filters: TimeSheetFilter = Query(...)):
        """ List all timesheets with filtering and cursor pagination. """
        qs = TimeSheet.objects.select_related(
            'employee',
            'employee__work_site',
            'register',
        ).all()

        return filters.filter(qs)

    @http_get('/timesheets/{timesheet_id}/can-modify', response=CanModifyOut, permissions=[ScopePermission('attendance:r')])
    def check_modification_status(self, timesheet_id: UUID):
        """ Formally check if a timesheet can still be modified. """
        logger.debug(
            "Checking timesheet modification rights",
            extra={"timesheet_id": str(timesheet_id)},
        )

        timesheet = get_object_or_404(TimeSheet, id=timesheet_id)
        can_modify = self.validation_service.can_modify_attendance(timesheet)
        reason = "Period locked or finalized" if not can_modify else "Editable"

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

    @http_get('/settings', response=AttendanceSettingsOut, permissions=[ScopePermission('attendance:r')])
    def get_settings(self):
        """ Retrieves global attendance settings and configuration. """
        return AttendanceCacheService.get_settings()

    @http_patch('/settings', response=AttendanceSettingsOut, permissions=[ScopePermission('attendance:a')])
    def update_settings(self, data: AttendanceSettingsUpdateIn):
        """ Updates global attendance calculation rules and configuration. """
        logger.info(
            "Attendance settings update requested",
            extra={"payload": data.model_dump(exclude_unset=True)},
        )

        settings = AttendanceCacheService.get_settings()

        for attr, value in data.model_dump(exclude_unset=True).items():
            setattr(settings, attr, value)

        settings.save()
        AttendanceCacheService.clear_global_attendance_cache()

        logger.info(
            "Attendance settings successfully updated",
            extra={"settings_id": settings.id},
        )

        return settings

