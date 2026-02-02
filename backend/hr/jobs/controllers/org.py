import logging
from injector import inject
from typing   import List
from uuid     import UUID
from django.shortcuts import get_object_or_404
from ninja.pagination import paginate
from oxutils.permissions.perms import ScopePermission
from oxutils.pagination.cursor import CursorPagination
from hr.jobs.models import Department
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    ControllerBase,
)

# Schemas
from hr.jobs.schemas import (
    DepartmentOut,
    DepartmentTreeOut,
    DepartmentCreateIn
)

# Services
from hr.jobs.services import OrganizationService
# Cache integration
from hr.services.cache_helpers import cache_api_response
        

logger = logging.getLogger(__name__)


@api_controller('/organization', tags=['Organization Structure'])
class OrganizationController(ControllerBase):
    """ Exposes the company's functional structure and departmental hierarchy. """

    @inject
    def __init__(self, org_service: OrganizationService):
        self.org_service = org_service

    @http_get('/departments', response=List[DepartmentOut], permissions=[ScopePermission('jobs:r')])
    @paginate(CursorPagination)
    @cache_api_response(timeout=60*60*24, key_prefix="dept_list", user_specific=False)
    def list_departments(self):
        """ Retrieves a flat list of all organizational departments. """
        logger.info("Listing all departments.")
        from hr.jobs.services.cache import JobsCacheService
        return JobsCacheService.get_all_departments(flat=True)

    @http_get('/tree', response=List[DepartmentTreeOut], permissions=[ScopePermission('jobs:r')])
    @cache_api_response(timeout=60*60*24, key_prefix="dept_tree", user_specific=False)
    def get_org_chart(self):
        """ Provides a hierarchical view of the organization for charting purposes. """
        logger.info("Generating organizational tree.")
        return self.org_service.get_department_tree()

    @http_post('/departments', response={201: DepartmentOut}, permissions=[ScopePermission('jobs:w')])
    def create_department(self, data: DepartmentCreateIn):
        """ Establishes a new department or sub-unit within the company. """
        logger.info(f"Department creation requested: {data.name}")

        dept = self.org_service.create_department(
            name=data.name,
            parent_id=data.parent_id,
            manager_id=data.manager_id
        )
        return 201, dept

    @http_patch('/departments/{department_id}/transfer-leadership/{new_manager_id}', response=DepartmentOut, permissions=[ScopePermission('jobs:u')])
    def transfer_leadership(self, department_id: UUID, new_manager_id: UUID):
        """ Changes a department's leader, including seniority validation. """
        logger.info(f"Leadership transfer initiated for Dept {department_id}")

        try:
            updated_dept = self.org_service.transfer_department_manager(
                department_id=department_id,
                new_manager_id=new_manager_id
            )
            return updated_dept
        except Exception as e:
            logger.error(f"Leadership transfer failed: {str(e)}")
            return self.create_response({"detail": "Transfer failed."}, status_code=400)

    @http_get('/departments/{department_id}', response=DepartmentOut, permissions=[ScopePermission('jobs:r')])
    def get_department_detail(self, department_id: UUID):
        """ Retrieves detailed information about a specific department. """
        return get_object_or_404(Department, id=department_id)

