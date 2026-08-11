from django.apps import AppConfig


class PerformanceConfig(AppConfig):
    name = 'hr.performance'
    label = 'hr_performance'
    verbose_name = 'Performance Evaluation'

    def ready(self):
        import hr.performance.signals

