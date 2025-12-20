from __future__ import annotations

import random
import string
from datetime import timedelta

from django.core.exceptions import ValidationError
from django.db import models, transaction
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

from utils_mixins.models import BaseModelMixin, SingletonMixin
from utils_mixins.fn import enum_to_choices

from .enums import WeekdayEnum, AttendanceStatus, BlockType


"""
Capabilities supported by these models:

1. Paid and unpaid breaks
2. Multiple breaks per day
3. Split work periods
4. Night shifts
5. Temporary exits
6. Partial absences
7. Planned vs actual comparison
8. HR audits
9. Multiple HR policies
10. Multi-country payroll support
"""


class TimeBlock(BaseModelMixin):
    """
    Atomic time segment within a workday.

    Used to represent work, breaks, or excused absences.
    """

    attendance_entry = models.ForeignKey(
        "AttendanceEntry",
        on_delete=models.CASCADE,
        related_name="time_blocks",
        verbose_name=_("Attendance entry"),
    )

    start_time = models.TimeField(verbose_name=_("Start time"))
    end_time = models.TimeField(verbose_name=_("End time"))

    type = models.CharField(
        max_length=20,
        choices=enum_to_choices(BlockType),
        default=BlockType.WORK.value,
        choices=[
            ("WORK", _("Work")),
            ("BREAK", _("Break")),
            ("EXCUSE", _("Excused absence")),
        ],
        verbose_name=_("Block type"),
    )

    paid = models.BooleanField(
        default=True,
        verbose_name=_("Paid"),
        help_text=_("Indicates whether this time block is paid."),
    )

    duration = models.DurationField(
        default=timedelta(0),
        editable=False,
        verbose_name=_("Duration"),
    )

    class Meta:
        ordering = ["start_time"]
        constraints = [
            models.CheckConstraint(
                condition=models.Q(end_time__gt=models.F("start_time")),
                name="timeblock_end_after_start",
            )
        ]


class ScheduleTemplate(BaseModelMixin):
    """
    Weekly schedule pattern.

    Acts as a reusable container for working schedules.
    Can be assigned to employees, teams, or departments.

    Examples:
        - Standard Day Shift
        - Night Shift
        - Weekend Staff
        - Warehouse Team A
    """

    name = models.CharField(
        max_length=255,
        unique=True,
        help_text=_("Human-readable name of the schedule template."),
    )
    description = models.TextField(
        blank=True,
        help_text=_("Optional description or notes."),
    )

    class Meta:
        ordering = ["name"]

    def __str__(self) -> str:
        return self.name


class ScheduleDay(BaseModelMixin):
    """
    Defines working hours for a single weekday inside a schedule template.
    """

    template = models.ForeignKey(
        ScheduleTemplate,
        on_delete=models.CASCADE,
        related_name="days",
        help_text=_("Parent schedule template."),
    )
    weekday = models.CharField(
        max_length=15,
        choices=enum_to_choices(WeekdayEnum),
        verbose_name=_("Weekday"),
    )
    opened_at = models.TimeField(
        verbose_name=_("Opening time"),
    )
    closed_at = models.TimeField(
        verbose_name=_("Closing time"),
    )
    is_open = models.BooleanField(
        default=True,
        verbose_name=_("Is working day"),
    )
    hours = models.DurationField(
        default=timedelta(0),
        editable=False,
        verbose_name=_("Scheduled hours"),
        help_text=_("Computed total scheduled duration for this day."),
    )

    class Meta:
        unique_together = ("template", "weekday")
        ordering = ["template", "weekday"]
        verbose_name = _("Schedule day")
        verbose_name_plural = _("Schedule days")

    def __str__(self) -> str:
        return f"{self.template.name} - {self.weekday}"


class ScheduleBreak(BaseModelMixin):
    """
    Planned break within a scheduled workday.
    """

    schedule_day = models.ForeignKey(
        ScheduleDay,
        on_delete=models.CASCADE,
        related_name="breaks",
    )

    start_time = models.TimeField()
    end_time = models.TimeField()
    paid = models.BooleanField(default=False)

    class Meta:
        ordering = ["start_time"]
        unique_together = ("schedule_day", "start_time", "end_time")


class Attendance(BaseModelMixin):
    """
    Collective attendance sheet for a specific date.

    Acts as the root container for all employee entries of the day.
    """

    name = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_("Name"),
    )
    date = models.DateField(
        unique=True,
        verbose_name=_("Date"),
    )
    code = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Code"),
    )
    closed = models.BooleanField(
        default=False,
        verbose_name=_("Closed"),
    )
    computed = models.BooleanField(
        default=False,
        verbose_name=_("Computed"),
    )

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

    def generate_code(self) -> str:
        """
        Lightweight identifier generator.
        Collision handling belongs to service layer.
        """
        date_part = timezone.now().strftime("%d%m%y")
        random_part = "".join(
            random.choices(string.ascii_letters + string.digits, k=6)
        )
        return f"{date_part}-{random_part}"

    def get_weekday_display(self) -> str:
        """
        Returns weekday name for display purposes.
        """
        return self.date.strftime("%A")


class AttendanceEntry(BaseModelMixin):
    """
    Attendance record for a single employee on a given day.
    """

    employee = models.ForeignKey(
        "hr.employees.models.Employee",
        on_delete=models.CASCADE,
        related_name="attendances",
        verbose_name=_("Employee"),
    )
    attendance = models.ForeignKey(
        Attendance,
        on_delete=models.CASCADE,
        related_name="entries",
        verbose_name=_("Attendance"),
    )
    leave = models.ForeignKey(
        "hr.leaves.models.Leave",
        on_delete=models.DO_NOTHING,
        null=True,
        blank=True,
        related_name="attendances",
        verbose_name=_("Leave"),
    )

    manual = models.BooleanField(
        default=False,
        verbose_name=_("Manual entry"),
    )

    total_hours = models.DurationField(
        default=timedelta(0),
        verbose_name=_("Total hours"),
    )
    overtime = models.DurationField(
        default=timedelta(0),
        verbose_name=_("Overtime"),
    )
    undertime = models.DurationField(
        default=timedelta(0),
        verbose_name=_("Undertime"),
    )

    total_worked = models.DurationField(
        default=timedelta(0),
        verbose_name=_("Worked time"),
    )
    total_break = models.DurationField(
        default=timedelta(0),
        verbose_name=_("Break time"),
    )
    total_paid = models.DurationField(
        default=timedelta(0),
        verbose_name=_("Paid time"),
    )

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
        return (
            f"{self.employee} - "
            f"{self.attendance.date.isoformat()} : "
            f"{self.get_status_display()}"
        )

    def clean(self) -> None:
        """
        Prevent modifications in closed attendance periods.
        """
        if self.attendance and self.attendance.date:
            if ClosingAttendance.objects.filter(
                date__gte=self.attendance.date
            ).exists():
                raise ValidationError(
                    _("Cannot create or modify entries in a closed period.")
                )
        super().clean()

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:
        """
        Persist entry after validation.
        Business logic is applied upstream by services.
        """
        self.full_clean()
        return super().save(*args, **kwargs)


class ClosingAttendance(BaseModelMixin):
    """
    Defines an immutable closing boundary for attendance periods.
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
    date = models.DateField(
        verbose_name=_("Closing date"),
    )
    locked = models.BooleanField(
        default=False,
        verbose_name=_("Locked"),
    )

    class Meta:
        ordering = ["-date"]
        verbose_name = _("Attendance closing")
        verbose_name_plural = _("Attendance closings")
        constraints = [
            models.UniqueConstraint(
                fields=["date"],
                name="unique_attendance_closing_date",
            )
        ]
        indexes = [
            models.Index(fields=["date"]),
        ]

    def __str__(self) -> str:
        return f"Closing until {self.date.isoformat()}"

    def clean(self) -> None:
        """
        Enforce chronological and immutability rules.
        """
        now = timezone.now()
        if self.date > (now + timedelta(hours=3)).date():
            raise ValidationError(
                _("Closing date cannot be more than 3 hours in the future.")
            )

        if self.locked:
            raise ValidationError(
                _("This closing is locked and cannot be modified.")
            )

        if self.last_closing and self.date <= self.last_closing.date:
            raise ValidationError(
                _("Closing date must be after the previous closing.")
            )

        super().clean()

    @transaction.atomic
    def save(self, *args, **kwargs) -> None:
        """
        Automatically link to the previous closing.
        """
        if self._state.adding and not self.last_closing:
            latest = ClosingAttendance.objects.first()
            if latest:
                self.last_closing = latest

        self.full_clean()
        result = super().save(*args, **kwargs)

        if self.last_closing:
            self.last_closing.next_closings.set([self])

        return result


class AttendanceSettings(SingletonMixin):
    """
    Global configuration for attendance behavior.
    """

    last_closing = models.ForeignKey(
        ClosingAttendance,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_("Last closing"),
    )
    late_acceptable = models.DurationField(
        default=timedelta(minutes=15),
        verbose_name=_("Acceptable lateness duration"),
    )
    accept_late_count = models.IntegerField(
        default=3,
        verbose_name=_("Allowed late occurrences"),
    )
    accept_excuse_count = models.IntegerField(
        default=3,
        verbose_name=_("Allowed excused absences"),
    )
    work_sunday = models.BooleanField(
        default=False,
        verbose_name=_("Work on Sunday"),
    )
    work_saturday = models.BooleanField(
        default=False,
        verbose_name=_("Work on Saturday"),
    )

    class Meta(SingletonMixin.Meta):
        ordering = ["-id"]
        verbose_name = _("Attendance settings")
        verbose_name_plural = _("Attendance settings")
