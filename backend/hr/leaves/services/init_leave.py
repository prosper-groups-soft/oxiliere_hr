from datetime import date
from uuid6 import uuid7
from injector import inject

from django.utils import timezone
from django.db import transaction
from .config import (
    LeavePolicyService,
    SeniorityRuleService,
    CircumstanceLeaveRuleService,
    PublicHolidayService
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


DEFAULT_PUBLIC_HOLIDAYS = [
    {"name": "Nouvel An", "date": date(2026, 1, 1), "country_code": "CD", "is_recurring": True},
    {"name": "Journée des Martyrs de l'Indépendance", "date": date(2026, 1, 4), "country_code": "CD", "is_recurring": True},
    {"name": "Commémoration de Laurent Désiré Kabila", "date": date(2026, 1, 16), "country_code": "CD", "is_recurring": True},
    {"name": "Commémoration de Patrice Emery Lumumba", "date": date(2026, 1, 17), "country_code": "CD", "is_recurring": True},
    {"name": "Journée de Simon Kimbangu et de la Conscience Africaine", "date": date(2026, 4, 6), "country_code": "CD", "is_recurring": True},
    {"name": "Fête du Travail", "date": date(2026, 5, 1), "country_code": "CD", "is_recurring": True},
    {"name": "Journée de la Libération et des Forces Armées", "date": date(2026, 5, 17), "country_code": "CD", "is_recurring": True},
    {"name": "Jour de l'Indépendance", "date": date(2026, 6, 30), "country_code": "CD", "is_recurring": True},
    {"name": "Fête des Parents", "date": date(2026, 8, 1), "country_code": "CD", "is_recurring": True},
    {"name": "GENOCOST (Journée commémorative du génocide congolais)", "date": date(2026, 8, 2), "country_code": "CD", "is_recurring": True},
    {"name": "Noël", "date": date(2026, 12, 25), "country_code": "CD", "is_recurring": True},
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
        holiday_service: PublicHolidayService,
    ):
        self.policy_service = policy_service
        self.seniority_service = seniority_service
        self.circumstance_service = circumstance_service
        self.holiday_service = holiday_service

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

        for holiday in DEFAULT_PUBLIC_HOLIDAYS:
            if not self.holiday_service.exists(
                name=holiday["name"],
                country_code=holiday["country_code"],
            ):

                data = holiday.copy()

                if data.get("is_recurring"):
                    data["date"] = data["date"].replace(
                        year=timezone.now().year
                    )

                self.holiday_service.create(data=data)

