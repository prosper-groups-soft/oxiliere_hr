from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.exceptions   import ValidationError
from auditlog.registry        import auditlog
from hr.models.base           import BaseAuditableModel

from .enums import PerformanceGoalType, ReviewStatus


class PerformanceReview(BaseAuditableModel):
    """ Employee performance review. """
    
    employee = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.CASCADE,
        related_name='performance_reviews',
        verbose_name=_("Employee")
    )
    reviewer = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews_given',
        verbose_name=_("Reviewer")
    )
    review_period_start = models.DateField(
        verbose_name=_("Period Start")
    )
    review_period_end = models.DateField(
        verbose_name=_("Period End")
    )
    status = models.CharField(
        max_length=15,
        choices=ReviewStatus.choices,
        default=ReviewStatus.DRAFT,
        verbose_name=_("Status")
    )

    # Goals (JSON)
    goals = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Goals"),
        help_text=_("List of goals: [{'description': '...', 'type': 'OBJECTIVE|KPI', 'rating': 1-5}]")
    )

    # Skills (JSON)
    skills = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_("Skills"),
        help_text=_("List of skills: [{'name': '...', 'level': 1-5}]")
    )

    # Comments
    employee_comment = models.TextField(
        blank=True,
        verbose_name=_("Employee Comment"),
        help_text=_("Self-assessment comment from the employee.")
    )
    reviewer_comment = models.TextField(
        blank=True,
        verbose_name=_("Reviewer Comment"),
        help_text=_("Assessment comment from the reviewer.")
    )

    # Overall rating
    overall_rating = models.PositiveSmallIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Overall Rating"),
        help_text=_("Overall rating out of 5.")
    )

    class Meta:
        db_table = "hr_performance_review"
        verbose_name = _("Performance Review")
        ordering = ['-review_period_end']

    def clean(self):
        """ Validate JSON fields. """
        for goal in self.goals:
            if goal.get('type') not in PerformanceGoalType.values:
                raise ValidationError(
                    _(f"Invalid goal type '{goal.get('type')}'. Must be one of: {', '.join(PerformanceGoalType.values)}")
                )
            rating = goal.get('rating')
            if rating is not None and not (1 <= rating <= 5):
                raise ValidationError(_("Goal rating must be between 1 and 5."))

    def __str__(self):
        return f"{self.employee} - {self.review_period_start} / {self.review_period_end}"


auditlog.register(PerformanceReview)

