import logging
from datetime import date
from injector import inject
from typing   import List
from ninja    import Query

from django.core.exceptions import ValidationError
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_delete,
    paginate,
    ControllerBase
)
from ninja.pagination import paginate
from oxutils.permissions.perms import ScopePermission

from oxutils.pagination.cursor import CursorPagination

from hr.attendance.models import (
    DailyRegister,
    PeriodArchiveLock
)
from hr.attendance.schemas import (
    DailyRegisterOut,
    DailyRegisterFinalizeIn,
    DailyRegisterFilter,
    PeriodArchiveLockOut,
    UnlockPeriodOut,
)

from hr.attendance.services import (
    AttendanceService,
    ValidationService,
    LockingService
)
# Cache integration
from hr.services.cache_helpers import cache_api_response
from hr.attendance.services    import AttendanceCacheService


logger = logging.getLogger(__name__)


@api_controller('/attendance/registry', tags=['Registry & Period Locks'])
class RegistryController(ControllerBase):
    """ API controller for managing the daily attendance registry and administrative period locks. """

    @inject
    def __init__(
        self,
        attendance_service: AttendanceService,
        validation_service: ValidationService,
        locking_service: LockingService,
    ):
        self.attendance_service = attendance_service
        self.validation_service = validation_service
        self.locking_service = locking_service

    @http_get('/entries', response=List[DailyRegisterOut], permissions=[ScopePermission('attendance:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*15, key_prefix="registry_entries", user_specific=False)
    def list_daily_registers(self, filters: DailyRegisterFilter = Query(...)):
        """ Returns a paginated history of daily attendance registers. """
        logger.debug("Daily register list requested")
        return filters.filter(DailyRegister.objects.all())

    @http_post('/daily-registers/finalize', response={200: DailyRegisterOut}, permissions=[ScopePermission('attendance:w')])
    def finalize_day(self, data: DailyRegisterFinalizeIn):
        """ Finalizes a specific day to calculate absences and freeze attendance records. """
        logger.info(
            "Daily register finalization requested",
            extra={"date": data.date},
        )

        try:
            register = self.attendance_service.finalize_daily_register(
                target_date=data.date
            )

            logger.info(
                "Daily register successfully finalized",
                extra={
                    "date": data.date,
                    "register_id": register.id,
                },
            )

            return 200, register

        except ValidationError as e:
            logger.warning(
                "Daily register finalization failed",
                extra={
                    "date": data.date,
                    "error": e.message,
                },
            )
            return self.create_response(
                {"detail": str(e.message)},
                status_code=400,
            )

        except Exception:
            logger.exception(
                "Unexpected error during daily register finalization",
                extra={"date": data.date},
            )
            raise

    @http_get('/locks', response=List[PeriodArchiveLockOut], permissions=[ScopePermission('attendance:r')])
    @paginate(CursorPagination)
    @cache_api_response(key_prefix="period_lock_list", user_specific=False)
    def list_locks(self):
        """ Retrieves the history of administrative attendance locks. """
        logger.debug("Period lock history requested")
        return PeriodArchiveLock.objects.select_related(
            'locked_by'
        ).all()

    @http_post('/locks', response={201: PeriodArchiveLockOut}, permissions=[ScopePermission('attendance:a')])
    def create_period_lock(self, locked_until: date, reason: str):
        """ Freezes all attendance data up to a specific date to secure payroll. """
        actor = self.context.request.user

        logger.warning(
            "Attendance period lock requested",
            extra={
                "locked_until": locked_until,
                "reason": reason,
                "actor_id": actor.id,
            },
        )

        try:
            lock = self.locking_service.lock_period(
                until_date=locked_until,
                user=actor,
                reason=reason
            )

            logger.warning(
                "Attendance period successfully locked",
                extra={
                    "lock_id": lock.id,
                    "locked_until": locked_until,
                    "actor_id": actor.id,
                },
            )

            return 201, lock

        except ValidationError as e:
            logger.warning(
                "Period lock failed",
                extra={
                    "locked_until": locked_until,
                    "error": str(e),
                },
            )
            return self.create_response(
                {"detail": str(e)},
                status_code=400,
            )

    @http_delete('/locks/active', response={200: UnlockPeriodOut, 404: dict}, permissions=[ScopePermission('attendance:a')])
    def unlock_active_period(self):
        """ Unlocks the currently active period to allow exceptional HR corrections. """
        
        actor = self.context.request.user
        settings = AttendanceCacheService.get_settings()
        previous_lock = settings.active_archive_lock
        
        if not previous_lock:
            logger.warning(
                "Unlock attempt with no active lock",
                extra={"actor_id": actor.id}
            )
            return 404, {"detail": "No active lock to unlock"}
        
        success = self.locking_service.unlock_last_period()
        
        if not success:
            return 404, {"detail": "No active lock to unlock"}
        
        logger.warning(
            "Attendance period unlocked",
            extra={
                "previous_lock_id": previous_lock.id,
                "previous_lock_until": previous_lock.locked_until,
                "actor_id": actor.id
            }
        )
        
        return 200, {
            "unlocked": True,
            "previous_lock": previous_lock
        }

