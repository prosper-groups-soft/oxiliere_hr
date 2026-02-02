from typing   import List
from uuid     import UUID
from injector import inject
from ninja    import Query
from ninja.pagination import paginate
from oxutils.pagination.cursor import CursorPagination
from oxutils.permissions.perms import ScopePermission

from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_put,
    http_delete,
    ControllerBase,
)
from django.core.exceptions import ValidationError

from hr.calendar.services import (
    CalendarService,
    EventInitService
)
from hr.calendar.schemas import (
    CalendarEventCreateIn,
    CalendarEventUpdateIn,
    CalendarEventOut,
    CalendarEventFilterIn,
)
from hr.services.cache_helpers import cache_api_response


@api_controller("/calendar", tags=["Calendar"])
class CalendarController(ControllerBase):
    """ Manages company schedule, public holidays, and special events. """
    
    @inject
    def __init__(
        self, 
        calendar_service: CalendarService, 
        init_event_service: EventInitService
    ):
        self.calendar_service = calendar_service
        self.init_event_service = init_event_service

    # --- Events ---

    @http_get("/events", response=List[CalendarEventOut], permissions=[ScopePermission('calendar:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24*7, key_prefix="calendar_events_list", user_specific=False)
    def list_events(self, filters: CalendarEventFilterIn = Query(...)):
        """ Lists all scheduled events with optional filtering by type or date. """
        qs = self.calendar_service.get_base_queryset()
        return filters.filter(qs).distinct()

    @http_get("/events/{event_id}", response=CalendarEventOut, permissions=[ScopePermission('calendar:r')])
    def get_event(self, event_id: UUID):
        """ Retrieves the details of a specific calendar event. """
        return self.calendar_service.get(id=event_id)

    @http_post("/events", response={201: CalendarEventOut}, permissions=[ScopePermission('calendar:w')])
    def create_event(self, payload: CalendarEventCreateIn):
        """ Schedules a new public holiday or company event. """
        try:
            event = self.calendar_service.create(data=payload.model_dump(exclude_none=True))
            return 201, event
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_put("/events/{event_id}", response=CalendarEventOut, permissions=[ScopePermission('calendar:u')])
    def update_event(self, event_id: UUID, payload: CalendarEventUpdateIn):
        """ Modifies the details of an existing calendar event. """
        try:
            instance = self.calendar_service.get(id=event_id)
            return self.calendar_service.update(
                instance=instance, 
                data=payload.model_dump(exclude_unset=True)
            )
        except ValidationError as e:
            return self.create_response({"detail": e.messages}, status_code=400)

    @http_delete("/events/{event_id}", response={204: None}, permissions=[ScopePermission('calendar:d')])
    def delete_event(self, event_id: UUID):
        """ Removes an event from the company calendar. """
        instance = self.calendar_service.get(id=event_id)
        self.calendar_service.delete(instance=instance)
        return 204, None


    @http_get("/init-default-events", response={200: List[CalendarEventOut]}, permissions=[ScopePermission('calendar:r')])
    def init_default_events(self):
        """ Initializes default events for the company."""
        return self.init_event_service.init_default_events()

