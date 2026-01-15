from typing import List
from uuid import UUID
from datetime import date
from injector import inject
from ninja.pagination import paginate
from oxutils.pagination.cursor import CursorPagination

from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_put,
    http_delete,
    ControllerBase,
)
from django.core.exceptions import ValidationError

from ..services.calendar import CalendarService
from ..schemas import (
    CalendarEventCreateIn,
    CalendarEventUpdateIn,
    CalendarEventOut,
    CalendarSettingsUpdateIn,
    CalendarSettingsOut
)


@api_controller("/calendar", tags=["Calendar"])
class CalendarController(ControllerBase):
    """
    Controller for managing Global Calendar and Company Settings.
    """

    @inject
    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service

    # --- Events ---

    @http_get("/events", response=List[CalendarEventOut])
    @paginate(CursorPagination)
    def list_events(self, start_date: date = None, end_date: date = None):
        """List calendar events, optionally filtered by date range."""
        return self.calendar_service.list_events(start_date, end_date)

    @http_post("/events", response={201: CalendarEventOut})
    def create_event(self, payload: CalendarEventCreateIn):
        """Create a new calendar event."""
        try:
            event = self.calendar_service.create_event(payload)
            return 201, event
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_put("/events/{event_id}", response=CalendarEventOut)
    def update_event(self, event_id: UUID, payload: CalendarEventUpdateIn):
        """Update an existing event."""
        try:
            return self.calendar_service.update_event(event_id, payload)
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_delete("/events/{event_id}", response={204: None})
    def delete_event(self, event_id: UUID):
        """Delete an event."""
        self.calendar_service.delete_event(event_id)
        return 204, None

    # --- Settings ---

    @http_get("/settings", response=CalendarSettingsOut)
    def get_settings(self):
        """Get global calendar settings."""
        return self.calendar_service.get_settings()

    @http_put("/settings", response=CalendarSettingsOut)
    def update_settings(self, payload: CalendarSettingsUpdateIn):
        """Update global calendar settings."""
        try:
            return self.calendar_service.update_settings(payload.dict(exclude_unchanged=True))
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)
