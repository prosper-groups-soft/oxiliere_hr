import logging
from uuid import UUID
from injector import inject

from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError, ObjectDoesNotExist
from django.http import Http404
from ninja_extra import (
    api_controller,
    http_post,
    ControllerBase,
)
from oxutils.permissions.perms import ScopePermission

# Models
from hr.employees.models import Employee

# Schemas
from hr.payroll.schemas import EmployeeContractOut
from hr.employees.schemas import EmployeeOnboardingContractIn

# Services
from hr.employees.services import EmployeeCareerService


logger = logging.getLogger(__name__)


@api_controller('/employees', tags=['Employee Career & Contracts'])
class EmployeeCareerController(ControllerBase):
    """API endpoints for employee career management, contracts, and positions."""

    @inject
    def __init__(self, career_service: EmployeeCareerService):
        self.career_service = career_service

    @http_post('/{employee_id}/contracts', response={201: EmployeeContractOut}, permissions=[ScopePermission('employees:w')])
    def create_employee_contract(self, employee_id: UUID, data: EmployeeOnboardingContractIn):
        """
        Creates a complete employment contract during onboarding.
        
        This endpoint:
        1. Creates an EmployeeContract (payroll)
        2. Creates an EmployeePositionHistory (current position assignment)
        3. Creates an EmployeeTransition (HIRE event)
        
        Returns the created contract.
        """
        
        employee = get_object_or_404(Employee, id=employee_id)
        
        logger.info(f"[Career] Creating contract for employee {employee.matricule}")
        
        try:
            contract = self.career_service.create_onboarding_contract(
                employee=employee,
                position_id=data.position_id,
                seniority_level_id=data.seniority_level_id,
                base_salary=data.base_salary,
                contract_type=data.contract_type,
                remuneration_type=data.remuneration_type,
                payment_period=data.payment_period,
                salary_base_type=data.salary_base_type,
                start_date=data.start_date,
                end_date=data.end_date,
                currency=data.currency,
                is_active=data.is_active,
            )
            
            logger.info(
                f"[Career] Contract created successfully via service",
                extra={
                    "contract_id": str(contract.id),
                    "employee_id": str(employee_id),
                    "position_id": str(data.position_id),
                    "seniority_level_id": str(data.seniority_level_id)
                }
            )
            
            return 201, contract
            
        except (ObjectDoesNotExist, Http404) as e:
            logger.warning(f"[Career] Resource not found: {e}")
            return self.create_response(
                {"detail": f"Resource not found: {str(e)}"},
                status_code=400
            )
        except ValidationError as e:
            logger.warning(f"[Career] Validation error: {e}")
            return self.create_response({"detail": str(e)}, status_code=400)
        except Exception as e:
            logger.exception(f"[Career] Unexpected error during contract creation")
            return self.create_response(
                {"detail": "An unexpected error occurred"},
                status_code=500
            )
