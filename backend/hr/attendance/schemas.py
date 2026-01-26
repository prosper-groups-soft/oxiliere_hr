from datetime import date, datetime, timedelta
from typing   import Optional, List

from ninja     import Schema, Field, FilterSchema, ModelSchema
from pydantic  import field_validator
from django.db import models

from hr.attendance.models import (
    DailyRegister,
    TimePunch,
    PeriodArchiveLock,
    ShiftPolicy,
    ShiftDetail,
    AttendanceSettings,
)
from hr.attendance.enums import PunchType


class DurationOut(Schema):
    seconds: int
    human: str


class DailyRegisterOut(ModelSchema):
    class Meta:
        model = DailyRegister
        fields = [
            "id",
            "date",
            "code",
            "total_employees_expected",
            "total_absences",
            "is_finalized",
        ]


class DailyRegisterFinalizeIn(Schema):
    date: date


class TimeSheetOut(Schema):
    id: int
    employee_id: int
    register_date: date

    recorded_work: timedelta
    recorded_break: timedelta
    overtime: timedelta
    shortfall: timedelta

    status: str
    remarks: Optional[str]


class TimeSheetUpdateIn(Schema):
    remarks: Optional[str] = None


class PunchCreateIn(Schema):
    timestamp: datetime
    punch_type: str = Field(default=PunchType.WORK)
    is_manual: bool = False


class PunchAdjustIn(Schema):
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None


class PunchOut(ModelSchema):
    class Meta:
        model = TimePunch
        fields = [
            "id",
            "punch_type",
            "start_at",
            "end_at",
            "duration",
            "is_manual_entry",
        ]


class PunchValidationOut(Schema):
    errors: List[str]
    is_valid: bool


class CanModifyOut(Schema):
    can_modify: bool
    reason: Optional[str] = None


class PeriodArchiveLockOut(ModelSchema):
    locked_by_id: Optional[int]

    class Meta:
        model = PeriodArchiveLock
        fields = [
            "id",
            "locked_until",
            "reason",
        ]


class ShiftDetailOut(ModelSchema):
    class Meta:
        model = ShiftDetail
        fields = [
            "weekday",
            "start_time",
            "end_time",
            "break_start_time",
            "break_duration",
            "is_working_day",
            "flexible_hours",
        ]


class ShiftPolicyOut(ModelSchema):
    details: List[ShiftDetailOut]

    class Meta:
        model = ShiftPolicy
        fields = [
            "id",
            "name",
            "description",
            "weekly_target_hours",
        ]


class ShiftPolicyCreateIn(Schema):
    name: str
    weekly_target_hours: int
    daily_configs: dict


class EmploymentSchemeAssignIn(Schema):
    employee_id: int
    policy_id: int
    start_date: date
    end_date: Optional[date] = None

    @field_validator("end_date")
    @classmethod
    def check_dates(cls, v, info):
        if v and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class WeeklyPlanningDayOut(Schema):
    date: date
    is_working: bool
    start: Optional[str]
    end: Optional[str]
    break_start: Optional[str]
    break_limit: Optional[timedelta]


class WeeklyPlanningOut(Schema):
    employee_id: int
    days: List[WeeklyPlanningDayOut]


class RotationCreateIn(Schema):
    employee_id: int
    start_date: date
    num_weeks: int
    policy_ids: List[int]


class RotationBackfillIn(Schema):
    look_ahead_days: int = 30


class AttendanceSettingsOut(ModelSchema):
    active_archive_lock_date: Optional[date]

    class Meta:
        model = AttendanceSettings
        fields = [
            "late_grace_period",
            "rounding_precision",
            "partial_absence_threshold"
        ]


class AttendanceSettingsUpdateIn(Schema):
    late_grace_period: Optional[timedelta]
    rounding_precision: Optional[int]
    partial_absence_threshold: Optional[timedelta]


class TimeSheetFilter(FilterSchema):
    employee_id: Optional[int]
    status: Optional[str]
    date_from: Optional[date]
    date_to: Optional[date]

    def filter_date_from(self, value: date):
        return models.Q(register__date__gte=value)

    def filter_date_to(self, value: date):
        return models.Q(register__date__lte=value)



class WorkingDaysPreviewOut(Schema):
    total_working_days: int
    breakdown: dict[int, int]
