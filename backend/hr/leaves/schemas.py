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
    PublicHoliday, 
    CompanyClosing, 
    LeaveBalance, 
    LeaveRequest, 
    LeaveRecall
)
from hr.schemas import LightUserOut


#  -------- Leave Policy -------- 
class LeavePolicyOut(ModelSchema):
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
    class Meta:
        model = LeavePolicy
        fields = [
            'name', 
            'standard_annual_days', 
            'allows_carry_over',
            'max_carry_over_days'
        ]
        fields_optional = "__all__"


#  -------- Public Holidays -------- 
class PublicHolidayOut(ModelSchema):
    class Meta:
        model = PublicHoliday
        fields = [
            'id', 
            'name', 
            'date', 
            'country_code', 
            'is_recurring'
        ]


class PublicHolidayCreate(ModelSchema):
    class Meta:
        model = PublicHoliday
        fields = [
            'name', 
            'date', 
            'country_code', 
            'is_recurring'
        ]


class PublicHolidayUpdate(PublicHolidayCreate):
    class Meta(PublicHolidayCreate.Meta):
        fields_optional = "__all__"


class PublicHolidayFilter(BaseFilter):
    country_code: Optional[str] = None
    year: Optional[int] = Field(None, q='date__year')

    def filter_search(self, value: str) -> models.Q:
        return models.Q(name__icontains=value)
        

#  -------- Company Closings -------- 
class CompanyClosingOut(ModelSchema):
    class Meta:
        model = CompanyClosing
        fields = [
            'id', 
            'name', 
            'start_date', 
            'end_date'
        ]
        

class CompanyClosingCreate(ModelSchema):
    class Meta:
        model = CompanyClosing
        fields = [
            'name', 
            'start_date', 
            'end_date'
        ]
        

class CompanyClosingUpdate(CompanyClosingCreate):
    class Meta(CompanyClosingCreate.Meta):
        fields_optional = "__all__"
    
    
class CompanyClosingFilter(BaseFilter):
    # Find closings starting on or after this date
    after: Optional[date] = Field(None, q='start_date__gte')
    # Find closings ending on or before this date
    before: Optional[date] = Field(None, q='end_date__lte')
    
    def filter_search(self, value: str) -> models.Q:
        return models.Q(name__icontains=value)


#  -------- Seniority Rules -------- 
class SeniorityRuleOut(ModelSchema):
    policy: LeavePolicyOut
    
    class Meta:
        model = SeniorityRule
        fields = ['id', 'years_of_service', 'bonus_days']


class SeniorityRuleCreate(ModelSchema):
    class Meta:
        model = SeniorityRule
        fields = ['years_of_service', 'bonus_days']


class SeniorityRuleUpdate(SeniorityRuleCreate):
    class Meta(SeniorityRuleCreate.Meta):
        fields_optional = "__all__"


class SeniorityRuleFilter(FilterSchema):
    min_years: Optional[int] = Field(None, q='years_of_service__gte')
    
    # This field uses the custom method below
    exact_years: Optional[int] = None

    def filter_exact_years(self, value: int) -> models.Q:
        """
        Custom filter logic for an exact number of years of service.
        """
        return models.Q(years_of_service=value)


#  -------- Circumstance Rules -------- 
class CircumstanceLeaveRuleOut(ModelSchema):
    policy: LeavePolicyOut

    class Meta:
        model = CircumstanceLeaveRule
        fields = ['id', 'type', 'duration_days', 'is_paid']


class CircumstanceLeaveRuleCreate(ModelSchema):
    class Meta:
        model = CircumstanceLeaveRule
        fields = ['type', 'duration_days', 'is_paid']


class CircumstanceLeaveRuleUpdate(CircumstanceLeaveRuleCreate):
    class Meta(CircumstanceLeaveRuleCreate.Meta):
        fields_optional = "__all__"


class CircumstanceLeaveRuleFilter(BaseFilter):
    type: Optional[str] = None
    is_paid: Optional[bool] = None
    
    def filter_search(self, value: str) -> models.Q:
        return models.Q(type__icontains=value)


#  -------- Leave Balance --------
class LeaveBalanceOut(ModelSchema):
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


class LeaveBalanceFilter(FilterSchema):
    employee_id: Optional[int] = None
    year: Optional[int] = None


#  -------- Leave Request --------
class LeaveRequestOut(ModelSchema):
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
    """Used by LeaveRequestService.create_request"""
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
        if 'start_date' in info.data and v < info.data['start_date']:
            raise ValueError("End date cannot be earlier than start date.")
        return v


class LeaveRequestUpdate(ModelSchema):
    """Mainly used for HR modifications via update_request_by_hr"""
    class Meta:
        model = LeaveRequest
        fields = ['start_date', 'end_date', 'comment']
        fields_optional = "__all__"


class LeaveRequestFilter(BaseFilter):
    employee_id: Optional[int] = None
    status: Optional[str] = None
    category: Optional[str] = None

    def filter_search(self, value: str) -> models.Q:
        """
        Broad global search across main fields and related models.
        """
        search_query = (
            models.Q(comment__icontains=value) |
            models.Q(employee__first_name__icontains=value) |
            models.Q(employee__middle_name__icontains=value) |
            models.Q(employee__last_name__icontains=value)
        )
        return search_query


#  -------- Batcj Leave Request --------
class BatchLeaveRequestItem(Schema):
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

