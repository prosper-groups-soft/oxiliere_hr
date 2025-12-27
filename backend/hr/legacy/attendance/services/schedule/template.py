from datetime import timedelta
from typing import Optional, List, Dict
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from hr.attendance.models import ScheduleTemplate
from .day import ScheduleDayWriterService


class ScheduleTemplateService:
    """
    Service layer for ScheduleTemplate:
    - CRUD operations
    - Duplication
    - Aggregations (total hours)
    """

    @staticmethod
    @transaction.atomic
    def create_template(
        name: str, 
        description: str = "", 
        days: Optional[List[Dict]] = None
    ) -> ScheduleTemplate:
        """
        Create a ScheduleTemplate and optionally create its ScheduleDays.
        """
        template = ScheduleTemplate.objects.create(name=name, description=description)
        if days:
            for day_data in days:
                ScheduleDayWriterService.create_day(
                    template_id=template.id,
                    weekday=day_data["weekday"],
                    opened_at=day_data["opened_at"],
                    closed_at=day_data["closed_at"],
                    is_open=day_data.get("is_open", True)
                )
        return template

    @staticmethod
    @transaction.atomic
    def update_template(
        template_id: int, 
        name: Optional[str] = None, 
        description: Optional[str] = None
    ) -> ScheduleTemplate:
        """
        Update a ScheduleTemplate fields.
        """
        try:
            template = ScheduleTemplate.objects.get(id=template_id)
        except ObjectDoesNotExist:
            raise ValueError(f"ScheduleTemplate with id {template_id} does not exist")

        if name is not None:
            template.name = name
        if description is not None:
            template.description = description
        template.save()
        return template

    @staticmethod
    @transaction.atomic
    def duplicate_template(template_id: int, new_name: str) -> ScheduleTemplate:
        """
        Duplicate a template along with all its ScheduleDays.
        """
        try:
            original = ScheduleTemplate.objects.prefetch_related("days").get(id=template_id)
        except ObjectDoesNotExist:
            raise ValueError(f"ScheduleTemplate with id {template_id} does not exist")

        new_template = ScheduleTemplate.objects.create(
            name=new_name, 
            description=original.description
        )
        for day in original.days.all():
            ScheduleDayWriterService.create_day(
                template_id=new_template.id,
                weekday=day.weekday,
                opened_at=day.opened_at,
                closed_at=day.closed_at,
                is_open=day.is_open
            )
        return new_template

    @staticmethod
    def total_hours(template_id: int) -> timedelta:
        """
        Compute total scheduled hours for this template.
        """
        return ScheduleDayWriterService.total_hours_for_template(template_id)


class ScheduleTemplateReaderService:
    """
    Handles retrieval of ScheduleTemplate instances.
    """

    @staticmethod
    def get_template(template_id: int) -> ScheduleTemplate:
        try:
            return ScheduleTemplate.objects.get(id=template_id)
        except ObjectDoesNotExist:
            raise ValueError(f"ScheduleTemplate with id {template_id} does not exist")

    @staticmethod
    def list_templates() -> List[ScheduleTemplate]:
        return list(ScheduleTemplate.objects.all().order_by("name"))
