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
# Integration of cache
from .cache import AttendanceCacheService


class LockingService:
    """
    Service responsible for freezing attendance data. 
    Prevents any modifications to past records after payroll processing or auditing.
    """

    @staticmethod
    @transaction.atomic
    def lock_period(until_date: date, user: User, reason: str = "") -> PeriodArchiveLock:
        """
        Freezes all attendance data on or before 'until_date'.
        Updates global settings and invalidates cache to enforce read-only status.
        """
        # 1. Validation: Future dates cannot be locked
        if until_date > timezone.now().date():
            raise ValidationError(_("You cannot lock a future date."))

        # 2. Sequential Validation: Locks must always move forward
        last_lock_date = AttendanceCacheService.get_lock_date()
        if last_lock_date and until_date <= last_lock_date:
            raise ValidationError(
                _("A lock already exists up to {date}. You can only extend the lock forward.")
                .format(date=last_lock_date)
            )

        # 3. Persistence: Create the lock record
        new_lock = PeriodArchiveLock.objects.create(
            locked_until=until_date,
            reason=reason,
            locked_by=user
        )

        # 4. Global State: Link the new lock to attendance settings
        settings = AttendanceCacheService.get_settings()
        settings.active_archive_lock = new_lock
        settings.save()

        # 5. Integrity: Ensure all registers in the period are finalized
        # We fetch registers to finalize them properly via the service logic
        from .attendance import AttendanceService
        unfinalized_registers = DailyRegister.objects.filter(
            date__lte=until_date, 
            is_finalized=False
        )
        for register in unfinalized_registers:
            AttendanceService.finalize_daily_register(register)

        # 6. Cache Invalidation: Force all nodes to recognize the new lock
        AttendanceCacheService.clear_global_attendance_cache()

        return new_lock

    @staticmethod
    def is_date_locked(target_date: date) -> bool:
        """
        High-performance check to verify if a specific date is immutable.
        Used by API views and Model clean() methods.
        """
        lock_date = AttendanceCacheService.get_lock_date()
        
        if not lock_date:
            return False
        return target_date <= lock_date

    @staticmethod
    @transaction.atomic
    def unlock_last_period() -> bool:
        """
        Rolls back the current active lock. 
        Used only in exceptional cases (HR corrections).
        """
        settings = AttendanceCacheService.get_settings()
        if settings.active_archive_lock:
            # We don't delete the ArchiveLock record (for audit purposes),
            # we simply detach it from the active settings.
            settings.active_archive_lock = None
            settings.save()
            
            # Flush cache to allow edits again
            AttendanceCacheService.clear_global_attendance_cache()
            return True
        return False

