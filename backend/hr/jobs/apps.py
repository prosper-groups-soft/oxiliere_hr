from django.apps import AppConfig


class JobsConfig(AppConfig):
    name = 'hr.jobs'
    label = 'hr_jobs'

    def ready(self):
        import hr.jobs.signals

