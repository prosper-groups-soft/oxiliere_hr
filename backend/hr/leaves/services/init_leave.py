import json
from pathlib import Path
from uuid6 import uuid7
from injector import inject

from django.db import transaction
from .config import (
    LeavePolicyService,
    SeniorityRuleService,
    CircumstanceLeaveRuleService
)
from ..models import (
    LeavePolicy as LeavePolicyModel,
    SeniorityRule,
    CircumstanceLeaveRule
)


def load_fixtures():
    """Load JSON fixtures from the configuration file."""
    fixtures_path = Path(__file__).parent.parent.parent / "fixtures" / "leaves" / "cd" / "rules.json"
    with open(fixtures_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def parse_fixtures(fixtures):
    """Parse fixtures and group by policy."""
    policies = {}
    
    for item in fixtures:
        model = item["model"]
        pk = item["pk"]
        fields = item["fields"]
        
        if model == "hr_leaves.leavepolicy":
            policies[pk] = {
                "id": pk,
                "name": fields["name"],
                "country_code": fields["country_code"],
                "standard_annual_days": fields["standard_annual_days"],
                "allows_carry_over": fields["allows_carry_over"],
                "max_carry_over_days": fields["max_carry_over_days"],
                "carry_over_expiration_month": fields["carry_over_expiration_month"],
                "seniority_rules": [],
                "circumstance_rules": []
            }
        elif model == "hr_leaves.seniorityrule":
            policy_id = fields["policy"]
            if policy_id in policies:
                policies[policy_id]["seniority_rules"].append({
                    "years_of_service": fields["years_of_service"],
                    "bonus_days": fields["bonus_days"]
                })
        elif model == "hr_leaves.circumstanceleaverule":
            policy_id = fields["policy"]
            if policy_id in policies:
                policies[policy_id]["circumstance_rules"].append({
                    "type": fields["type"],
                    "duration_days": fields["duration_days"],
                    "is_paid": fields["is_paid"],
                    "description": fields.get("description", "")
                })
    
    return list(policies.values())


class LeaveInitializerService:
    """ Pre-configures the system with default leave policies and statutory rules. """

    @inject
    def __init__(
        self,
        policy_service: LeavePolicyService,
        seniority_service: SeniorityRuleService,
        circumstance_service: CircumstanceLeaveRuleService,
    ):
        self.policy_service = policy_service
        self.seniority_service = seniority_service
        self.circumstance_service = circumstance_service

    @transaction.atomic
    def initialize_defaults(self, force_reset: bool = False):
        """ 
        Installs or resets default leave configurations from fixtures.
        
        Args:
            force_reset: If True, deletes existing rules and recreates them from fixtures.
                        If False, only creates if policy doesn't exist.
        """
        fixtures = load_fixtures()
        policies_data = parse_fixtures(fixtures)
        
        for policy_data in policies_data:
            policy_exists = self.policy_service.exists(
                name=policy_data["name"],
                country_code=policy_data["country_code"],
            )
            
            if not policy_exists:
                # Initial creation
                policy_fields = {
                    k: v for k, v in policy_data.items()
                    if k not in ("id", "seniority_rules", "circumstance_rules")
                }
                policy_id = policy_data.get("id") or uuid7()
                policy = self.policy_service.create(
                    data=policy_fields,
                    id=policy_id
                )
                
                # Create rules
                for rule in policy_data.get("seniority_rules", []):
                    self.seniority_service.create(data=rule, policy_id=policy.id)
                for rule in policy_data.get("circumstance_rules", []):
                    self.circumstance_service.create(data=rule, policy_id=policy.id)
                    
            elif force_reset:
                # Reset: update policy fields and sync rules
                try:
                    policy = LeavePolicyModel.objects.get(
                        country_code=policy_data["country_code"],
                        name=policy_data["name"]
                    )
                    
                    # Update policy fields from fixtures
                    policy.standard_annual_days = policy_data["standard_annual_days"]
                    policy.allows_carry_over = policy_data["allows_carry_over"]
                    policy.max_carry_over_days = policy_data["max_carry_over_days"]
                    policy.carry_over_expiration_month = policy_data["carry_over_expiration_month"]
                    policy.max_consecutive_days = policy_data.get("max_consecutive_days", 30)
                    policy.notice_period_days = policy_data.get("notice_period_days", 15)
                    policy.save()
                    
                    # Sync seniority_rules (update or create)
                    fixture_seniority_years = set()
                    for rule in policy_data.get("seniority_rules", []):
                        years = rule["years_of_service"]
                        fixture_seniority_years.add(years)
                        SeniorityRule.objects.update_or_create(
                            policy=policy,
                            years_of_service=years,
                            defaults={"bonus_days": rule["bonus_days"]}
                        )
                    # Delete rules not in fixtures
                    policy.seniority_rules.exclude(years_of_service__in=fixture_seniority_years).delete()
                    
                    # Sync circumstance_rules (update or create)
                    fixture_types = set()
                    for rule in policy_data.get("circumstance_rules", []):
                        rule_type = rule["type"]
                        fixture_types.add(rule_type)
                        CircumstanceLeaveRule.objects.update_or_create(
                            policy=policy,
                            type=rule_type,
                            defaults={
                                "duration_days": rule["duration_days"],
                                "is_paid": rule["is_paid"],
                                "description": rule.get("description", "")
                            }
                        )
                    # Delete rules not in fixtures
                    policy.circumstanceleaverule_set.exclude(type__in=fixture_types).delete()
                        
                except LeavePolicyModel.DoesNotExist:
                    pass
