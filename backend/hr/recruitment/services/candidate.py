import logging
from hr.recruitment.models import Candidate


logger = logging.getLogger(__name__)


class CandidateService:
    """
    Service layer for managing candidate profiles.
    Handles lifecycle operations such as retrieval, creation, and profile updates
    within the recruitment talent pool.
    """

    def get_or_create_candidate(self, email, defaults):
        """
        Retrieves an existing candidate or creates a new one.
        Takes into account first_name, middle_name, and last_name.
        """
        email = email.lower().strip()
        candidate, created = Candidate.objects.get_or_create(
            email=email,
            defaults=defaults
        )
        
        if created:
            logger.info(f"[CandidateService] New candidate created: {email}")
        else:
            logger.info(f"[CandidateService] Existing candidate retrieved: {email}")
            
        return candidate

    def update_profile(self, candidate_id, data):
        """Updates candidate information (e.g., new phone number or LinkedIn profile)."""
        candidate = Candidate.objects.get(id=candidate_id)
        for field, value in data.items():
            setattr(candidate, field, value)
        candidate.save()
        return candidate

