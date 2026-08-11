import logging
from decimal import Decimal, InvalidOperation
from typing import Dict, Any
from uuid import UUID

from django.db import transaction
from django.core.exceptions import ValidationError
from django.db.models import QuerySet
from django.utils import timezone

from hr.payroll.models import (
    SalaryAdvance,
    AdvanceDeductionConfiguration,
    RepaymentRecord,
)
from hr.payroll.enums import (
    AdvanceStatus,
    AdvanceRiskLevel,
    AdvanceDeductionBase,
    AdvanceDeductionWindow,
)
from hr.employees.models import Employee
from hr.enums import Currency
from hr.payroll.services.integration.exchange import ExchangeRateService


logger = logging.getLogger(__name__)


class AdvanceManagementService:
    """ Manages salary advances, approvals, and repayment configurations. """

    # ===== RISK ASSESSMENT =====

    @classmethod
    def assess_risk_level(
        cls,
        amount: Decimal,
        repayment_percentage: Decimal,
        base_salary: Decimal | None = None,
    ) -> str:
        """
        Évalue le risque de non-remboursement d'une avance.

        Règles RDC alignées sur l'UI :
        - HIGH  : prélèvement > 50 % du salaire net estimé, ou montant > 50 % du brut
        - MEDIUM: prélèvement > 30 % du net, ou montant > 30 % du brut
        - LOW   : sinon
        """
        amount = Decimal(str(amount or 0))
        repayment_percentage = Decimal(str(repayment_percentage or 0))

        # Salaire net estimé (~80 % du brut) si le brut n'est pas fourni
        net_estimate = (base_salary * Decimal('0.8')) if base_salary else Decimal('0')
        deduction = amount * (repayment_percentage / Decimal('100')) if repayment_percentage > 0 else Decimal('0')

        if net_estimate > 0:
            ratio = (deduction / net_estimate) * Decimal('100')
            if ratio > Decimal('50') or (base_salary and amount > base_salary * Decimal('0.5')):
                return AdvanceRiskLevel.HIGH
            if ratio > Decimal('30') or (base_salary and amount > base_salary * Decimal('0.3')):
                return AdvanceRiskLevel.MEDIUM
        elif base_salary:
            if amount > base_salary * Decimal('0.5'):
                return AdvanceRiskLevel.HIGH
            if amount > base_salary * Decimal('0.3'):
                return AdvanceRiskLevel.MEDIUM

        return AdvanceRiskLevel.LOW

    # ===== ADVANCE CRUD =====

    @classmethod
    @transaction.atomic
    def create_advance(cls, data: Dict[str, Any], actor=None) -> SalaryAdvance:
        """ Creates a new salary advance request (status PENDING). """
        logger.debug("[Advances] Creating advance", extra={"data": data, "actor": actor})

        employee_id = data.get('employee_id') or data.get('employee')
        try:
            employee = Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            logger.warning(
                "[Advances] Employee not found",
                extra={"employee_id": employee_id}
            )
            raise ValidationError(f"Employee {employee_id} not found")

        amount = Decimal(str(data.get('amount', 0)))
        if amount <= 0:
            logger.warning("[Advances] Invalid amount", extra={"amount": amount})
            raise ValidationError("Advance amount must be positive")

        # Devise de l'avance (défaut : devise du contrat actif)
        contract = employee.contracts.filter(is_active=True).order_by('-created_at').first()
        contract_currency = getattr(contract, 'currency', None) or Currency.CDF
        advance_currency = str(data.get('currency') or contract_currency or Currency.CDF)
        advance_currency = advance_currency.upper()

        # Taux figé à la création (audit financier, pattern payslips)
        exchange_rate_used = None
        if advance_currency == Currency.USD:
            exchange_rate_used = ExchangeRateService.get_exchange_rate(Currency.USD, Currency.CDF)

        # Règle RDC : plafond de 50 % du salaire de base (sécurité financière)
        # Le salaire est dans la devise du contrat → on convertit le montant avant comparaison
        base_salary = getattr(contract, 'base_salary', None) or None
        if base_salary and exchange_rate_used is not None and advance_currency != contract_currency:
            amount_in_salary_currency = (amount * exchange_rate_used).quantize(Decimal('0.01'))
        else:
            amount_in_salary_currency = amount

        if base_salary and amount_in_salary_currency > base_salary * Decimal('0.5'):
            logger.warning(
                "[Advances] Amount exceeds 50% of base salary",
                extra={"amount": amount_in_salary_currency, "base_salary": base_salary}
            )
            raise ValidationError("Advance amount cannot exceed 50% of the employee's base salary")

        # Le taux de remboursement est défini par la RH à l'approbation ;
        # on garde un défaut sûr si le demandeur n'en fournit pas.
        raw_percentage = data.get('repayment_percentage', 20)
        try:
            raw_decimal = Decimal(str(raw_percentage))
        except (TypeError, ValueError, InvalidOperation):
            raw_decimal = Decimal('0')
        # Ignore 0 ou négatif : seul un % strictement positif est accepté.
        # Un % invalide retombe sur le défaut 20 (la RH fixera la valeur finale à l'approbation).
        if raw_decimal <= 0:
            raw_decimal = Decimal('20')
        repayment_percentage = raw_decimal
        risk_level = cls.assess_risk_level(amount_in_salary_currency, repayment_percentage, base_salary)

        advance = SalaryAdvance.objects.create(
            employee=employee,
            amount=amount,
            reason=data.get('reason', ''),
            advance_type=data.get('advance_type', 'NORMAL'),
            # Un brouillon reste en DRAFT tant que l'employé ne l'a pas soumis
            status=AdvanceStatus.PENDING if data.get('submit', False) else AdvanceStatus.DRAFT,
            repayment_percentage=repayment_percentage,
            # Config de déduction : défauts sûrs si le demandeur n'en fournit pas
            # (les clés None du schéma ne doivent pas écraser les défauts).
            salary_base_for_deduction=data.get('salary_base_for_deduction') or AdvanceDeductionBase.NET,
            tax_timing=data.get('tax_timing') or 'AFTER_TAX',
            deduction_window=data.get('deduction_window') or AdvanceDeductionWindow.ALL_MONTHS,
            deduction_start_date=data.get('deduction_start_date') or None,
            deduction_end_date=data.get('deduction_end_date') or None,
            currency=advance_currency,
            exchange_rate_used=exchange_rate_used,
            risk_level=risk_level,
            requested_by=actor,
        )

        logger.info(
            "[Advances] Advance created",
            extra={"advance_id": advance.id, "employee_id": employee.id, "amount": amount, "risk_level": risk_level}
        )
        return advance

    @classmethod
    def get_advance_detail(cls, advance_id: UUID) -> SalaryAdvance:
        """ Retrieves full details and configuration of an advance. """
        logger.debug("[Advances] Getting advance detail", extra={"advance_id": advance_id})

        return SalaryAdvance.objects.select_related(
            'employee',
            'requested_by',
            'approved_by',
        ).prefetch_related(
            'deduction_configs',
        ).get(id=advance_id)

    @classmethod
    @transaction.atomic
    def update_advance(cls, advance_id: UUID, data: Dict[str, Any], actor=None) -> SalaryAdvance:
        """ Updates a draft or pending advance request. """
        logger.debug("[Advances] Updating advance", extra={"advance_id": advance_id})

        advance = SalaryAdvance.objects.get(id=advance_id)

        # Only DRAFT or PENDING advances can be modified
        if advance.status not in (AdvanceStatus.DRAFT, AdvanceStatus.PENDING):
            logger.warning(
                "[Advances] Cannot update non-draft/non-pending advance",
                extra={"advance_id": advance_id, "status": advance.status}
            )
            raise ValidationError(f"Can only update DRAFT or PENDING advances (current: {advance.status})")

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

        if 'repayment_percentage' in data and data['repayment_percentage'] is not None:
            raw = data['repayment_percentage']
            if str(raw).strip() != '':
                advance.repayment_percentage = Decimal(str(raw))

        # Re-évalue le risque après modification du montant / du taux
        base_salary = advance.employee.base_salary if hasattr(advance.employee, 'base_salary') else None
        advance.risk_level = cls.assess_risk_level(advance.amount, advance.repayment_percentage, base_salary)

        advance.save()
        logger.info("[Advances] Advance updated", extra={"advance_id": advance_id})
        return advance

    @classmethod
    @transaction.atomic
    def submit_advance(cls, advance_id: UUID, actor=None) -> SalaryAdvance:
        """
        Submit a draft advance request.
        Status: DRAFT → PENDING (enters the HR approval queue).
        """
        logger.debug("[Advances] Submitting advance", extra={"advance_id": advance_id})

        advance = SalaryAdvance.objects.get(id=advance_id)

        if advance.status != AdvanceStatus.DRAFT:
            logger.warning(
                "[Advances] Cannot submit non-draft advance",
                extra={"advance_id": advance_id, "status": advance.status}
            )
            raise ValidationError(f"Can only submit DRAFT advances (current: {advance.status})")

        advance.status = AdvanceStatus.PENDING
        advance.save()

        logger.info("[Advances] Advance submitted", extra={"advance_id": advance_id})
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

        if advance.status != AdvanceStatus.PENDING:
            logger.warning(
                "[Advances] Cannot approve non-pending advance",
                extra={"advance_id": advance_id, "status": advance.status}
            )
            raise ValidationError(f"Can only approve PENDING advances (current: {advance.status})")

        advance.status = AdvanceStatus.APPROVED
        advance.approved_by = actor
        advance.approved_date = timezone.now()
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

        if advance.status != AdvanceStatus.PENDING:
            logger.warning(
                "[Advances] Cannot reject non-pending advance",
                extra={"advance_id": advance_id, "status": advance.status}
            )
            raise ValidationError(f"Can only reject PENDING advances (current: {advance.status})")

        advance.status = AdvanceStatus.REJECTED
        advance.rejection_reason = reason
        advance.rejected_by = actor
        advance.rejected_date = timezone.now()
        advance.save()

        logger.info("[Advances] Advance rejected", extra={"advance_id": advance_id})
        return advance

    @classmethod
    @transaction.atomic
    def activate_advance(cls, advance_id: UUID, actor=None) -> SalaryAdvance:
        """
        Move an approved advance into the ACTIVE (deductible) state.
        Status: APPROVED → ACTIVE
        """
        logger.debug("[Advances] Activating advance", extra={"advance_id": advance_id})

        advance = SalaryAdvance.objects.get(id=advance_id)

        if advance.status != AdvanceStatus.APPROVED:
            logger.warning(
                "[Advances] Cannot activate non-approved advance",
                extra={"advance_id": advance_id, "status": advance.status}
            )
            raise ValidationError(f"Can only activate APPROVED advances (current: {advance.status})")

        advance.status = AdvanceStatus.ACTIVE
        advance.save()

        logger.info("[Advances] Advance activated", extra={"advance_id": advance_id})
        return advance

    # ===== ADVANCE QUERIES =====

    @classmethod
    def get_active_advances(cls, employee_id: UUID) -> QuerySet:
        """ Retrieves all currently deductible advances for an employee. """
        logger.debug("[Advances] Getting active advances", extra={"employee_id": employee_id})

        return SalaryAdvance.objects.filter(
            employee_id=employee_id,
            status=AdvanceStatus.ACTIVE,
            is_closed=False,
        ).select_related(
            'employee',
        ).prefetch_related(
            'deduction_configs',
            'employee__position_history__position',
            'employee__position_history__org_unit',
        ).order_by('deduction_configs__priority_order')

    @classmethod
    def get_employee_advance_history(cls, employee_id: UUID) -> QuerySet:
        """ Retrieves the full history of advances for an employee. """
        logger.debug("[Advances] Getting advance history", extra={"employee_id": employee_id})

        return SalaryAdvance.objects.filter(
            employee_id=employee_id
        ).select_related(
            'employee',
        ).prefetch_related(
            'deduction_configs',
            'employee__position_history__position',
            'employee__position_history__org_unit',
        ).order_by('-requested_date')

    @classmethod
    def get_advance_balance(cls, advance_id: UUID) -> Dict[str, Any]:
        """ Calculates current balance and repayment progress for an advance. """
        logger.debug("[Advances] Calculating advance balance", extra={"advance_id": advance_id})

        advance = SalaryAdvance.objects.get(id=advance_id)

        remaining = advance.amount - advance.deducted_amount
        progress = int((advance.deducted_amount / advance.amount * 100)) if advance.amount > 0 else 0

        # Champs aligns sur AdvanceBalanceOut
        return {
            'advance_id': advance_id,
            'total_amount': advance.amount,
            'total_repaid': advance.deducted_amount,
            'remaining_balance': remaining,
            'repayment_progress': progress,
            'estimated_repayment_date': None,
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
        config, _ = AdvanceDeductionConfiguration.objects.get_or_create(
            advance=advance,
            employee=advance.employee,
            defaults={
                'priority_order': data.get('priority_order', data.get('priority', 1)),
                'is_active': data.get('is_active', True),
            }
        )

        # --- Deduction parameters on the advance ---
        if data.get('repayment_percentage') is not None:
            advance.repayment_percentage = Decimal(str(data['repayment_percentage']))
        if data.get('salary_base_for_deduction') is not None:
            advance.salary_base_for_deduction = data['salary_base_for_deduction']
        if data.get('tax_timing') is not None:
            advance.tax_timing = data['tax_timing']
        if data.get('deduction_window') is not None:
            advance.deduction_window = data['deduction_window']
        if data.get('deduction_start_date') is not None:
            advance.deduction_start_date = data['deduction_start_date']
        if data.get('deduction_end_date') is not None:
            advance.deduction_end_date = data['deduction_end_date']
        advance.save()

        # Update advance status to ACTIVE after configuration
        if advance.status == AdvanceStatus.APPROVED:
            advance.status = AdvanceStatus.ACTIVE
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
        """
        Updates the repayment configuration for an advance.

        This is the SINGLE entry point for the deduction parameters at
        approval time. Deduction fields are persisted on the SalaryAdvance
        (repayment_percentage, base, timing, window, dates), while priority
        and activation live on the AdvanceDeductionConfiguration.
        """
        logger.debug(
            "[Advances] Updating configuration",
            extra={"advance_id": advance_id, "data": data}
        )

        try:
            advance = SalaryAdvance.objects.get(id=advance_id)
        except SalaryAdvance.DoesNotExist:
            logger.warning("[Advances] Advance not found", extra={"advance_id": advance_id})
            raise ValidationError(f"Advance {advance_id} not found")

        config, _ = AdvanceDeductionConfiguration.objects.get_or_create(
            employee=advance.employee,
            advance=advance,
            defaults={'priority_order': data.get('priority_order', 1), 'is_active': data.get('is_active', True)}
        )

        # --- Deduction parameters on the advance ---
        if 'repayment_percentage' in data and data['repayment_percentage'] is not None:
            advance.repayment_percentage = Decimal(str(data['repayment_percentage']))
        if 'salary_base_for_deduction' in data and data['salary_base_for_deduction'] is not None:
            advance.salary_base_for_deduction = data['salary_base_for_deduction']
        if 'tax_timing' in data and data['tax_timing'] is not None:
            advance.tax_timing = data['tax_timing']
        if 'deduction_window' in data and data['deduction_window'] is not None:
            advance.deduction_window = data['deduction_window']
        if 'deduction_start_date' in data and data['deduction_start_date'] is not None:
            advance.deduction_start_date = data['deduction_start_date']
        if 'deduction_end_date' in data and data['deduction_end_date'] is not None:
            advance.deduction_end_date = data['deduction_end_date']
        advance.save()

        # Move an approved advance into the ACTIVE (deductible) state after config
        if advance.status == AdvanceStatus.APPROVED:
            advance.status = AdvanceStatus.ACTIVE
            advance.save()

        # --- Config-level fields (priority, activation) ---
        if 'priority_order' in data and data['priority_order'] is not None:
            config.priority_order = data['priority_order']
        if 'is_active' in data and data['is_active'] is not None:
            config.is_active = data['is_active']

        config.save()
        logger.info("[Advances] Configuration updated", extra={"advance_id": advance_id})
        return config

    @classmethod
    def list_all_advance_configurations(cls) -> QuerySet:
        """ Lists all advance deduction configurations. """
        logger.debug("[Advances] Listing all deduction configurations")

        return AdvanceDeductionConfiguration.objects.select_related(
            'advance',
            'employee',
        ).all()

    # ===== REPAYMENT =====

    @classmethod
    def get_repayment_history(cls, advance_id: UUID) -> QuerySet:
        """ Retrieves all repayment transactions for an advance. """
        logger.debug("[Advances] Getting repayment history", extra={"advance_id": advance_id})

        # Verify advance exists
        SalaryAdvance.objects.get(id=advance_id)

        return RepaymentRecord.objects.filter(
            salary_advance_id=advance_id
        ).order_by('-repayment_date')

    @classmethod
    @transaction.atomic
    def record_repayment(cls, advance_id: UUID, amount: Decimal, payslip_id: UUID | None = None, actor=None) -> RepaymentRecord:
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
            salary_advance=advance,
            amount=amount,
            payslip_id=payslip_id,
            created_by=actor,
        )

        # Update advance total repaid
        advance.deducted_amount += amount

        # Check if fully repaid
        if advance.deducted_amount >= advance.amount:
            advance.is_closed = True
            advance.status = AdvanceStatus.CLOSED

        advance.save()

        logger.info(
            "[Advances] Repayment recorded",
            extra={"advance_id": advance_id, "amount": amount, "repayment_id": repayment.id}
        )
        return repayment
