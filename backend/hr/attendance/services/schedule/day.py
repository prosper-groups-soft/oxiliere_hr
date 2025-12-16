from django.utils import timezone
from django.db import transaction
from django.core.exceptions import ObjectDoesNotExist
from datetime import time, timedelta
from hr.attendance.models import ScheduleDay, ScheduleTemplate
from typing import Optional, List


class ScheduleDayWriterService:
    """
    Service layer for ScheduleDay:
    - creation / update
    - compute hours
    - validation beyond model-level constraints
    - template-level aggregations
    """

    @staticmethod
    def compute_hours(opened_at: time, closed_at: time) -> timedelta:
        """
        Compute the duration between opened_at and closed_at.
        Supports overnight shifts.
        """
        today = timezone.now().date()
        opened_dt = timezone.datetime.combine(today, opened_at)
        closed_dt = timezone.datetime.combine(today, closed_at)
        delta = closed_dt - opened_dt
        if delta.total_seconds() < 0:
            delta += timedelta(days=1)
        return delta

    @staticmethod
    @transaction.atomic
    def create_day(
        template_id: int, 
        weekday: str, 
        opened_at: time, 
        closed_at: time, 
        is_open: bool = True
    ) -> ScheduleDay:
        """
        Create a ScheduleDay with computed hours.
        """
        hours = ScheduleDayWriterService.compute_hours(opened_at, closed_at)
        day = ScheduleDay.objects.create(
            template_id=template_id,
            weekday=weekday,
            opened_at=opened_at,
            closed_at=closed_at,
            is_open=is_open,
            hours=hours
        )
        return day

    @staticmethod
    @transaction.atomic
    def update_day(
        day_id: int, 
        opened_at: Optional[time] = None, 
        closed_at: Optional[time] = None, 
        is_open: Optional[bool] = None
    ) -> ScheduleDay:
        """
        Update fields of a ScheduleDay and recalc hours if times change.
        """
        try:
            day = ScheduleDay.objects.get(id=day_id)
        except ObjectDoesNotExist:
            raise ValueError(f"ScheduleDay with id {day_id} does not exist")

        if opened_at is not None:
            day.opened_at = opened_at
        if closed_at is not None:
            day.closed_at = closed_at
        if is_open is not None:
            day.is_open = is_open

        day.hours = ScheduleDayWriterService.compute_hours(day.opened_at, day.closed_at)
        day.save()
        return day

    @staticmethod
    def total_hours_for_template(template_id: int) -> timedelta:
        """
        Compute total scheduled hours for all ScheduleDays of a template.
        """
        try:
            template = ScheduleTemplate.objects.prefetch_related("days").get(id=template_id)
        except ObjectDoesNotExist:
            raise ValueError(f"ScheduleTemplate with id {template_id} does not exist")

        return sum((day.hours for day in template.days.all()), timedelta(0))


class ScheduleDayReaderService:
    """
    Handles retrieval and aggregation of ScheduleDay instances.
    """

    @staticmethod
    def get_day(day_id: int) -> ScheduleDay:
        try:
            return ScheduleDay.objects.get(id=day_id)
        except ObjectDoesNotExist:
            raise ValueError(f"ScheduleDay with id {day_id} does not exist")

    @staticmethod
    def list_days_for_template(template_id: int) -> List[ScheduleDay]:
        return list(ScheduleDay.objects.filter(template_id=template_id).order_by("weekday"))
