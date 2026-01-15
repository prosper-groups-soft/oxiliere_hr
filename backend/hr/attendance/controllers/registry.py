import logging
from typing import List
from datetime import date

from django.core.exceptions import ValidationError
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    paginate,
    ControllerBase,
)

from oxutils.pagination.cursor import CursorPagination

from hr.attendance.models import (
    DailyRegister,
    PeriodArchiveLock,
    AttendanceSettings,
)
from hr.attendance.schemas import (
    DailyRegisterOut,
    DailyRegisterFinalizeIn,
    PeriodArchiveLockOut,
    AttendanceSettingsOut,
    AttendanceSettingsUpdateIn,
)

from hr.attendance.services import (
    AttendanceService,
    ValidationService,
)
from injector import inject


logger = logging.getLogger(__name__)


@api_controller('/attendance/registry', tags=['Registry & Period Locks'])
class RegistryController(ControllerBase):
    """
    API controller responsible for:
    - Daily attendance register lifecycle
    - Payroll period locking
    - Global attendance settings management
    """

    @inject
    def __init__(
        self,
        attendance_service: AttendanceService,
        validation_service: ValidationService,
    ):
        # Inject domain services to keep controllers thin
        self.attendance_service = attendance_service
        self.validation_service = validation_service

    # Daily registers
    # -----------------------------------------------------------------
    @http_get('/daily-registers', response=List[DailyRegisterOut])
    @paginate(CursorPagination)
    def list_daily_registers(self):
        """
        Return a paginated list of daily registers ordered by most recent date.
        """
        logger.debug("Daily register list requested")

        # Simple read-only query, ordered for operational clarity
        return DailyRegister.objects.all().order_by('-date')

    @http_post('/daily-registers/finalize', response={200: DailyRegisterOut})
    def finalize_day(self, data: DailyRegisterFinalizeIn):
        """
        Finalize a specific day:
        - Calculates absences
        - Freezes attendance counters
        - Prevents further punch modifications
        """
        logger.info(
            "Daily register finalization requested",
            extra={"date": data.date},
        )

        try:
            # Delegate day finalization logic to the service layer
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
            # Expected business rule violation (already finalized, locked period, etc.)
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
            # Unexpected error → capture full stack trace
            logger.exception(
                "Unexpected error during daily register finalization",
                extra={"date": data.date},
            )
            raise

    # Period locks (payroll protection)
    # -----------------------------------------------------------------
    @http_get('/locks', response=List[PeriodArchiveLockOut])
    def list_locks(self):
        """
        Retrieve the history of attendance period locks
        used to secure payroll calculations.
        """
        logger.debug("Period lock history requested")

        # Include the user who created the lock for audit purposes
        return PeriodArchiveLock.objects.select_related(
            'locked_by'
        ).all()

    @http_post('/locks', response={201: PeriodArchiveLockOut})
    def create_period_lock(self, locked_until: date, reason: str):
        """
        Lock all attendance data up to a given date.
        This operation is critical and directly impacts payroll integrity.
        """
        actor = self.context.request.user

        logger.warning(
            "Attendance period lock requested",
            extra={
                "locked_until": locked_until,
                "reason": reason,
                "actor_id": actor.id,
            },
        )

        # Persist the lock in the database
        lock = PeriodArchiveLock.objects.create(
            locked_until=locked_until,
            reason=reason,
            locked_by=actor,
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

    # Global attendance settings
    # -----------------------------------------------------------------
    @http_get('/settings', response=AttendanceSettingsOut)
    def get_settings(self):
        """
        Retrieve global attendance configuration
        (grace periods, rounding rules, tolerances, etc.).
        """
        logger.debug("Attendance settings requested")

        # AttendanceSettings is a singleton
        return AttendanceSettings.get_solo()

    @http_patch('/settings', response=AttendanceSettingsOut)
    def update_settings(self, data: AttendanceSettingsUpdateIn):
        """
        Update global attendance calculation rules.
        """
        logger.info(
            "Attendance settings update requested",
            extra={"payload": data.model_dump(exclude_unset=True)},
        )

        settings = AttendanceSettings.objects.first()

        # Apply only provided fields to the settings instance
        for attr, value in data.model_dump(exclude_unset=True).items():
            setattr(settings, attr, value)

        settings.save()

        logger.info(
            "Attendance settings successfully updated",
            extra={"settings_id": settings.id},
        )

        return settings

