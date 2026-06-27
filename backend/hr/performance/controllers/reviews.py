import logging
from uuid import UUID

from django.core.exceptions import ValidationError

from ninja import Query
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema,
)
from oxutils.permissions.perms import ScopePermission

from hr.performance.models import PerformanceReview
from hr.performance.schemas import (
    PerformanceReviewCreateIn,
    PerformanceReviewUpdateIn,
    PerformanceReviewOut,
    PerformanceReviewListFilterIn,
)
from hr.performance.services.performance import PerformanceService
from hr.performance.permissions import (
    WRITE_REVIEW,
    READ_REVIEW,
    UPDATE_REVIEW,
)


logger = logging.getLogger(__name__)


@api_controller('/performance', tags=['Performance'])
class PerformanceReviewController(ControllerBase):

    # ===== CREATE =====

    @http_post('/reviews', response={201: PerformanceReviewOut}, permissions=[ScopePermission(WRITE_REVIEW)])
    def create_review(self, payload: PerformanceReviewCreateIn):
        """Create a new performance review."""
        try:
            review = PerformanceService.create_review(
                payload.model_dump(),
                actor=self.context.request.user
            )
            return 201, review
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== UPDATE =====

    @http_patch(
        '/reviews/{review_id}', 
        response=PerformanceReviewOut, 
        permissions=[ScopePermission(UPDATE_REVIEW)]
    )
    def update_review(self, review_id: UUID, payload: PerformanceReviewUpdateIn):
        """Update an existing performance review."""
        try:
            review = PerformanceService.update_review(
                review_id,
                payload.model_dump(exclude_unset=True),
                actor=self.context.request.user
            )
            return review
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Review not found"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== LIST (employee) =====

    @http_get(
        '/reviews/employee/{employee_id}',
        response=PaginatedResponseSchema[PerformanceReviewOut],
        permissions=[ScopePermission(READ_REVIEW)]
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_employee_reviews(
        self, 
        employee_id: UUID,
        filters: PerformanceReviewListFilterIn = Query(...)  
    ):
        """List performance reviews for an employee with pagination."""
        qs = PerformanceReview.objects.filter(employee_id=employee_id).order_by('-review_period_end')
        qs = filters.filter(qs).distinct()
        return qs

    # ===== LIST (pending for reviewer) =====

    @http_get(
        '/reviews/pending/{reviewer_id}', 
        response=PaginatedResponseSchema[PerformanceReviewOut],
        permissions=[ScopePermission(READ_REVIEW)]
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_pending_reviews(self, reviewer_id: UUID, filters: PerformanceReviewListFilterIn = Query(...)):
        """List reviews pending acknowledgment by a reviewer."""
        qs = PerformanceReview.objects.filter(
            reviewer_id=reviewer_id,
            status="SUBMITTED"
        ).order_by('-review_period_end')
        qs = filters.filter(qs).distinct()
        return qs

