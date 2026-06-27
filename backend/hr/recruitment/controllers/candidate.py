import logging
from injector  import inject
from uuid      import UUID
from ninja     import File
from ninja.files import UploadedFile
from django.shortcuts import get_object_or_404
from ninja_extra import (
    api_controller,
    http_get,
    http_patch,
    http_post,
    ControllerBase,
)
from oxutils.permissions.perms import ScopePermission

# Schemas
from hr.recruitment.schemas import (
    CandidateOut,
    CandidateUpdateIn,
    CandidateApplicationsSyncIn,
)
from hr.jobs.models import Position
from hr.recruitment.models import Candidate, Application, JobOffer
from hr.recruitment.services.candidate import CandidateService


logger = logging.getLogger(__name__)


@api_controller('/recruitment/candidates', tags=['Recruitment - Candidates'])
class CandidateController(ControllerBase):
    """API endpoints for managing candidate profiles."""

    @inject
    def __init__(self, candidate_service: CandidateService):
        self.candidate_service = candidate_service

    @http_get('/{candidate_id}', response=CandidateOut, permissions=[ScopePermission('recruitment:r')])
    def get_candidate(self, candidate_id: UUID):
        """Retrieve a single candidate profile."""
        candidate = get_object_or_404(Candidate, id=candidate_id)
        return candidate

    @http_patch('/{candidate_id}', response=CandidateOut, permissions=[ScopePermission('recruitment:u')])
    def update_candidate(self, candidate_id: UUID, data: CandidateUpdateIn):
        """Update a candidate's profile information."""
        candidate = get_object_or_404(Candidate, id=candidate_id)
        actor = getattr(self.context.request, 'user', None)

        updated = self.candidate_service.update_profile(
            candidate_id=candidate_id,
            data=data.model_dump(exclude_unset=True),
        )
        return updated

    @http_post('/{candidate_id}/upload-photo', response=CandidateOut, permissions=[ScopePermission('recruitment:u')])
    def upload_photo(self, candidate_id: UUID, file: File[UploadedFile]):
        """Upload a profile photo for a candidate."""
        candidate = get_object_or_404(Candidate, id=candidate_id)
        actor = getattr(self.context.request, 'user', None)

        candidate.profile_photo = file
        candidate.save(update_fields=['profile_photo', 'updated_by', 'updated_at'])

        logger.info(f"[API] Profile photo uploaded for candidate {candidate_id}")
        return candidate

    @http_post('/{candidate_id}/upload-resume', response=CandidateOut, permissions=[ScopePermission('recruitment:u')])
    def upload_resume(self, candidate_id: UUID, resume: File[UploadedFile]):
        """Upload or replace a resume for a candidate."""
        candidate = get_object_or_404(Candidate, id=candidate_id)
        actor = getattr(self.context.request, 'user', None)

        candidate.resume = resume
        candidate.save(update_fields=['resume', 'updated_by', 'updated_at'])

        logger.info(f"[API] Resume uploaded for candidate {candidate_id}")
        return candidate

    @http_patch('/{candidate_id}/sync-applications', response=CandidateOut, permissions=[ScopePermission('recruitment:u')])
    def sync_applications(
        self,
        candidate_id: UUID,
        data: CandidateApplicationsSyncIn,
    ):
        """Sync a candidate's applications: add/remove positions, update priorities."""
        candidate = get_object_or_404(Candidate, id=candidate_id)
        offer = get_object_or_404(JobOffer, id=data.offer_id)

        existing_apps = Application.objects.filter(
            candidate=candidate,
            job_offer=offer,
            deleted__isnull=True
        )

        positions_to_keep = data.position_ids or []
        priorities = data.position_priorities or {}

        # 1. Remove applications for positions no longer selected
        existing_apps.exclude(
            target_position_id__in=positions_to_keep
        ).delete()

        # 2. Add missing applications or update priorities
        for pos_id in positions_to_keep:
            pos = Position.objects.filter(id=pos_id).first()
            priority = priorities.get(pos_id, 'MEDIUM')

            app, created = Application.objects.get_or_create(
                job_offer=offer,
                candidate=candidate,
                target_position=pos,
                defaults={
                    'priority': priority,
                    'cover_letter': data.cover_letter or '',
                    'status': 'PENDING',
                }
            )
            if not created and app.priority != priority:
                app.priority = priority
                app.save(update_fields=['priority'])

        logger.info(f"[API] Applications synced for candidate {candidate_id}")
        return candidate

