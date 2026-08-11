from datetime import date
from uuid import UUID
from typing import List, Dict, Any
from django.db.models import Q
from hr.payroll.models import (
    PayrollAdjustment,
    ContractAdjustment,
    EmployeeContract,
)
from hr.payroll.services.contracts import EmployeeContractService


class AdjustmentResolverService:
    """ Identifies bonuses and deductions applicable to an employee contract. """

    @classmethod
    def get_applicable_adjustments(cls, employee_id: UUID, reference_date: date) -> List[Dict[str, Any]]:
        """ Retrieves active mandatory and contract-specific adjustments for a specific date.

        Conforme au métamodèle : les éléments de paie sont attachés au *contrat*
        (ContractAdjustment), pas directement à l'employé. Le contrat actif à la
        date de référence est résolu, puis ses éléments récurrents sont combinés
        avec les règles globales obligatoires (is_mandatory).
        """
        # 1. Retrieval of mandatory global adjustments (e.g., Housing 25%, Transport)
        global_mandatory = PayrollAdjustment.objects.filter(
            is_mandatory=True,
            is_active=True
        )

        # 2. Résolution du contrat actif à la date de référence.
        #    Le contrat est la source de vérité pour les éléments récurrents.
        contract = None
        try:
            contract = EmployeeContractService.get_contract_on_date(
                employee_id, reference_date
            )
        except EmployeeContract.DoesNotExist:
            # Pas de contrat actif sur la période : seuls les ajustements
            # globaux obligatoires s'appliquent (l'employé n'est pas payé).
            contract = None

        # 3. Retrieval of contract-specific assignments active at the reference date
        if contract is not None:
            specific_assignments = ContractAdjustment.objects.filter(
                contract_id=contract.id,
                is_active=True,
                start_date__lte=reference_date
            ).filter(
                Q(end_date__isnull=True) | Q(end_date__gte=reference_date)
            ).select_related('adjustment')
        else:
            specific_assignments = ContractAdjustment.objects.none()

        # Dictionary to resolve conflicts (Key: Adjustment ID)
        resolved_map = {}

        # Step A: Populate with mandatory global rules
        for adj in global_mandatory:
            resolved_map[adj.id] = {
                'id': adj.id,
                'label': adj.name,
                'type': adj.adjustment_type,
                'mode': adj.calculation_mode,
                'amount': adj.amount,
                'percentage': adj.percentage,
                'is_mandatory': True,
                'is_taxable': adj.is_taxable,
                'is_cnss_subject': adj.is_cnss_subject
            }

        # Step B: Apply contract-specific overrides
        # If the contract has a custom amount or percentage, it overrides the global rule.
        for assignment in specific_assignments:
            adj = assignment.adjustment

            resolved_map[adj.id] = {
                'id': adj.id,
                'label': adj.name,
                'type': adj.adjustment_type,
                'mode': adj.calculation_mode,

                # Priority to custom contract amount
                'amount': assignment.custom_amount if assignment.custom_amount is not None else adj.amount,

                # Priority to custom contract percentage (négocié au contrat)
                'percentage': assignment.custom_percentage if assignment.custom_percentage is not None else adj.percentage,

                'is_mandatory': adj.is_mandatory,
                'is_taxable': adj.is_taxable,
                'is_cnss_subject': adj.is_cnss_subject
            }

        return list(resolved_map.values())

