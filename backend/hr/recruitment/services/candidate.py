import logging
from hr.recruitment.models import Candidate, Application, JobOffer
from hr.jobs.models import Position


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
        """Updates candidate information and syncs applications if position_ids provided."""
        candidate = Candidate.objects.get(id=candidate_id)

        # Extract application-related fields
        offer_id = data.pop('offer_id', None)
        position_ids = data.pop('position_ids', None)
        position_priorities = data.pop('position_priorities', None)

        # Update candidate fields
        for field, value in data.items():
            setattr(candidate, field, value)
        candidate.save()

        # Sync applications if offer_id and position_ids are provided
        if offer_id and position_ids is not None:
            offer = JobOffer.objects.filter(id=offer_id).first()
            if offer and len(position_ids) > 0:
                existing_apps = Application.objects.filter(
                    candidate=candidate,
                    job_offer=offer,
                    deleted__isnull=True
                )

                priorities = position_priorities or {}

                # Remove applications no longer selected
                existing_apps.exclude(
                    target_position_id__in=position_ids
                ).delete()

                # Create missing or update existing
                for pos_id in position_ids:
                    pos = Position.objects.filter(id=pos_id).first()
                    priority = priorities.get(pos_id, 'MEDIUM')

                    app, created = Application.objects.get_or_create(
                        job_offer=offer,
                        candidate=candidate,
                        target_position=pos,
                        defaults={
                            'priority': priority,
                            'status': 'PENDING',
                        }
                    )
                    if not created and app.priority != priority:
                        app.priority = priority
                        app.save(update_fields=['priority'])

        return candidate

