"""
Utility functions for employee-related operations.
"""
from typing import Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from hr.employees.models import Employee


def get_employee_full_name(employee: Optional["Employee"]) -> Optional[str]:
    """
    Construit le nom complet d'un employé à partir de ses prénoms et nom.
    
    Args:
        employee: Instance de Employee ou None
        
    Returns:
        Nom complet formaté ou None si l'employé est None
    """
    if not employee:
        return None
    parts = [employee.first_name]
    if employee.middle_name:
        parts.append(employee.middle_name)
    parts.append(employee.last_name)
    return " ".join(parts)
