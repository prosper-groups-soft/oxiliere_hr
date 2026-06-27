from datetime import date, datetime, timedelta
from uuid     import UUID
from typing   import Optional, List, Literal

from django.db import models
from django.db.models import Q
from pydantic  import field_validator
from ninja     import Schema, FilterSchema, ModelSchema

from hr.attendance.models import (
    DailyRegister,
    TimePunch,
    PeriodArchiveLock,
    ShiftPolicy,
    ShiftDetail,
    ShiftPeriod,
    AttendanceSettings
)
from hr.employees.schemas import EmployeeOut
from hr.attendance.enums  import PunchType
from hr.schemas import BaseFilter


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
            "total_excused",
            "is_finalized",
        ]


class DailyRegisterFinalizeIn(Schema):
    date: date
    

class DailyRegisterFilter(BaseFilter):
    is_finalized: Optional[bool]
    date_from: Optional[date]
    date_to: Optional[date]
    
    def filter_date_from(self, value: date):
        return models.Q(date__gte=value)
    
    def filter_date_to(self, value: date):
        return models.Q(date__lte=value)
    
    def filter_search(self, value: str):
        return models.Q(code__icontains=value)
    

class DailyViewFilter(BaseFilter):
    """ Filters for the daily attendance view. """
    date: date
    org_unit: Optional[str] = None
    status: Optional[str] = None


class DailyViewEntryOut(Schema):
    """
    Enriched attendance entry for the daily register view.
    Includes check-in/out times, expected schedule, and computed anomalies.
    """
    id: UUID
    employee_id: UUID
    employee_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    avatar_url: Optional[str] = None
    job_title: Optional[str] = None
    org_unit_id: Optional[UUID] = None
    org_unit_name: Optional[str] = None

    register_date: date

    # Horaires réels (depuis les TimePunch)
    check_in: Optional[str] = None      # HH:mm du premier WORK punch
    check_out: Optional[str] = None     # HH:mm du dernier WORK punch
    check_in_at: Optional[datetime] = None   # timestamp ISO complet
    check_out_at: Optional[datetime] = None
    check_in_punch_id: Optional[UUID] = None  # ID du premier WORK punch (pour edition inline)
    check_out_punch_id: Optional[UUID] = None # ID du dernier WORK punch
    is_manual_entry: bool = False

    # Horaires attendus (depuis le planning)
    expected_in: Optional[str] = None   # HH:mm
    expected_out: Optional[str] = None  # HH:mm
    expected_break_duration: Optional[int] = None  # minutes

    # Informations sur le planning
    is_working_day: bool = False
    schedule_name: Optional[str] = None    # nom de la politique/shift
    schedule_source: Optional[str] = None  # "policy" | "override" | "holiday" | "none"

    # Durées calculées
    recorded_work: timedelta = timedelta(0)
    recorded_break: timedelta = timedelta(0)
    overtime: timedelta = timedelta(0)
    shortfall: timedelta = timedelta(0)
    status: str = "ABSENT"
    remarks: Optional[str] = None

    # Verrouillage
    is_locked: bool = False
    is_finalized: bool = False

    # Anomalies calculées
    anomalies: list[str] = []
    

class TimeSheetOut(Schema):
    employee: EmployeeOut
    
    id: UUID
    register_date: date

    recorded_work: timedelta
    recorded_break: timedelta
    overtime: timedelta
    shortfall: timedelta

    status: str
    remarks: Optional[str]

    @staticmethod
    def resolve_register_date(obj):
        return obj.register.date


class TimeSheetUpdateIn(Schema):
    remarks: Optional[str] = None
    status: Optional[str] = None  # Permet de changer le statut (ex: ABSENT → EXCUSED)

class PunchCreateIn(Schema):
    timestamp: datetime
    punch_type: PunchType = PunchType.WORK
    is_manual: bool = False
    employee_id: UUID = None # Optional for HR
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class PunchAdjustIn(Schema):
    start_at: Optional[datetime] = None
    end_at: Optional[datetime] = None
    punch_type: Optional[PunchType] = None


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


class SelfPunchIn(Schema):
    """ Minimal input for self-punching: only timestamp + location. """
    timestamp: datetime
    latitude: Optional[float] = None
    longitude: Optional[float] = None


class SelfPunchOut(Schema):
    """
    Returns the punch result + an action indicator.
    action='in' means a new punch was created (clock-in).
    action='out' means an open punch was closed (clock-out).
    """
    punch: PunchOut
    action: Literal["in", "out"]
    employee_id: UUID


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


class ShiftPeriodOut(ModelSchema):
    class Meta:
        model = ShiftPeriod
        fields = [
            "id",
            "name",
            "period_type",
            "start_time",
            "end_time",
        ]


class ShiftDetailOut(ModelSchema):
    periods: List[ShiftPeriodOut]

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
    description: Optional[str] = ""
    weekly_target_hours: int
    daily_configs: dict
    
    
class ShiftPolicyUpdateIn(Schema):
    name: Optional[str] = None
    description: Optional[str] = None
    weekly_target_hours: Optional[int] = None  # in hours (same as ShiftPolicyCreateIn)
    daily_configs: Optional[dict] = None


class EmploymentSchemeAssignIn(Schema):
    employee_id: UUID
    policy_id: UUID
    start_date: date
    end_date: Optional[date] = None
    recurrence: str = "NONE"
    override_policy_id: Optional[UUID] = None
    override_valid_from: Optional[date] = None
    override_valid_until: Optional[date] = None
    override_recurrence: str = "NONE"
    override_recurrence_count: Optional[int] = None

    @field_validator("end_date")
    @classmethod
    def check_dates(cls, v, info):
        if v and v <= info.data["start_date"]:
            raise ValueError("end_date must be after start_date")
        return v


class EmploymentSchemeUpdateIn(Schema):
    """ All fields optional — only provided fields will be updated. """
    policy_id: Optional[UUID] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    recurrence: Optional[str] = None
    override_policy_id: Optional[UUID] = None
    override_valid_from: Optional[date] = None
    override_valid_until: Optional[date] = None
    override_recurrence: Optional[str] = None
    override_recurrence_count: Optional[int] = None


class AssignmentFilterIn(BaseFilter):
    """ Filters for the assignment list endpoint. """

    org_unit: Optional[str] = None
    recurrence: Optional[str] = None

    def filter_org_unit(self, value: Optional[str]) -> Q:
        """Filter by org unit ID (supports comma-separated UUIDs)."""
        if not value:
            return Q()
        if ',' in value:
            org_unit_ids = [u.strip() for u in value.split(',')]
            return Q(employee__position_history__org_unit__id__in=org_unit_ids, employee__position_history__is_current=True)
        return Q(employee__position_history__org_unit__id=value, employee__position_history__is_current=True)

    def filter_recurrence(self, value: Optional[str]) -> Q:
        """Filter by override recurrence mode (supports comma-separated)."""
        if not value:
            return Q()
        if ',' in value:
            modes = [m.strip().upper() for m in value.split(',')]
            return Q(override_recurrence__in=modes)
        return Q(override_recurrence__iexact=value.upper())

    def filter_search(self, value: str) -> Q:
        """Search across employee names and policy names."""
        return (
            Q(employee__last_name__icontains=value) |
            Q(employee__first_name__icontains=value) |
            Q(policy__name__icontains=value)
        )

    def apply_ordering(self, qs, ordering: Optional[str] = None):
        if not ordering:
            return qs.order_by('employee__last_name')
        ordering_map = {
            'name': ['employee__last_name', 'employee__first_name'],
            '-name': ['-employee__last_name', '-employee__first_name'],
            'policy': ['policy__name', 'employee__last_name'],
            '-policy': ['-policy__name', 'employee__last_name'],
            'org_unit': ['employee__position_history__org_unit__name', 'employee__last_name'],
            '-org_unit': ['-employee__position_history__org_unit__name', 'employee__last_name'],
        }
        order_fields = ordering_map.get(ordering, ['employee__last_name'])
        return qs.order_by(*order_fields)


class EmploymentSchemeOut(Schema):
    id: UUID
    employee_id: UUID
    employee_name: str
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_name: Optional[str] = None
    profile_photo: Optional[str] = None
    policy_id: UUID
    policy_name: str
    valid_from: date
    valid_until: Optional[date] = None
    is_active: bool = True
    recurrence: str = "NONE"
    job_title: Optional[str] = None
    current_status: Optional[str] = None
    override_policy_id: Optional[UUID] = None
    override_policy_name: Optional[str] = None
    override_valid_from: Optional[date] = None
    override_valid_until: Optional[date] = None
    override_recurrence: str = "NONE"
    override_recurrence_count: Optional[int] = None

    org_unit_id: Optional[UUID] = None
    org_unit_name: Optional[str] = None

    @staticmethod
    def resolve_employee_name(obj):
        return obj.employee.full_name

    @staticmethod
    def resolve_first_name(obj):
        return obj.employee.first_name

    @staticmethod
    def resolve_last_name(obj):
        return obj.employee.last_name

    @staticmethod
    def resolve_middle_name(obj):
        return obj.employee.middle_name

    @staticmethod
    def resolve_profile_photo(obj):
        return obj.employee.profile_photo.url if obj.employee.profile_photo else None

    @staticmethod
    def resolve_policy_name(obj):
        return obj.policy.name

    @staticmethod
    def resolve_job_title(obj):
        positions = getattr(obj.employee, 'prefetched_current_position', [])
        if positions:
            pos = positions[0]
            return pos.position.name if pos.position else None
        return None

    @staticmethod
    def resolve_current_status(obj):
        status_list = getattr(obj.employee, 'prefetched_current_status', [])
        if status_list and len(status_list) > 0:
            return status_list[0].status
        return None

    @staticmethod
    def resolve_org_unit_id(obj):
        positions = getattr(obj.employee, 'prefetched_current_position', [])
        if positions:
            pos = positions[0]
            return pos.org_unit.id if pos.org_unit else None
        return None

    @staticmethod
    def resolve_org_unit_name(obj):
        positions = getattr(obj.employee, 'prefetched_current_position', [])
        if positions:
            pos = positions[0]
            return pos.org_unit.name if pos.org_unit else None
        return None

    @staticmethod
    def resolve_override_policy_name(obj):
        if obj.override_policy:
            return obj.override_policy.name
        return None


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
    class Meta:
        model = AttendanceSettings
        fields = [
            "late_grace_period",
            "rounding_precision",
            "partial_absence_threshold"
        ]


class AttendanceSettingsUpdateIn(Schema):
    late_grace_period: Optional[timedelta] = None
    rounding_precision: Optional[int] = None
    partial_absence_threshold: Optional[timedelta] = None


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


# --- Maintenance Schemas ---

class MaintenanceDateIn(Schema):
    date: date


class ClosePunchesOut(Schema):
    """ Results of an automated punch closing operation. """
    closed_count: int
    affected_employees: List[EmployeeOut]
    details: List[dict]


class FlagAbsencesOut(Schema):
    """ Results of an automated absence flagging operation. """
    flagged_count: int
    absent_employees: List[EmployeeOut]
    details: List[dict]


# --- Validation Schemas ---

class TimesheetValidationIn(Schema):
    timesheet_id: UUID


class TimesheetValidationOut(Schema):
    """ Results of a timesheet consistency audit. """
    is_valid: bool
    errors: List[str]
    warnings: List[str]
    timesheet_summary: dict


# --- Extension Schemas ---

class WorkingDayCheckOut(Schema):
    """ Results of a specific working day check. """
    is_working: bool
    date: date
    employee_id: UUID
    shift: Optional[ShiftDetailOut] = None


class UnlockPeriodOut(Schema):
    """ Results of an administrative period unlock. """
    unlocked: bool
    previous_lock: Optional[PeriodArchiveLockOut] = None
