from ninja import ModelSchema
from typing import Optional, List
from .models import (
    ScheduleTemplate, 
    ScheduleDay, 
    Attendance, 
    AttendanceEntry, 
    ClosingAttendance, 
    AttendanceSettings
)
from hr.employees.schemas import EmployeeDetailOut
from hr.leaves.schemas import LeaveDetailOut



#---------------------  ScheduleTemplate Schemas  --------------------------
SCHEDULE_TEMPLATE_FIELDS = [
    'name',
    'description',
]
class ScheduleTemplateCreateIn(ModelSchema):
    """Schema for creating a schedule template."""

    class Meta:
        model = ScheduleTemplate
        fields = SCHEDULE_TEMPLATE_FIELDS
        fields_optional = ['description']


class ScheduleTemplateUpdateIn(ModelSchema):
    """Schema for updating a schedule template."""

    class Meta:
        model = ScheduleTemplate
        fields = SCHEDULE_TEMPLATE_FIELDS
        fields_optional = "__all__"


class ScheduleTemplateOut(ModelSchema):
    """Detailed schedule template including related schedule days."""

    class LightScheduleDayOut(ModelSchema):
        """Nested representation of a schedule day."""
        class Meta:
            model = ScheduleDay
            fields = [
                "id",
                "weekday",
                "opened_at",
                "closed_at",
                "is_open",
                "hours",
            ]

    days: List[LightScheduleDayOut]

    class Meta:
        model = ScheduleTemplate
        fields = [
            "id",
            *SCHEDULE_TEMPLATE_FIELDS
        ]


#--------------------------  ScheduleDay Schemas  ---------------------------
SCHEDULE_DAY_FIELDS = [
    'weekday',
    'opened_at',
    'closed_at',
    'is_open',
]
class ScheduleDayCreateIn(ModelSchema):
    """Schema for creating a schedule day."""

    class Meta:
        model = ScheduleDay
        fields = [
            'template_id',
            *SCHEDULE_DAY_FIELDS
        ]
        fields_optional = ['is_open']


class ScheduleDayUpdateIn(ModelSchema):
    """Schema for updating a schedule day."""

    class Meta:
        model = ScheduleDay
        fields = [
            'template_id',
            *SCHEDULE_DAY_FIELDS
        ]
        fields_optional = "__all__"


class ScheduleDayDetailOut(ModelSchema):
    """Detailed representation of a schedule day."""

    class LightScheduleTemplateOut(ModelSchema):
        class Meta:
            model = ScheduleTemplate
            fields = ["id", "name"]

    template: LightScheduleTemplateOut

    class Meta:
        model = ScheduleDay
        fields = [
            "id",
            "weekday",
            "opened_at",
            "closed_at",
            "is_open",
            "hours",
            "template",
        ]


#---------------------  Attendance Schemas  ----------------------------
ATTENDANCE_FIELDS = [
    'name',
    'date',
    'code',
    'closed',
]
class AttendanceCreateIn(ModelSchema):

    class Meta:
        model = Attendance
        fields = ATTENDANCE_FIELDS
        fields_optional = [
            'name',
            'closed'
        ]


class AttendanceUpdateIn(ModelSchema):

    class Meta:
        model = Attendance
        fields = ATTENDANCE_FIELDS
        fields_optional = '__all__'


class AttendanceDetailOut(ModelSchema):

    class Meta:
        model = Attendance
        fields = [
            'id',
            'computed',
            *ATTENDANCE_FIELDS
        ]


#----------------------  AttendanceEntry Schemas  --------------------------
ATTENDANCE_ENTRY_FIELDS = [
    'manual',
    'check_in_time',
    'check_out_time',
]
class AttendanceEntryCreateIn(ModelSchema):

    class Meta:
        model = AttendanceEntry
        fields = [
            'employee_id',
            'attendance_id',
            'leave_id',
            *ATTENDANCE_ENTRY_FIELDS
        ]
        fields_optional = [
            'manual', 
            'check_out_time',
            'leave_id'
        ]


class AttendanceEntryUpdateIn(ModelSchema):

    class Meta:
        model = AttendanceEntry
        fields = [
            'employee_id',
            'attendance_id',
            'leave_id',
            *ATTENDANCE_ENTRY_FIELDS,
        ]
        fields_optional = '__all__'


class AttendanceEntryDetailOut(ModelSchema):
    employee: EmployeeDetailOut
    attendance: AttendanceDetailOut
    leave: Optional[LeaveDetailOut]

    class Meta:
        model = AttendanceEntry
        fields = [
            'id',
            'employee',
            'attendance',
            'leave',
            'total_hours',
            'overtime',
            'undertime',
            'status',
            *ATTENDANCE_ENTRY_FIELDS,
        ]


#-----------------  ClosingAttendance Schemas ----------------------------
CLOSING_ATTENDANCE_FIELDS = [
    'date',
    'locked',
]
class ClosingAttendanceCreateIn(ModelSchema):
    
    class Meta:
        model = ClosingAttendance
        fields = [
            'last_closing_id',
            *CLOSING_ATTENDANCE_FIELDS
        ]
        fields_optional = [
            'last_closing_id', 
            'locked'
        ]


class ClosingAttendanceUpdateIn(ModelSchema):

    class Meta:
        model = ClosingAttendance
        fields = [
            'last_closing_id',
            *CLOSING_ATTENDANCE_FIELDS
        ]
        fields_optional = '__all__'


class ClosingAttendanceDetailOut(ModelSchema):

    class LightClosingAttendanceDetailOut(ModelSchema):
        class Meta:
            model = ClosingAttendance
            fields = ['id', *CLOSING_ATTENDANCE_FIELDS]

    last_closing: Optional[LightClosingAttendanceDetailOut]

    class Meta:
        model = ClosingAttendance
        fields = [
            'id',
            'last_closing',
            *CLOSING_ATTENDANCE_FIELDS
        ]



#-----------------  AttendanceSettings Schemas   ----------------------
ATTENDANCE_SETTINGS_FIELDS = [
    'late_acceptable',
    'accept_late_count',
    'accept_excuse_count',
    'work_sunday',
    'work_saturday',
    'total_working_time',
]


class AttendanceSettingsUpdateIn(ModelSchema):
    
    class Meta:
        model = AttendanceSettings
        fields = ATTENDANCE_SETTINGS_FIELDS
        fields_optional = '__all__'


class AttendanceSettingsDetailOut(ModelSchema):
    last_closing: Optional[ClosingAttendanceDetailOut]

    class Meta:
        model = AttendanceSettings
        fields = [
            'id',
            'last_closing',
            *ATTENDANCE_SETTINGS_FIELDS
        ]

