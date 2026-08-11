import logging
from typing import Annotated
from uuid import UUID

from django.core.exceptions import ValidationError

from ninja import Query
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_delete,
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
    PerformanceReviewUpdateEmployeeIn,
    PerformanceReviewUpdateManagerIn,
    PerformanceReviewCalibrateIn,
    DisputeReviewIn,
    PerformanceReviewOut,
    PerformanceReviewListFilterIn,
)
from hr.performance.services.performance import PerformanceService
from hr.performance.services.calibration import CalibrationService
from hr.performance.permissions import (
    WRITE_REVIEW,
    READ_REVIEW,
    UPDATE_REVIEW,
    DELETE_REVIEW,
    APPROVE_REVIEW,
)


logger = logging.getLogger(__name__)


@api_controller('/performance/reviews', tags=['Performance - Reviews'])
class PerformanceReviewController(ControllerBase):

    # ===== CREATE =====

    @http_post(
        '/',
        response={201: PerformanceReviewOut},
        permissions=[ScopePermission(WRITE_REVIEW)],
    )
    def create_review(self, payload: PerformanceReviewCreateIn):
        """Crée une évaluation en statut EMPLOYEE_DRAFT."""
        actor = getattr(self.context.request, 'user', None)
        try:
            review = PerformanceService.create_review(
                payload.model_dump(),
                actor=actor,
            )
            return 201, review
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== GET (single) =====

    @http_get(
        '/{review_id}',
        response=PerformanceReviewOut,
        permissions=[ScopePermission(READ_REVIEW)],
    )
    def get_review(self, review_id: UUID):
        """Détail d'une évaluation."""
        try:
            return PerformanceReview.objects.select_related('campaign', 'employee', 'manager').get(id=review_id)
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)

    # ===== LIST =====

    @http_get(
        '/',
        response=PaginatedResponseSchema[PerformanceReviewOut],
        permissions=[ScopePermission(READ_REVIEW)],
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_all_reviews(self, filters: Annotated[PerformanceReviewListFilterIn, Query(...)]):
        """Liste paginée des évaluations (filtres : campaign, status, employee, manager)."""
        qs = PerformanceReview.objects.select_related(
            'campaign', 'employee', 'manager'
        ).all().order_by('-campaign__start_date')
        qs = filters.filter(qs).distinct()
        return qs

    # ===== UPDATE (employé) =====

    @http_patch(
        '/{review_id}/employee',
        response=PerformanceReviewOut,
        permissions=[ScopePermission(UPDATE_REVIEW)],
    )
    def update_employee_review(self, review_id: UUID, payload: PerformanceReviewUpdateEmployeeIn):
        """Met à jour l'auto-évaluation (EMPLOYEE_DRAFT)."""
        actor = getattr(self.context.request, 'user', None)
        try:
            review = PerformanceService.update_employee_review(
                review_id,
                payload.model_dump(exclude_unset=True),
                actor=actor,
            )
            return review
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== UPDATE (manager) =====

    @http_patch(
        '/{review_id}/manager',
        response=PerformanceReviewOut,
        permissions=[ScopePermission(UPDATE_REVIEW)],
    )
    def update_manager_review(self, review_id: UUID, payload: PerformanceReviewUpdateManagerIn):
        """Met à jour l'évaluation manager (MANAGER_DRAFT)."""
        actor = getattr(self.context.request, 'user', None)
        try:
            review = PerformanceService.update_manager_review(
                review_id,
                payload.model_dump(exclude_unset=True),
                actor=actor,
            )
            return review
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== DELETE =====

    @http_delete(
        '/{review_id}',
        response={204: None},
        permissions=[ScopePermission(DELETE_REVIEW)],
    )
    def delete_review(self, review_id: UUID):
        """Supprime une évaluation (EMPLOYEE_DRAFT uniquement)."""
        actor = getattr(self.context.request, 'user', None)
        try:
            PerformanceService.delete_review(review_id, actor=actor)
            return 204, None
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== SUBMIT EMPLOYEE =====

    @http_post(
        '/{review_id}/submit-employee',
        response=PerformanceReviewOut,
        permissions=[ScopePermission(UPDATE_REVIEW)],
    )
    def submit_employee(self, review_id: UUID):
        """Soumission employé : EMPLOYEE_DRAFT → MANAGER_DRAFT."""
        actor = getattr(self.context.request, 'user', None)
        try:
            review = PerformanceService.submit_employee_review(review_id, actor=actor)
            return review
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== SUBMIT MANAGER =====

    @http_post(
        '/{review_id}/submit-manager',
        response=PerformanceReviewOut,
        permissions=[ScopePermission(APPROVE_REVIEW)],
    )
    def submit_manager(self, review_id: UUID):
        """Soumission manager : MANAGER_DRAFT → SUBMITTED + calcul score."""
        actor = getattr(self.context.request, 'user', None)
        try:
            review = PerformanceService.submit_manager_review(review_id, actor=actor)
            return review
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== CALIBRATE =====

    @http_post(
        '/{review_id}/calibrate',
        response=PerformanceReviewOut,
        permissions=[ScopePermission(APPROVE_REVIEW)],
    )
    def calibrate_review(self, review_id: UUID, payload: PerformanceReviewCalibrateIn):
        """Calibrage RH : SUBMITTED → CALIBRATED."""
        actor = getattr(self.context.request, 'user', None)
        try:
            review = CalibrationService.calibrate(
                review_id=review_id,
                calibrated_score=payload.calibrated_score,
                reason=payload.reason,
                actor=actor,
            )
            return review
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== ACKNOWLEDGE =====

    @http_post(
        '/{review_id}/acknowledge',
        response=PerformanceReviewOut,
        permissions=[ScopePermission(UPDATE_REVIEW)],
    )
    def acknowledge_review(self, review_id: UUID):
        """Prise de connaissance employé : SUBMITTED → ACKNOWLEDGED."""
        actor = getattr(self.context.request, 'user', None)
        try:
            review = PerformanceService.acknowledge_review(review_id, actor=actor)
            return review
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== DISPUTE =====

    @http_post(
        '/{review_id}/dispute',
        response=PerformanceReviewOut,
        permissions=[ScopePermission(UPDATE_REVIEW)],
    )
    def dispute_review(self, review_id: UUID, payload: DisputeReviewIn):
        """Contestation employé : active le flag disputed avec motif."""
        actor = getattr(self.context.request, 'user', None)
        try:
            review = PerformanceService.dispute_review(
                review_id, reason=payload.reason, actor=actor
            )
            return review
        except PerformanceReview.DoesNotExist:
            return self.create_response({"detail": "Évaluation introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== LIST EMPLOYEE =====

    @http_get(
        '/employee/{employee_id}',
        response=PaginatedResponseSchema[PerformanceReviewOut],
        permissions=[ScopePermission(READ_REVIEW)],
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_employee_reviews(self, employee_id: UUID, filters: Annotated[PerformanceReviewListFilterIn, Query(...)]):
        """Liste les évaluations d'un employé."""
        qs = PerformanceReview.objects.filter(employee_id=employee_id).select_related(
            'campaign', 'employee', 'manager'
        ).order_by('-campaign__start_date')
        qs = filters.filter(qs).distinct()
        return qs

    # ===== LIST PENDING =====

    @http_get(
        '/pending/{reviewer_id}',
        response=PaginatedResponseSchema[PerformanceReviewOut],
        permissions=[ScopePermission(READ_REVIEW)],
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_pending_reviews(self, reviewer_id: UUID):
        """Liste les évaluations en attente d'action par un manager/RH."""
        qs = PerformanceReview.objects.filter(
            manager_id=reviewer_id,
        ).exclude(
            status__in=['CALIBRATED', 'ACKNOWLEDGED']
        ).select_related('campaign', 'employee', 'manager').order_by('-campaign__start_date')
        return qs

