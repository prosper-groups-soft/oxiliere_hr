from __future__ import annotations
from datetime import date
from django.db import transaction
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

from hr.attendance.models import (
    PeriodArchiveLock, 
    AttendanceSettings, 
    DailyRegister
)


class LockingService:
    """
    Service responsible for freezing attendance data. 
    Ensures that past records remain untouched after payroll processing.
    """

    @staticmethod
    @transaction.atomic
    def lock_period(until_date: date, user: User, reason: str = "") -> PeriodArchiveLock:
        """
        Creates a new archive lock and updates global settings to point to it.
        All data on or before 'until_date' will become read-only.
        """
        # 1. Validation: Cannot lock a future date
        if until_date > date.today():
            raise ValidationError(_("You cannot lock a future date."))

        # 2. Check if a lock already exists for this date or later
        last_lock_date = AttendanceSettings.get_last_lock_date()
        if last_lock_date and until_date <= last_lock_date:
            raise ValidationError(
                _("A lock already exists up to {date}. You can only extend the lock forward.")
                .format(date=last_lock_date)
            )

        # 3. Create the lock record
        new_lock = PeriodArchiveLock.objects.create(
            locked_until=until_date,
            reason=reason,
            locked_by=user
        )

        # 4. Update Global Settings
        settings = AttendanceSettings.load()
        settings.active_archive_lock = new_lock
        settings.save()

        # 5. Optional: Finalize all DailyRegisters within this period
        DailyRegister.objects.filter(
            date__lte=until_date, 
            is_finalized=False
        ).update(is_finalized=True)

        return new_lock

    @staticmethod
    def is_date_locked(target_date: date) -> bool:
        """
        Quick check used by other services or model clean() methods 
        to verify if a specific date is immutable.
        """
        lock_date = AttendanceSettings.get_last_lock_date()
        if not lock_date:
            return False
        return target_date <= lock_date

    @staticmethod
    @transaction.atomic
    def unlock_last_period() -> bool:
        """
        In rare cases, HR might need to reopen a period.
        This removes the current active lock from settings.
        """
        settings = AttendanceSettings.load()
        if settings.active_archive_lock:
            settings.active_archive_lock = None
            settings.save()
            return True
        return False

