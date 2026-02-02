import logging
from injector import inject
from uuid     import UUID
from typing   import List
from oxutils.permissions.perms import ScopePermission

from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    ControllerBase,
)

# --- Schemas ---
from hr.jobs.schemas import (
    CareerHistoryOut,
    EmployeeMoveIn,
    InitialAssignmentIn,
)

# --- Services ---
from hr.jobs.services import CareerService
from hr.employees.services import EmployeeQueryService


logger = logging.getLogger(__name__)


@api_controller('/career', tags=['Career Management'])
class CareerController(ControllerBase):
    """ Handles employee career moves, promotions, and professional timeline visibility. """

    @inject
    def __init__(
        self,
        career_service: CareerService,
        employee_query_service: EmployeeQueryService,
    ):
        self.career_service = career_service
        self.employee_query = employee_query_service

    @http_get('/{employee_id}/history', response=List[CareerHistoryOut], permissions=[ScopePermission('jobs:r')])
    def get_employee_career_history(self, employee_id: UUID):
        """ Retrieves the full professional timeline for a specific employee. """
        employee = self.employee_query.get_employee_by_id(employee_id)
        if not employee:
            logger.warning(f"History request: Employee {employee_id} not found.")
            return self.create_response("Employee not found", status_code=404)

        return self.career_service.get_career_summary(employee)

    @http_post('/{employee_id}/onboard', response={201: CareerHistoryOut}, permissions=[ScopePermission('jobs:w')])
    def initial_assignment(self, employee_id: UUID, data: InitialAssignmentIn):
        """ Formally records the starting role and department for a new hire. """
        employee = self.employee_query.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        try:
            history = self.career_service.assign_initial_position(
                employee=employee,
                position_id=data.position_id,
                department_id=data.department_id,
                start_date=data.start_date
            )
            logger.info(f"Initial assignment recorded for {employee.matricule}")
            return 201, history
        except ValueError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{employee_id}/promote', response={200: CareerHistoryOut}, permissions=[ScopePermission('jobs:w')])
    def promote_employee(self, employee_id: UUID, data: EmployeeMoveIn):
        """ Records a promotion, lateral move, or departmental transfer. """
        employee = self.employee_query.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        logger.info(f"Processing transition request for {employee.matricule}")

        try:
            new_record = self.career_service.move_employee(
                employee=employee,
                new_position_id=data.new_position_id,
                new_department_id=data.new_department_id,
                effective_date=data.effective_date,
                description=data.description
            )
            return 200, new_record
        except ValueError as e:
            logger.error(f"Movement failed for {employee.matricule}: {str(e)}")
            return self.create_response({"detail": str(e)}, status_code=400)

