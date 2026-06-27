import logging
from uuid import UUID
from injector import inject
from ninja_extra import (
    api_controller,
    http_post,
    ControllerBase
)
from django.core.exceptions import ValidationError

# Schemas
from hr.employees.schemas import (
    EmployeeOut,
    EmployeeStatusIn,
    EmployeeSuspensionIn,
    EmployeeReactiveIn,
    EmployeeOffboardingIn,
)

# Services
from hr.employees.services import (
    EmployeeStatusService,
    EmployeeQueryService,
)


logger = logging.getLogger(__name__)


@api_controller('/employees', tags=['Employee Lifecycle'])
class EmployeeLifecycleController(ControllerBase):
    """ API endpoints for employee employment status and contract lifecycle. """

    @inject
    def __init__(
        self,
        status_service: EmployeeStatusService,
        query_service: EmployeeQueryService,
    ):
        self.status_service = status_service
        self.query_service = query_service

    @http_post('/{employee_id}/lifecycle/transition', response=EmployeeOut)
    def transition_status(self, employee_id: UUID, data: EmployeeStatusIn):
        """ Changes employee status and modifies system access accordingly. """
        
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        payload = data.model_dump()

        try:
            self.status_service.transition_status(
                employee=employee,
                new_status=payload.get('new_status'),
                effective_date=payload.get('effective_date'),
                reason=payload.get('reason'),
                actor=actor,
            )
            logger.info(f"[API] Transition: {employee.matricule} -> {data.new_status}")
            return employee

        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/{employee_id}/lifecycle/suspend', response=EmployeeOut)
    def suspend_access(self, employee_id: UUID, data: EmployeeSuspensionIn):
        """ Triggers administrative lockout and suspension of access. """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)

        self.status_service.suspend_access(
            employee=employee,
            reason=data.reason,
            actor=actor,
        )

        return employee
    
    @http_post('/{employee_id}/lifecycle/reactivate', response=EmployeeOut)
    def reactivate_employee(self, employee_id: UUID, data: EmployeeReactiveIn):
        """ Restores employee to active state and portal access. """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)

        self.status_service.reactivate_employee(
            employee=employee,
            reason=data.reason,
            actor=actor,
            is_active=data.is_active,
            can_connect=data.can_connect,
        )

        return employee

    @http_post('/{employee_id}/lifecycle/offboard', response=EmployeeOut)
    def offboard_employee(self, employee_id: UUID, data: EmployeeOffboardingIn):
        """ Records official contract termination and company exit. """
        employee = self.query_service.get_employee_by_id(employee_id)
        if not employee:
            return self.create_response("Employee not found", status_code=404)

        actor = getattr(self.context.request, 'user', None)
        payload = data.model_dump()

        logger.warning(f"[API] OFFBOARDING initiated for {employee.matricule}")

        self.status_service.offboard_employee(
            employee=employee,
            termination_date=payload.get('end_date'),  # Schema → service mapping
            reason=payload.get('reason'),
            departure_type=payload.get('departure_type', 'TERMINATED'),
            actor=actor,
        )

        return employee
