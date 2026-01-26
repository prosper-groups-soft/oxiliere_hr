from datetime import date
from uuid import UUID
from typing import List, Dict, Any
from django.db.models import Q
from hr.payroll.models import (
    PayrollAdjustment, 
    EmployeeAdjustment
)

class AdjustmentResolverService:
    """
    Identifies bonuses and deductions applicable to an employee in DRC.
    Manages priority between mandatory global rules and employee-specific overrides.
    """

    @classmethod
    def get_applicable_adjustments(cls, employee_id: UUID, reference_date: date) -> List[Dict[str, Any]]:
        """
        Retrieves all active adjustments for a given date.
        
        Priority:
        1. Mandatory adjustments are included by default.
        2. Employee-specific adjustments override global values or add new bonuses/deductions.
        """
        # 1. Retrieval of mandatory global adjustments (e.g., Housing 25%, Transport)
        global_mandatory = PayrollAdjustment.objects.filter(
            is_mandatory=True, 
            is_active=True
        )

        # 2. Retrieval of employee-specific assignments active at the reference date
        specific_assignments = EmployeeAdjustment.objects.filter(
            employee_id=employee_id,
            is_active=True,
            start_date__lte=reference_date
        ).filter(
            Q(end_date__isnull=True) | Q(end_date__gte=reference_date)
        ).select_related('adjustment')

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
                'is_mandatory': True
            }

        # Step B: Apply employee-specific overrides
        # If the employee has a custom amount or percentage, it overrides the global rule.
        for assignment in specific_assignments:
            adj = assignment.adjustment
            
            resolved_map[adj.id] = {
                'id': adj.id,
                'label': adj.name,
                'type': adj.adjustment_type,
                'mode': adj.calculation_mode,
                
                # Priority to custom employee amount
                'amount': assignment.custom_amount if assignment.custom_amount is not None else adj.amount,
                
                # Priority to custom employee percentage (New in 2026)
                'percentage': assignment.custom_percentage if assignment.custom_percentage is not None else adj.percentage, 
                
                'is_mandatory': adj.is_mandatory
            }

        return list(resolved_map.values())

