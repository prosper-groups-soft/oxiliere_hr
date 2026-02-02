from django.apps import AppConfig


class AttendanceConfig(AppConfig):
    name = 'hr.attendance'
    label = 'hr_attendance'

    def ready(self):
        import hr.attendance.signals
        
