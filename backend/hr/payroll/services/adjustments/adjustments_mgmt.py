import logging
from uuid    import UUID
from decimal import Decimal
from datetime  import date
from django.db import transaction
from django.db.models import Q
from django.core.exceptions import ValidationError

from hr.payroll.models import PayrollAdjustment, ContractAdjustment, EmployeeContract
from hr.payroll.enums  import CalculationMode
from hr.payroll.services.contracts import EmployeeContractService


logger = logging.getLogger(__name__)


class AdjustmentManagementService:
    """ Manages life-cycle and assignment of payroll bonuses and deductions.

    Les éléments de paie sont rattachés au *contrat* (ContractAdjustment),
    conformément au métamodèle : `Contrat de travail ──1──>* Élément de paie`.
    Les méthodes « par employé » conservées ci-dessous résolvent le contrat
    actif à la date concernée (point d'entrée pratique pour le calcul des
    bulletins et les affichages fiche employé).
    """

    # ===== ADJUSTMENT TYPE MANAGEMENT =====

    @classmethod
    def get_adjustment_type(cls, adjustment_id: UUID) -> PayrollAdjustment:
        """ Retrieves a specific adjustment type configuration. """
        logger.debug("[AdjustmentService] Getting adjustment type", extra={"adjustment_id": adjustment_id})
        return PayrollAdjustment.objects.get(id=adjustment_id)

    @classmethod
    @transaction.atomic
    def create_adjustment_type(cls, data: dict, actor=None) -> PayrollAdjustment:
        """ Creates a new adjustment template. """
        logger.info(
            "[AdjustmentService] Creating adjustment type",
            extra={"adjustment_name": data.get('name'), "type": data.get('adjustment_type')},
        )

        # Validation
        if not data.get('name'):
            raise ValidationError("Adjustment name is required")

        if not data.get('adjustment_type'):
            raise ValidationError("Adjustment type is required")

        # Create adjustment
        adjustment = PayrollAdjustment.objects.create(**data)
        logger.info(
            "[AdjustmentService] Adjustment type created",
            extra={"adjustment_id": adjustment.id, "adjustment_name": adjustment.name},
        )

        return adjustment

    @classmethod
    @transaction.atomic
    def update_adjustment_type(cls, adjustment_id: UUID, data: dict, actor=None) -> PayrollAdjustment:
        """ Updates an existing adjustment template. """
        logger.info("[AdjustmentService] Updating adjustment type", extra={"adjustment_id": adjustment_id})

        adjustment = PayrollAdjustment.objects.get(id=adjustment_id)

        # Update allowed fields
        allowed_fields = ['name', 'adjustment_type', 'calculation_mode', 'amount', 'percentage', 'is_mandatory', 'is_active', 'is_taxable', 'is_cnss_subject', 'formula_description']
        for field in allowed_fields:
            if field in data:
                setattr(adjustment, field, data[field])

        adjustment.save()
        logger.info("[AdjustmentService] Adjustment type updated", extra={"adjustment_id": adjustment_id})

        return adjustment

    @classmethod
    @transaction.atomic
    def delete_adjustment_type(cls, adjustment_id: UUID, actor=None) -> None:
        """ Deletes an adjustment template if not currently assigned to any contract. """
        logger.info("[AdjustmentService] Deleting adjustment type", extra={"adjustment_id": adjustment_id})

        adjustment = PayrollAdjustment.objects.get(id=adjustment_id)

        # Check if any contract adjustments use this type
        contract_count = ContractAdjustment.objects.filter(adjustment=adjustment).count()
        if contract_count > 0:
            raise ValidationError(f"Cannot delete: {contract_count} contract adjustments use this type")

        adjustment_name = adjustment.name
        adjustment.delete()
        logger.info("[AdjustmentService] Adjustment type deleted", extra={"adjustment_name": adjustment_name})

    # ===== CONTRACT ADJUSTMENT MANAGEMENT =====

    @classmethod
    def get_contract_adjustments(cls, contract_id: UUID) -> list[ContractAdjustment]:
        """ Retrieves all adjustments assigned to a specific contract. """
        logger.debug("[AdjustmentService] Getting contract adjustments", extra={"contract_id": contract_id})

        return list(ContractAdjustment.objects.filter(
            contract_id=contract_id
        ).select_related('adjustment').order_by('-start_date'))

    @classmethod
    def get_employee_adjustments(cls, employee_id: UUID) -> list[ContractAdjustment]:
        """ Retrieves all adjustments of the currently active contract of an employee.

        Point d'entrée par employé : résout le contrat actif (aujour d'hui),
        puis retourne ses éléments de paie. Si aucun contrat actif, liste vide.
        """
        logger.debug("[AdjustmentService] Getting employee adjustments", extra={"employee_id": employee_id})

        try:
            contract = EmployeeContractService.get_active_contract(employee_id)
        except EmployeeContract.DoesNotExist:
            return []

        return cls.get_contract_adjustments(contract.id)

    @classmethod
    def get_contract_adjustment(cls, adjustment_id: UUID) -> ContractAdjustment:
        """ Retrieves a specific contract-adjustment assignment by ID. """
        logger.debug("[AdjustmentService] Getting contract adjustment", extra={"adjustment_id": adjustment_id})

        return ContractAdjustment.objects.select_related('adjustment', 'contract').get(id=adjustment_id)

    @classmethod
    def get_employee_adjustment(cls, adjustment_id: UUID) -> ContractAdjustment:
        """ Alias rétro-compatible : délègue à get_contract_adjustment. """
        return cls.get_contract_adjustment(adjustment_id)

    @classmethod
    @transaction.atomic
    def create_contract_adjustment(cls, data: dict, actor=None) -> ContractAdjustment:
        """ Assigns a payroll adjustment to a specific contract.

        Le champ `employee` est dénormalisé depuis le contrat (requêtes par
        employé et calcul des bulletins) — l'appelant fournit `contract`
        (UUID) ; `employee` est dérivé automatiquement.
        """
        logger.info(
            "[AdjustmentService] Creating contract adjustment",
            extra={"contract_id": data.get('contract'), "adjustment_id": data.get('adjustment')},
        )

        # Validate contract exists
        contract_id = data.get('contract')
        if not contract_id:
            raise ValidationError("Contract is required")

        try:
            contract = EmployeeContractService.get_contract_by_id(contract_id)
        except EmployeeContract.DoesNotExist:
            raise ValidationError("Contract not found")

        # Validate adjustment exists
        adjustment_id = data.get('adjustment')
        if not adjustment_id:
            raise ValidationError("Adjustment type is required")

        try:
            PayrollAdjustment.objects.get(id=adjustment_id)
        except PayrollAdjustment.DoesNotExist:
            raise ValidationError("Adjustment type not found")

        # Validate dates if provided
        start_date = data.get('start_date')
        end_date = data.get('end_date')

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before end date")

        # Dénormalisation : l'employé est dérivé du contrat
        create_data = dict(data)
        create_data.pop('contract', None)
        create_data['contract'] = contract
        create_data['employee'] = contract.employee

        # Create contract adjustment
        adjustment = ContractAdjustment.objects.create(**create_data)
        logger.info(
            "[AdjustmentService] Contract adjustment created",
            extra={"adjustment_id": adjustment.id, "contract_id": contract_id, "employee_id": contract.employee_id},
        )

        return adjustment

    @classmethod
    def create_employee_adjustment(cls, data: dict, actor=None) -> ContractAdjustment:
        """ Rétro-compatible : si un `employee` est fourni, résout son contrat
        actif avant de déléguer à create_contract_adjustment. """
        if data.get('employee') and not data.get('contract'):
            employee_id = data.pop('employee')
            try:
                contract = EmployeeContractService.get_active_contract(employee_id)
            except EmployeeContract.DoesNotExist:
                raise ValidationError("No active contract found for this employee")
            data['contract'] = contract.id
        return cls.create_contract_adjustment(data, actor=actor)

    @classmethod
    @transaction.atomic
    def update_contract_adjustment(cls, adjustment_id: UUID, data: dict, actor=None) -> ContractAdjustment:
        """ Updates an existing contract-adjustment assignment. """
        logger.info("[AdjustmentService] Updating contract adjustment", extra={"adjustment_id": adjustment_id})

        adjustment = ContractAdjustment.objects.get(id=adjustment_id)

        # Validate dates if provided
        start_date = data.get('start_date') or adjustment.start_date
        end_date = data.get('end_date') or adjustment.end_date

        if start_date and end_date:
            if start_date > end_date:
                raise ValidationError("Start date must be before end date")

        # Update allowed fields (custom_percentage inclus — négociation au contrat)
        allowed_fields = ['start_date', 'end_date', 'custom_amount', 'custom_percentage', 'is_active']
        for field in allowed_fields:
            if field in data:
                setattr(adjustment, field, data[field])

        adjustment.save()
        logger.info("[AdjustmentService] Contract adjustment updated", extra={"adjustment_id": adjustment_id})

        return adjustment

    @classmethod
    def update_employee_adjustment(cls, adjustment_id: UUID, data: dict, actor=None) -> ContractAdjustment:
        """ Alias rétro-compatible : délègue à update_contract_adjustment. """
        return cls.update_contract_adjustment(adjustment_id, data, actor=actor)

    @classmethod
    @transaction.atomic
    def delete_contract_adjustment(cls, adjustment_id: UUID, actor=None) -> None:
        """ Removes an adjustment assignment from a contract. """
        logger.info("[AdjustmentService] Deleting contract adjustment", extra={"adjustment_id": adjustment_id})

        adjustment = ContractAdjustment.objects.get(id=adjustment_id)

        contract_id = adjustment.contract_id
        adj_type = adjustment.adjustment_id

        adjustment.delete()
        logger.info(
            "[AdjustmentService] Contract adjustment deleted",
            extra={"contract_id": contract_id, "adjustment_id": adj_type},
        )

    @classmethod
    def delete_employee_adjustment(cls, adjustment_id: UUID, actor=None) -> None:
        """ Alias rétro-compatible : délègue à delete_contract_adjustment. """
        return cls.delete_contract_adjustment(adjustment_id, actor=actor)

    # ===== ACTIVE ADJUSTMENTS FOR PAYROLL =====

    @classmethod
    def get_active_adjustments_for_contract(cls, contract_id: UUID, payroll_date: date) -> list[ContractAdjustment]:
        """ Retrieves all adjustments active for a contract on a specific payroll date. """
        logger.debug(
            "[AdjustmentService] Getting active adjustments for contract",
            extra={"contract_id": contract_id, "payroll_date": payroll_date},
        )

        return list(ContractAdjustment.objects.filter(
            Q(contract_id=contract_id) &
            Q(is_active=True) &
            Q(start_date__lte=payroll_date) &
            (Q(end_date__isnull=True) | Q(end_date__gte=payroll_date))
        ).select_related('adjustment').order_by('created_at'))

    @classmethod
    def get_active_adjustments_for_employee(cls, employee_id: UUID, payroll_date: date) -> list[ContractAdjustment]:
        """ Retrieves all adjustments active for an employee on a specific payroll date.

        Résout le contrat actif à la date (via EmployeeContractService) puis
        délègue à get_active_adjustments_for_contract.
        """
        logger.debug(
            "[AdjustmentService] Getting active adjustments for payroll",
            extra={"employee_id": employee_id, "payroll_date": payroll_date},
        )

        try:
            contract = EmployeeContractService.get_contract_on_date(employee_id, payroll_date)
        except EmployeeContract.DoesNotExist:
            return []

        return cls.get_active_adjustments_for_contract(contract.id, payroll_date)

    @classmethod
    def calculate_adjustment_amount(cls, contract_adjustment: ContractAdjustment, gross_salary: Decimal | None = None) -> Decimal:
        """ Calculates the monetary value of an adjustment based on its configuration.

        Priorité : custom_amount du contrat → custom_percentage du contrat →
        valeurs standard du catalogue (PayrollAdjustment).
        Conforme au mode de calcul du catalogue (CalculationMode).
        """
        # If custom amount is set, use it (négociation au contrat)
        if contract_adjustment.custom_amount is not None:
            return contract_adjustment.custom_amount

        # Otherwise, calculate based on adjustment type
        adjustment = contract_adjustment.adjustment

        if adjustment.calculation_mode == CalculationMode.FIXED and adjustment.amount:
            return adjustment.amount

        if adjustment.calculation_mode == CalculationMode.PERCENTAGE and gross_salary:
            percentage = (
                contract_adjustment.custom_percentage
                if contract_adjustment.custom_percentage is not None
                else adjustment.percentage
            )
            if percentage is not None:
                return (gross_salary * Decimal(str(percentage)) / Decimal('100')).quantize(Decimal('0.01'))

        return Decimal('0.00')

