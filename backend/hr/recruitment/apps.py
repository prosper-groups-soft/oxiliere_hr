from django.apps import AppConfig


class RecruitmentConfig(AppConfig):
    name = 'hr.recruitment'
    label = 'hr_recruitment'

    def ready(self):
        import hr.recruitment.signals

