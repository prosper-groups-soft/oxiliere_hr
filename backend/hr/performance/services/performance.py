import logging
from uuid      import UUID
from django.db import transaction
from django.core.exceptions import ValidationError

from hr.performance.models import PerformanceReview


logger = logging.getLogger(__name__)


class PerformanceService:

    @classmethod
    @transaction.atomic
    def create_review(cls, data: dict, actor=None) -> PerformanceReview:
        review = PerformanceReview.objects.create(
            employee_id=data['employee_id'],
            reviewer_id=data.get('reviewer_id'),
            review_period_start=data['review_period_start'],
            review_period_end=data['review_period_end'],
            goals=data.get('goals', []),
            skills=data.get('skills', []),
            employee_comment=data.get('employee_comment', ''),
            reviewer_comment=data.get('reviewer_comment', ''),
            created_by=actor,
        )
        logger.info("Performance review created", extra={"review_id": review.id})
        return review

    @classmethod
    @transaction.atomic
    def update_review(cls, review_id: UUID, data: dict, actor=None) -> PerformanceReview:
        review = PerformanceReview.objects.get(id=review_id)

        if review.status != "DRAFT":
            raise ValidationError("Can only update draft reviews.")

        for field in ['reviewer_id', 'status', 'goals', 'skills', 'employee_comment', 'reviewer_comment', 'overall_rating']:
            if field in data:
                setattr(review, field, data[field])

        review.updated_by = actor
        review.save()
        return review

    @classmethod
    def get_reviews_for_employee(cls, employee_id: UUID) -> list[PerformanceReview]:
        return PerformanceReview.objects.filter(employee_id=employee_id).order_by('-review_period_end')

    @classmethod
    def get_pending_reviews(cls, reviewer_id: UUID) -> list[PerformanceReview]:
        return PerformanceReview.objects.filter(
            reviewer_id=reviewer_id,
            status="SUBMITTED"
        ).order_by('-review_period_end')

