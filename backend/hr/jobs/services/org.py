import logging
from uuid import UUID
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.shortcuts import get_object_or_404

from hr.jobs.models import Department
from hr.employees.models import Employee
from hr.jobs.enums import PositionLevel


logger = logging.getLogger(__name__)


class OrganizationService:
    """ Manages the departmental hierarchy and leadership assignments. """

    @transaction.atomic
    def create_department(
        self, 
        name: str, 
        parent_id: Optional[UUID] = None, 
        manager_id: Optional[UUID] = None
    ) -> Department:
        """ Establishes a new organizational unit within the company hierarchy. """
        parent = None
        if parent_id:
            parent = get_object_or_404(Department, id=parent_id)
            
        dept = Department.objects.create(
            name=name,
            parent=parent,
            manager_id=manager_id
        )
        
        logger.info(f"Department '{name}' created")
        return dept

    def get_department_tree(self, parent: Optional[Department] = None) -> List[Dict[str, Any]]:
        """ Generates a hierarchical view of the company's organizational structure. """
        departments = Department.objects.filter(parent=parent).select_related('manager')
        
        tree = []
        for dept in departments:
            tree.append({
                "id": str(dept.id),
                "name": dept.name,
                "manager": dept.manager.full_name if dept.manager else None,
                "sub_departments": self.get_department_tree(parent=dept)
            })
        return tree

    @transaction.atomic
    def transfer_department_manager(self, department_id: UUID, new_manager_id: UUID) -> Department:
        """ Assigns a new leader to a department, ensuring appropriate seniority level. """
        dept = get_object_or_404(Department, id=department_id)
        new_manager = get_object_or_404(Employee, id=new_manager_id)

        current_role = new_manager.position_history.filter(is_current=True).first()
        
        if current_role and current_role.position.level not in [
            PositionLevel.MANAGER, 
            PositionLevel.DIRECTOR, 
            PositionLevel.EXECUTIVE
        ]:
            logger.warning(
                f"Leadership assignment: '{new_manager.full_name}' holds a lower seniority level "
                f"({current_role.position.level})."
            )

        dept.manager = new_manager
        dept.save()
        
        logger.info(f"Leadership for '{dept.name}' transferred to {new_manager.full_name}")
        return dept

