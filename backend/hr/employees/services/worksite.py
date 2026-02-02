from hr.employees.models import WorkSite
from core.services.crud  import BaseCRUDService


class WorkSiteService(BaseCRUDService):
    """ Service for managing physical work sites. """
    model = WorkSite
    allowed_update_fields = [
        'name', 'latitude', 'longitude', 'allowed_radius'
    ]
    
    