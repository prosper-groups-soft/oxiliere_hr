from core.services import BaseCRUDService
from hr.leaves.models import (
    LeavePolicy,
    SeniorityRule,
    CircumstanceLeaveRule
)


class LeavePolicyService(BaseCRUDService):
    """ Manages the creation and modification of company-wide leave policies. """
    model = LeavePolicy
    allowed_update_fields = [
        'name', 
        'standard_annual_days', 
        'allows_carry_over', 
        'max_carry_over_days', 
        'carry_over_expiration_month'
    ]


class SeniorityRuleService(BaseCRUDService):
    """ Manages rules for bonus leave days based on employee length of service. """
    model = SeniorityRule
    allowed_update_fields = [
        'years_of_service', 
        'bonus_days'
    ]


class CircumstanceLeaveRuleService(BaseCRUDService):
    """ Manages entitlements for special leave events such as marriages or bereavements. """
    model = CircumstanceLeaveRule
    allowed_update_fields = [
        'type', 
        'duration_days', 
        'is_paid'
    ]

