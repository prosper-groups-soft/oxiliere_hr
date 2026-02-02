import logging
from decimal import Decimal
from typing import Dict, Any
from uuid import UUID

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import QuerySet

from hr.payroll.models import (
    SalaryAdvance,
    AdvanceDeductionConfiguration,
    RepaymentRecord,
)
from hr.employees.models import Employee


logger = logging.getLogger(__name__)


class AdvanceManagementService:
    """ Manages salary advances, approvals, and repayment configurations. """

    # ===== ADVANCE CRUD =====

    @classmethod
    @transaction.atomic
    def create_advance(cls, data: Dict[str, Any], actor=None) -> SalaryAdvance:
        """ Creates a new salary advance request. """
        logger.debug("[Advances] Creating advance", extra={"data": data, "actor": actor})

        # Validate employee
        try:
            employee = Employee.objects.get(id=data.get('employee_id'))
        except Employee.DoesNotExist:
            logger.warning(
                "[Advances] Employee not found",
                extra={"employee_id": data.get('employee_id')}
            )
            raise ValidationError(f"Employee {data.get('employee_id')} not found")

        # Validate amount
        amount = Decimal(str(data.get('amount', 0)))
        if amount <= 0:
            logger.warning("[Advances] Invalid amount", extra={"amount": amount})
            raise ValidationError("Advance amount must be positive")

        # Create advance
        advance = SalaryAdvance.objects.create(
            employee=employee,
            amount=amount,
            reason=data.get('reason', ''),
            advance_type=data.get('advance_type', 'NORMAL'),
            status='PENDING',
            requested_by=actor,
        )

        logger.info(
            "[Advances] Advance created",
            extra={"advance_id": advance.id, "employee_id": employee.id, "amount": amount}
        )
        return advance

    @classmethod
    def get_advance_detail(self, advance_id: UUID) -> SalaryAdvance:
        """ Retrieves full details and configuration of an advance. """
        logger.debug("[Advances] Getting advance detail", extra={"advance_id": advance_id})

        return SalaryAdvance.objects.select_related(
            'employee',
            'requested_by',
            'approved_by',
            'deduction_configuration',
        ).get(id=advance_id)

    @classmethod
    @transaction.atomic
    def update_advance(cls, advance_id: UUID, data: Dict[str, Any], actor=None) -> SalaryAdvance:
        """ Updates a pending advance request. """
        logger.debug("[Advances] Updating advance", extra={"advance_id": advance_id})

        advance = SalaryAdvance.objects.get(id=advance_id)

        # Only PENDING advances can be modified
        if advance.status != 'PENDING':
            logger.warning(
                "[Advances] Cannot update non-pending advance",
                extra={"advance_id": advance_id, "status": advance.status}
            )
            raise ValidationError(f"Can only update PENDING advances (current: {advance.status})")

        # Update allowed fields
        if 'amount' in data:
            amount = Decimal(str(data['amount']))
            if amount <= 0:
                raise ValidationError("Amount must be positive")
            advance.amount = amount

        if 'reason' in data:
            advance.reason = data['reason']

        if 'advance_type' in data:
            advance.advance_type = data['advance_type']

        advance.save()
        logger.info("[Advances] Advance updated", extra={"advance_id": advance_id})
        return advance

    @classmethod
    @transaction.atomic
    def approve_advance(cls, advance_id: UUID, actor=None) -> SalaryAdvance:
        """
        Approve a pending advance request.
        Status: PENDING → APPROVED
        """
        logger.debug("[Advances] Approving advance", extra={"advance_id": advance_id})

        advance = SalaryAdvance.objects.get(id=advance_id)

        if advance.status != 'PENDING':
            logger.warning(
                "[Advances] Cannot approve non-pending advance",
                extra={"advance_id": advance_id, "status": advance.status}
            )
            raise ValidationError(f"Can only approve PENDING advances (current: {advance.status})")

        advance.status = 'APPROVED'
        advance.approved_by = actor
        advance.save()

        logger.info("[Advances] Advance approved", extra={"advance_id": advance_id})
        return advance

    @classmethod
    @transaction.atomic
    def reject_advance(cls, advance_id: UUID, reason: str = '', actor=None) -> SalaryAdvance:
        """
        Reject a pending advance request.
        Status: PENDING → REJECTED
        """
        logger.debug("[Advances] Rejecting advance", extra={"advance_id": advance_id})

        advance = SalaryAdvance.objects.get(id=advance_id)

        if advance.status != 'PENDING':
            logger.warning(
                "[Advances] Cannot reject non-pending advance",
                extra={"advance_id": advance_id, "status": advance.status}
            )
            raise ValidationError(f"Can only reject PENDING advances (current: {advance.status})")

        advance.status = 'REJECTED'
        advance.rejection_reason = reason
        advance.save()

        logger.info("[Advances] Advance rejected", extra={"advance_id": advance_id})
        return advance

    # ===== ADVANCE QUERIES =====

    @classmethod
    def get_active_advances(cls, employee_id: UUID) -> QuerySet:
        """ Retrieves all currently deductible advances for an employee. """
        logger.debug("[Advances] Getting active advances", extra={"employee_id": employee_id})

        return SalaryAdvance.objects.filter(
            employee_id=employee_id,
            status='ACTIVE',
            is_closed=False,
        ).select_related(
            'employee',
            'deduction_configuration',
        ).order_by('deduction_configuration__priority')

    @classmethod
    def get_employee_advance_history(cls, employee_id: UUID) -> QuerySet:
        """ Retrieves the full history of advances for an employee. """
        logger.debug("[Advances] Getting advance history", extra={"employee_id": employee_id})

        return SalaryAdvance.objects.filter(
            employee_id=employee_id
        ).select_related(
            'employee',
            'deduction_configuration',
        ).order_by('-requested_date')

    @classmethod
    def get_advance_balance(cls, advance_id: UUID) -> Dict[str, Any]:
        """ Calculates current balance and repayment progress for an advance. """
        logger.debug("[Advances] Calculating advance balance", extra={"advance_id": advance_id})

        advance = SalaryAdvance.objects.get(id=advance_id)

        remaining = advance.amount - advance.deducted_amount
        progress = int((advance.deducted_amount / advance.amount * 100)) if advance.amount > 0 else 0

        return {
            'advance_id': advance_id,
            'amount': advance.amount,
            'deducted_amount': advance.deducted_amount,
            'remaining_balance': remaining,
            'repayment_progress': progress,
            'is_closed': advance.is_closed,
        }

    # ===== CONFIGURATION CRUD =====

    @classmethod
    @transaction.atomic
    def create_advance_configuration(
        cls,
        advance_id: UUID,
        data: Dict[str, Any],
        actor=None
    ) -> AdvanceDeductionConfiguration:
        """
        Create deduction configuration for an advance.
        
        Defines how the advance will be repaid (4 dimensions):
        1. Base salary (GROSS or NET)
        2. Tax timing (BEFORE_TAX or AFTER_TAX)
        3. Deduction window (ALL_MONTHS or CUSTOM_PERIOD)
        4. Priority order (for multi-advance deduction)
        """
        logger.debug(
            "[Advances] Creating configuration",
            extra={"advance_id": advance_id, "data": data}
        )

        # Validate advance exists
        try:
            advance = SalaryAdvance.objects.get(id=advance_id)
        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            raise ValidationError(f"Advance {advance_id} not found")

        # Create configuration
        config = AdvanceDeductionConfiguration.objects.create(
            advance=advance,
            salary_base=data.get('salary_base', 'GROSS'),
            tax_timing=data.get('tax_timing', 'AFTER_TAX'),
            deduction_window=data.get('deduction_window', 'ALL_MONTHS'),
            priority=data.get('priority', 1),
            deduction_start_date=data.get('deduction_start_date'),
            deduction_end_date=data.get('deduction_end_date'),
        )

        # Update advance status to ACTIVE after configuration
        if advance.status == 'APPROVED':
            advance.status = 'ACTIVE'
            advance.save()

        logger.info(
            "[Advances] Configuration created",
            extra={"advance_id": advance_id, "config_id": config.id}
        )
        return config

    @classmethod
    def get_advance_configuration(cls, advance_id: UUID) -> AdvanceDeductionConfiguration:
        """ Retrieves the repayment configuration for an advance. """
        logger.debug(
            "[Advances] Getting configuration",
            extra={"advance_id": advance_id}
        )

        return AdvanceDeductionConfiguration.objects.select_related(
            'advance'
        ).get(advance_id=advance_id)

    @classmethod
    @transaction.atomic
    def update_advance_configuration(cls, advance_id: UUID, data: Dict[str, Any], actor=None) -> AdvanceDeductionConfiguration:
        """ Updates the repayment configuration for an advance. """
        logger.debug(
            "[Advances] Updating configuration",
            extra={"advance_id": advance_id}
        )

        config = AdvanceDeductionConfiguration.objects.get(advance_id=advance_id)

        # Update allowed fields
        if 'salary_base' in data:
            config.salary_base = data['salary_base']
        if 'tax_timing' in data:
            config.tax_timing = data['tax_timing']
        if 'deduction_window' in data:
            config.deduction_window = data['deduction_window']
        if 'priority' in data:
            config.priority = data['priority']
        if 'deduction_start_date' in data:
            config.deduction_start_date = data['deduction_start_date']
        if 'deduction_end_date' in data:
            config.deduction_end_date = data['deduction_end_date']

        config.save()
        logger.info("[Advances] Configuration updated", extra={"advance_id": advance_id})
        return config

    # ===== REPAYMENT =====

    @classmethod
    def get_repayment_history(cls, advance_id: UUID) -> QuerySet:
        """ Retrieves all repayment transactions for an advance. """
        logger.debug("[Advances] Getting repayment history", extra={"advance_id": advance_id})

        # Verify advance exists
        SalaryAdvance.objects.get(id=advance_id)

        return RepaymentRecord.objects.filter(
            advance_id=advance_id
        ).order_by('-repayment_date')

    @classmethod
    @transaction.atomic
    def record_repayment(cls, advance_id: UUID, amount: Decimal, payslip_id: UUID = None, actor=None) -> RepaymentRecord:
        """ Records a manual or automatic repayment against an advance. """
        logger.debug(
            "[Advances] Recording repayment",
            extra={"advance_id": advance_id, "amount": amount}
        )

        # Validate amount
        if amount <= 0:
            raise ValidationError("Repayment amount must be positive")

        # Get advance
        advance = SalaryAdvance.objects.get(id=advance_id)

        # Create repayment
        repayment = RepaymentRecord.objects.create(
            advance=advance,
            amount=amount,
            payslip_id=payslip_id,
            recorded_by=actor,
        )

        # Update advance total repaid
        advance.deducted_amount += amount
        
        # Check if fully repaid
        if advance.deducted_amount >= advance.amount:
            advance.is_closed = True
            advance.status = 'CLOSED'

        advance.save()

        logger.info(
            "[Advances] Repayment recorded",
            extra={"advance_id": advance_id, "amount": amount, "repayment_id": repayment.id}
        )
        return repayment
