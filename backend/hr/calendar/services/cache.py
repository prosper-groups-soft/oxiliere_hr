"""
Calendar caching services.

Handles caching of calendar events and working days calculations.
"""

from django.core.cache import cache
from django.utils import timezone
from datetime import timedelta
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.calendar.models import CalendarEvent


class CalendarCacheService:
    """Cache operations for calendar module."""
    
    @staticmethod
    def get_holidays_in_period(start_date, end_date):
        """
        Get all holidays in date period (stable - long cache).
        
        Args:
            start_date: Period start date
            end_date: Period end date
        
        Returns:
            List of holiday dates
        """
        cache_key = CacheKeys.holidays(start_date, end_date)
        holidays = cache.get(cache_key)
        
        if holidays is None:
            holidays = list(
                CalendarEvent.objects.filter(
                    type='holiday',
                    date__range=[start_date, end_date]
                ).values_list('date', flat=True)
            )
            
            cache.set(cache_key, holidays, timeout=60*60*24*7)  # 7 days
        
        return holidays
    
    @staticmethod
    def get_company_closures_in_period(start_date, end_date):
        """Get company closure dates in period (stable - long cache)."""
        cache_key = generate_cache_key(
            "hr:calendar:closures", start_date, end_date
        )
        closures = cache.get(cache_key)
        
        if closures is None:
            closures = list(
                CalendarEvent.objects.filter(
                    type='company_closure',
                    date__range=[start_date, end_date]
                ).values_list('date', flat=True)
            )
            
            cache.set(cache_key, closures, timeout=60*60*24*7)  # 7 days
        
        return closures
    
    @staticmethod
    def is_working_day(date):
        """
        Check if a date is a working day.
        
        Args:
            date: Date to check
        
        Returns:
            Boolean indicating if day is working day
        """
        # Weekend check (no cache needed)
        if date.weekday() >= 5:  # Saturday=5, Sunday=6
            return False
        
        # Check holidays
        cache_key = generate_cache_key("hr:calendar:is_working", date)
        is_working = cache.get(cache_key)
        
        if is_working is None:
            # Check if holiday or closure
            event_count = CalendarEvent.objects.filter(
                date=date,
                type__in=['holiday', 'company_closure']
            ).count()
            
            is_working = event_count == 0
            cache.set(cache_key, is_working, timeout=60*60*24*7)  # 7 days
        
        return is_working
    
    @staticmethod
    def count_working_days(start_date, end_date):
        """
        Count working days in period (cached calculation).
        
        Args:
            start_date: Period start date
            end_date: Period end date
        
        Returns:
            Integer count of working days
        """
        cache_key = CacheKeys.working_days(start_date, end_date)
        count = cache.get(cache_key)
        
        if count is None:
            # Get holidays and closures
            holidays = CalendarCacheService.get_holidays_in_period(
                start_date, end_date
            )
            closures = CalendarCacheService.get_company_closures_in_period(
                start_date, end_date
            )
            
            non_working_dates = set(holidays) | set(closures)
            
            # Count working days
            count = 0
            current_date = start_date
            
            while current_date <= end_date:
                # Check if working day (not weekend and not holiday/closure)
                if current_date.weekday() < 5 and current_date not in non_working_dates:
                    count += 1
                
                current_date += timedelta(days=1)
            
            cache.set(cache_key, count, timeout=60*60*24*7)  # 7 days
        
        return count
    
    @staticmethod
    def get_calendar_event(event_id):
        """Get calendar event by ID."""
        cache_key = generate_cache_key("hr:calendar:event", event_id)
        event = cache.get(cache_key)
        
        if event is None:
            event = CalendarEvent.objects.filter(
                id=event_id
            ).first()
            
            if event:
                cache.set(cache_key, event, timeout=60*60*24)  # 24h
        
        return event
    
    @staticmethod
    def get_events_in_period(start_date, end_date, event_type=None):
        """Get all calendar events in period."""
        cache_key = generate_cache_key(
            "hr:calendar:events_period", start_date, end_date, event_type
        )
        events = cache.get(cache_key)
        
        if events is None:
            query = CalendarEvent.objects.filter(
                date__range=[start_date, end_date]
            )
            
            if event_type:
                query = query.filter(type=event_type)
            
            events = list(query.order_by('date'))
            cache.set(cache_key, events, timeout=60*60*24)  # 24h
        
        return events
    
    @staticmethod
    def get_holidays_current_year():
        """Get all holidays for current year."""
        today = timezone.now().date()
        year_start = today.replace(month=1, day=1)
        year_end = today.replace(month=12, day=31)
        
        return CalendarCacheService.get_holidays_in_period(
            year_start, year_end
        )
    
    @staticmethod
    def clear_period_cache(start_date, end_date):
        """Clear calendar cache for a date period."""
        cache.delete(CacheKeys.holidays(start_date, end_date))
        cache.delete(CacheKeys.working_days(start_date, end_date))
        cache.delete(generate_cache_key(
            "hr:calendar:closures", start_date, end_date
        ))
        cache.delete(generate_cache_key(
            "hr:calendar:events_period", start_date, end_date, None
        ))
    
    @staticmethod
    def clear_all_calendar_cache():
        """Clear all calendar cache (use sparingly)."""
        from django_redis import get_redis_connection
        
        redis_conn = get_redis_connection("default")
        pattern = "*hr:calendar*"
        keys = redis_conn.keys(pattern)
        if keys:
            redis_conn.delete(*keys)
