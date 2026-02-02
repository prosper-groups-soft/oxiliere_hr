from django.apps import AppConfig


class EmployeesConfig(AppConfig):
    name = 'hr.employees'
    label = 'hr_employees'

    def ready(self):
        import hr.employees.signals

