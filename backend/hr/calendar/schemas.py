from ninja.orm import ModelSchema
from uuid import UUID
from typing import Optional
from datetime import date
from ninja import Field
from django.db.models import Q

from .models import CalendarEvent
from hr.schemas import BaseFilter


# --- Calendar Event Schemas ---

class CalendarEventCreateIn(ModelSchema):
    class Meta:
        model = CalendarEvent
        fields = [
            "name",
            "event_type",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "is_workable",
            "recurrent",
            "description",
            "status",
            "country_code",
        ]
        fields_optional = [
            "end_date",
            "start_time",
            "end_time",
            "recurrent",
            "description",
            "status",
        ]


class CalendarEventUpdateIn(ModelSchema):
    class Meta:
        model = CalendarEvent
        fields = [
            "name",
            "event_type",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "is_workable",
            "recurrent",
            "description",
            "status",
        ]
        fields_optional = "__all__"


class CalendarEventOut(ModelSchema):
    id: UUID
    class Meta:
        model = CalendarEvent
        fields = [
            "id",
            "name",
            "code",
            "event_type",
            "start_date",
            "end_date",
            "start_time",
            "end_time",
            "is_workable",
            "recurrent",
            "description",
            "description",
            "status",
            "country_code",
            "created_at",
            "updated_at",
        ]


class CalendarEventFilterIn(BaseFilter):
    """Filter schema for calendar events."""
    
    event_type: Optional[str] = None
    is_workable: Optional[bool] = None
    status: Optional[str] = None
    recurrent: Optional[str] = None
    country_code: Optional[str] = None
    
    # Date range filtering
    start_date: Optional[date] = Field(None, description="Filter events starting from this date")
    end_date: Optional[date] = Field(None, description="Filter events ending before this date")
    
    def filter_start_date(self, value: date) -> Q:
        """Filter events that overlap with or occur after the start date."""
        # Events that end on or after the start date (or have no end date and start on/after)
        return Q(end_date__gte=value) | Q(end_date__isnull=True, start_date__gte=value)
    
    def filter_end_date(self, value: date) -> Q:
        """Filter events that overlap with or occur before the end date."""
        # Events that start on or before the end date
        return Q(start_date__lte=value)

    def filter_search(self, value: str) -> Q:
        """Filter events by name or code."""
        return (
            Q(name__icontains=value) | 
            Q(code__icontains=value) | 
            Q(description__icontains=value)
        )

