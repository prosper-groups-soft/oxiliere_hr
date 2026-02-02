from typing import Optional, List
from uuid import UUID
from datetime import date
from decimal import Decimal
from pydantic import field_validator, ValidationInfo
from ninja import ModelSchema, FilterSchema, Field, Schema
from django.db import models

from hr.schemas import BaseFilter
from .models import (
    LeavePolicy, 
    SeniorityRule, 
    CircumstanceLeaveRule, 
    LeaveBalance, 
    LeaveRequest, 
    LeaveRecall,
    LeaveTransaction
)
from hr.schemas import LightUserOut


#  -------- Leave Policy -------- 
class LeavePolicyOut(ModelSchema):
    """ Comprehensive details of a corporate leave policy. """
    class Meta:
        model = LeavePolicy
        fields = [
            "id", 
            "name", 
            "country_code", 
            "standard_annual_days",
            "allows_carry_over",
            "max_carry_over_days",
            "carry_over_expiration_month"
        ]


class LeavePolicyCreate(ModelSchema):
    """ Data required to establish a new leave policy. """
    class Meta:
        model = LeavePolicy
        fields = [
            'name', 
            'country_code', 
            'standard_annual_days', 
            'allows_carry_over', 
            'max_carry_over_days'
        ]


class LeavePolicyUpdate(ModelSchema):
    """ Data for modifying an existing leave policy. """
    class Meta:
        model = LeavePolicy
        fields = [
            'name', 
            'standard_annual_days', 
            'allows_carry_over',
            'max_carry_over_days'
        ]
        fields_optional = "__all__"





#  -------- Seniority Rules -------- 
class SeniorityRuleOut(ModelSchema):
    """ Details of a seniority-based leave benefit. """
    policy: LeavePolicyOut
    
    class Meta:
        model = SeniorityRule
        fields = ['id', 'years_of_service', 'bonus_days']


class SeniorityRuleCreate(ModelSchema):
    """ Data for creating a new seniority rule. """
    class Meta:
        model = SeniorityRule
        fields = ['years_of_service', 'bonus_days']


class SeniorityRuleUpdate(SeniorityRuleCreate):
    """ Data for updating a seniority rule. """
    class Meta(SeniorityRuleCreate.Meta):
        fields_optional = "__all__"


class SeniorityRuleFilter(FilterSchema):
    """ Filters for searching seniority rules. """
    min_years: Optional[int] = Field(None, q='years_of_service__gte')
    
    # This field uses the custom method below
    exact_years: Optional[int] = None

    def filter_exact_years(self, value: int) -> models.Q:
        """ Filters by an exact number of years of service. """
        return models.Q(years_of_service=value)


#  -------- Circumstance Rules -------- 
class CircumstanceLeaveRuleOut(ModelSchema):
    """ Details of a special leave category (e.g., family events). """
    policy: LeavePolicyOut

    class Meta:
        model = CircumstanceLeaveRule
        fields = ['id', 'type', 'duration_days', 'is_paid']


class CircumstanceLeaveRuleCreate(ModelSchema):
    """ Data for defining a new special leave category. """
    class Meta:
        model = CircumstanceLeaveRule
        fields = ['type', 'duration_days', 'is_paid']


class CircumstanceLeaveRuleUpdate(CircumstanceLeaveRuleCreate):
    """ Data for modifying a special leave category. """
    class Meta(CircumstanceLeaveRuleCreate.Meta):
        fields_optional = "__all__"


class CircumstanceLeaveRuleFilter(BaseFilter):
    """ Filters for searching special leave categories. """
    type: Optional[str] = None
    is_paid: Optional[bool] = None
    
    def filter_search(self, value: str) -> models.Q:
        """ Searches by leave type name. """
        return models.Q(type__icontains=value)


#  -------- Leave Balance --------
class LeaveBalanceOut(ModelSchema):
    """ Summary of an employee's leave entitlement and usage for a specific year. """
    remaining_days: Decimal   # Computed property
    total_granted: Decimal    # Computed property
    
    class Meta:
        model = LeaveBalance
        fields = [
            'id', 
            'employee', 
            'year', 
            'base_entitlement', 
            'seniority_bonus', 
            'used_days', 
        ]


class CarryOverSchema(Schema):
    """ Details of leave days carried over from a previous year. """
    total: Decimal
    used: Decimal
    available: Decimal
    expires_at: date


class LeaveBalanceSummary(Schema):
    """ Combined summary of annual leave and carry-overs. """
    allocated: Decimal
    deducted: Decimal
    available: Decimal
    carry_over: Optional[CarryOverSchema] = None
    total_available: Decimal


class LeaveBalanceFilter(FilterSchema):
    """ Filters for searching employee leave balances. """
    employee_id: Optional[int] = None
    year: Optional[int] = None


#  -------- Leave Request --------
class LeaveRequestOut(ModelSchema):
    """ Detailed information about an individual leave request. """
    class Meta:
        model = LeaveRequest
        fields = [
            'id',
            'employee',
            'category',
            'circumstance_type', 
            'start_date', 
            'end_date', 
            'requested_days', 
            'status', 
            'attachment', 
            'comment'
        ]


class LeaveRequestCreate(ModelSchema):
    """ Data required to submit a new leave application. """
    category: str
    start_date: date
    end_date: date

    class Meta:
        model = LeaveRequest
        fields = [
            'category', 
            'circumstance_type', 
            'start_date', 
            'end_date', 
            'comment'
        ]
    
    @field_validator("end_date")
    @classmethod
    def validate_dates(cls, v: date, info: ValidationInfo):
        """ Ensures the start date does not exceed the end date. """
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("End date must be after the start date.")
        return v


class LeaveRequestUpdate(ModelSchema):
    """ Data for HR to modify an existing leave request. """
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'comment']
        fields_optional = "__all__"


class LeaveRequestFilter(BaseFilter):
    """ Filters for searching leave applications. """
    employee_id: Optional[int] = None
    status: Optional[str] = None
    category: Optional[str] = None

    def filter_search(self, value: str) -> models.Q:
        """ Broad search across comments and employee names. """
        search_query = (
            models.Q(comment__icontains=value) |
            models.Q(employee__first_name__icontains=value) |
            models.Q(employee__middle_name__icontains=value) |
            models.Q(employee__last_name__icontains=value)
        )
        return search_query


#  -------- Batcj Leave Request --------
class BatchLeaveRequestItem(Schema):
    """ Details for a single leave request within a batch submission. """
    employee_id: UUID
    category: str
    start_date: date
    end_date: date
    circumstance_type: Optional[str] = None
    comment: Optional[str] = None


class BatchLeaveRequestCreate(Schema):
    requests: List[BatchLeaveRequestItem]
    

class BatchLeaveRequestResult(Schema):
    employee_id: UUID
    success: bool
    leave_request_id: Optional[UUID] = None
    error: Optional[str] = None


class BatchLeaveRequestReport(Schema):
    results: List[BatchLeaveRequestResult]


class BatchActionSchema(Schema):
    request_ids: List[UUID]
    reason: Optional[str] = None
    recall_date: Optional[date] = None


#  -------- Leave Recall --------
class LeaveRecallOut(ModelSchema):
    recalled_by: Optional[LightUserOut]
    
    class Meta:
        model = LeaveRecall
        fields = [
            'id',
            'leave_request',
            'recall_date',
            'reason',
            'recalled_by',
            'created_at'
        ]


class LeaveRecallCreate(ModelSchema):
    class Meta:
        model = LeaveRecall
        fields = [
            'recall_date', 
            'reason'
        ]


#  -------- Leave Transaction --------
class LeaveTransactionOut(ModelSchema):
    class Meta:
        model = LeaveTransaction
        fields = [
            'id',
            'employee',
            'year',
            'amount',
            'transaction_type',
            'leave_request',
            'reason',
            'created_at'
        ]


class LeaveTransactionFilter(FilterSchema):
    employee_id: Optional[UUID] = None
    year: Optional[int] = None
    transaction_type: Optional[str] = None


#  -------- Admin Adjustments --------
class BalanceAdjustmentIn(Schema):
    year: int
    amount: Decimal
    reason: str


class CarryOverAdjustmentIn(Schema):
    source_year: int
    amount: Decimal
    reason: str
    new_expiration: Optional[date] = None
