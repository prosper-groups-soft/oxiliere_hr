import logging
from injector import inject
from uuid     import UUID
from typing   import List, Dict

from ninja.pagination import paginate
from ninja_extra      import (
    api_controller,
    http_get,
    http_post,
    ControllerBase,
)
from oxutils.permissions.perms import ScopePermission
from oxutils.pagination.cursor import CursorPagination

# Schemas
from hr.jobs.schemas import (
    JobFamilyOut,
    PositionOut,
    PositionCreateIn
)
from hr.jobs.models import JobFamily
# Services
from hr.jobs.services import JobService
from hr.jobs.enums    import PositionLevel
# Cache integration
from hr.services.cache_helpers import cache_api_response


logger = logging.getLogger(__name__)


@api_controller('/jobs', tags=['Job Repository'])
class JobController(ControllerBase):
    """ Manages the corporate job catalog, including families and position levels. """

    @inject
    def __init__(self, job_service: JobService):
        self.job_service = job_service

    @http_get('/families', response=List[JobFamilyOut], permissions=[ScopePermission('jobs:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24, key_prefix="job_families_list", user_specific=False)
    def list_job_families(self):
        """ Retrieves all registered job families. """
        return JobFamily.objects.all()

    @http_post('/positions', response={201: PositionOut}, permissions=[ScopePermission('jobs:w')])
    def create_position(self, data: PositionCreateIn):
        """ Defines a new position within the corporate job repository. """
        logger.info(f"Creating position '{data.name}' at level {data.level}")
        
        position = self.job_service.create_position_with_family(
            name=data.name,
            family_name=data.family_name,
            level=data.level,
            description=data.description
        )
        return 201, position

    @http_get('/families/{family_id}/career-path', response=List[PositionOut])
    @paginate(CursorPagination)
    def get_family_career_path(self, family_id: UUID):
        """
        Returns the logical progression of roles within a specific family.
        Ordered by seniority (Trainee -> ... -> Executive).
        """
        return self.job_service.get_career_path(family_id)

    @http_get('/by-level/{level}', response=List[PositionOut])
    @paginate(CursorPagination)
    def list_positions_by_seniority(self, level: PositionLevel):
        """
        Filters all company positions by a specific seniority level.
        Example: "Show me all 'Senior' roles across all departments."
        """
        return self.job_service.get_positions_by_level(level)

    @http_get('/catalog', response=Dict[str, List[str]])
    def get_full_catalog(self):
        """
        Returns a simplified map of the entire job catalog:
        { "Engineering": ["Junior Dev", "Senior Dev"], "HR": ["Recruiter"] }
        """
        return self.job_service.get_family_structure()

