import logging
from uuid import UUID
from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError

from hr.performance.models import Campaign, PerformanceReview
from hr.performance.enums import ReviewStatus
from hr.performance.services.score_calculator import ScoreCalculator


logger = logging.getLogger(__name__)


class PerformanceService:

    @classmethod
    @transaction.atomic
    def create_review(cls, data: dict, actor=None) -> PerformanceReview:
        """Crée une évaluation en statut EMPLOYEE_DRAFT, liée à une campagne."""
        campaign_id = data['campaign_id']
        campaign = Campaign.objects.get(id=campaign_id)

        review = PerformanceReview.objects.create(
            campaign_id=campaign_id,
            employee_id=data['employee_id'],
            manager_id=data.get('manager_id'),
            goals=data.get('goals') or [dict(g) for g in campaign.default_goals],
            skills=data.get('skills') or [dict(s) for s in campaign.default_skills],
            employee_comment=data.get('employee_comment', ''),
            status=ReviewStatus.EMPLOYEE_DRAFT,
            created_by=actor,
        )
        logger.info(
            "Performance review created",
            extra={
                "review_id": review.id,
                "employee_id": review.employee_id,
                "campaign_id": review.campaign_id,
            },
        )
        return review

    @classmethod
    @transaction.atomic
    def update_employee_review(cls, review_id: UUID, data: dict, actor=None) -> PerformanceReview:
        """Met à jour l'auto-évaluation par l'employé (EMPLOYEE_DRAFT)."""
        review = PerformanceReview.objects.get(id=review_id)

        if review.status != ReviewStatus.EMPLOYEE_DRAFT:
            raise ValidationError(
                "L'auto-évaluation ne peut être modifiée qu'en statut EMPLOYEE_DRAFT."
            )

        for field in ['goals', 'skills', 'employee_comment']:
            if field in data:
                setattr(review, field, data[field])

        review.updated_by = actor
        review.save()
        return review

    @classmethod
    @transaction.atomic
    def update_manager_review(cls, review_id: UUID, data: dict, actor=None) -> PerformanceReview:
        """Met à jour l'évaluation par l'évaluateur (EMPLOYEE_DRAFT ou SUBMITTED)."""
        review = PerformanceReview.objects.get(id=review_id)

        if review.status not in [ReviewStatus.EMPLOYEE_DRAFT, ReviewStatus.SUBMITTED]:
            raise ValidationError(
                "L'évaluation ne peut être modifiée qu'en statut EMPLOYEE_DRAFT ou SUBMITTED."
            )

        for field in ['goals_manager', 'skills_manager', 'manager_comment', 'manager_overall_score']:
            if field in data:
                setattr(review, field, data[field])

        review.updated_by = actor
        review.save()
        return review

    @classmethod
    @transaction.atomic
    def submit_employee_review(cls, review_id: UUID, actor=None) -> PerformanceReview:
        """Soumission par l'employé.

        Enregistre employee_submitted_at. Si le manager a déjà soumis,
        passe directement à SUBMITTED avec calcul du score.
        """
        review = PerformanceReview.objects.select_related('campaign').get(id=review_id)

        if review.employee_submitted_at is not None:
            raise ValidationError("L'employé a déjà soumis son auto-évaluation.")

        if review.status not in [ReviewStatus.EMPLOYEE_DRAFT, ReviewStatus.SUBMITTED]:
            raise ValidationError(
                f"Impossible de soumettre : statut actuel '{review.status}'."
            )

        review.employee_submitted_at = timezone.now()
        review.updated_by = actor

        # Si le manager a déjà soumis ou pas de manager → SUBMITTED
        if review.manager_submitted_at is not None or review.manager is None:
            if review.manager is None:
                review.goals_manager = review.goals
                review.skills_manager = review.skills
                review.manager_submitted_at = timezone.now()
            review.status = ReviewStatus.SUBMITTED
            review.save()
            _update_review_score(review)
            logger.info(
                "Employee submitted — both sides done, review SUBMITTED",
                extra={"review_id": review.id, "overall_score": review.overall_score, "actor": str(actor)},
            )
        else:
            review.status = ReviewStatus.EMPLOYEE_DRAFT
            review.save()
            logger.info(
                "Employee submitted — waiting for evaluator",
                extra={"review_id": review.id, "actor": str(actor)},
            )

        return review

    @classmethod
    @transaction.atomic
    def submit_manager_review(cls, review_id: UUID, actor=None) -> PerformanceReview:
        """Soumission par l'évaluateur.

        Enregistre manager_submitted_at. Si l'employé a déjà soumis,
        passe directement à SUBMITTED avec calcul du score.
        """
        review = PerformanceReview.objects.select_related('campaign').get(id=review_id)

        if review.manager_submitted_at is not None:
            raise ValidationError("L'évaluateur a déjà soumis son évaluation.")

        if review.status not in [ReviewStatus.EMPLOYEE_DRAFT, ReviewStatus.SUBMITTED]:
            raise ValidationError(
                f"Impossible de soumettre : statut actuel '{review.status}'."
            )

        if review.manager is None:
            review.manager_id = actor.id if actor else None

        review.manager_submitted_at = timezone.now()
        review.updated_by = actor

        # Si l'employé a déjà soumis → SUBMITTED
        if review.employee_submitted_at is not None:
            review.status = ReviewStatus.SUBMITTED
            review.save()
            _update_review_score(review)
            logger.info(
                "Evaluator submitted — both sides done, review SUBMITTED",
                extra={"review_id": review.id, "overall_score": review.overall_score, "actor": str(actor)},
            )
        else:
            review.status = ReviewStatus.EMPLOYEE_DRAFT
            review.save()
            logger.info(
                "Evaluator submitted — waiting for employee",
                extra={"review_id": review.id, "actor": str(actor)},
            )

        return review

    @classmethod
    @transaction.atomic
    def acknowledge_review(cls, review_id: UUID, actor=None) -> PerformanceReview:
        """Prise de connaissance par l'employé : SUBMITTED → ACKNOWLEDGED."""
        review = PerformanceReview.objects.get(id=review_id)

        if review.status != ReviewStatus.SUBMITTED:
            raise ValidationError(
                f"Impossible d'accuser réception : statut actuel '{review.status}', attendu SUBMITTED."
            )

        review.status = ReviewStatus.ACKNOWLEDGED
        review.acknowledged_at = timezone.now()
        review.updated_by = actor
        review.save()

        logger.info(
            "Review acknowledged by employee",
            extra={"review_id": review.id, "actor": str(actor)},
        )
        return review

    @classmethod
    @transaction.atomic
    def dispute_review(cls, review_id: UUID, reason: str = "", actor=None) -> PerformanceReview:
        """Contestation par l'employé : active le flag disputed + enregistre le motif."""
        review = PerformanceReview.objects.get(id=review_id)

        if review.status not in [ReviewStatus.CALIBRATED, ReviewStatus.SUBMITTED]:
            raise ValidationError(
                "Seules les évaluations soumises ou calibrées peuvent être contestées."
            )

        review.disputed = True
        review.dispute_reason = reason
        review.updated_by = actor
        review.save()

        logger.info(
            "Review disputed by employee",
            extra={"review_id": review.id, "reason": reason, "actor": str(actor)},
        )
        return review

    @classmethod
    @transaction.atomic
    def delete_review(cls, review_id: UUID, actor=None) -> None:
        """Supprime une évaluation (EMPLOYEE_DRAFT uniquement)."""
        review = PerformanceReview.objects.get(id=review_id)

        if review.status != ReviewStatus.EMPLOYEE_DRAFT:
            raise ValidationError(
                "Seules les évaluations en statut EMPLOYEE_DRAFT peuvent être supprimées."
            )

        review.delete()

        logger.info(
            "Performance review deleted",
            extra={"review_id": review.id, "actor": str(actor)},
        )


def _update_review_score(review: PerformanceReview) -> None:
    """Calcule et persiste le score global d'une évaluation après soumission."""
    try:
        overall_score = ScoreCalculator.calculate_overall_score(review)
        if overall_score is not None:
            review.overall_score = overall_score
            review.save(update_fields=['overall_score'])
    except Exception as e:
        logger.warning(
            "Score calculation failed for review",
            extra={"review_id": review.id, "error": str(e)},
        )


