from django.apps import AppConfig


class CalendarConfig(AppConfig):
    name = 'hr.calendar'
    label = 'hr_calendar'

    def ready(self):
        import hr.calendar.signals

