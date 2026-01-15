import logging
from injector import inject
from uuid import UUID
from typing import List

from ninja import Query
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
    """
    ORCHESTRATION LAYER - CAREER
    
    Handles employee movements, promotions, and career path visibility.
    Delegates atomic transitions to CareerService to ensure data integrity.
    """

    @inject
    def __init__(
        self,
        career_service: CareerService,
        employee_query_service: EmployeeQueryService,
    ):
        """
        Dependency injection for career and employee query services.
        """
        self.career_service = career_service
        self.employee_query = employee_query_service

    # READ OPERATIONS
    # ------------------------------------------------------------------
    @http_get('/{employee_id}/history', response=List[CareerHistoryOut])
    def get_employee_career_history(self, employee_id: UUID):
        """
        Retrieves the full professional timeline of an employee.
        Includes enriched data such as calculated durations for each position held.
        """
        employee = self.employee_query.get_employee_by_id(employee_id)
        if not employee:
            logger.warning(f"[API] History request failed: Employee {employee_id} not found.")
            return self.create_response("Employee not found", status_code=404)

        # Returns an enriched list (e.g., including 'days_spent' calculations)
        return self.career_service.get_career_summary(employee)

    # WRITE OPERATIONS (TRANSITIONS)
    # ------------------------------------------------------------------
    @http_post('/{employee_id}/onboard', response={201: CareerHistoryOut})
    def initial_assignment(self, employee_id: UUID, data: InitialAssignmentIn):
        """
        Assigns the first position and department to a newly hired employee.
        Used exclusively during the final stage of onboarding.
        """
        employee = self.employee_query.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        try:
            # IDs are passed to the service which handles object retrieval and validation.
            history = self.career_service.assign_initial_position(
                employee=employee,
                position_id=data.position_id,
                department_id=data.department_id,
                start_date=data.start_date
            )
            logger.info(f"[API] Initial assignment successful for employee {employee.matricule}")
            return 201, history
        except ValueError as e:
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_post('/{employee_id}/promote', response={200: CareerHistoryOut})
    def promote_employee(self, employee_id: UUID, data: EmployeeMoveIn):
        """
        Executes a promotion or transfer. 
        Automatically closes the current position and opens a new one within an atomic transaction.
        """
        employee = self.employee_query.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        logger.info(f"[API] Processing promotion/transfer request for employee {employee.matricule}")

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
            logger.error(f"[API] Movement failed for {employee.matricule}: {str(e)}")
            return self.create_response({"detail": str(e)}, status_code=400)

