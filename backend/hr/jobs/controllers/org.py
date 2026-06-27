import logging
from injector import inject
from typing   import List
from uuid     import UUID
from django.shortcuts import get_object_or_404
from ninja_extra.pagination import (
    paginate,
    PageNumberPaginationExtra, 
    PaginatedResponseSchema
)
from oxutils.permissions.perms import ScopePermission
from hr.jobs.models import OrgUnit, Position
from ninja_extra    import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_delete,
    ControllerBase,
)

# Schemas
from hr.jobs.schemas import (
    OrgUnitOut,
    OrgUnitTreeOut,
    OrgUnitCreateIn,
    OrgUnitUpdateIn,
    PositionOut,
    EmployeeAssignIn,
)

# Services
from hr.jobs.services import OrganizationService
# Cache integration
from hr.services.cache_helpers import cache_api_response

        
logger = logging.getLogger(__name__)


@api_controller('/organization', tags=['Organization Structure'])
class OrganizationController(ControllerBase):
    """ Exposes the company's organizational structure and unit hierarchy. """

    @inject
    def __init__(self, org_service: OrganizationService):
        self.org_service = org_service

    @http_get('/units', response=PaginatedResponseSchema[OrgUnitOut], permissions=[ScopePermission('jobs:r')])
    @paginate(PageNumberPaginationExtra, page_size=100)
    @cache_api_response(timeout=60*5, key_prefix="unit_list", user_specific=False)
    def list_units(self):
        """ Retrieves a flat list of all organizational units. """
        logger.info("Listing all units.")
        return OrgUnit.objects.all().select_related('manager', 'affoint')

    @http_get('/tree', response=List[OrgUnitTreeOut], permissions=[ScopePermission('jobs:r')])
    @cache_api_response(timeout=60*5, key_prefix="org_tree", user_specific=False)
    def get_org_chart(self):
        """ Provides a hierarchical view of the organization for charting purposes. """
        logger.info("Generating organizational tree.")
        return self.org_service.get_org_tree()

    @http_post('/units', response={201: OrgUnitOut}, permissions=[ScopePermission('jobs:w')])
    def create_unit(self, data: OrgUnitCreateIn):
        """ Establishes a new organizational unit within the company. """
        logger.info(f"Unit creation requested: {data.name} (type: {data.type})")

        unit = self.org_service.create_unit(
            name=data.name,
            unit_type=data.type or "DEPARTMENT",
            parent_id=data.parent_id,
            manager_id=data.manager_id,
            affoint_id=data.affoint_id,
            authorized_headcount=data.authorized_headcount or 0
        )
        return 201, unit

    @http_patch('/units/{unit_id}', response=OrgUnitOut, permissions=[ScopePermission('jobs:u')])
    def update_unit(self, unit_id: UUID, data: OrgUnitUpdateIn):
        """ Updates an existing organizational unit. """
        logger.info(f"Unit update requested: {unit_id}")

        unit = self.org_service.update_unit(
            unit_id=unit_id,
            name=data.name,
            unit_type=data.type,
            parent_id=data.parent_id,
            manager_id=data.manager_id,
            affoint_id=data.affoint_id,
            authorized_headcount=data.authorized_headcount
        )
        return unit

    @http_delete('/units/{unit_id}', response={204: None}, permissions=[ScopePermission('jobs:d')])
    def delete_unit(self, unit_id: UUID):
        """ Deletes an organizational unit. """
        logger.info(f"Unit deletion requested: {unit_id}")
        try:
            self.org_service.delete_unit(unit_id)
            return 204, None
        except Exception as e:
            logger.error(f"Unit deletion failed: {str(e)}")
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/units/{unit_id}/transfer-leadership/{new_manager_id}', response=OrgUnitOut, permissions=[ScopePermission('jobs:u')])
    def transfer_leadership(self, unit_id: UUID, new_manager_id: UUID):
        """ Changes an organizational unit's leader, including seniority validation. """
        logger.info(f"Leadership transfer initiated for unit {unit_id}")

        try:
            updated_unit = self.org_service.transfer_leadership(
                unit_id=unit_id,
                new_manager_id=new_manager_id
            )
            return updated_unit
        except Exception as e:
            logger.error(f"Leadership transfer failed: {str(e)}")
            return self.create_response({"detail": "Transfer failed."}, status_code=400)

    @http_get('/units/{unit_id}', response=OrgUnitOut, permissions=[ScopePermission('jobs:r')])
    def get_unit_detail(self, unit_id: UUID):
        """ Retrieves detailed information about a specific organizational unit. """
        return get_object_or_404(OrgUnit.objects.select_related('manager', 'affoint'), id=unit_id)

    @http_get('/units/{unit_id}/positions', response=PaginatedResponseSchema[PositionOut], permissions=[ScopePermission('jobs:r')])
    @paginate(PageNumberPaginationExtra, page_size=100)
    def get_unit_positions(self, unit_id: UUID):
        """ Retrieves all positions linked to a specific organizational unit (structural approach).

        Returns all positions where Position.org_unit_id = unit_id,
        including vacant positions (not yet assigned to employees).
        """

        # Return all positions directly linked to this org unit
        return Position.objects.filter(
            org_unit_id=unit_id
        ).select_related('job_family').order_by('name')

    @http_post('/units/{unit_id}/employees/{employee_id}/assign', response={200: dict}, permissions=[ScopePermission('jobs:u')])
    def assign_employee_to_unit(self, unit_id: UUID, employee_id: UUID, data: EmployeeAssignIn = None):
        """Assigns an employee to an organizational unit."""
        logger.info(f"Assigning employee {employee_id} to unit {unit_id}")

        try:
            position_id = data.position_id if data else None
            history_entry = self.org_service.assign_employee_to_unit(
                employee_id=employee_id,
                org_unit_id=unit_id,
                position_id=position_id
            )

            return 200, {
                "message": "Employee assigned successfully.",
                "employee_id": str(employee_id),
                "org_unit_id": str(unit_id),
                "assignment_id": str(history_entry.id)
            }
        except Exception as e:
            logger.error(f"Failed to assign employee: {str(e)}")
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/employees/{employee_id}/unassign', response={200: dict}, permissions=[ScopePermission('jobs:u')])
    def unassign_employee_from_unit(self, employee_id: UUID):
        """Removes an employee from their current organizational unit."""
        logger.info(f"Unassigning employee {employee_id}")

        try:
            self.org_service.unassign_employee_from_unit(employee_id=employee_id)

            return 200, {
                "message": "Employee unassigned successfully.",
                "employee_id": str(employee_id)
            }
        except Exception as e:
            logger.error(f"Failed to unassign employee: {str(e)}")
            return self.create_response({"detail": str(e)}, status_code=400)

