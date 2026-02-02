import json
import os
from django.conf import settings
from hr.calendar.models import CalendarEvent


class EventInitService:

    def init_default_events(self):
        """Initialize default events by reading the JSON fixtures file."""
        
        fixture_path = os.path.join(
            settings.BASE_DIR, 
            'fixtures', 
            'calendar/cd' 
            'event.json'
        )
        
        with open(fixture_path, 'r', encoding='utf-8') as f:
            data_list = json.load(f)
        
        initialized_events = []

        for item in data_list:
            fields = item['fields']
            pk = item.get('pk')
            
            event, created = CalendarEvent.objects.update_or_create(
                code=fields['code'],
                defaults={
                    "id": pk,
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

