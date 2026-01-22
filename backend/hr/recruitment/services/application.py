import logging
from django.db import transaction
from django.core.exceptions import ValidationError
from django.utils import timezone
from hr.recruitment.models import Application, JobOffer
from .candidate import CandidateService
from hr.recruitment.enums import ApplicationStatus


logger = logging.getLogger(__name__)


class ApplicationService:
    def __init__(self, candidate_service: CandidateService):
        self.candidate_service = candidate_service

    @transaction.atomic
    def submit_application(self, job_offer_id, candidate_data, resume_file, cover_letter=None):
        """
        Handles the arrival of a new application.
        1. Retrieves or creates the candidate (via CandidateService).
        2. Checks if the offer is still active.
        3. Prevents duplicate applications for the same offer.
        4. Saves the CV/Resume.
        """
        offer = JobOffer.objects.get(id=job_offer_id)
        
        # 2. Checks if the offer is still active (including end date and max applications limit)
        if not offer.is_active or (offer.end_date and offer.end_date < timezone.now().date()):
            raise ValidationError("This offer is no longer accepting applications.")

        if offer.max_applications:
            current_count = Application.objects.filter(job_offer=offer).count()
            if current_count >= offer.max_applications:
                raise ValidationError("The maximum number of applications for this position has been reached.")

        # Using candidate service to ensure uniqueness
        candidate = self.candidate_service.get_or_create_candidate(
            email=candidate_data['email'],
            defaults={
                'first_name': candidate_data['first_name'],
                'middle_name': candidate_data['middle_name'],
                'last_name': candidate_data['last_name'],
                'phone': candidate_data.get('phone'),
                'linkedin_profile': candidate_data.get('linkedin_profile'),
            }
        )

        # 3. Prevents duplicate applications for the same offer.
        if Application.objects.filter(job_offer=offer, candidate=candidate).exists():
            raise ValidationError("You have already applied for this offer.")

        # 4. Saves the CV/Resume.
        application = Application.objects.create(
            job_offer=offer,
            candidate=candidate,
            resume=resume_file,
            cover_letter=cover_letter,
            status=ApplicationStatus.PENDING
        )
        
        logger.info(f"New application from {candidate.email} for {offer.title}")
        return application

    def change_status(self, application_id, new_status, actor=None):
        """
        Updates the status and handles side effects (audit log).
        """
        application = Application.objects.get(id=application_id)
        old_status = application.status
        
        # In Django Ninja / Models, ensure you access the correct status choices
        if new_status not in ApplicationStatus.values:
            raise ValueError("Invalid status.")

        application.status = new_status
        application.save()
        
        logger.info(f"Application {application_id} changed from {old_status} to {new_status} by {actor}")
        return application

    def get_applications_by_offer(self, job_offer_id):
        """Returns all applications for an offer, sorted by date."""
        return Application.objects.filter(
            job_offer_id=job_offer_id
        ).select_related('candidate').order_by('-applied_at')
        
    