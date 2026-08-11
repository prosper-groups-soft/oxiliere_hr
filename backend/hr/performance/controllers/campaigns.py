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

from hr.performance.models import Campaign, CampaignParticipation, CampaignEvaluator
from hr.performance.schemas import (
    CampaignCreateIn,
    CampaignUpdateIn,
    CampaignOut,
    CampaignParticipationOut,
    ParticipantPreviewOut,
    AddParticipantIn,
    AddEvaluatorIn,
    CampaignListFilterIn,
)
from hr.performance.services.campaigns import CampaignService
from hr.performance.permissions import READ_REVIEW, WRITE_REVIEW, APPROVE_REVIEW
from hr.jobs.models import EmployeePositionHistory


logger = logging.getLogger(__name__)


@api_controller('/performance/campaigns', tags=['Performance - Campaigns'])
class CampaignController(ControllerBase):

    # ===== LIST =====

    @http_get(
        '/',
        response=PaginatedResponseSchema[CampaignOut],
        permissions=[ScopePermission(READ_REVIEW)],
    )
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_campaigns(self, filters: Annotated[CampaignListFilterIn, Query(...)]):
        """Liste paginée des campagnes."""
        qs = Campaign.objects.all().order_by('-start_date')
        qs = filters.filter(qs).distinct()
        return qs

    # ===== CREATE =====

    @http_post(
        '/',
        response={201: CampaignOut},
        permissions=[ScopePermission(WRITE_REVIEW)],
    )
    def create_campaign(self, payload: CampaignCreateIn):
        """Crée une nouvelle campagne (statut DRAFT)."""
        actor = getattr(self.context.request, 'user', None)
        try:
            campaign = CampaignService.create_campaign(
                data=payload.model_dump(),
                actor=actor,
            )
            return 201, campaign
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== DETAIL =====

    @http_get(
        '/{campaign_id}',
        response=CampaignOut,
        permissions=[ScopePermission(READ_REVIEW)],
    )
    def get_campaign(self, campaign_id: UUID):
        """Détail d'une campagne."""
        try:
            return Campaign.objects.get(id=campaign_id)
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)

    # ===== UPDATE =====

    @http_patch(
        '/{campaign_id}',
        response=CampaignOut,
        permissions=[ScopePermission(WRITE_REVIEW)],
    )
    def update_campaign(self, campaign_id: UUID, payload: CampaignUpdateIn):
        """Met à jour une campagne (DRAFT uniquement)."""
        actor = getattr(self.context.request, 'user', None)
        try:
            campaign = CampaignService.update_campaign(
                campaign_id=campaign_id,
                data=payload.model_dump(exclude_unset=True),
                actor=actor,
            )
            return campaign
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== DELETE =====

    @http_delete(
        '/{campaign_id}',
        response={204: None},
        permissions=[ScopePermission(WRITE_REVIEW)],
    )
    def delete_campaign(self, campaign_id: UUID):
        """Supprime une campagne (DRAFT uniquement, sans évaluations)."""
        actor = getattr(self.context.request, 'user', None)
        try:
            CampaignService.delete_campaign(campaign_id, actor=actor)
            return 204, None
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== ACTIVATE =====

    @http_post(
        '/{campaign_id}/activate',
        response=CampaignOut,
        permissions=[ScopePermission(APPROVE_REVIEW)],
    )
    def activate_campaign(self, campaign_id: UUID):
        """Active une campagne : DRAFT → ACTIVE + création auto des évaluations."""
        actor = getattr(self.context.request, 'user', None)
        try:
            campaign = CampaignService.activate_campaign(
                campaign_id=campaign_id,
                actor=actor,
            )
            return campaign
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== CLOSE =====

    @http_post(
        '/{campaign_id}/close',
        response=CampaignOut,
        permissions=[ScopePermission(APPROVE_REVIEW)],
    )
    def close_campaign(self, campaign_id: UUID):
        """Clôture une campagne : ACTIVE → CLOSED."""
        actor = getattr(self.context.request, 'user', None)
        try:
            campaign = CampaignService.close_campaign(
                campaign_id=campaign_id,
                actor=actor,
            )
            return campaign
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== PARTICIPANTS LIST =====

    @http_get(
        '/{campaign_id}/participants',
        response=list[CampaignParticipationOut],
        permissions=[ScopePermission(READ_REVIEW)],
    )
    def list_participants(self, campaign_id: UUID):
        """Liste les participants d'une campagne."""
        return CampaignParticipation.objects.filter(campaign_id=campaign_id).select_related('employee')

    # ===== PARTICIPANTS DETAIL =====

    @http_get(
        '/{campaign_id}/participants/detail',
        response=list[ParticipantPreviewOut],
        permissions=[ScopePermission(READ_REVIEW)],
    )
    def list_participants_detail(self, campaign_id: UUID):
        """Liste les participants avec leurs infos (nom, photo, poste, unité)."""
        records = CampaignParticipation.objects.filter(
            campaign_id=campaign_id
        ).select_related('employee')

        result = []
        for p in records:
            emp = p.employee
            pos = EmployeePositionHistory.objects.filter(
                employee=emp, is_current=True
            ).select_related("position", "org_unit").first()
            result.append({
                "id": str(emp.id),
                "name": emp.full_name,
                "last_name": emp.last_name,
                "first_name": emp.first_name,
                "middle_name": emp.middle_name or None,
                "job_title": pos.position.name if pos and pos.position else None,
                "org_unit": pos.org_unit.name if pos and pos.org_unit else None,
                "profile_photo": emp.profile_photo.url if emp.profile_photo else None,
            })
        return result

    # ===== ADD PARTICIPANT =====

    @http_post(
        '/{campaign_id}/add-participant',
        response={201: CampaignParticipationOut},
        permissions=[ScopePermission(WRITE_REVIEW)],
    )
    def add_participant(self, campaign_id: UUID, payload: AddParticipantIn):
        """Ajoute un participant à une campagne."""
        actor = getattr(self.context.request, 'user', None)
        try:
            participation = CampaignService.add_participant(
                campaign_id=campaign_id,
                employee_id=payload.employee_id,
                actor=actor,
            )
            return 201, participation
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== REMOVE PARTICIPANT =====

    @http_post(
        '/{campaign_id}/remove-participant',
        response={204: None},
        permissions=[ScopePermission(WRITE_REVIEW)],
    )
    def remove_participant(self, campaign_id: UUID, payload: AddParticipantIn):
        """Retire un participant d'une campagne (DRAFT uniquement)."""
        actor = getattr(self.context.request, 'user', None)
        try:
            CampaignService.remove_participant(
                campaign_id=campaign_id,
                employee_id=payload.employee_id,
                actor=actor,
            )
            return 204, None
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== EVALUATORS LIST =====

    @http_get(
        '/{campaign_id}/evaluators',
        response=list[CampaignParticipationOut],
        permissions=[ScopePermission(READ_REVIEW)],
    )
    def list_evaluators(self, campaign_id: UUID):
        """Liste les évaluateurs d'une campagne."""
        return CampaignEvaluator.objects.filter(campaign_id=campaign_id).select_related('employee')

    # ===== EVALUATORS DETAIL =====

    @http_get(
        '/{campaign_id}/evaluators/detail',
        response=list[ParticipantPreviewOut],
        permissions=[ScopePermission(READ_REVIEW)],
    )
    def list_evaluators_detail(self, campaign_id: UUID):
        """Liste les évaluateurs avec leurs infos (nom, photo, poste, unité)."""
        records = CampaignEvaluator.objects.filter(
            campaign_id=campaign_id
        ).select_related('employee')

        result = []
        for p in records:
            emp = p.employee
            pos = EmployeePositionHistory.objects.filter(
                employee=emp, is_current=True
            ).select_related("position", "org_unit").first()
            result.append({
                "id": str(emp.id),
                "name": emp.full_name,
                "last_name": emp.last_name,
                "first_name": emp.first_name,
                "middle_name": emp.middle_name or None,
                "job_title": pos.position.name if pos and pos.position else None,
                "org_unit": pos.org_unit.name if pos and pos.org_unit else None,
                "profile_photo": emp.profile_photo.url if emp.profile_photo else None,
            })
        return result

    # ===== ADD EVALUATOR =====

    @http_post(
        '/{campaign_id}/add-evaluator',
        response={201: CampaignParticipationOut},
        permissions=[ScopePermission(WRITE_REVIEW)],
    )
    def add_evaluator(self, campaign_id: UUID, payload: AddEvaluatorIn):
        """Ajoute un évaluateur à une campagne."""
        actor = getattr(self.context.request, 'user', None)
        try:
            evaluator, _ = CampaignEvaluator.objects.get_or_create(
                campaign_id=campaign_id,
                employee_id=payload.employee_id,
            )
            return 201, evaluator
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== REMOVE EVALUATOR =====

    @http_post(
        '/{campaign_id}/remove-evaluator',
        response={204: None},
        permissions=[ScopePermission(WRITE_REVIEW)],
    )
    def remove_evaluator(self, campaign_id: UUID, payload: AddEvaluatorIn):
        """Retire un évaluateur d'une campagne (DRAFT uniquement)."""
        actor = getattr(self.context.request, 'user', None)
        try:
            CampaignEvaluator.objects.filter(
                campaign_id=campaign_id,
                employee_id=payload.employee_id,
            ).delete()
            return 204, None
        except Campaign.DoesNotExist:
            return self.create_response({"detail": "Campagne introuvable"}, status_code=404)
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)
