from typing   import List
from uuid     import UUID
from ninja    import Query
from injector import inject
from ninja.pagination import paginate
from ninja_extra      import (
    api_controller, 
    http_get, 
    http_post, 
    http_patch, 
    http_delete, 
    ControllerBase
)
from oxutils.pagination.cursor import CursorPagination
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

    @http_get('', response=List[WorkSiteOut])
    @paginate(CursorPagination)
    def list_worksites(self, filters: WorkSiteFilterIn = Query(...)):
        """ Returns a filtered list of all physical work sites. """
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
