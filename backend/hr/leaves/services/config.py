from safedelete.config import HARD_DELETE

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
        'carry_over_expiration_month',
        'max_consecutive_days',
        'notice_period_days'
    ]


class SeniorityRuleService(BaseCRUDService):
    """ Manages rules for bonus leave days based on employee length of service. """
    model = SeniorityRule
    allowed_update_fields = [
        'years_of_service',
        'bonus_days'
    ]

    def update(self, instance, data):
        """
        Update a seniority rule, handling unique constraint conflicts.
        Delete any conflicting rules with the same years_of_service to maintain
        single rule per policy constraint.
        """
        years_value = data.get('years_of_service', instance.years_of_service)
        
        # Always check for and delete ALL conflicting rules
        # Use all_with_deleted() to include soft-deleted objects that still exist in DB
        conflicting = self.model.objects.all_with_deleted().filter(
            policy=instance.policy,
            years_of_service=years_value
        ).exclude(id=instance.id)

        # Delete all conflicting rules (could be multiple due to previous errors)
        for rule in conflicting:
            # Hard delete to actually remove from DB
            rule.delete(force_policy=HARD_DELETE)

        return super().update(instance=instance, data=data)


class CircumstanceLeaveRuleService(BaseCRUDService):
    """ Manages entitlements for special leave events such as marriages or bereavements. """
    model = CircumstanceLeaveRule
    allowed_update_fields = [
        'type', 
        'duration_days', 
        'is_paid',
        'description'
    ]

