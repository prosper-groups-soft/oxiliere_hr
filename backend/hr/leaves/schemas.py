from datetime import date
from uuid import UUID
from typing import Optional
from ninja import Schema
from ninja.orm import ModelSchema
from hr.employees.schemas import EmployeeDetailOut
from .models import Leave, LeaveEmployee
from utils_mixins.schemas import LightUserDetailOut, BaseSearchFilter




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


class LeaveFilterIn(BaseSearchFilter):
    status: Optional[str] = None
    leave_type: Optional[str] = None
    paid: Optional[bool] = None
    approver_id: Optional[UUID] = None
    employee_id: Optional[UUID] = None
    everyone: Optional[bool] = None
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    search: Optional[str] = None


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
        

# --------------------   LeaveCreateEmployeesIn Schema   ---------------------------
class LeaveCreateEmployeesIn(Schema):
    employee_ids: list[int]
    start_date: str
    end_date: str
    reason: Optional[str] = None
    everyone: Optional[bool] = False
    paid: Optional[bool] = True
    leave_type: Optional[str] = "annual Leave"
    status: Optional[str] = "pending"
    approved_at: Optional[str] = None
    
    