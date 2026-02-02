from django.apps import AppConfig


class BankingConfig(AppConfig):
    name = 'hr.banking'
    label = 'hr_banking'

    def ready(self):
        import hr.banking.signals

