from uuid6 import uuid7
from injector import inject

from django.db import transaction
from .config import (
    LeavePolicyService,
    SeniorityRuleService,
    CircumstanceLeaveRuleService
)


DEFAULT_POLICIES = [
    {
        "name": "RDC Labor Law Standard",
        "country_code": "CD",
        "standard_annual_days": 18,
        "allows_carry_over": False,
        "max_carry_over_days": 10,
        "carry_over_expiration_month": 3,
        "seniority_rules": [
            {"years_of_service": 1, "bonus_days": 1},
            {"years_of_service": 5, "bonus_days": 2},
        ],
        "circumstance_rules": [
            {"type": "marriage_employee", "duration_days": 2, "is_paid": True},
            {"type": "birth_spouse", "duration_days": 2, "is_paid": True},
            {"type": "death_1st_degree", "duration_days": 4, "is_paid": True},
            {"type": "death_2nd_degree", "duration_days": 2, "is_paid": True},
            {"type": "child_marriage", "duration_days": 1, "is_paid": True},
            {"type": "moving", "duration_days": 1, "is_paid": True},
        ],
    }
]


class LeaveInitializerService:
    """
    Service to initialize default leave policies, seniority rules,
    circumstance leave rules, and public holidays.
    """

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
    def initialize_defaults(self):
        """
        Initialize all default policies and rules if they do not exist.
        """
        for policy_data in DEFAULT_POLICIES:
            policy_id = policy_data["id"]

            if not self.policy_service.exists(
                name=policy_data["name"],
                country_code=policy_data["country_code"],
            ):

                policy_fields = {
                    k: v for k, v in policy_data.items()
                    if k not in ("seniority_rules", "circumstance_rules", "id")
                }

                policy = self.policy_service.create(
                    data=policy_fields,
                    id=uuid7()
                )

                for rule in policy_data.get("seniority_rules", []):
                    self.seniority_service.create(
                        data=rule,
                        policy_id=policy.id
                    )

                for rule in policy_data.get("circumstance_rules", []):
                    self.circumstance_service.create(
                        data=rule,
                        policy_id=policy.id
                    )

