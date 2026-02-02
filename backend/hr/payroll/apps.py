from django.apps import AppConfig


class PayrollConfig(AppConfig):
    name = 'hr.payroll'
    label = 'hr_payroll'

    def ready(self):
        import hr.payroll.signals

