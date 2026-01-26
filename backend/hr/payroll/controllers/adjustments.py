"""
PAYROLL ADJUSTMENTS CONTROLLER

Manages manual adjustments to payroll:
- Create and manage bonuses and deductions
- Apply adjustments to employee paychecks
- Configure mandatory vs optional adjustments
- Track adjustment history and audit trail
"""

import logging
from typing import List
from uuid import UUID
from injector import inject

from django.core.exceptions import ValidationError
from ninja import Query
from ninja.pagination import paginate
from ninja_extra import (
    api_controller,
    http_get,
    http_post,
    http_patch,
    http_delete,
    ControllerBase,
)
from oxutils.pagination.cursor import CursorPagination

from hr.payroll.models import PayrollAdjustment, EmployeeAdjustment
from hr.payroll.schemas import (
    PayrollAdjustmentCreateIn,
    PayrollAdjustmentOut,
    PayrollAdjustmentUpdateIn,
    EmployeeAdjustmentCreateIn,
    EmployeeAdjustmentOut,
    EmployeeAdjustmentUpdateIn,
    AdjustmentListFilterIn,
    EmployeeAdjustmentListFilterIn,
)
from hr.payroll.services.adjustments_mgmt import AdjustmentManagementService


logger = logging.getLogger(__name__)


@api_controller('/payroll/adjustments', tags=['Payroll Adjustments'])
class PayrollAdjustmentsController(ControllerBase):
    """
    Manage payroll adjustments (bonuses, deductions, special payments).
    
    Responsibilities:
    - Define adjustment types (bonus, deduction, special payment)
    - Apply adjustments to specific employees
    - Configure adjustment rules (mandatory, amount, frequency)
    - Track adjustment history
    """

    @inject
    def __init__(self, adjustment_service: AdjustmentManagementService):
        self.adjustment_service = adjustment_service

    # ===== PAYROLL ADJUSTMENT TYPES =====

    @http_get('/types/', response=List[PayrollAdjustmentOut])
    @paginate(CursorPagination)
    def list_adjustment_types(self, filters: AdjustmentListFilterIn = Query(...)):
        """
        List all adjustment types (bonuses, deductions, special payments).
        
        Supports filtering by:
        - Type (BONUS, DEDUCTION, SPECIAL_PAYMENT)
        - Is mandatory
        - Active status
        """
        logger.debug("[Adjustments] Listing adjustment types", extra={"filters": filters.model_dump()})

        qs = PayrollAdjustment.objects.all().order_by('name')

        # Apply filters
        return filters.filter(qs)

    @http_get('/types/{adjustment_id}', response=PayrollAdjustmentOut)
    def get_adjustment_type(self, adjustment_id: UUID):
        """
        Retrieve details of a specific adjustment type.
        """
        logger.debug("[Adjustments] Getting adjustment type", extra={"adjustment_id": adjustment_id})

        try:
            adjustment = self.adjustment_service.get_adjustment_type(adjustment_id)
            return adjustment

        except PayrollAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Type not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Adjustment type not found"},
                status_code=404,
            )

    @http_post('/types/', response={201: PayrollAdjustmentOut})
    def create_adjustment_type(self, data: PayrollAdjustmentCreateIn):
        """
        Create a new adjustment type (bonus, deduction, special payment).
        
        Example:
        - "Performance Bonus" - BONUS type, 5% of salary
        - "Professional Tax" - DEDUCTION type, mandatory
        - "End of Year Bonus" - SPECIAL_PAYMENT type, 13th month
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Creating adjustment type", extra={"actor": actor})

        try:
            adjustment = self.adjustment_service.create_adjustment_type(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info(
                "[Adjustments] Adjustment type created",
                extra={"adjustment_id": adjustment.id, "name": adjustment.name},
            )
            return 201, adjustment

        except ValidationError as e:
            logger.warning("[Adjustments] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/types/{adjustment_id}', response=PayrollAdjustmentOut)
    def update_adjustment_type(self, adjustment_id: UUID, data: PayrollAdjustmentUpdateIn):
        """
        Update an adjustment type definition.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Updating adjustment type", extra={"adjustment_id": adjustment_id})

        try:
            adjustment = self.adjustment_service.update_adjustment_type(
                adjustment_id=adjustment_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return adjustment

        except PayrollAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Type not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Adjustment type not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Adjustments] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_delete('/types/{adjustment_id}')
    def delete_adjustment_type(self, adjustment_id: UUID):
        """
        Delete an adjustment type (only if no employee adjustments exist).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Deleting adjustment type", extra={"adjustment_id": adjustment_id})

        try:
            self.adjustment_service.delete_adjustment_type(
                adjustment_id=adjustment_id,
                actor=actor,
            )
            logger.info("[Adjustments] Adjustment type deleted", extra={"adjustment_id": adjustment_id})
            return {"message": "Adjustment type deleted successfully"}

        except PayrollAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Type not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Adjustment type not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Adjustments] Cannot delete type", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    # ===== EMPLOYEE ADJUSTMENTS =====

    @http_get('/employee/', response=List[EmployeeAdjustmentOut])
    @paginate(CursorPagination)
    def list_employee_adjustments(self, filters: EmployeeAdjustmentListFilterIn = Query(...)):
        """
        List employee adjustments with filtering.
        
        Supports filtering by:
        - Employee
        - Adjustment type
        - Effective date range
        - Active status
        """
        logger.debug("[Adjustments] Listing employee adjustments", extra={"filters": filters.model_dump()})

        qs = EmployeeAdjustment.objects.select_related(
            'employee',
            'adjustment',
        ).all().order_by('-effective_date')

        # Apply filters
        return filters.filter(qs)

    @http_get('/employee/{employee_id}', response=List[EmployeeAdjustmentOut])
    def list_employee_specific_adjustments(self, employee_id: UUID):
        """
        List all adjustments for a specific employee.
        
        Returns active and inactive adjustments for the employee.
        """
        logger.debug("[Adjustments] Listing adjustments for employee", extra={"employee_id": employee_id})

        adjustments = self.adjustment_service.get_employee_adjustments(employee_id)
        return adjustments

    @http_get('/employee/{adjustment_id}', response=EmployeeAdjustmentOut)
    def get_employee_adjustment(self, adjustment_id: UUID):
        """
        Retrieve details of a specific employee adjustment.
        """
        logger.debug("[Adjustments] Getting employee adjustment", extra={"adjustment_id": adjustment_id})

        try:
            adjustment = self.adjustment_service.get_employee_adjustment(adjustment_id)
            return adjustment

        except EmployeeAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Adjustment not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Employee adjustment not found"},
                status_code=404,
            )

    @http_post('/employee/', response={201: EmployeeAdjustmentOut})
    def apply_adjustment_to_employee(self, data: EmployeeAdjustmentCreateIn):
        """
        Apply an adjustment to a specific employee.
        
        Example:
        - Apply "Performance Bonus" to John Doe: 50,000 CDF
        - Apply "Professional Tax" to Jane Smith: 5,000 CDF
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Applying adjustment to employee", extra={"actor": actor})

        try:
            adjustment = self.adjustment_service.create_employee_adjustment(
                data=data.model_dump(),
                actor=actor,
            )
            logger.info(
                "[Adjustments] Adjustment applied",
                extra={"employee_id": adjustment.employee_id, "adjustment_type": adjustment.adjustment_id},
            )
            return 201, adjustment

        except ValidationError as e:
            logger.warning("[Adjustments] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_patch('/employee/{adjustment_id}', response=EmployeeAdjustmentOut)
    def update_employee_adjustment(self, adjustment_id: UUID, data: EmployeeAdjustmentUpdateIn):
        """
        Update an employee adjustment (amount, dates, status).
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Updating employee adjustment", extra={"adjustment_id": adjustment_id})

        try:
            adjustment = self.adjustment_service.update_employee_adjustment(
                adjustment_id=adjustment_id,
                data=data.model_dump(exclude_unset=True),
                actor=actor,
            )
            return adjustment

        except EmployeeAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Adjustment not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Employee adjustment not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Adjustments] Validation error", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)

    @http_delete('/employee/{adjustment_id}')
    def delete_employee_adjustment(self, adjustment_id: UUID):
        """
        Remove an adjustment from an employee.
        """
        actor = getattr(self.context.request, 'user', None)
        logger.info("[Adjustments] Deleting employee adjustment", extra={"adjustment_id": adjustment_id})

        try:
            self.adjustment_service.delete_employee_adjustment(
                adjustment_id=adjustment_id,
                actor=actor,
            )
            logger.info("[Adjustments] Adjustment removed", extra={"adjustment_id": adjustment_id})
            return {"message": "Adjustment removed successfully"}

        except EmployeeAdjustment.DoesNotExist:
            logger.warning("[Adjustments] Adjustment not found", extra={"adjustment_id": adjustment_id})
            return self.create_response(
                {"detail": "Employee adjustment not found"},
                status_code=404,
            )

        except ValidationError as e:
            logger.warning("[Adjustments] Cannot delete adjustment", extra={"error": str(e)})
            return self.create_response({"detail": str(e)}, status_code=400)
