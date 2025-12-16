from __future__ import annotations
from typing import Dict, Any
from django.db import transaction
from hr.attendance.models import AttendanceSettings


class AttendanceSettingsService:
    """
    Service to read/update AttendanceSettings singleton.

    Responsibilities:
    - provide a single point to mutate settings safely
    - allow transactional updates and validation
    """

    @staticmethod
    def get_settings() -> AttendanceSettings:
        # Singleton pattern: model should ensure a single instance exists
        settings = AttendanceSettings.get_instance()
        return settings

    @staticmethod
    @transaction.atomic
    def update_settings(values: Dict[str, Any]) -> AttendanceSettings:
        settings = AttendanceSettingsService.get_settings()
        for k, v in values.items():
            if not hasattr(settings, k):
                raise ValueError(f"Unknown settings attribute: {k}")
            setattr(settings, k, v)
        settings.full_clean()
        settings.save()
        return settings

