import logging
from typing import List
from injector import inject

from django.core.exceptions import ValidationError
from ninja import File, Form
from ninja.files import UploadedFile
from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from oxutils.pagination.cursor import CursorPagination

# Schemas
from hr.recruitment.schemas import (
    ApplicationOut,
    ApplicationCreateIn,
)
from hr.recruitment.enums import ApplicationStatus

# Models 
from hr.recruitment.models import Application

# Services
from hr.recruitment.services import ApplicationService


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

    @http_post('/{offer_id}/apply', response={201: ApplicationOut}, auth=None)
    def submit_application(
        self,
        offer_id: int,
        data: ApplicationCreateIn = Form(...),
        resume: UploadedFile = File(...)
    ):
        """
        Submits an application from a candidate.
        Combines form data with the resume file.
        """
        logger.info(
            f"[API] New application for offer {offer_id} from {data.email}"
        )

        try:
            # Pass the data to the service layer
            # data.model_dump() converts the schema into a dictionary for the service
            application = self.application_service.submit_application(
                job_offer_id=offer_id,
                candidate_data=data.model_dump(),
                resume_file=resume,
                cover_letter=data.cover_letter
            )
            return 201, application

        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.error(f"Submission error: {str(e)}")
            return self.create_response(
                {"detail": "An unexpected error occurred."},
                status_code=500
            )

    @http_get('/', response=List[ApplicationOut])
    @paginate(CursorPagination)
    def list_applications(self, offer_id: int = None):
        """
        Lists applications. Can be filtered by job offer.
        """
        if offer_id:
            return self.application_service.get_applications_by_offer(offer_id)

        # If no offer_id is provided, return all applications
        return Application.objects.select_related(
            'candidate',
            'job_offer'
        ).all()

    @http_patch('/{application_id}/status', response=ApplicationOut)
    def update_application_status(
        self,
        application_id: int,
        new_status: ApplicationStatus
    ):
        """
        Manually updates the application status (Shortlisted, Rejected, etc.).
        """
        actor = getattr(self.context.request, 'user', None)
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

    @http_get('/{application_id}', response=ApplicationOut)
    def get_application_detail(self, application_id: int):
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

