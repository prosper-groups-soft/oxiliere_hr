from __future__ import annotations

import secrets
import string
from datetime import timedelta

from django.conf import settings
from django.core.exceptions import ValidationError
from django.db import models
from django.utils.translation import gettext_lazy as _

from auditlog.registry import auditlog

from hr.models import BaseAuditableModel
from hr.enums import WeekdayEnum, TimeSheetStatus, PunchType


class ShiftPolicy(BaseAuditableModel):
    """
    Defines a working time policy (e.g., Standard 35h, Night Shift).
    Acts as a parent template for daily schedules.
    """
    name = models.CharField(max_length=255, unique=True, verbose_name=_("Policy Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    # Contractual weekly hour goal
    weekly_target_hours = models.DurationField(
        default=timedelta(hours=40),
        verbose_name=_("Weekly Target")
    )

    class Meta:
        db_table = "atnd_shift_policy"
        ordering = ["name"]
        verbose_name = _("Shift Policy")
        verbose_name_plural = _("Shift Policies")

    def __str__(self) -> str:
        return self.name


class ShiftDetail(BaseAuditableModel):
    """
    Daily schedule details for each day of the week within a policy.
    Defines when the employee is expected to start and finish.
    """
    policy = models.ForeignKey(ShiftPolicy, on_delete=models.CASCADE, related_name="details")
    weekday = models.CharField(max_length=15, choices=WeekdayEnum.choices)
    
    start_time = models.TimeField(verbose_name=_("Expected Start"))
    end_time = models.TimeField(verbose_name=_("Expected End"))
    
    break_start_time = models.TimeField(
        null=True, blank=True, 
        verbose_name=_("Scheduled break time")
    )
    break_duration = models.DurationField(
        default=timedelta(minutes=45), 
        verbose_name=_("Authorized break duration")
    )
    
    is_working_day = models.BooleanField(default=True, verbose_name=_("Is Working Day"))
    flexible_hours = models.BooleanField(
        default=False, 
        help_text=_("If true, start/end times are used for duration calculation but are not strictly enforced.")
    )

    class Meta:
        db_table = "atnd_shift_detail"
        unique_together = ("policy", "weekday")
        verbose_name = _("Shift Detail")


class EmploymentScheme(BaseAuditableModel):
    """
    Link table associating an employee with a shift policy.
    Handles seasonality (e.g., summer vs. winter contracts) via validity dates.
    """
    employee = models.ForeignKey(
        "hr_employees.Employee", 
        on_delete=models.CASCADE, 
        related_name="schemes"
    )
    policy = models.ForeignKey(ShiftPolicy, on_delete=models.PROTECT, verbose_name=_("Policy"))
    
    valid_from = models.DateField(verbose_name=_("Effective Date"))
    valid_until = models.DateField(null=True, blank=True, verbose_name=_("Expiry Date"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))

    class Meta:
        db_table = "atnd_employment_scheme"
        ordering = ["-valid_from"]
        verbose_name = _("Employment Scheme")


class ShiftAssignment(BaseAuditableModel):
    """
    Overrides the regular schedule for an employee on a specific date.
    Useful for rotations, replacements, or unforeseen circumstances.
    """
    employee = models.ForeignKey("hr_employees.Employee", on_delete=models.CASCADE)
    date = models.DateField()

    # Links to an existing ShiftDetail (from another policy)
    # or the hours could be redefined here directly.
    shift_detail = models.ForeignKey(ShiftDetail, on_delete=models.PROTECT)
    
    class Meta:
        db_table = "atnd_shift_assignment"
        unique_together = ("employee", "date")


class RotationPattern(BaseAuditableModel):
    """
    Defines the rotation rule for an employee.
    E.g.: Alternating between 'Team A' and 'Team B'.
    """
    employee = models.ForeignKey("hr_employees.Employee", on_delete=models.CASCADE, related_name="rotations")
    policies = models.JSONField(help_text=_("List of ShiftPolicy IDs in cycle order"))
    start_date = models.DateField(help_text=_("Start date of the very first cycle"))
    end_date = models.DateField(null=True, blank=True, help_text=_("Optional end date for the rotation"))
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "atnd_rotation_pattern"


class DailyRegister(BaseAuditableModel):
    """
    Master container for a specific date. Groups all employee 
    attendance sheets for that day.
    """
    date = models.DateField(unique=True, verbose_name=_("Register Date"))
    code = models.CharField(max_length=100, unique=True, editable=False, verbose_name=_("Reference Code"))
    
    # Global daily statistics
    total_employees_expected = models.PositiveIntegerField(default=0)
    total_absences = models.PositiveIntegerField(default=0)
    is_finalized = models.BooleanField(default=False, verbose_name=_("Finalized"))

    class Meta:
        db_table = "atnd_daily_register"
        ordering = ["-date"]
        verbose_name = _("Daily Register")

    def save(self, *args, **kwargs):
        """Generates a unique code (DR-YYYYMMDD-XXXX) upon creation."""
        if not self.code:
            date_str = self.date.strftime("%Y%m%d")
            rand = "".join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(4))
            self.code = f"DR-{date_str}-{rand}"
        super().save(*args, **kwargs)


class TimeSheet(BaseAuditableModel):
    """
    Daily attendance summary for a specific employee.
    Stores worked totals and calculates deviations (overtime/shortfall).
    """
    employee = models.ForeignKey("hr_employees.Employee", on_delete=models.CASCADE)
    register = models.ForeignKey(DailyRegister, on_delete=models.CASCADE, related_name="sheets")
    
    # Totals calculated via TimePunches
    recorded_work = models.DurationField(default=timedelta(0), verbose_name=_("Effective Work"))
    recorded_break = models.DurationField(default=timedelta(0), verbose_name=_("Total Break"))
    
    # Comparison with theoretical schedule
    overtime = models.DurationField(default=timedelta(0), verbose_name=_("Overtime"))
    shortfall = models.DurationField(default=timedelta(0), verbose_name=_("Shortfall"))
    
    status = models.CharField(
        max_length=20, 
        choices=TimeSheetStatus.choices, 
        default=TimeSheetStatus.ABSENT
    )
    remarks = models.TextField(blank=True, verbose_name=_("HR Notes"))

    class Meta:
        db_table = "atnd_timesheet"
        unique_together = ("employee", "register")
        verbose_name = _("Time Sheet")

    def clean(self):
        """Checks if the period is locked by archiving before allowing modifications."""
        # Note: Ensure AttendanceSettings is imported or defined
        lock_date = AttendanceSettings.get_last_lock_date()
        if lock_date and self.register.date <= lock_date:
            raise ValidationError(_("This date is archived and cannot be modified."))
        super().clean()


class TimePunch(BaseAuditableModel):
    """
    Raw time segment (Clock-in/Clock-out). 
    Uses DateTimeField to support shifts crossing midnight (Night shifts).
    """
    timesheet = models.ForeignKey(TimeSheet, on_delete=models.CASCADE, related_name="punches")
    punch_type = models.CharField(max_length=20, choices=PunchType.choices, default=PunchType.WORK)
    
    start_at = models.DateTimeField(verbose_name=_("Punch In"))
    end_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Punch Out"))
    
    duration = models.DurationField(default=timedelta(0), verbose_name=_("Segment Duration"))
    is_manual_entry = models.BooleanField(
        default=False, 
        help_text=_("Flagged if entry was created or modified manually by an administrator.")
    )

    class Meta:
        db_table = "atnd_time_punch"
        ordering = ["start_at"]
        verbose_name = _("Time Punch")

    def save(self, *args, **kwargs):
        """Automatically calculates duration if both timestamps are present."""
        if self.start_at and self.end_at:
            self.duration = self.end_at - self.start_at
        super().save(*args, **kwargs)


class PeriodArchiveLock(BaseAuditableModel):
    """
    Defines an immutability barrier. Any data prior to 
    'locked_until' can no longer be modified (monthly closing).
    """
    locked_until = models.DateField(unique=True, verbose_name=_("Locked Until Date"))
    reason = models.CharField(max_length=255, blank=True)
    locked_by = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True
    )

    class Meta:
        db_table = "atnd_archive_lock"
        verbose_name = _("Period Archive Lock")


class AttendanceSettings(BaseAuditableModel):
    """
    Global module configuration (Singleton).
    Defines universal rules for time calculations and constraints.
    """
    active_archive_lock = models.ForeignKey(
        PeriodArchiveLock, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Active Archive Lock")
    )
    
    # Lateness Management (Human-centric approach)
    late_grace_period = models.DurationField(
        default=timedelta(minutes=5),
        help_text=_("Allowed time after the official start without being flagged as 'Late'."),
        verbose_name=_("Late Grace Period")
    )
    
    # Rounding (Optional)
    rounding_precision = models.PositiveIntegerField(
        default=1,
        help_text=_("Precision in minutes for final calculations (e.g., 5, 15)."),
        verbose_name=_("Rounding Precision")
    )

    # Technical safeguard to ensure only one settings record exists
    singleton_enforcer = models.IntegerField(default=1, unique=True, editable=False)

    class Meta:
        db_table = "atnd_attendance_settings"
        verbose_name = _("Attendance Settings")

    @classmethod
    def load(cls) -> "AttendanceSettings":
        """
        Loads the unique settings instance or creates it if it doesn't exist.
        """
        obj, _ = cls.objects.get_or_create(singleton_enforcer=1)
        return obj

    @classmethod
    def get_last_lock_date(cls):
        """
        Retrieves the current archive lock date for validation purposes.
        """
        st = cls.load()
        return st.active_archive_lock.locked_until if st.active_archive_lock else None


# --- AUDIT LOG REGISTRATION ---

auditlog.register(ShiftPolicy)
auditlog.register(ShiftDetail)
auditlog.register(EmploymentScheme)
auditlog.register(ShiftAssignment)
auditlog.register(RotationPattern)
auditlog.register(DailyRegister)
auditlog.register(TimeSheet)
auditlog.register(TimePunch)
auditlog.register(PeriodArchiveLock)
auditlog.register(AttendanceSettings)

