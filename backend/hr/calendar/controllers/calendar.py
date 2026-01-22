from typing import List
from uuid import UUID
from injector import inject
from ninja import Query
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

from hr.calendar.services.calendar import CalendarService
from hr.calendar.schemas import (
    CalendarEventCreateIn,
    CalendarEventUpdateIn,
    CalendarEventOut,
    CalendarEventFilterIn,
)


@api_controller("/calendar", tags=["Calendar"])
class CalendarController(ControllerBase):
    @inject
    def __init__(self, calendar_service: CalendarService):
        self.calendar_service = calendar_service

    # --- Events ---

    @http_get("/events", response=List[CalendarEventOut])
    @paginate(CursorPagination)
    def list_events(self, filters: CalendarEventFilterIn = Query(...)):
        """List calendar events with filtering."""
        qs = self.calendar_service.get_base_queryset()
        return filters.filter(qs).distinct()

    @http_get("/events/{event_id}", response=CalendarEventOut)
    def get_event(self, event_id: UUID):
        """Retrieve a single calendar event."""
        return self.calendar_service.get(id=event_id)

    @http_post("/events", response={201: CalendarEventOut})
    def create_event(self, payload: CalendarEventCreateIn):
        """Create a new calendar event."""
        try:
            event = self.calendar_service.create(data=payload.model_dump(exclude_none=True))
            return 201, event
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_put("/events/{event_id}", response=CalendarEventOut)
    def update_event(self, event_id: UUID, payload: CalendarEventUpdateIn):
        """Update an existing calendar event."""
        try:
            # 1. Retrieve the instance
            instance = self.calendar_service.get(id=event_id)
            # 2. Update using the data dictionary
            return self.calendar_service.update(
                instance=instance, 
                data=payload.model_dump(exclude_unset=True)
            )
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_delete("/events/{event_id}", response={204: None})
    def delete_event(self, event_id: UUID):
        """Delete a calendar event."""
        instance = self.calendar_service.get(id=event_id)
        self.calendar_service.delete(instance=instance)
        return 204, None

