import logging
from typing   import List
from uuid     import UUID
from injector import inject
from django.core.exceptions import ValidationError
from ninja            import Query
from ninja.pagination import paginate
from ninja_extra      import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)
from oxutils.permissions.perms import ScopePermission
from oxutils.pagination.cursor import CursorPagination

from hr.recruitment.models  import JobOffer
from hr.recruitment.schemas import (
    JobOfferOut,
    JobOfferCreateIn,
    JobOfferFilter,
)

from hr.recruitment.services.job_offer import JobOfferService
# Cache integration
from hr.services.cache_helpers import cache_api_response


logger = logging.getLogger(__name__)


@api_controller('/recruitment/offers', tags=['Recruitment - Job Offers'])
class JobOfferController(ControllerBase):
    """
    Manages the lifecycle of job offers.
    - Public: Browsing open positions.
    - Internal: Creation and publication by recruiters.
    """

    @inject
    def __init__(self, job_offer_service: JobOfferService):
        self.job_offer_service = job_offer_service

    @http_get('/', response=List[JobOfferOut], permissions=[ScopePermission('recruitment:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24, key_prefix="job_offers_list", user_specific=False)
    def list_public_offers(self, filters: JobOfferFilter = Query(...)):
        """
        Public endpoint for the career site.
        Returns only active and published job offers.
        """
        logger.info("[API] Candidate browsing public job offers.")
        
        qs = self.job_offer_service.get_public_listings()
        
        return filters.filter(qs)

    @http_post('/', response={201: JobOfferOut}, permissions=[ScopePermission('recruitment:w')])
    def create_job_offer(self, data: JobOfferCreateIn):
        """
        Creates a new job offer in draft mode (not published by default).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Job offer creation by {actor}")

        try:
            offer = self.job_offer_service.create_offer(
                title=data.title,
                target_position=data.target_position_id,
                department=data.department_id,
                recruiter=data.recruiter_id,
                description=data.description,
                requirements=data.requirements,
                location=data.location,
                salary_range=data.salary_range,
                end_date=data.end_date
            )
            return 201, offer
        except Exception as e:
            logger.error(f"Error while creating the job offer: {str(e)}")
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_get('/{offer_id}', response=JobOfferOut, permissions=[ScopePermission('recruitment:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="offer_detail", user_specific=False)
    def get_offer_detail(self, offer_id: UUID):
        """
        Retrieves the details of a specific job offer.
        """
        try:
            return JobOffer.objects.select_related(
                'target_position',
                'department'
            ).get(id=offer_id)
        except JobOffer.DoesNotExist:
            return self.create_response("Job offer not found", status_code=404)

    @http_patch('/{offer_id}/publish', response=JobOfferOut, permissions=[ScopePermission('recruitment:w')])
    def publish_offer(self, offer_id: int):
        """
        Makes the job offer visible on the career site.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Publishing job offer {offer_id} by {actor}")
        
        try:
            offer = self.job_offer_service.publish_offer(offer_id)
            return offer
        except ValidationError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/{offer_id}/close', response=JobOfferOut, permissions=[ScopePermission('recruitment:w')])
    def close_job_offer(self, offer_id: int):
        """
        Manually closes a job offer.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Closing job offer {offer_id} by {actor}")
        
        try:
            offer = self.job_offer_service.close_offer(offer_id)
            return offer
        except Exception as e:
            return self.create_response({"detail": str(e)}, status_code=400)

