from __future__ import annotations
import random
import string
from datetime import timedelta
from typing import Optional, Tuple
from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from utils_mixins.models import (
    BaseModelMixin, 
    SingletonMixin
)
from utils_mixins.fn import enum_to_choices
from .managers import AttendanceManager
from .enums import WeekdayEnum, AttendanceStatus


class ScheduleTemplate(BaseModelMixin):
    """
    Represents a scheduling template (a full weekly plan).

    This entity is the "container" or "pattern" for working schedules.
    A company, department, team, or employee can be assigned to a specific
    schedule template.

    Examples:
    - "Standard Day Shift"
    - "Night Shift"
    - "Weekend Staff"
    - "Warehouse Team A"

    The template itself does not store specific daily hours. Those are
    defined in the related `ScheduleDay` model, allowing the system to
    create multiple reusable schedule structures without duplication.

    This design also supports:
    - cloning templates;
    - versioning in the future;
    - caching frequently accessed templates;
    - assigning templates dynamically to employees;
    - partial templates (only some days defined).
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Human-readable name of the schedule template.")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Optional notes or details about the schedule template.")
    )

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return self.name


class ScheduleDay(BaseModelMixin):
    """
    Represents one weekday configuration inside a ScheduleTemplate.

    Each ScheduleTemplate may contain up to 7 ScheduleDay entries,
    one for each weekday. Together, they form a complete weekly schedule.

    Key concepts:
    - A ScheduleDay stores the working hours for a single weekday.
    - A template cannot contain two entries for the same weekday.
    - Overnight shifts are supported (closing time earlier than opening time).
    - The `hours` field is automatically computed before saving to the DB.
      It's persisted to make analytics and queries significantly faster.

    This design allows:
    - Multiple reusable schedule templates;
    - Templates with custom durations per day;
    - Efficient calculation of total hours per template;
    - Future caching (e.g. Redis) of per-template schedule blocks;
    - Extending with seasonal logic or temporary overrides.
    """
    template = models.ForeignKey(
        ScheduleTemplate,
        on_delete=models.CASCADE,
        related_name="days",
        help_text=_("The schedule template to which this day belongs.")
    )
    weekday = models.CharField(
        max_length=15,
        choices=enum_to_choices(WeekdayEnum),
        verbose_name=_("Weekday"),
        help_text=_("Day of the week belonging to this schedule.")
    )
    opened_at = models.TimeField(
        verbose_name=_("Opens at"),
        help_text=_("Start time for this weekday’s working period.")
    )
    closed_at = models.TimeField(
        verbose_name=_("Closes at"),
        help_text=_("End time for this weekday’s working period.")
    )
    is_open = models.BooleanField(
        default=True,
        verbose_name=_("Is open"),
        help_text=_("Whether this weekday is considered a working day.")
    )
    hours = models.DurationField(
        default=timedelta(0),
        editable=False,
        verbose_name=_("Scheduled hours"),
        help_text=_("Total computed scheduled duration for this weekday.")
    )

    class Meta:
        unique_together = ("template", "weekday")
        ordering = ["template", "weekday"]
        verbose_name = _("Schedule")
        verbose_name_plural = _("Schedules")

    def __str__(self):
        return f"{self.template.name} - {self.weekday}"


class Attendance(BaseModelMixin):
    """
    Represents the global daily attendance sheet for a specific date.

    This model defines a *single collective sheet per day*.
    Each Attendance is linked to multiple AttendanceEntry records, one per employee,
    forming the “daily register”. The unique constraint on `date` ensures the system
    never creates more than one sheet for the same day.

    Responsibilities:
    - Minimal persistence: stores date, status (closed/computed), and generated code.
    - Acts as the root object for all employee attendance entries for that day.
    - Delegates business logic (sheet creation, generating codes with collision
      avoidance, closing operations, recomputation, bulk entry creation) to the
      AttendanceService.

    Notes:
    - Because this model represents a *collective* sheet, it contains no reference
      to `Employee`. Employees appear only through `AttendanceEntry`.
    - A closed Attendance sheet becomes immutable at the entry level.
    """

    name = models.CharField(max_length=255, verbose_name=_("Name"), null=True, blank=True)
    date = models.DateField(unique=True, verbose_name=_("Date"))
    code = models.CharField(max_length=100, unique=True, verbose_name=_("Code"))
    closed = models.BooleanField(default=False, verbose_name=_("Closed"))
    computed = models.BooleanField(default=False, verbose_name=_("Computed"))

    objects = AttendanceManager()

    class Meta:
        ordering = ["-date"]
        verbose_name = _("Attendance")
        verbose_name_plural = _("Attendances")
        indexes = [
            models.Index(fields=["date"]),
            models.Index(fields=["closed"]),
        ]

    def __str__(self) -> str:
        return f"Attendance {self.date.isoformat()}"

    # Helper methods (kept minimal):
    def generate_code(self) -> str:
        """
        Lightweight code generator. Production logic (collision avoidance,
        formatting rules) should be handled in service layer.
        """
        date_part = timezone.now().strftime("%d%m%y")
        random_part = "".join(random.choices(string.ascii_letters + string.digits, k=6))
        return f"{date_part}-{random_part}"

    def get_weekday_display(self) -> str:
        """
        Return a display-friendly weekday. Keep mapping / localization in services
        or a central helper if you support multiple locales.
        """
        return self.date.strftime("%A")


class AttendanceEntry(BaseModelMixin):
    """
    Represents a single employee’s attendance record inside a daily Attendance sheet.

    One AttendanceEntry = one employee for the given day (Attendance).
    The (employee, attendance) unique constraint enforces that an employee can appear
    only once in a day’s sheet. This aligns with the “collective daily register”
    design of the Attendance model.

    Responsibilities:
    - Store check-in/check-out times and precomputed durations.
    - Keep raw and computed fields lightweight for efficient reporting.
    - Expose helper methods for simple duration calculations.
    - Defer business rules (lateness, status decisions, overtime policies, 
      schedule comparison, validations) to AttendanceEntryService.

    Notes:
    - Computed fields (total_hours, overtime, undertime) are stored to optimize
      high-volume reporting queries.
    - Entries inherit the date indirectly from their Attendance; this ensures
      perfect daily grouping and avoids data divergence.
    """

    employee = models.ForeignKey(
        "hr.employees.models.Employee", 
        on_delete=models.CASCADE, 
        related_name="attendances", 
        verbose_name=_("Employee")
    )
    attendance = models.ForeignKey(
        Attendance, 
        on_delete=models.CASCADE, 
        related_name="entries", 
        verbose_name=_("Attendance")
    )
    leave = models.ForeignKey(
        "hr.leaves.models.Leave",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="attendances",
        verbose_name=_("Leave"),
    )
    manual = models.BooleanField(default=False, verbose_name=_("Manual entry"))
    check_in_time = models.TimeField(verbose_name=_("Check-in time"))
    check_out_time = models.TimeField(blank=True, null=True, verbose_name=_("Check-out time"))
    total_hours = models.DurationField(default=timedelta(0), verbose_name=_("Total hours"))
    overtime = models.DurationField(default=timedelta(0), verbose_name=_("Overtime"))
    undertime = models.DurationField(default=timedelta(0), verbose_name=_("Undertime"))
    status = models.CharField(
        choices=enum_to_choices(AttendanceStatus),
        default=AttendanceStatus.ABSENT.value,
        verbose_name=_("Status"),
    )

    class Meta:
        unique_together = ("employee", "attendance")
        ordering = ["-attendance__date"]
        verbose_name = _("Attendance entry")
        verbose_name_plural = _("Attendance entries")
        indexes = [
            models.Index(fields=["employee", "attendance"]),
            models.Index(fields=["employee", "attendance", "status"]),
        ]

    def __str__(self) -> str:
        # Use attendance.date because this model has no direct date field
        return f"{self.employee} - {self.attendance.date.isoformat()} : {self.get_status_display()}"

    # ---------- Lightweight helpers (no heavy DB access) ----------
    def get_total_hours_delta(self) -> timedelta:
        """
        Compute duration between check-in and check-out times.
        Returns timedelta(0) when check_out_time is missing.
        Handles overnight shifts when check_out_time < check_in_time.
        """
        if not (self.check_in_time and self.check_out_time):
            return timedelta(0)

        # combine with a reference date (attendance.date) — better than using timezone.now()
        ref_date = self.attendance.date
        start = timezone.datetime.combine(ref_date, self.check_in_time)
        end = timezone.datetime.combine(ref_date, self.check_out_time)
        delta = end - start
        if delta.total_seconds() < 0:
            delta += timedelta(days=1)
        return delta

    def recalc_durations(self, scheduled_hours: Optional[timedelta]) -> Tuple[timedelta, timedelta, timedelta]:
        """
        Recalculate total_hours/overtime/undertime based on the provided scheduled_hours.
        - scheduled_hours may be None (in which case overtime/undertime are zero).
        Returns a tuple (total_hours, overtime, undertime).
        Service layer should call this helper and persist results.
        """
        total = self.get_total_hours_delta()
        overtime = timedelta(0)
        undertime = timedelta(0)
        if scheduled_hours is not None:
            # overtime is positive when total > scheduled_hours
            overtime = total - scheduled_hours
            if overtime.total_seconds() < 0:
                # represent undertime as positive duration in undertime field
                undertime = -overtime
                overtime = timedelta(0)
        return total, overtime, undertime

    # Validation: keep simple, guard against closed periods.
    def clean(self) -> None:
        # If attendance is provided, ensure date is not in a closed period.
        if self.attendance and self.attendance.date:
            if ClosingAttendance.objects.filter(date__gte=self.attendance.date).exists():
                raise ValidationError(_("Cannot create or modify an entry within a closed period."))
        super().clean()

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:
        """
        Keep save simple: run full_clean and delegate.
        Business logic (status decisions and calculations) should be applied
        by AttendanceEntryService which will set the fields before calling save().
        """
        self.full_clean()
        return super().save(*args, **kwargs)


class ClosingAttendance(BaseModelMixin):
    """
    Defines a closing boundary for attendance periods.

    Once a closing is created for a given date, all Attendance sheets on or before
    that date become frozen (immutable). This enables payroll validation, historical
    integrity, and prevents retroactive modifications.

    Responsibilities:
    - Store the closing date and maintain a linked-list chain of closings
      (previous) for traversal and audit history.
    - Enforce minimal invariants at the model level:
        * closing date cannot move backward,
        * locked closings are immutable,
        * closing date cannot exceed acceptable future thresholds.
    """

    last_closing = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        editable=False,
        related_name="next_closings",
        verbose_name=_("Previous closing"),
    )
    date = models.DateField(verbose_name=_("Closing date"))
    locked = models.BooleanField(default=False, verbose_name=_("Locked"))

    class Meta:
        verbose_name = _("Closing attendance")
        verbose_name_plural = _("Closing attendances")
        constraints = [
            models.UniqueConstraint(fields=["date"], name="closing_attendance_unique_date")
        ]
        indexes = [models.Index(fields=["date"])]
        ordering = ["-date"]

    def __str__(self) -> str:
        return f"Closing until {self.date.isoformat()}"

    def clean(self) -> None:
        """
        Validate:
        - date cannot be further than X hours in the future (policy).
        - if locked is True it's not editable (model enforces).
        - new closing date should be after last_closing.date.
        """
        # example policy: not more than 3 hours in the future
        now = timezone.now()
        max_future = now + timedelta(hours=3)
        if self.date > max_future.date():
            raise ValidationError(_("Closing date cannot be more than 3 hours in the future."))

        if self.locked:
            raise ValidationError(_("This closing is locked and cannot be modified."))

        if self.last_closing and self.date <= self.last_closing.date:
            raise ValidationError(_("Closing date must be after the previous closing date."))

        super().clean()

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:
        """
        Set last_closing automatically on new record (if not provided).
        Run full_clean, persist.
        """
        if self._state.adding and not self.last_closing:
            latest = ClosingAttendance.objects.first()
            if latest:
                self.last_closing = latest

        self.full_clean()
        result = super().save(*args, **kwargs)

        # Do minimal linking (maintain previous object's next_closing pointer).
        if self.last_closing:
            self.last_closing.next_closings.set([self])  # keep relation consistent
        return result

    def delete(self, using=None, keep_parents=False):
        return super().delete(using=using, keep_parents=keep_parents)


class AttendanceSettings(SingletonMixin):
    """
    Singleton model storing attendance-related configuration.
    
    - Holds global configuration for attendance logic.
    - Keep fields minimal. Use a service to update settings and propagate side-effects.

    Use AttendanceSettingsService to mutate settings + trigger cache invalidation.
    """
    last_closing = models.ForeignKey(
        ClosingAttendance, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name=_("Last closing")
    )
    late_acceptable = models.DurationField(
        default=timedelta(minutes=15), 
        verbose_name=_("Late acceptable duration")
    )
    accept_late_count = models.IntegerField(
        default=3, 
        verbose_name=_("Allowed late count")
    )
    accept_excuse_count = models.IntegerField(
        default=3, 
        verbose_name=_("Allowed excuse count")
    )
    work_sunday = models.BooleanField(
        default=False, 
        verbose_name=_("Work on Sunday")
    )
    work_saturday = models.BooleanField(
        default=False, 
        verbose_name=_("Work on Saturday")
    )
    total_working_time = models.DurationField(
        default=timedelta(hours=0), 
        verbose_name=_("Total working time")
    )

    class Meta(SingletonMixin.Meta):
        ordering = ["-id"]
        verbose_name = _("Attendance settings")
        verbose_name_plural = _("Attendance settings")

