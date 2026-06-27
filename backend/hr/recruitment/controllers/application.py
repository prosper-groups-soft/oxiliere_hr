import logging
from typing import Optional
from injector import inject
from uuid     import UUID
from django.core.exceptions import ValidationError
from ninja       import File, Form, Query
from ninja.files import UploadedFile
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
    PaginatedResponseSchema
)
from oxutils.permissions.perms import ScopePermission

from hr.recruitment.schemas  import (
    ApplicationOut, ApplicationCreateIn,
    CandidateWithApplicationsOut, ApplicationUpdateIn,
    ApplicationEvaluationIn, ApplicationOfferIn,
)
from hr.recruitment.enums    import ApplicationStatus
from hr.recruitment.models   import Application
from hr.recruitment.services import ApplicationService
from hr.recruitment.filters  import ApplicationFilter


logger = logging.getLogger(__name__)


@api_controller('/recruitment/applications', tags=['Recruitment - Applications'])
class ApplicationController(ControllerBase):
    """
    Manages the application workflow.
    Note: Submission uses 'multipart/form-data' to support resume upload.
    """

    @inject
    def __init__(self, application_service: ApplicationService):
        self.application_service = application_service

    @http_post('/{offer_id}/apply', response={201: ApplicationOut}, permissions=[ScopePermission('recruitment:w')])
    def submit_application(
        self,
        offer_id: UUID,
        data: ApplicationCreateIn = Form(...),  # type: ignore[reportCallIssue]
        resume: Optional[UploadedFile] = File(None)  # type: ignore[reportCallIssue]
    ):
        """
        Submits an application from a candidate.
        Combines form data with the resume file.
        """
        logger.info(
            f"[API] New application for offer {offer_id} from {data.email}"
        )

        try:
            return 201, self.application_service.submit_application(
                job_offer_id=offer_id,
                candidate_data=data.model_dump(),
                resume_file=resume,
                cover_letter=data.cover_letter or data.notes
            )

        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.error(f"Submission error: {str(e)}")
            return self.create_response(
                {"detail": "An unexpected error occurred."},
                status_code=500
            )

    @http_get('/', response=PaginatedResponseSchema[ApplicationOut], permissions=[ScopePermission('recruitment:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_applications(
        self,
        offer_id: Optional[UUID] = None,
        filters: ApplicationFilter = Query(...)
    ):
        """
        Lists applications with server-side filtering and search.
        Supports filtering by offer_id, status, source, priority, and text search.
        """
        if offer_id:
            return self.application_service.get_applications_by_offer(offer_id, filters)

        return self.application_service.get_all_applications(filters)

    @http_get('/candidates', response=PaginatedResponseSchema[CandidateWithApplicationsOut], permissions=[ScopePermission('recruitment:r')])
    @paginate(PageNumberPaginationExtra, page_size=50)
    def list_candidates_with_apps(
        self,
        offer_id: Optional[UUID] = None,
        filters: ApplicationFilter = Query(...)
    ):
        """
        Lists candidates grouped with their applications for a job offer.
        Pagination is by candidate (not by application).
        """
        if not offer_id:
            return []
        return self.application_service.get_candidates_with_applications(offer_id, filters)

    @http_patch('/{application_id}/status', response=ApplicationOut, permissions=[ScopePermission('recruitment:u')])
    def update_application_status(
        self,
        application_id: UUID,
        new_status: ApplicationStatus
    ):
        """
        Manually updates the application status (Shortlisted, Rejected, etc.).
        """
        actor = getattr(self.context.request, 'user', None) if self.context else None
        logger.info(
            f"[API] Application status change for {application_id} by {actor}"
        )

        try:
            application = self.application_service.change_status(
                application_id=application_id,
                new_status=new_status,
                actor=actor
            )
            return application
        except (ValidationError, ValueError) as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{application_id}', response=ApplicationOut, permissions=[ScopePermission('recruitment:u')])
    def update_application(
        self,
        application_id: UUID,
        data: ApplicationUpdateIn
    ):
        """
        Updates application metadata (e.g. priority).
        """
        try:
            app = Application.objects.get(id=application_id)
            for attr, value in data.model_dump(exclude_none=True).items():
                setattr(app, attr, value)
            app.save()
            return app
        except Application.DoesNotExist:
            return self.create_response(
                "Application not found",
                status_code=404
            )

    @http_post('/{application_id}/upload-resume', response=ApplicationOut, permissions=[ScopePermission('recruitment:u')])
    def upload_resume(
        self,
        application_id: UUID,
        resume: UploadedFile = File(...)
    ):
        """Upload or replace a resume for an application."""
        try:
            app = Application.objects.select_related('candidate').get(id=application_id)
            candidate = app.candidate
            candidate.resume = resume
            candidate.save(update_fields=['resume'])
            return app
        except Application.DoesNotExist:
            return self.create_response(
                "Application not found",
                status_code=404
            )

    @http_patch('/{application_id}/evaluation', response=ApplicationOut, permissions=[ScopePermission('recruitment:u')])
    def update_evaluation(
        self,
        application_id: UUID,
        data: ApplicationEvaluationIn
    ):
        """Update evaluation scores for an application."""
        try:
            app = Application.objects.get(id=application_id)
            if data.scores is not None:
                app.scores = data.scores
            if data.evaluation_notes is not None:
                app.evaluation_notes = data.evaluation_notes
            app.save()
            return app
        except Application.DoesNotExist:
            return self.create_response({"detail": "Application not found"}, status_code=404)

    @http_patch('/{application_id}/offer', response=ApplicationOut, permissions=[ScopePermission('recruitment:u')])
    def update_offer(
        self,
        application_id: UUID,
        data: ApplicationOfferIn
    ):
        """Update offer details for an application."""
        try:
            app = Application.objects.get(id=application_id)
            if data.salary_min is not None:
                app.salary_min = data.salary_min
            if data.salary_max is not None:
                app.salary_max = data.salary_max
            if data.salary_currency is not None:
                app.salary_currency = data.salary_currency
            if data.offer_start_date is not None:
                app.offer_start_date = data.offer_start_date
            # Auto-transition to OFFER status if not already
            if app.status != ApplicationStatus.OFFER:
                app.status = ApplicationStatus.OFFER
            app.save()
            return app
        except Application.DoesNotExist:
            return self.create_response({"detail": "Application not found"}, status_code=404)

    @http_get('/{application_id}', response=ApplicationOut, permissions=[ScopePermission('recruitment:r')])
    def get_application_detail(self, application_id: UUID):
        """
        Detailed view of an application.
        """
        try:
            return Application.objects.select_related(
                'candidate',
                'job_offer'
            ).get(id=application_id)
        except Application.DoesNotExist:
            return self.create_response(
                "Application not found",
                status_code=404
            )

