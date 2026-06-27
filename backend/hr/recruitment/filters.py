from typing     import Optional, List
from hr.schemas import BaseFilter
from django.db.models import Q


class ApplicationFilter(BaseFilter):
    """
    Filter parameters for listing applications.
    Supports text search, stage/status filter, source filter, priority filter, position filter.
    """
    status: Optional[List[str]] = None
    source: Optional[List[str]] = None
    priority: Optional[List[str]] = None
    position_id: Optional[List[str]] = None
    gender: Optional[List[str]] = None

    def filter_search(self, value):
        if value:
            return (
                Q(candidate__first_name__icontains=value) |
                Q(candidate__middle_name__icontains=value) |
                Q(candidate__last_name__icontains=value) |
                Q(candidate__email__icontains=value)
            )
        return Q()

    def filter_status(self, value):
        if value:
            return Q(status__in=value)
        return Q()

    def filter_source(self, value):
        if value:
            return Q(candidate__source__in=value)
        return Q()

    def filter_priority(self, value):
        if value:
            return Q(priority__in=value)
        return Q()

    def filter_position_id(self, value):
        if value:
            return Q(target_position_id__in=value)
        return Q()

    def filter_gender(self, value):
        if value:
            return Q(candidate__gender__in=value)
        return Q()


class InterviewFilter(BaseFilter):
    """
    Filter parameters for listing interviews.
    Supports filtering by candidate_id or application_id.
    """
    candidate_id: Optional[str] = None
    application_id: Optional[str] = None
    offer_id: Optional[str] = None

    def filter_candidate_id(self, value):
        if value:
            return Q(application__candidate_id=value)
        return Q()

    def filter_application_id(self, value):
        if value:
            return Q(application_id=value)
        return Q()

    def filter_offer_id(self, value):
        if value:
            return Q(application__job_offer_id=value)
        return Q()
