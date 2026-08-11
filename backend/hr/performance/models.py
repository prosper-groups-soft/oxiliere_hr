from django.db import models
from django.db.models import Q
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ValidationError
from auditlog.registry import auditlog
from hr.models.base import BaseAuditableModel
from django.conf import settings

from .enums import (
    CampaignStatus,
    CampaignType,
    ReviewStatus,
    PerformanceGoalType,
)


class Campaign(BaseAuditableModel):
    """Campagne d'évaluation (ex: SA1 2026).

    Une campagne est une période d'évaluation définie par le service RH,
    qui constitue le cadre temporel et organisationnel dans lequel
    les évaluations sont réalisées.
    """
    name = models.CharField(
        max_length=255,
        verbose_name=_("Nom"),
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description"),
        help_text=_("Description / instructions générales"),
    )
    campaign_type = models.CharField(
        max_length=20,
        choices=CampaignType.choices,
        verbose_name=_("Type de campagne"),
    )
    start_date = models.DateField(
        verbose_name=_("Date de début"),
    )
    end_date = models.DateField(
        verbose_name=_("Date de fin"),
    )
    submission_deadline = models.DateField(
        verbose_name=_("Date limite de soumission"),
    )
    status = models.CharField(
        max_length=15,
        choices=CampaignStatus.choices,
        default=CampaignStatus.DRAFT,
        verbose_name=_("Statut"),
    )
    goal_weight = models.FloatField(
        default=0.6,
        verbose_name=_("Poids des objectifs"),
        help_text=_("Poids des objectifs dans le score (défaut: 0.6)"),
    )
    skill_weight = models.FloatField(
        default=0.4,
        verbose_name=_("Poids des compétences"),
        help_text=_("Poids des compétences dans le score (défaut: 0.4)"),
    )
    default_goals = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Objectifs par défaut"),
        help_text=_(
            "Liste d'objectifs par défaut copiés (snapshot) dans chaque évaluation. "
            "L'employé peut les modifier/supprimer/ajouter librement."
        ),
    )
    default_skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Compétences par défaut"),
        help_text=_(
            "Liste de compétences par défaut copiées (snapshot) dans chaque évaluation. "
            "L'employé peut les modifier/supprimer/ajouter librement."
        ),
    )
    participants = models.ManyToManyField(
        'hr_employees.Employee',
        through='CampaignParticipation',
        through_fields=('campaign', 'employee'),
        related_name='campaign_participations_m2m',
        verbose_name=_("Participants"),
    )
    evaluators = models.ManyToManyField(
        'hr_employees.Employee',
        through='CampaignEvaluator',
        through_fields=('campaign', 'employee'),
        related_name='campaign_evaluators_m2m',
        verbose_name=_("Évaluateurs"),
    )

    class Meta:
        db_table = "perf_campaign"
        verbose_name = _("Campagne")
        verbose_name_plural = _("Campagnes")
        ordering = ['-start_date']

    def clean(self):
        """Invariants documentés."""
        errors = {}
        if self.start_date and self.end_date and self.start_date > self.end_date:
            errors['end_date'] = _("La date de fin doit être postérieure à la date de début.")
        if self.end_date and self.submission_deadline and self.end_date > self.submission_deadline:
            errors['submission_deadline'] = _(
                "La date limite de soumission doit être postérieure à la date de fin."
            )
        if self.goal_weight is not None and self.skill_weight is not None:
            total = self.goal_weight + self.skill_weight
            if abs(total - 1.0) > 0.01:
                errors['goal_weight'] = _(
                    "La somme goal_weight + skill_weight doit être égale à 1."
                )
        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.name} ({self.get_campaign_type_display()})"


class CampaignParticipation(BaseAuditableModel):
    """Association entre une campagne et un employé participant."""
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='participation_records',
        verbose_name=_("Campagne"),
    )
    employee = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.CASCADE,
        related_name='campaign_participations',
        verbose_name=_("Employé"),
    )

    class Meta:
        db_table = "perf_campaign_participation"
        verbose_name = _("Participation à une campagne")
        verbose_name_plural = _("Participations aux campagnes")
        constraints = [
            models.UniqueConstraint(
                fields=['campaign', 'employee'],
                condition=Q(deleted__isnull=True),
                name='uq_campaign_participation_active',
            )
        ]

    def __str__(self):
        return f"{self.employee} - {self.campaign.name}"


class CampaignEvaluator(BaseAuditableModel):
    """Association entre une campagne et un employé évaluateur (manager)."""
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='evaluator_records',
        verbose_name=_("Campagne"),
    )
    employee = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.CASCADE,
        related_name='campaign_evaluations',
        verbose_name=_("Évaluateur"),
    )

    class Meta:
        db_table = "perf_campaign_evaluator"
        verbose_name = _("Évaluateur de campagne")
        verbose_name_plural = _("Évaluateurs de campagne")
        constraints = [
            models.UniqueConstraint(
                fields=['campaign', 'employee'],
                condition=Q(deleted__isnull=True),
                name='uq_campaign_evaluator_active',
            )
        ]

    def __str__(self):
        return f"{self.employee} - Évaluateur ({self.campaign.name})"


class PerformanceReview(BaseAuditableModel):
    """Évaluation d'un employé pour une campagne.

    Contient les contributions de l'employé (auto-évaluation) et du manager
    (évaluation), ainsi que les résultats du calibrage.
    """
    campaign = models.ForeignKey(
        Campaign,
        on_delete=models.CASCADE,
        related_name='reviews',
        verbose_name=_("Campagne"),
    )
    employee = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.CASCADE,
        related_name='performance_reviews',
        verbose_name=_("Employé"),
    )
    manager = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews_given',
        verbose_name=_("Manager évaluateur"),
    )
    status = models.CharField(
        max_length=20,
        choices=ReviewStatus.choices,
        default=ReviewStatus.EMPLOYEE_DRAFT,
        verbose_name=_("Statut"),
    )
    disputed = models.BooleanField(
        default=False,
        verbose_name=_("Contestée"),
    )
    dispute_reason = models.TextField(
        blank=True, default="",
        verbose_name=_("Motif de contestation"),
        help_text=_("Motif fourni par l'employé pour contester l'évaluation."),
    )

    # Auto-évaluation (rempli par l'employé en EMPLOYEE_DRAFT)
    goals = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Objectifs (employé)"),
        help_text=_(
            "Liste d'objectifs saisis par l'employé. "
            "Format: [{'description': '...', 'type': 'OBJECTIVE|KPI', "
            "'weight': 0.5, 'employee_rating': 1-5, 'status': 'PENDING'}]"
        ),
    )
    skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Compétences (employé)"),
        help_text=_(
            "Liste de compétences évaluées par l'employé. "
            "Format: [{'name': '...', 'category': 'TECHNICAL|BEHAVIORAL|LEADERSHIP', "
            "'employee_level': 1-5}]"
        ),
    )
    employee_comment = models.TextField(
        blank=True,
        verbose_name=_("Commentaire employé"),
        help_text=_("Auto-évaluation : commentaire de l'employé."),
    )

    # Évaluation manager (rempli en MANAGER_DRAFT)
    goals_manager = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Objectifs (manager)"),
        help_text=_(
            "Évaluation des objectifs par le manager. "
            "Format: [{'description': '...', 'type': 'OBJECTIVE|KPI', "
            "'weight': 0.5, 'manager_rating': 1-5, 'manager_comment': '...', "
            "'status': 'ACHIEVED'}]"
        ),
    )
    skills_manager = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Compétences (manager)"),
        help_text=_(
            "Évaluation des compétences par le manager. "
            "Format: [{'name': '...', 'category': 'TECHNICAL|BEHAVIORAL|LEADERSHIP', "
            "'manager_level': 1-5}]"
        ),
    )
    manager_comment = models.TextField(
        blank=True,
        verbose_name=_("Commentaire manager"),
        help_text=_("Évaluation : commentaire du manager."),
    )
    manager_overall_score = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Note indicative manager"),
        help_text=_("Note globale subjective saisie par le manager (1-5)."),
    )

    # Scores
    overall_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Score final"),
        help_text=_("Score final calculé automatiquement (moyenne pondérée)."),
    )
    calibrated_score = models.FloatField(
        null=True,
        blank=True,
        verbose_name=_("Score calibré"),
        help_text=_("Score ajusté après calibrage RH (écrase overall_score si présent)."),
    )

    # Dates clés
    employee_submitted_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Soumission employé"),
    )
    manager_submitted_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Soumission manager"),
    )
    acknowledged_at = models.DateTimeField(
        null=True, blank=True,
        verbose_name=_("Date de prise de connaissance"),
    )

    class Meta:
        db_table = "perf_review"
        verbose_name = _("Évaluation")
        verbose_name_plural = _("Évaluations")
        ordering = ['-campaign__start_date']
        constraints = [
            models.UniqueConstraint(
                fields=['campaign', 'employee'],
                condition=Q(deleted__isnull=True),
                name='uq_review_per_campaign_per_employee',
                violation_error_message=_(
                    "Un employé ne peut avoir qu'une seule évaluation par campagne."
                ),
            )
        ]

    def clean(self):
        """Invariants documentés."""
        errors = {}
        if self.manager and self.manager == self.employee:
            errors['manager'] = _("Un employé ne peut pas être son propre évaluateur.")

        if self.goals and isinstance(self.goals, list):
            for i, goal in enumerate(self.goals):
                goal_type = goal.get('type')
                if goal_type and goal_type not in PerformanceGoalType.values:
                    errors[f'goals_{i}'] = _(
                        f"Type d'objectif invalide '{goal_type}'."
                    )
                rating = goal.get('employee_rating')
                if rating is not None and not (1 <= rating <= 5):
                    errors[f'goals_{i}_rating'] = _(
                        "La note employé doit être entre 1 et 5."
                    )

        if self.goals_manager and isinstance(self.goals_manager, list):
            for i, goal in enumerate(self.goals_manager):
                rating = goal.get('manager_rating')
                if rating is not None and not (1 <= rating <= 5):
                    errors[f'goals_manager_{i}'] = _(
                        "La note manager doit être entre 1 et 5."
                    )

        if errors:
            raise ValidationError(errors)

    def __str__(self):
        return f"{self.employee} - {self.campaign.name}"


class Calibration(BaseAuditableModel):
    """Calibrage RH d'une évaluation.

    Le calibrage est le processus par lequel le service RH ajuste les scores
    pour assurer la cohérence et l'équité entre les équipes.
    """
    evaluation = models.ForeignKey(
        PerformanceReview,
        on_delete=models.CASCADE,
        related_name='calibrations',
        verbose_name=_("Évaluation"),
    )
    original_score = models.FloatField(
        verbose_name=_("Score original"),
        help_text=_("Score avant calibrage."),
    )
    calibrated_score = models.FloatField(
        verbose_name=_("Score calibré"),
        help_text=_("Score après calibrage."),
    )
    reason = models.TextField(
        verbose_name=_("Justification"),
        help_text=_("Justification de l'ajustement."),
    )
    calibrated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='calibrations_performed',
        verbose_name=_("Calibré par"),
    )
    calibrated_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Date de calibrage"),
    )

    class Meta:
        db_table = "perf_calibration"
        verbose_name = _("Calibrage")
        verbose_name_plural = _("Calibrages")
        ordering = ['-calibrated_at']

    def __str__(self):
        return f"Calibrage {self.evaluation} : {self.original_score} → {self.calibrated_score}"


class DevelopmentPlan(BaseAuditableModel):
    """Plan de développement post-évaluation.

    Ensemble d'actions de formation ou de mentorat définies après l'évaluation
    pour améliorer les compétences d'un employé.
    """
    evaluation = models.OneToOneField(
        PerformanceReview,
        on_delete=models.CASCADE,
        related_name='development_plan',
        verbose_name=_("Évaluation"),
    )
    items = models.JSONField(
        default=list,
        verbose_name=_("Actions"),
        help_text=_(
            "Liste d'actions de développement. "
            "Format: [{'action': '...', 'deadline': 'YYYY-MM-DD', 'status': 'PENDING|COMPLETED'}]"
        ),
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Date de complétion"),
    )

    class Meta:
        db_table = "perf_development_plan"
        verbose_name = _("Plan de développement")
        verbose_name_plural = _("Plans de développement")

    def __str__(self):
        return f"Plan de développement - {self.evaluation}"


auditlog.register(Campaign)
auditlog.register(CampaignParticipation)
auditlog.register(CampaignEvaluator)
auditlog.register(PerformanceReview)
auditlog.register(Calibration)
auditlog.register(DevelopmentPlan)

