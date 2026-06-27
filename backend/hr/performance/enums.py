from django.db import models
from django.utils.translation import gettext_lazy as _


class ReviewStatus(models.TextChoices):
    DRAFT = "DRAFT", _("Draft")
    SUBMITTED = "SUBMITTED", _("Submitted")
    ACKNOWLEDGED = "ACKNOWLEDGED", _("Acknowledged")


class PerformanceGoalType(models.TextChoices):
    OBJECTIVE = "OBJECTIVE", _("Objective")
    KPI = "KPI", _("KPI")

