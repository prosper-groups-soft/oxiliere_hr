from __future__ import annotations
from datetime   import timedelta
from django.conf            import settings
from django.core.exceptions import ValidationError
from django.db              import models
from django.db.models       import Q
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog
from hr.models.base    import BaseAuditableModel
from .enums    import (
    TimeSheetStatus,
    PunchType,
    RecurrenceType,
)
from hr.utils.gen import generate_daily_register_code
from hr.enums     import WeekdayEnum


class ShiftPolicy(BaseAuditableModel):
    """ Template defining working hours and break rules (e.g., Standard 40h). """
    name = models.CharField(max_length=255, verbose_name=_("Policy Name"))
    description = models.TextField(blank=True, verbose_name=_("Description"))
    
    weekly_target_hours = models.PositiveSmallIntegerField(
        default=40,
        verbose_name=_("Weekly Target")
    )

    class Meta:
        db_table = "atnd_shift_policy"
        ordering = ["name"]
        constraints = [
            models.UniqueConstraint(
                fields=['name'],
                condition=Q(deleted__isnull=True),
                name='unique_shift_policy_name'
            ),
        ]
        verbose_name = _("Shift Policy")
        verbose_name_plural = _("Shift Policies")

    def __str__(self) -> str:
        return self.name


class ShiftDetail(BaseAuditableModel):
    """ Specific daily schedule configuration within a policy. """
    policy = models.ForeignKey(ShiftPolicy, on_delete=models.CASCADE, related_name="details")
    weekday = models.CharField(max_length=15, choices=WeekdayEnum.choices)
    
    start_time = models.TimeField(verbose_name=_("Expected Start"))
    end_time = models.TimeField(verbose_name=_("Expected End"))
    
    break_start_time = models.TimeField(
        null=True, blank=True, 
        verbose_name=_("Scheduled Break Start")
    )
    break_duration = models.DurationField(
        default=timedelta(minutes=45), 
        verbose_name=_("Authorized Break Duration")
    )
    
    is_working_day = models.BooleanField(default=True, verbose_name=_("Is Working Day"))
    flexible_hours = models.BooleanField(
        default=False, 
        help_text=_("If enabled, strict start/end times are ignored for duration calculations.")
    )

    class Meta:
        db_table = "atnd_shift_detail"
        constraints = [
            models.UniqueConstraint(
                fields=['policy', 'weekday'],
                condition=Q(deleted__isnull=True),
                name='unique_shift_detail_policy_weekday'
            ),
        ]
        verbose_name = _("Shift Detail")


class ShiftPeriod(BaseAuditableModel):
    """ Specific scheduled interval (work or break) within a ShiftDetail. """
    shift_detail = models.ForeignKey(
        ShiftDetail, 
        on_delete=models.CASCADE, 
        related_name="periods"
    )
    name = models.CharField(max_length=100, blank=True, verbose_name=_("Period Name"))
    period_type = models.CharField(
        max_length=20, 
        choices=PunchType.choices, 
        default=PunchType.WORK,
        verbose_name=_("Period Type")
    )
    start_time = models.TimeField(verbose_name=_("Start Time"))
    end_time = models.TimeField(verbose_name=_("End Time"))

    class Meta:
        db_table = "atnd_shift_period"
        ordering = ["start_time"]
        verbose_name = _("Shift Period")
        verbose_name_plural = _("Shift Periods")

    def __str__(self) -> str:
        return f"{self.shift_detail.weekday} - {self.name or self.period_type} ({self.start_time}-{self.end_time})"


class EmploymentScheme(BaseAuditableModel):
    """ Assigns a shift policy to an employee for a specific period. """
    employee = models.ForeignKey(
        "hr_employees.Employee", 
        on_delete=models.CASCADE, 
        related_name="schemes"
    )
    policy = models.ForeignKey(ShiftPolicy, on_delete=models.PROTECT, verbose_name=_("Policy"))
    
    valid_from = models.DateField(verbose_name=_("Effective Date"))
    valid_until = models.DateField(null=True, blank=True, verbose_name=_("Expiry Date"))
    
    is_active = models.BooleanField(default=True, verbose_name=_("Active"))
    recurrence = models.CharField(
        max_length=20,
        choices=RecurrenceType.choices,
        default=RecurrenceType.NONE,
        verbose_name=_("Recurrence"),
    )
    
    # Override / replacement policy (temporary shift change)
    override_policy = models.ForeignKey(
        ShiftPolicy,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="override_schemes",
        verbose_name=_("Override Policy"),
    )
    override_valid_from = models.DateField(
        null=True, blank=True,
        verbose_name=_("Override Effective Date"),
    )
    override_valid_until = models.DateField(
        null=True, blank=True,
        verbose_name=_("Override Expiry Date"),
    )
    override_recurrence = models.CharField(
        max_length=20,
        choices=RecurrenceType.choices,
        default=RecurrenceType.NONE,
        verbose_name=_("Override Recurrence"),
    )
    override_recurrence_count = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name=_("Override Recurrence Count"),
    )

    class Meta:
        db_table = "atnd_employment_scheme"
        ordering = ["-valid_from"]
        verbose_name = _("Employment Scheme")


class ShiftAssignment(BaseAuditableModel):
    """ One-time daily schedule override for exceptional work patterns. """
    employee = models.ForeignKey("hr_employees.Employee", on_delete=models.CASCADE)
    date = models.DateField()
    shift_detail = models.ForeignKey(ShiftDetail, on_delete=models.PROTECT)
    
    class Meta:
        db_table = "atnd_shift_assignment"
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'],
                condition=Q(deleted__isnull=True),
                name='unique_shift_assignment_employee_date'
            ),
        ]


class RotationPattern(BaseAuditableModel):
    """ Defines a recurring cyclic rotation of shift policies. """
    employee = models.ForeignKey("hr_employees.Employee", on_delete=models.CASCADE, related_name="rotations")
    policies = models.JSONField(help_text=_("Ordered list of ShiftPolicy IDs in the rotation cycle."))
    start_date = models.DateField(help_text=_("Commencement date of the first cycle."))
    end_date = models.DateField(null=True, blank=True, help_text=_("Optional expiration date for this rotation."))
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = "atnd_rotation_pattern"


class DailyRegister(BaseAuditableModel):
    """ Daily attendance log consolidating all employee entries. """
    date = models.DateField(unique=True, verbose_name=_("Register Date"))
    code = models.CharField(max_length=100, unique=True, editable=False, verbose_name=_("Reference Code"))
    
    total_employees_expected = models.PositiveIntegerField(default=0)
    total_absences = models.PositiveIntegerField(default=0)
    total_excused = models.PositiveIntegerField(default=0)
    is_finalized = models.BooleanField(default=False, verbose_name=_("Finalized"))

    class Meta:
        db_table = "atnd_daily_register"
        ordering = ["-date"]
        verbose_name = _("Daily Register")

    def save(self, *args, **kwargs):
        """ Generates a unique reference code on first save. """
        if not self.code:
            self.code = generate_daily_register_code(self.date)
        super().save(*args, **kwargs)


class TimeSheet(BaseAuditableModel):
    """ Daily summary of work hours, breaks, and overtime for an individual employee. """
    employee = models.ForeignKey("hr_employees.Employee", on_delete=models.CASCADE)
    register = models.ForeignKey(DailyRegister, on_delete=models.CASCADE, related_name="sheets")
    
    recorded_work = models.DurationField(default=timedelta(0), verbose_name=_("Effective Work"))
    recorded_break = models.DurationField(default=timedelta(0), verbose_name=_("Total Break"))
    
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
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'register'],
                condition=Q(deleted__isnull=True),
                name='unique_timesheet_employee_register'
            ),
        ]
        verbose_name = _("Time Sheet")

    def clean(self):
        """ Prevents modification if the period is locked for payroll. """
        lock_date = AttendanceSettings.get_last_lock_date()
        if lock_date and self.register.date <= lock_date:
            raise ValidationError(_("This date is archived and cannot be modified."))
        super().clean()


class TimePunch(BaseAuditableModel):
    """ Discrete log of a single clock-in, clock-out, or break segment. """
    timesheet = models.ForeignKey(TimeSheet, on_delete=models.CASCADE, related_name="punches")
    punch_type = models.CharField(max_length=20, choices=PunchType.choices, default=PunchType.WORK)
    
    start_at = models.DateTimeField(verbose_name=_("Punch In"))
    end_at = models.DateTimeField(null=True, blank=True, verbose_name=_("Punch Out"))
    
    duration = models.DurationField(default=timedelta(0), verbose_name=_("Segment Duration"))
    is_manual_entry = models.BooleanField(
        default=False, 
        help_text=_("Indicates if this punch was manually created or adjusted by an administrator.")
    )

    class Meta:
        db_table = "atnd_time_punch"
        ordering = ["start_at"]
        verbose_name = _("Time Punch")
        
    @property
    def calculated_duration(self) -> timedelta:
        """ Returns the time difference between start and end timestamps. """
        if self.start_at and self.end_at:
            return self.end_at - self.start_at
        return timedelta(0)
    
    def clean(self):
        """ Ensures no changes are made to locked attendance periods. """
        from hr.attendance.services.locking import LockingService
        if LockingService.is_date_locked(self.timesheet.register.date):
            raise ValidationError("This date is locked and cannot be modified.")

    def save(self, *args, **kwargs):
        """ Validates timestamps and records duration. """
        self.full_clean()
        super().save(*args, **kwargs)


class PeriodArchiveLock(BaseAuditableModel):
    """ Administrative lock to protect final attendance data from changes. """
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
    """ Global configuration for attendance calculation rules and grace periods. """
    active_archive_lock = models.ForeignKey(
        PeriodArchiveLock, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        verbose_name=_("Active Archive Lock")
    )
    
    late_grace_period = models.DurationField(
        default=timedelta(minutes=5),
        help_text=_("Tolerance period after the official start time before being flagged as late."),
        verbose_name=_("Late Grace Period")
    )
    
    rounding_precision = models.PositiveIntegerField(
        default=1,
        help_text=_("Precision in minutes for final hour calculations (e.g., 5, 10, 15)."),
        verbose_name=_("Rounding Precision")
    )

    singleton_enforcer = models.IntegerField(default=1, unique=True, editable=False)

    partial_absence_threshold = models.DurationField(
        default=timedelta(minutes=30),
        help_text=_("Threshold duration of missing time to classify work as partial rather than present."),
        verbose_name=_("Partial Absence Threshold")
    )

    class Meta:
        db_table = "atnd_attendance_settings"
        verbose_name = _("Attendance Settings")

    @classmethod
    def load(cls) -> "AttendanceSettings":
        """ Retrieves the unique global settings instance. """
        obj, _ = cls.objects.get_or_create(singleton_enforcer=1)
        return obj

    @classmethod
    def get_last_lock_date(cls):
        """ Retrieves the current administrative lock date for the module. """
        st = cls.load()
        return st.active_archive_lock.locked_until if st.active_archive_lock else None


# --- Audit log registration ---
auditlog.register(ShiftPolicy)
auditlog.register(ShiftDetail)
auditlog.register(ShiftPeriod)
auditlog.register(EmploymentScheme)
auditlog.register(ShiftAssignment)
auditlog.register(RotationPattern)
auditlog.register(DailyRegister)
auditlog.register(TimeSheet)
auditlog.register(TimePunch)
auditlog.register(PeriodArchiveLock)
auditlog.register(AttendanceSettings)

