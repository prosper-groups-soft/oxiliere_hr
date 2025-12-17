from typing import List, Optional, Any
from ninja.orm import ModelSchema
from hr.employees.schemas import EmployeeDetailOut
from .models import Leave, LeaveEmployee
from utils_mixins.schemas import LightUserDetailOut


# ---------------------   Leave Schemas   -------------------------
LEAVE_FIELDS = [
    'start_date',
    'end_date',
    'reason',
    'everyone',
    'paid',
    'leave_type',
    'status',
    'approved_at'
]
class LeaveCreateIn(ModelSchema):

    class Meta:
        model = Leave
        fields = [
            'applicable_to_id',
            *LEAVE_FIELDS
        ]
        fields_optional = [
            'reason',
            'everyone',
            'paid',
            'leave_type',
            'status',
            'approved_at'
        ]


class LeaveUpdateIn(ModelSchema):

    class Meta:
        model = Leave
        fields = [
            'applicable_to_id',
            *LEAVE_FIELDS
        ]
        fields_optional = '__all__'


class LeaveDetailOut(ModelSchema):
    applicable_to: Optional[EmployeeDetailOut]
    approved_by: Optional[LightUserDetailOut]

    class Meta:
        model = Leave
        fields = [
            'applicable_to',
            'approved_by',
            *LEAVE_FIELDS
        ]


# --------------------   LeaveEmployee Schemas   ---------------------------
LEAVE_EMPLOYEE_FIELDS = [
    'employee_id',
    'leave_id',
    'created_by',
]
class LeaveEmployeeCreateIn(ModelSchema):

    class Meta:
        model = LeaveEmployee
        fields = LEAVE_EMPLOYEE_FIELDS
        fields_optional = [
            'created_by'
        ]


class LeaveEmployeeUpdateIn(ModelSchema):

    class Meta:
        model = LeaveEmployee
        fields = LEAVE_EMPLOYEE_FIELDS
        fields_optional = '__all__'


class LeaveEmployeeDetailOut(ModelSchema):
    employee:  EmployeeDetailOut
    leave: LeaveDetailOut
    created_by: LightUserDetailOut

    class Meta:
        model = LeaveEmployee
        fields = [
            'employee',
            'leave',
            'created_by',
        ]
        
