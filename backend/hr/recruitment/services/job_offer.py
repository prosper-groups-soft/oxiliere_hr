import logging
from django.utils import timezone
from hr.recruitment.models import JobOffer
from hr.jobs.models import Position
from hr.employees.models import Employee


logger = logging.getLogger(__name__)


class JobOfferService:
    """
    Service responsible for managing the lifecycle of job offers,
    including creation, publication, and retrieval of public listings.
    """

    def create_offer(self, title, target_position_ids, vacancy_ids, recruiter_id, position_slots=None, **kwargs):
        """
        Creates a new job offer.
        Accepts IDs for relationships and fetches the corresponding objects.
        position_slots: dict mapping position_id -> number of slots for that position
        """
        target_positions = Position.objects.filter(id__in=target_position_ids)
        recruiter = Employee.objects.get(id=recruiter_id) if recruiter_id else None

        # Calculate total slots from position_slots if provided, otherwise use kwargs['slots'] or default
        if position_slots:
            total_slots = sum(position_slots.values())
        else:
            total_slots = kwargs.get('slots', 1)

        # Remove slots from kwargs to avoid duplicate keyword argument error in create()
        kwargs.pop('slots', None)

        offer = JobOffer.objects.create(
            title=title,
            recruiter=recruiter,
            slots=total_slots,
            position_slots=position_slots or {},
            **kwargs
        )
        offer.target_positions.set(target_position_ids)
        if vacancy_ids:
            offer.vacancies.set(vacancy_ids)
        logger.info(
            f"[JobOfferService] Job offer created: {title} with {target_positions.count()} positions and {len(vacancy_ids) if vacancy_ids else 0} vacancies"
        )
        return offer

    def publish_offer(self, offer_id):
        """
        Makes the job offer visible on the career site.
        """
        offer = JobOffer.objects.get(id=offer_id)
        offer.is_published = True
        offer.published_at = timezone.now()
        offer.is_active = True
        offer.save()
        logger.info(f"[JobOfferService] Job offer published: {offer.title}")
        return offer

    def close_offer(self, offer_id):
        """
        Deactivates the job offer so that it is no longer visible
        and no longer open for applications.
        """
        offer = JobOffer.objects.get(id=offer_id)
        offer.is_active = False
        # Optional: the offer may remain published but inactive
        offer.is_published = False
        offer.save()

        logger.info(f"[JobOfferService] Job offer closed: {offer.title}")
        return offer

    def get_public_listings(self):
        """
        Returns active and published job offers available to external candidates.
        """
        return JobOffer.objects.filter(
            is_published=True,
            is_active=True,
            end_date__gte=timezone.now().date()
        ).prefetch_related('target_positions', 'vacancies', 'vacancies__position')

    def get_all_offers(self):
        """
        Returns all job offers.
        """
        return JobOffer.objects.all().prefetch_related('target_positions', 'vacancies', 'vacancies__position')

    def update_offer(self, offer_id, **data):
        """
        Updates an existing job offer.
        """
        offer = JobOffer.objects.get(id=offer_id)
        
        # Handle relationships
        if 'target_position_ids' in data:
            target_positions = data.pop('target_position_ids')
            offer.target_positions.set(target_positions)
        
        if 'vacancy_ids' in data:
            vacancies = data.pop('vacancy_ids')
            offer.vacancies.set(vacancies)
            
        if 'recruiter_id' in data:
            recruiter_id = data.pop('recruiter_id')
            offer.recruiter = Employee.objects.get(id=recruiter_id) if recruiter_id else None
            
        # Update other fields
        for key, value in data.items():
            if value is not None:
                setattr(offer, key, value)
                
        offer.save()
        logger.info(f"[JobOfferService] Job offer updated: {offer.title}")
        return offer


