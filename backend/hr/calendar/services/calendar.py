from datetime import timedelta, date
from typing import Set

from django.db.models import Q

from core.services import BaseCRUDService
from hr.enums import CountryCode

from hr.calendar.enums import (
    CalendarEventStatus,
    CalendarEventRecurrence
)

from hr.calendar.models import CalendarEvent


class CalendarService(BaseCRUDService):
    """
    Service for managing Calendar Events (Holidays, Company Closings).
    Standard CRUD operations are inherited from BaseCRUDService.
    """
    model = CalendarEvent
    allowed_update_fields = [
        'name', 
        'event_type', 
        'country_code', 
        'start_date', 
        'end_date', 
        'start_time', 
        'end_time', 
        'is_workable', 
        'recurrent', 
        'description', 
        'status'
    ]

    def get_base_queryset(self):
        """
        Returns the default queryset for events, ordered by date.
        """
        return self.model.objects.all().order_by('start_date', 'start_time')

    # --- Non-Working Day & Event Logic ---

    @staticmethod
    def is_non_working_day(day: date, country_code: str = CountryCode.DRC) -> bool:
        """
        Checks if a specific date is a non-working day (Public Holiday, Company Closure, etc.).
        Does NOT check for weekends (handled by Attendance module).
        """
        # Fetch only non-workable and approved events
        # Note: We filter by country code (specific or global)
        events = CalendarEvent.objects.filter(
            Q(country_code=country_code) | Q(country_code__isnull=True),
            is_workable=False,
            status=CalendarEventStatus.APPROVED
        )

        for event in events:
            # Handle Yearly Recurrence
            if event.recurrent == CalendarEventRecurrence.YEARLY:
                try:
                    event_start = date(day.year, event.start_date.month, event.start_date.day)
                    if event.end_date:
                        # Calculate duration in days
                        duration = (event.end_date - event.start_date).days
                        event_end = event_start + timedelta(days=duration)
                        if event_start <= day <= event_end:
                            return True
                    elif event_start == day:
                        return True
                except ValueError:
                    # Handle Feb 29th on non-leap years
                    continue
            
            # Handle One-time Events
            else:
                end_date = event.end_date or event.start_date
                if event.start_date <= day <= end_date:
                    return True

        return False

    @staticmethod
    def get_non_working_dates_in_range(start_date: date, end_date: date, country_code: str = CountryCode.DRC) -> Set[date]:
        """
        Returns a set of dates that are marked as non-working days within a specific range.
        Optimized to fetch events once and process in-memory.
        """
        non_working_dates = set()
        if start_date > end_date:
            return non_working_dates

        # Optimization: Fetch all potentially relevant events once
        # For recurrent events, we fetch all. For non-recurrent, we filter by range.
        events = CalendarEvent.objects.filter(
            Q(country_code=country_code) | Q(country_code__isnull=True),
            is_workable=False,
            status=CalendarEventStatus.APPROVED
        ).filter(
            Q(recurrent=CalendarEventRecurrence.YEARLY) |
            Q(start_date__lte=end_date, end_date__gte=start_date) |
            Q(start_date__lte=end_date, end_date__isnull=True, start_date__gte=start_date -穿越_timedelta_placeholder_replace_later) # Simplified range check
        )
        
        # Refined fetching logic to be safe and performant
        events = CalendarEvent.objects.filter(
            Q(country_code=country_code) | Q(country_code__isnull=True),
            is_workable=False,
            status=CalendarEventStatus.APPROVED
        )

        for event in events:
            if event.recurrent == CalendarEventRecurrence.YEARLY:
                # For each year in the range, check if the event falls within it
                for year in range(start_date.year, end_date.year + 1):
                    try:
                        ev_start = date(year, event.start_date.month, event.start_date.day)
                        duration = (event.end_date - event.start_date).days if event.end_date else 0
                        ev_end = ev_start + timedelta(days=duration)
                        
                        # Calculate intersection of [ev_start, ev_end] and [start_date, end_date]
                        intersect_start = max(start_date, ev_start)
                        intersect_end = min(end_date, ev_end)
                        
                        curr = intersect_start
                        while curr <= intersect_end:
                            non_working_dates.add(curr)
                            curr += timedelta(days=1)
                    except ValueError:
                        continue
            else:
                ev_start = event.start_date
                ev_end = event.end_date or event.start_date
                
                intersect_start = max(start_date, ev_start)
                intersect_end = min(end_date, ev_end)
                
                curr = intersect_start
                while curr <= intersect_end:
                    non_working_dates.add(curr)
                    curr += timedelta(days=1)
            
        return non_working_dates

    @staticmethod
    def count_non_working_days_in_range(start_date: date, end_date: date, country_code: str = CountryCode.DRC) -> int:
        """
        Returns the number of non-working days between two dates.
        """
        return len(CalendarService.get_non_working_dates_in_range(start_date, end_date, country_code))

