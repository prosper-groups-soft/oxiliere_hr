import logging
from datetime import timedelta
from django_redis import get_redis_connection
from django.core.cache import cache
from django.utils      import timezone
from hr.services.cache_helpers import generate_cache_key, CacheKeys
from hr.calendar.models import CalendarEvent


class CalendarCacheService:
    """ Performance optimization and data caching for the calendar module. """
    
    @staticmethod
    def get_holidays_in_period(start_date, end_date):
        """ Retrieves a cached list of holiday dates within a specific period. """
        cache_key = CacheKeys.holidays(start_date, end_date)
        holidays = cache.get(cache_key)
        
        if holidays is None:
            holidays = list(
                CalendarEvent.objects.filter(
                    type='holiday',
                    date__range=[start_date, end_date]
                ).values_list('date', flat=True)
            )
            cache.set(cache_key, holidays, timeout=60*60*24*7)
        
        return holidays
    
    @staticmethod
    def get_company_closures_in_period(start_date, end_date):
        """ Retrieves cached company closure dates for a given period. """
        cache_key = generate_cache_key("hr:calendar:closures", start_date, end_date)
        closures = cache.get(cache_key)
        
        if closures is None:
            closures = list(
                CalendarEvent.objects.filter(
                    type='company_closure',
                    date__range=[start_date, end_date]
                ).values_list('date', flat=True)
            )
            cache.set(cache_key, closures, timeout=60*60*24*7)
        
        return closures
    
    @staticmethod
    def is_working_day(date):
        """ Checks if a specific date is a business day (not a weekend, holiday, or closing). """
        if date.weekday() >= 5:
            return False
        
        cache_key = generate_cache_key("hr:calendar:is_working", date)
        is_working = cache.get(cache_key)
        
        if is_working is None:
            event_count = CalendarEvent.objects.filter(
                date=date,
                type__in=['holiday', 'company_closure']
            ).count()
            
            is_working = event_count == 0
            cache.set(cache_key, is_working, timeout=60*60*24*7)
        
        return is_working
    
    @staticmethod
    def count_working_days(start_date, end_date):
        """ Calculates the total number of business days in a given period using cached results. """
        cache_key = CacheKeys.working_days(start_date, end_date)
        count = cache.get(cache_key)
        
        if count is None:
            holidays = CalendarCacheService.get_holidays_in_period(start_date, end_date)
            closures = CalendarCacheService.get_company_closures_in_period(start_date, end_date)
            non_working_dates = set(holidays) | set(closures)
            
            count = 0
            current_date = start_date
            while current_date <= end_date:
                if current_date.weekday() < 5 and current_date not in non_working_dates:
                    count += 1
                current_date += timedelta(days=1)
            
            cache.set(cache_key, count, timeout=60*60*24*7)
        
        return count
    
    @staticmethod
    def get_calendar_event(event_id):
        """ Retrieves a cached instance of a specific calendar event. """
        cache_key = generate_cache_key("hr:calendar:event", event_id)
        event = cache.get(cache_key)
        
        if event is None:
            event = CalendarEvent.objects.filter(id=event_id).first()
            if event:
                cache.set(cache_key, event, timeout=60*60*24)
        
        return event
    
    @staticmethod
    def get_events_in_period(start_date, end_date, event_type=None):
        """ Provides an optimized list of calendar events for a specified date range. """
        cache_key = generate_cache_key("hr:calendar:events_period", start_date, end_date, event_type)
        events = cache.get(cache_key)
        
        if events is None:
            query = CalendarEvent.objects.filter(date__range=[start_date, end_date])
            if event_type:
                query = query.filter(type=event_type)
            
            events = list(query.order_by('date'))
            cache.set(cache_key, events, timeout=60*60*24)
        
        return events
    
    @staticmethod
    def get_holidays_current_year():
        """ Retrieves all public holidays for the current calendar year. """
        today = timezone.now().date()
        year_start = today.replace(month=1, day=1)
        year_end = today.replace(month=12, day=31)
        return CalendarCacheService.get_holidays_in_period(year_start, year_end)
    
    @staticmethod
    def clear_period_cache(start_date, end_date):
        """ Invalidates cached calendar data for a specific date range. """
        cache.delete(CacheKeys.holidays(start_date, end_date))
        cache.delete(CacheKeys.working_days(start_date, end_date))
        cache.delete(generate_cache_key("hr:calendar:closures", start_date, end_date))
        cache.delete(generate_cache_key("hr:calendar:events_period", start_date, end_date, None))
    
    @staticmethod
    def clear_api_cache_prefix(prefix: str):
        """ Clears specific API response caches. """
        from hr.services.cache_helpers import invalidate_cache_prefix
        invalidate_cache_prefix(prefix)

    @staticmethod
    def clear_all_calendar_cache():
        """ Performs a global cleanup of all calendar-related cache data. """

        logger = logging.getLogger(__name__)
        redis_conn = get_redis_connection("default")
        
        pattern = "*hr:calendar*"
        keys = list(redis_conn.scan_iter(match=pattern, count=100))
        if keys:
            redis_conn.delete(*keys)
        
        CalendarCacheService.clear_api_cache_prefix("calendar_events_list")
        CalendarCacheService.clear_api_cache_prefix("public_holidays")
        
        logger.info("All calendar cache cleared.")
