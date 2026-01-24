from datetime            import date
from uuid                import UUID
from django.db.models    import Q
from typing              import List, Dict, Any
from hr.payroll.models   import (
    PayrollAdjustment, 
    EmployeeAdjustment
)


class AdjustmentResolverService:
    """
    Handles the logic of identifying which bonuses and deductions apply to an employee.
    Manages the priority between global mandatory settings and specific employee overrides.
    """

    @classmethod
    def get_applicable_adjustments(cls, employee_id: UUID, reference_date: date) -> List[Dict[str, Any]]:
        """
        Retrieves all active adjustments for an employee at a specific date.
        
        Logic:
        1. Fetch all mandatory global adjustments.
        2. Fetch all specific EmployeeAdjustment records for this employee.
        3. If an EmployeeAdjustment exists for a specific PayrollAdjustment, 
           it takes priority (especially for custom amounts).
        """
        # 1. Fetch Global Mandatory Adjustments
        global_mandatory = PayrollAdjustment.objects.filter(
            is_mandatory=True, 
            is_active=True
        )

        # 2. Fetch Employee-Specific Adjustments active during reference_date
        specific_assignments = EmployeeAdjustment.objects.filter(
            employee_id=employee_id,
            is_active=True,
            start_date__lte=reference_date
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=reference_date)
        ).select_related('adjustment')

        # Dictionary to store final resolved adjustments (Key: Adjustment ID)
        resolved_map = {}

        # First, populate with global mandatory adjustments
        for adj in global_mandatory:
            resolved_map[adj.id] = {
                'source': adj,
                'amount': adj.amount,
                'percentage': adj.percentage,
                'label': adj.name,
                'type': adj.adjustment_type,
                'mode': adj.calculation_mode
            }

        # Second, apply specific assignments (these override or add to global ones)
        for assignment in specific_assignments:
            adj = assignment.adjustment
            resolved_map[adj.id] = {
                'source': adj,
                # Use custom_amount if provided, otherwise fallback to global config
                'amount': assignment.custom_amount if assignment.custom_amount else adj.amount,
                'percentage': adj.percentage,
                'label': adj.name,
                'type': adj.adjustment_type,
                'mode': adj.calculation_mode
            }

        return list(resolved_map.values())

