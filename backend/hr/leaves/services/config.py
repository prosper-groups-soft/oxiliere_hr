from core.services import BaseCRUDService
from hr.leaves.models import (
    LeavePolicy,
    SeniorityRule,
    CircumstanceLeaveRule
)


class LeavePolicyService(BaseCRUDService):
    model = LeavePolicy
    allowed_update_fields = [
        'name', 
        'standard_annual_days', 
        'allows_carry_over', 
        'max_carry_over_days', 
        'carry_over_expiration_month'
    ]


class SeniorityRuleService(BaseCRUDService):
    model = SeniorityRule
    allowed_update_fields = [
        'years_of_service', 
        'bonus_days'
    ]


class CircumstanceLeaveRuleService(BaseCRUDService):
    model = CircumstanceLeaveRule
    allowed_update_fields = [
        'type', 
        'duration_days', 
        'is_paid'
    ]

