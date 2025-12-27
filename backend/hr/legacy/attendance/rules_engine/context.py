from datetime import timedelta
from django.utils.timezone import datetime
from typing import List, Optional
from core.rules_engine.context import RuleContext
from attendance.models import (
    AttendanceEntry,
    Attendance,
    ScheduleDay,
    TimeBlock,
    AttendanceSettings,
)


class AttendanceRuleContext(RuleContext):
    """
    Pure RuleContext for attendance module.
    Contains all data a rule may need for evaluating a single AttendanceEntry.
    """

    def __init__(
        self,
        attendance_entry: AttendanceEntry,
        schedule_day: Optional[ScheduleDay] = None,
        settings: Optional[AttendanceSettings] = None,
    ):
        if attendance_entry is None:
            raise ValueError("attendance_entry cannot be None")

        self.attendance_entry: AttendanceEntry = attendance_entry
        self.attendance: Attendance = attendance_entry.attendance
        self.employee = attendance_entry.employee
        self.leave = attendance_entry.leave
        self.manual: bool = attendance_entry.manual
        self.date: datetime.date = self.attendance.date
        self.weekday: str = self.attendance.get_weekday_display()
        self.schedule_day: Optional[ScheduleDay] = schedule_day
        self.settings: AttendanceSettings = settings or AttendanceSettings.load()

        # Fetch all TimeBlocks for this entry, ordered by start_time
        self.time_blocks: List[TimeBlock] = list(
            attendance_entry.time_blocks.all().order_by("start_time")
        )

        # Precompute simple aggregates (optional)
        self.total_worked: timedelta = attendance_entry.total_worked
        self.total_break: timedelta = attendance_entry.total_break
        self.total_paid: timedelta = attendance_entry.total_paid
        self.total_hours: timedelta = attendance_entry.total_hours
        self.overtime: timedelta = attendance_entry.overtime
        self.undertime: timedelta = attendance_entry.undertime
        self.status: str = attendance_entry.status

    def __repr__(self):
        return (
            f"<AttendanceRuleContext(employee={self.employee}, date={self.date}, "
            f"time_blocks={len(self.time_blocks)}, status={self.status})>"
        )
