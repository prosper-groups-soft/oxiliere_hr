from hr.employees.models import WorkSite
from core.services.crud  import BaseCRUDService


class WorkSiteService(BaseCRUDService):
    """
    Service for managing Work Sites.
    Standard CRUD operations are inherited from BaseCRUDService.
    """
    model = WorkSite
    allowed_update_fields = [
        'name',
        'latitude',
        'longitude',
        'allowed_radius'
    ]
    
    