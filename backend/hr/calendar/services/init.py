import json
from pathlib import Path
from django.conf import settings
from hr.calendar.enums import CalendarEventType
from hr.calendar.models import CalendarEvent


class EventInitService:

    def init_default_events(self):
        """Initialize default events by reading the JSON fixtures file."""
        

        fixture_path = Path(settings.BASE_DIR).parent / 'hr' / 'fixtures' / 'calendar' / 'cd' / 'event.json'
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        initialized_events = []

        for item in data_list:
            fields = item['fields']

            event, created = CalendarEvent.objects.update_or_create(
                code=fields['code'],
                defaults={
                    "name": fields['name'],
                    "start_date": fields['start_date'],
                    "country_code": fields['country_code'],
                    "event_type": fields['event_type'],
                    "recurrent": fields['recurrent'],
                    "is_workable": fields['is_workable'],
                    "status": fields['status'],
                }
            )
            initialized_events.append(event)

        return initialized_events

    def reset_holidays(self, country_code: str = 'CD'):
        """
        Supprime tous les jours fériés (PUBLIC_HOLIDAY) du pays donné,
        puis les réimporte depuis le fixture. Les autres événements
        (formations, fermetures, échéances, etc.) sont préservés.
        """
        CalendarEvent.objects.filter(
            event_type=CalendarEventType.PUBLIC_HOLIDAY,
            country_code=country_code,
        ).delete()

        return self.init_default_events()
