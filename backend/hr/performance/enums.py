from django.db import models
from django.utils.translation import gettext_lazy as _


class CampaignStatus(models.TextChoices):
    """Statuts d'une campagne d'évaluation."""
    DRAFT = "DRAFT", _("Brouillon")
    ACTIVE = "ACTIVE", _("Active")
    CLOSED = "CLOSED", _("Clôturée")


class CampaignType(models.TextChoices):
    """Types de campagne d'évaluation."""
    ANNUAL = "ANNUAL", _("Annuelle")
    SEMESTRIAL = "SEMESTRIAL", _("Semestrielle")
    TRIMESTRIAL = "TRIMESTRIAL", _("Trimestrielle")
    PROBATION = "PROBATION", _("Période d'essai")


class ReviewStatus(models.TextChoices):
    """Les 5 états du cycle de vie d'une évaluation.

    EMPLOYEE_DRAFT  →  MANAGER_DRAFT  →  SUBMITTED  →  CALIBRATED  →  ACKNOWLEDGED
    """
    EMPLOYEE_DRAFT = "EMPLOYEE_DRAFT", _("Auto-évaluation")
    MANAGER_DRAFT = "MANAGER_DRAFT", _("Évaluation manager")
    SUBMITTED = "SUBMITTED", _("Soumise")
    CALIBRATED = "CALIBRATED", _("Calibrée")
    ACKNOWLEDGED = "ACKNOWLEDGED", _("Approuvée")


class SkillCategory(models.TextChoices):
    """Catégories de compétence."""
    TECHNICAL = "TECHNICAL", _("Technique")
    BEHAVIORAL = "BEHAVIORAL", _("Comportementale")
    LEADERSHIP = "LEADERSHIP", _("Leadership")


class GoalStatus(models.TextChoices):
    """Statuts d'un objectif dans une évaluation."""
    PENDING = "PENDING", _("En attente")
    ACHIEVED = "ACHIEVED", _("Atteint")
    PARTIAL = "PARTIAL", _("Partiellement atteint")
    NOT_ACHIEVED = "NOT_ACHIEVED", _("Non atteint")
    CANCELLED = "CANCELLED", _("Annulé")


class PerformanceGoalType(models.TextChoices):
    """Types d'objectif."""
    OBJECTIVE = "OBJECTIVE", _("Objectif qualitatif")
    KPI = "KPI", _("KPI")

