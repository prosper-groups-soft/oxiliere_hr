import logging
from uuid import UUID
from django.db import transaction
from django.core.exceptions import ValidationError

from hr.performance.models import PerformanceReview, Calibration
from hr.performance.enums import ReviewStatus


logger = logging.getLogger(__name__)


class CalibrationService:

    @classmethod
    @transaction.atomic
    def calibrate(cls, review_id: UUID, calibrated_score: float, reason: str, actor=None) -> PerformanceReview:
        """
        Calibre une évaluation : SUBMITTED → CALIBRATED.

        Crée un enregistrement Calibration et met à jour le calibrated_score.
        """
        review = PerformanceReview.objects.select_related('campaign').get(id=review_id)

        if review.status != ReviewStatus.SUBMITTED:
            raise ValidationError(
                f"Impossible de calibrer une évaluation avec le statut '{review.status}'. "
                f"Le statut doit être 'SUBMITTED'."
            )

        # Créer l'enregistrement de calibrage
        Calibration.objects.create(
            evaluation=review,
            original_score=review.overall_score or 0.0,
            calibrated_score=calibrated_score,
            reason=reason,
            calibrated_by=actor,
        )

        # Mettre à jour l'évaluation
        review.calibrated_score = calibrated_score
        review.status = ReviewStatus.CALIBRATED
        review.updated_by = actor
        review.save()

        logger.info(
            "Review calibrated",
            extra={
                "review_id": review.id,
                "original_score": review.overall_score,
                "calibrated_score": calibrated_score,
                "reason": reason,
                "actor": str(actor),
            },
        )
        return review

    @classmethod
    @transaction.atomic
    def recalibrate(cls, review_id: UUID, new_calibrated_score: float, reason: str, actor=None) -> PerformanceReview:
        """
        Re-calibre une évaluation déjà CALIBRATED (nouveau calibrage explicite).

        Crée un nouvel enregistrement Calibration avec le nouveau score.
        """
        review = PerformanceReview.objects.select_related('campaign').get(id=review_id)

        if review.status != ReviewStatus.CALIBRATED:
            raise ValidationError(
                f"Impossible de re-calibrer une évaluation avec le statut '{review.status}'."
            )

        # Récupérer le dernier calibrage pour avoir l'original_score
        last_calibration = Calibration.objects.filter(evaluation=review).order_by('-calibrated_at').first()
        original_score = last_calibration.calibrated_score if last_calibration else (review.overall_score or 0.0)

        # Nouvel enregistrement
        Calibration.objects.create(
            evaluation=review,
            original_score=original_score,
            calibrated_score=new_calibrated_score,
            reason=reason,
            calibrated_by=actor,
        )

        review.calibrated_score = new_calibrated_score
        review.updated_by = actor
        review.save()

        logger.info(
            "Review recalibrated",
            extra={
                "review_id": review.id,
                "previous_score": original_score,
                "new_calibrated_score": new_calibrated_score,
                "reason": reason,
                "actor": str(actor),
            },
        )
        return review
