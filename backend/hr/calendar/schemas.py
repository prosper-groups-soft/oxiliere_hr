from ninja import Schema
from ninja.orm import ModelSchema
from typing import Optional, List
from datetime import date, time
from uuid import UUID

from .models import CalendarEvent, CalendarSettings


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
            "status",
            "created_at",
            "updated_at",
        ]


# --- Calendar Settings Schemas ---

class CalendarSettingsUpdateIn(ModelSchema):
    class Meta:
        model = CalendarSettings
        fields = [
            "show_anniversaries",
            "show_deadlines",
            "work_days_per_week",
        ]
        fields_optional = "__all__"

class CalendarSettingsOut(ModelSchema):
    id: UUID
    class Meta:
        model = CalendarSettings
        fields = [
            "id",
            "show_anniversaries",
            "show_deadlines",
            "work_days_per_week",
            "updated_at",
        ]
