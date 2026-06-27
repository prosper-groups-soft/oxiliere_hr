from uuid     import UUID
from ninja    import Query
from injector import inject
from ninja_extra      import (
    api_controller, 
    http_get, 
    http_post, 
    http_patch, 
    http_delete, 
    ControllerBase
)
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra,
    PaginatedResponseSchema
)
from hr.employees.services import (
    WorkSiteService
)
from hr.employees.schemas import (
    WorkSiteOut, 
    WorkSiteCreateIn, 
    WorkSiteUpdateIn,
    WorkSiteFilterIn
)


@api_controller('/work-sites', tags=['Work Site'])
class WorkSiteController(ControllerBase):
    """ API endpoints for managing physical work locations. """

    @inject
    def __init__(self, worksite_service: WorkSiteService):
        self.worksite_service = worksite_service


    @http_get('', response=PaginatedResponseSchema[WorkSiteOut])
    @paginate(PageNumberPaginationExtra, page_size=8)
    def list_worksites(self, filters: WorkSiteFilterIn = Query(...)):
        """
        GET /api/work-sites
        List all work sites with optional filtering (page-based pagination).
        """
        return filters.filter(self.worksite_service.list())
    
    
    @http_post('', response={201: WorkSiteOut})
    def create_worksite(self, data: WorkSiteCreateIn):
        """ Registers a new physical work location. """
        return 201, self.worksite_service.create(data=data.model_dump())


    @http_patch('/{site_id}', response=WorkSiteOut)
    def update_worksite(self, site_id: UUID, data: WorkSiteUpdateIn):
        """ Updates geographic or metadata details for a work site. """
        instance = self.worksite_service.get(id=site_id)
        return self.worksite_service.update(
            instance=instance, 
            data=data.model_dump(exclude_unset=True)
        )
        
        
    @http_delete('/{site_id}', response={204: None})
    def delete_worksite(self, site_id: UUID):
        """ Removes a work site from the system. """
        instance = self.worksite_service.get(id=site_id)
        self.worksite_service.delete(instance=instance)
        return 204, None

