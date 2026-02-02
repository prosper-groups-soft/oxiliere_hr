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
    """ Data required to schedule a new holiday or company event. """
    class Meta:
        model = CalendarEvent
        fields = [
            "name", "event_type", "start_date", "end_date", "start_time", 
            "end_time", "is_workable", "recurrent", "description", 
            "status", "country_code",
        ]
        fields_optional = [
            "end_date", "start_time", "end_time", "recurrent", 
            "description", "status",
        ]


class CalendarEventUpdateIn(ModelSchema):
    """ Schema for modifying an existing calendar event. """
    class Meta:
        model = CalendarEvent
        fields = [
            "name", "event_type", "start_date", "end_date", "start_time", 
            "end_time", "is_workable", "recurrent", "description", "status",
        ]
        fields_optional = "__all__"


class CalendarEventOut(ModelSchema):
    """ Public calendar event details for API responses. """
    id: UUID
    class Meta:
        model = CalendarEvent
        fields = [
            "id", "name", "code", "event_type", "start_date", "end_date", 
            "start_time", "end_time", "is_workable", "recurrent", 
            "description", "status", "country_code", "created_at", "updated_at",
        ]


class CalendarEventFilterIn(BaseFilter):
    """ Parameters for searching and filtering the company calendar. """
    
    event_type: Optional[str] = None
    is_workable: Optional[bool] = None
    status: Optional[str] = None
    recurrent: Optional[str] = None
    country_code: Optional[str] = None
    
    start_date: Optional[date] = Field(None, description="Include events occurring on or after this date")
    end_date: Optional[date] = Field(None, description="Include events occurring on or before this date")
    
    def filter_start_date(self, value: date) -> Q:
        """ Filters for events that are active after the specified start date. """
        return Q(end_date__gte=value) | Q(end_date__isnull=True, start_date__gte=value)
    
    def filter_end_date(self, value: date) -> Q:
        """ Filters for events that start before the specified end date. """
        return Q(start_date__lte=value)

    def filter_search(self, value: str) -> Q:
        """ Searches events by name, code, or description. """
        return (
            Q(name__icontains=value) | 
            Q(code__icontains=value) | 
            Q(description__icontains=value)
        )

