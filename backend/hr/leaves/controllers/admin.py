import logging
from uuid import UUID

from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from ninja_extra import (
    api_controller,
    http_post,
    ControllerBase,
)
from injector import inject

from hr.employees.models import Employee
from hr.leaves.services import LeaveAdminService
from hr.leaves.schemas import (
    LeaveTransactionOut,
    BalanceAdjustmentIn,
    CarryOverAdjustmentIn
)


logger = logging.getLogger(__name__)


@api_controller('/leaves/admin', tags=['Leave Management (Admin)'])
class LeaveAdminController(ControllerBase):
    """ Administrative endpoints for manual leave adjustments and corrections. """

    @inject
    def __init__(self, admin_service: LeaveAdminService):
        self.admin_service = admin_service

    @http_post('/adjust-balance/{employee_id}', response=LeaveTransactionOut)
    def adjust_balance(self, employee_id: UUID, data: BalanceAdjustmentIn):
        """ Manually adjusts an employee's annual leave balance for a specific year. """
        employee = get_object_or_404(Employee, id=employee_id)
        actor = self.context.request.user
        
        try:
            return self.admin_service.adjust_balance(
                employee=employee,
                year=data.year,
                amount=data.amount,
                reason=data.reason,
                hr_user=actor
            )
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

    @http_post('/adjust-carry-over/{employee_id}', response=LeaveTransactionOut)
    def adjust_carry_over(self, employee_id: UUID, data: CarryOverAdjustmentIn):
        """ Manually adjusts or initializes leave days carried over from a previous year. """
        employee = get_object_or_404(Employee, id=employee_id)
        actor = self.context.request.user
        
        try:
            return self.admin_service.adjust_carry_over(
                employee=employee,
                source_year=data.source_year,
                amount=data.amount,
                reason=data.reason,
                hr_user=actor,
                new_expiration=data.new_expiration
            )
        except ValidationError as e:
            return self.create_response({"detail": str(e.message)}, status_code=400)

