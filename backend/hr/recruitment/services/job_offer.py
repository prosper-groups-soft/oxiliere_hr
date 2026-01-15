import logging
from django.utils import timezone
from hr.recruitment.models import JobOffer
from hr.jobs.models import Position, Department
from hr.employees.models import Employee


logger = logging.getLogger(__name__)


class JobOfferService:
    """
    Service responsible for managing the lifecycle of job offers,
    including creation, publication, and retrieval of public listings.
    """

    def create_offer(self, title, target_position_id, department_id, recruiter_id, **kwargs):
        """
        Creates a new job offer.
        Accepts IDs for relationships and fetches the corresponding objects.
        """
        target_position = Position.objects.get(id=target_position_id)
        department = Department.objects.get(id=department_id)
        recruiter = Employee.objects.get(id=recruiter_id)

        offer = JobOffer.objects.create(
            title=title,
            target_position=target_position,
            department=department,
            recruiter=recruiter,
            **kwargs
        )
        logger.info(
            f"[JobOfferService] Job offer created: {title} for department {department.name}"
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
        ).select_related('target_position', 'department')

