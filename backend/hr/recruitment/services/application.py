import logging
from injector import inject
from collections import OrderedDict
from django.db    import transaction
from django.db.models import Q
from django.utils import timezone
from django.core.exceptions import ValidationError
from hr.recruitment.models  import Application, JobOffer
from hr.jobs.models import Position
from .candidate import CandidateService
from hr.recruitment.enums import ApplicationStatus, CandidatePriority


logger = logging.getLogger(__name__)


class ApplicationService:
    @inject
    def __init__(self, candidate_service: CandidateService):
        self.candidate_service = candidate_service

    @transaction.atomic
    def submit_application(self, job_offer_id: str, candidate_data, resume_file=None, cover_letter=None):
        """
        Handles the arrival of a new application.
        1. Retrieves or creates the candidate (via CandidateService).
        2. Checks if the offer is still active.
        3. Creates applications for each target position (or one without position).
        4. Saves the CV/Resume.
        """
        offer = JobOffer.objects.get(id=job_offer_id)

        # 2. Checks if the offer is still active
        if not offer.is_active or (offer.end_date and offer.end_date < timezone.now().date()):
            raise ValidationError("This offer is no longer accepting applications.")

        if offer.max_applications:
            current_count = Application.objects.filter(job_offer=offer).count()
            if current_count >= offer.max_applications:
                raise ValidationError("The maximum number of applications for this position has been reached.")

        defaults = {
            'first_name': candidate_data['first_name'],
            'middle_name': candidate_data.get('middle_name') or "",
            'last_name': candidate_data['last_name'],
            'phone': candidate_data.get('phone'),
            'linkedin_profile': candidate_data.get('linkedin_profile'),
            'gender': candidate_data.get('gender') or 'NOT_SPECIFIED',
            'source': candidate_data.get('source'),
            'location': candidate_data.get('location'),
            'position': candidate_data.get('position'),
            'experience': candidate_data.get('experience'),
            'summary': candidate_data.get('summary'),
            'skills': candidate_data.get('skills') or [],
            'technical_score': candidate_data.get('technical_score'),
            'experience_score': candidate_data.get('experience_score'),
            'communication_score': candidate_data.get('communication_score'),
            'culture_score': candidate_data.get('culture_score'),
        }

        # Using candidate service to ensure uniqueness
        candidate = self.candidate_service.get_or_create_candidate(
            email=candidate_data['email'],
            defaults=defaults
        )

        effective_cover_letter = cover_letter or candidate_data.get('cover_letter') or candidate_data.get('notes')

        # 3. Get target positions from data
        target_position_ids = candidate_data.get('target_position_ids') or []

        base_payload = {
            'job_offer': offer,
            'candidate': candidate,
            'cover_letter': effective_cover_letter,
            'status': ApplicationStatus.PENDING,
            'priority': candidate_data.get('priority') or CandidatePriority.MEDIUM,
        }

        # Save resume on the candidate (not per-application)
        if resume_file is not None:
            candidate.resume = resume_file
            candidate.save(update_fields=['resume'])

        applications = []

        if target_position_ids:
            # Create one application per target position
            position_priorities = candidate_data.get('position_priorities') or {}
            for pos_id in target_position_ids:
                pos = Position.objects.get(id=pos_id)

                # Priority: per-position > global > MEDIUM
                app_priority = position_priorities.get(pos_id) or candidate_data.get('priority') or CandidatePriority.MEDIUM

                # Check uniqueness per (offer, candidate, position)
                if Application.objects.filter(
                    job_offer=offer,
                    candidate=candidate,
                    target_position=pos
                ).exists():
                    raise ValidationError(
                        f"You have already applied for the position '{pos.name}'."
                    )

                app = Application.objects.create(
                    **{k: v for k, v in base_payload.items() if k != 'priority'},
                    target_position=pos,
                    priority=app_priority,
                )
                applications.append(app)
                logger.info(
                    f"New application from {candidate.email} for {offer.title} - position '{pos.name}'"
                )
        else:
            # Legacy: create one application without specific position
            if Application.objects.filter(
                job_offer=offer,
                candidate=candidate,
                target_position__isnull=True
            ).exists():
                raise ValidationError("You have already applied for this offer.")

            app = Application.objects.create(**base_payload)
            applications.append(app)
            logger.info(f"New application from {candidate.email} for {offer.title}")

        # Return the first application for backward compatibility
        return applications[0]

    def change_status(self, application_id, new_status, actor=None):
        """
        Updates the status and handles side effects (audit log).
        """
        application = Application.objects.get(id=application_id)
        old_status = application.status

        if new_status not in ApplicationStatus.values:
            raise ValueError("Invalid status.")

        application.status = new_status
        application.save()

        logger.info(f"Application {application_id} changed from {old_status} to {new_status} by {actor}")
        return application

    def get_applications_by_offer(self, job_offer_id, filters=None):
        """Returns all applications for an offer, filtered and sorted by date."""
        qs = Application.objects.filter(
            job_offer_id=job_offer_id
        ).select_related('candidate', 'target_position').order_by('-applied_at')

        if filters is not None:
            qs = filters.filter(qs)

        return qs

    def get_candidates_with_applications(self, job_offer_id, filters=None):
        """
        Returns a list of candidates grouped with their applications.
        Each candidate carries its applications in `_applications`.
        Applications are sorted by applied_at (newest first).
        """
        # 1. Récupérer toutes les applications pour cette offre
        apps_qs = Application.objects.filter(
            job_offer_id=job_offer_id
        ).select_related('candidate', 'target_position').order_by('-applied_at')

        if filters is not None:
            apps_qs = filters.filter(apps_qs)

        # 2. Grouper par candidat
        candidate_map: OrderedDict = OrderedDict()

        for app in apps_qs:
            candidate = app.candidate
            if candidate.id not in candidate_map:
                candidate._applications = []
                candidate_map[candidate.id] = candidate
            candidate_map[candidate.id]._applications.append(app)

        # 3. Retourner la liste des candidats (ordonnée par la plus récente application)
        return list(candidate_map.values())

    def get_all_applications(self, filters=None):
        """Returns all applications with filtering."""
        qs = Application.objects.select_related(
            'candidate',
            'job_offer',
            'target_position'
        ).order_by('-applied_at')

        if filters is not None:
            qs = filters.filter(qs)

        return qs