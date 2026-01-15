from typing import List, Dict, Any, Optional
from uuid import UUID
from datetime import date

from django.db import transaction
from django.db.models import Q
from django.utils import timezone

from ..models import CalendarEvent, CalendarSettings
from ..schemas import CalendarEventCreateIn, CalendarEventUpdateIn

class CalendarService:
    """
    Service for managing Calendar Events and Global Settings.
    """

    # --- Event Management ---

    @transaction.atomic
    def create_event(self, payload: CalendarEventCreateIn) -> CalendarEvent:
        """Create a new calendar event."""
        event = CalendarEvent.objects.create(**payload.dict(exclude_none=True))
        return event

    @transaction.atomic
    def update_event(self, event_id: UUID, payload: CalendarEventUpdateIn) -> CalendarEvent:
        """Update an existing event."""
        event = CalendarEvent.objects.get(id=event_id)
        for attr, value in payload.dict(exclude_unchanged=True).items():
            setattr(event, attr, value)
        event.full_clean()
        event.save()
        return event

    @transaction.atomic
    def delete_event(self, event_id: UUID):
        """Delete a calendar event."""
        event = CalendarEvent.objects.get(id=event_id)
        event.delete()

    def list_events(self, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[CalendarEvent]:
        """
        List events, optionally filtered by a date range.
        If a range is provided, finds events that overlap with it.
        """
        qs = CalendarEvent.objects.all().order_by('start_date')
        
        if start_date and end_date:
            # Overlap logic: Event Start <= Range End AND Event End >= Range Start
            # Note: Event End date defaults to start_date if null (for single day events) 
            # but model field is nullable. To handle overlap correctly in DB queries:
            
            # Simple approach: filter where start_date is within range OR end_date is within range
            # Or effectively: start_date <= end_date AND (end_date >= start_date OR (end_date IS NULL AND start_date >= start_date))
            
            qs = qs.filter(
                Q(start_date__lte=end_date) & 
                (Q(end_date__gte=start_date) | Q(end_date__isnull=True, start_date__gte=start_date))
            )

        return qs


    # --- Settings Management ---

    def get_settings(self) -> CalendarSettings:
        """Get the singleton settings instance, or create default."""
        settings, _ = CalendarSettings.objects.get_or_create(pk=1) # Ensure singleton by ID or just use first()
        # Better approach for singleton:
        settings = CalendarSettings.objects.first()
        if not settings:
            settings = CalendarSettings.objects.create()
        return settings

    @transaction.atomic
    def update_settings(self, payload: Dict[str, Any]) -> CalendarSettings:
        """Update global calendar settings."""
        settings = self.get_settings()
        for attr, value in payload.items():
            if hasattr(settings, attr):
                setattr(settings, attr, value)
        settings.full_clean()
        settings.save()
        return settings
