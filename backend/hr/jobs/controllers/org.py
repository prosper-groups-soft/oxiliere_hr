import logging
from injector import inject
from uuid import UUID
from typing import List

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


logger = logging.getLogger(__name__)


@api_controller('/organization', tags=['Organization Structure'])
class OrganizationController(ControllerBase):
    """
    ORCHESTRATION LAYER - DEPARTMENTS
    
    Exposes the functional structure of the company.
    Handles department creation, hierarchy visualization (Tree),
    and leadership transfers.
    """

    @inject
    def __init__(self, org_service: OrganizationService):
        self.org_service = org_service

    @http_get('/tree', response=List[DepartmentTreeOut])
    def get_company_tree(self):
        """
        Generates a top-down recursive view of the entire organization.
        Ideal for organizational charts on the front-end.
        """
        logger.info("[API] Generating full organizational tree.")
        return self.org_service.get_department_tree()

    @http_post('/departments', response={201: DepartmentOut})
    def create_department(self, data: DepartmentCreateIn):
        """
        Creates a new functional unit or sub-department.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Creating department '{data.name}' (Requested by: {actor})")

        dept = self.org_service.create_department(
            name=data.name,
            parent_id=data.parent_id,
            manager_id=data.manager_id
        )
        return 201, dept

    @http_patch('/departments/{department_id}/transfer-leadership/{new_manager_id}', response=DepartmentOut)
    def transfer_leadership(self, department_id: UUID, new_manager_id: UUID):
        """
        Changes the manager of a department.
        Includes seniority validation via the service layer.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info(f"[API] Leadership transfer initiated for Dept {department_id}")

        try:
            updated_dept = self.org_service.transfer_department_manager(
                department_id=department_id,
                new_manager_id=new_manager_id
            )
            return updated_dept
        except Exception as e:
            logger.error(f"[API] Leadership transfer failed: {str(e)}")
            return self.create_response({"detail": "Transfer failed."}, status_code=400)

    @http_get('/departments/{department_id}', response=DepartmentOut)
    def get_department_detail(self, department_id: UUID):
        """
        Provides detailed information about a specific department.
        """
        from hr.jobs.models import Department
        from django.shortcuts import get_object_or_404
        
        return get_object_or_404(Department, id=department_id)

