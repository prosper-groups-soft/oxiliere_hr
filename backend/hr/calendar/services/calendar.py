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
    """ Central management for company holidays, closings, and special events. """
    model = CalendarEvent
    allowed_update_fields = [
        'name', 'event_type', 'country_code', 'start_date', 'end_date', 
        'start_time', 'end_time', 'is_workable', 'recurrent', 'description', 'status'
    ]

    def get_base_queryset(self):
        """ Retrieves the default chronological list of all events. """
        return self.model.objects.all().order_by('start_date', 'start_time')

    # --- Non-Working Day & Event Logic ---

    @staticmethod
    def is_non_working_day(day: date, country_code: str = CountryCode.DRC) -> bool:
        """ 
        Checks if a specific date is a non-working day (Holiday or Closing). 
        Note: Weekend logic is handled by the Attendance module.
        """
        events = CalendarEvent.objects.filter(
            Q(country_code=country_code) | Q(country_code__isnull=True),
            is_workable=False,
            status=CalendarEventStatus.APPROVED
        )

        for event in events:
            # Yearly Recurrence Logic
            if event.recurrent == CalendarEventRecurrence.YEARLY:
                try:
                    event_start = date(day.year, event.start_date.month, event.start_date.day)
                    if event.end_date:
                        duration = (event.end_date - event.start_date).days
                        event_end = event_start + timedelta(days=duration)
                        if event_start <= day <= event_end:
                            return True
                    elif event_start == day:
                        return True
                except ValueError:
                    continue
            
            # One-time Event Logic
            else:
                end_date = event.end_date or event.start_date
                if event.start_date <= day <= end_date:
                    return True

        return False

    @staticmethod
    def get_non_working_dates_in_range(start_date: date, end_date: date, country_code: str = CountryCode.DRC) -> Set[date]:
        """ Identifies all non-working dates within a specified period for scheduling purposes. """
        non_working_dates = set()
        if start_date > end_date:
            return non_working_dates

        events = CalendarEvent.objects.filter(
            Q(country_code=country_code) | Q(country_code__isnull=True),
            is_workable=False,
            status=CalendarEventStatus.APPROVED
        )

        for event in events:
            if event.recurrent == CalendarEventRecurrence.YEARLY:
                for year in range(start_date.year, end_date.year + 1):
                    try:
                        ev_start = date(year, event.start_date.month, event.start_date.day)
                        duration = (event.end_date - event.start_date).days if event.end_date else 0
                        ev_end = ev_start + timedelta(days=duration)
                        
                        intersect_start = max(start_date, ev_start)
                        intersect_end = min(end_date, ev_end)
                        
                        curr = intersect_start
                        while curr <= intersect_end:
                            non_working_dates.add(curr)
                            curr += timedelta(days=1)
                    except ValueError:
                        continue
            else:
                intersect_start = max(start_date, event.start_date)
                intersect_end = min(end_date, event.end_date or event.start_date)
                
                curr = intersect_start
                while curr <= intersect_end:
                    non_working_dates.add(curr)
                    curr += timedelta(days=1)
            
        return non_working_dates

    @staticmethod
    def count_non_working_days_in_range(start_date: date, end_date: date, country_code: str = CountryCode.DRC) -> int:
        """ Calculates the total number of non-working days in a given period. """
        return len(CalendarService.get_non_working_dates_in_range(start_date, end_date, country_code))


    def init_default_events(self):
        """ Initializes default events for the company."""
        
