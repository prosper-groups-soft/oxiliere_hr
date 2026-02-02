import logging
from django.dispatch import receiver
from django.db       import transaction
from django.db.models.signals import post_save, post_delete

from hr.calendar.models import CalendarEvent
from hr.calendar.services.cache import CalendarCacheService


logger = logging.getLogger(__name__)


@receiver([post_save, post_delete], sender=CalendarEvent)
def invalidate_calendar_cache(sender, instance, **kwargs):
    """ Automatically clears all calendar caches whenever public holidays or events are modified. """
    
    def clear_cache():
        CalendarCacheService.clear_all_calendar_cache()
        logger.debug(f"Calendar cache invalidated for Event {instance.id}")
    
    transaction.on_commit(clear_cache)
