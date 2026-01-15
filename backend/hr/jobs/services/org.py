import logging
from uuid import UUID
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.shortcuts import get_object_or_404

from hr.jobs.models import Department
from hr.employees.models import Employee
from hr.enums import PositionLevel


logger = logging.getLogger(__name__)


class OrganizationService:
    """
    Service to manage the organizational structure (Departments).
    """

    @transaction.atomic
    def create_department(
        self, 
        name: str, 
        parent_id: Optional[UUID] = None, 
        manager_id: Optional[UUID] = None
    ) -> Department:
        """
        Creates a department and validates hierarchical constraints.
        """
        parent = None
        if parent_id:
            # Verify that the parent department exists
            parent = get_object_or_404(Department, id=parent_id)
            
        # Optional check: A department cannot be its own parent 
        # (Primarily relevant for update operations)

        dept = Department.objects.create(
            name=name,
            parent=parent,
            manager_id=manager_id
        )
        
        logger.info(f"Department '{name}' created with ID {dept.id}")
        return dept

    def get_department_tree(self, parent: Optional[Department] = None) -> List[Dict[str, Any]]:
        """
        Returns a recursive tree of departments for organizational visualization.
        """
        # Use select_related to prevent N+1 queries on department managers
        departments = Department.objects.filter(parent=parent).select_related('manager')
        
        tree = []
        for dept in departments:
            tree.append({
                "id": str(dept.id), # Convert UUID to string for API JSON compatibility
                "name": dept.name,
                "manager": dept.manager.full_name if dept.manager else None,
                "sub_departments": self.get_department_tree(parent=dept) # Recursive call
            })
        return tree

    @transaction.atomic
    def transfer_department_manager(self, department_id: UUID, new_manager_id: UUID) -> Department:
        """
        Updates the manager of a department and ensures the new manager 
        has the appropriate seniority level.
        """
        dept = get_object_or_404(Department, id=department_id)
        new_manager = get_object_or_404(Employee, id=new_manager_id)

        # Business Logic: A department manager should ideally hold at least a 'MANAGER' level.
        # Access current role via the EmployeePositionHistory model.
        current_role = new_manager.position_history.filter(is_current=True).first()
        
        if current_role and current_role.position.level not in [
            PositionLevel.MANAGER, 
            PositionLevel.DIRECTOR, 
            PositionLevel.EXECUTIVE
        ]:
            logger.warning(
                f"Assigning manager '{new_manager.full_name}' who has a lower seniority level "
                f"({current_role.position.level})."
            )

        dept.manager = new_manager
        dept.save()
        
        logger.info(f"Leadership for department '{dept.name}' transferred to {new_manager.full_name}")
        return dept

