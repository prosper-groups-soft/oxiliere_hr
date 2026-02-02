from __future__   import annotations
from datetime     import date
from django.db    import transaction
from django.utils import timezone
from django.contrib.auth.models import User
from django.core.exceptions     import ValidationError
from django.utils.translation   import gettext_lazy as _

from hr.attendance.models import (
    PeriodArchiveLock, 
    DailyRegister
)
from .attendance import AttendanceService
# Integration of cache
from .cache import AttendanceCacheService


class LockingService:
    """ Administrative service to freeze attendance data and prevent modifications. """

    @staticmethod
    @transaction.atomic
    def lock_period(until_date: date, user: User, reason: str = "") -> PeriodArchiveLock:
        """ Freezes all attendance records on or before the specified date. """
        if until_date > timezone.now().date():
            raise ValidationError(_("You cannot lock a future date."))

        last_lock_date = AttendanceCacheService.get_lock_date()
        if last_lock_date and until_date <= last_lock_date:
            raise ValidationError(
                _("A lock already exists up to {date}.").format(date=last_lock_date)
            )

        new_lock = PeriodArchiveLock.objects.create(
            locked_until=until_date,
            reason=reason,
            locked_by=user
        )

        settings = AttendanceCacheService.get_settings()
        settings.active_archive_lock = new_lock
        settings.save()

        unfinalized_registers = DailyRegister.objects.filter(
            date__lte=until_date, 
            is_finalized=False
        )
        for register in unfinalized_registers:
            AttendanceService.finalize_daily_register(register)

        AttendanceCacheService.clear_global_attendance_cache()
        return new_lock

    @staticmethod
    def is_date_locked(target_date: date) -> bool:
        """ Verifies if a specific date is immutable. """
        lock_date = AttendanceCacheService.get_lock_date()
        return target_date <= lock_date if lock_date else False

    @staticmethod
    @transaction.atomic
    def unlock_last_period() -> bool:
        """ Rolls back the active administrative lock to allow exceptional corrections. """
        settings = AttendanceCacheService.get_settings()
        if settings.active_archive_lock:
            settings.active_archive_lock = None
            settings.save()
            AttendanceCacheService.clear_global_attendance_cache()
            return True
        return False

