import logging
from uuid import UUID
from typing import Optional, List, Dict, Any
from django.db import transaction
from django.shortcuts import get_object_or_404
from cacheops import invalidate_model

from hr.jobs.models import OrgUnit, EmployeePositionHistory, Position
from hr.employees.models import Employee
from hr.jobs.enums import PositionLevel
from hr.jobs.services.cache import JobsCacheService
from hr.utils import get_employee_full_name
from django.utils import timezone


logger = logging.getLogger(__name__)


class OrganizationService:
    """ Manages the organizational structure hierarchy and leadership assignments. """

    @transaction.atomic
    def create_unit(
        self, 
        name: str, 
        unit_type: str = "DEPARTMENT",
        parent_id: Optional[UUID] = None, 
        manager_id: Optional[UUID] = None,
        affoint_id: Optional[UUID] = None,
        authorized_headcount: int = 0
    ) -> OrgUnit:
        """ Establishes a new organizational unit within the company hierarchy. """
        parent = None
        if parent_id:
            parent = get_object_or_404(OrgUnit, id=parent_id)
            
        unit = OrgUnit.objects.create(
            name=name,
            type=unit_type,
            parent=parent,
            manager_id=manager_id,
            affoint_id=affoint_id,
            authorized_headcount=authorized_headcount
        )
        
        logger.info(f"Unit '{name}' created (type: {unit_type})")
        return unit

    @transaction.atomic
    def update_unit(
        self,
        unit_id: UUID,
        name: Optional[str] = None,
        unit_type: Optional[str] = None,
        parent_id: Optional[UUID] = None,
        manager_id: Optional[UUID] = None,
        affoint_id: Optional[UUID | str] = None,
        authorized_headcount: Optional[int] = None
    ) -> OrgUnit:
        """ Updates an existing organizational unit. """
        unit = get_object_or_404(OrgUnit, id=unit_id)
        
        if name is not None:
            unit.name = name
        if unit_type is not None:
            unit.type = unit_type
        if parent_id is not None:
            unit.parent = get_object_or_404(OrgUnit, id=parent_id) if parent_id else None
        if manager_id is not None:
            unit.manager_id = manager_id
        if affoint_id is not None:
            if affoint_id == "":
                unit.affoint_id = None  # Supprimer l'adjoint
            else:
                unit.affoint_id = affoint_id
        if authorized_headcount is not None:
            unit.authorized_headcount = authorized_headcount
            
        unit.save()
        logger.info(f"Unit '{unit.name}' updated")
        return unit

    def get_org_tree(self, parent: Optional[OrgUnit] = None) -> List[Dict[str, Any]]:
        """ Generates a hierarchical view of the company's organizational structure. """
        # Récupère toutes les unités avec leurs managers/adjoints en une seule requête
        units = OrgUnit.objects.filter(parent=parent).select_related(
            'manager', 
            'manager__user',
            'affoint',
            'affoint__user'
        )
        
        # Construit l'arbre récursivement en retournant des dicts
        tree = []
        for unit in units:
            tree.append({
                "id": unit.id,
                "name": unit.name,
                "type": unit.type,  # Code technique (DEPARTMENT, BRANCH, etc.)
                "employee_count": unit.employee_count,
                "authorized_headcount": unit.authorized_headcount,
                "manager": unit.manager,
                "affoint": unit.affoint,
                "sub_units": self.get_org_tree(parent=unit)
            })
        
        return tree

    @transaction.atomic
    def delete_unit(self, unit_id: UUID) -> None:
        """ Deletes an organizational unit. """
        unit = get_object_or_404(OrgUnit, id=unit_id)

        if unit.sub_units.exists():
            raise ValueError(
                f'Impossible de supprimer l\'unité "{unit.name}" : '
                'elle contient encore des sous-unités. '
                'Déplacez ou supprimez d\'abord les sous-unités.'
            )

        active_assignments = unit.position_history.filter(is_current=True).count()
        if active_assignments > 0:
            raise ValueError(
                f'Impossible de supprimer l\'unité "{unit.name}" : '
                f'{active_assignments} affectation(s) active(s) y sont encore rattachée(s). '
                'Réaffectez ou clôturez d\'abord ces affectations.'
            )

        if unit.job_offers.exists():
            raise ValueError(
                f'Impossible de supprimer l\'unité "{unit.name}" : '
                'des offres de recrutement y sont encore rattachées. '
            )

        unit.delete()
        logger.info(f"Unit '{unit_id}' deleted")

    @transaction.atomic
    def transfer_leadership(self, unit_id: UUID, new_manager_id: UUID) -> OrgUnit:
        """ Assigns a new leader to an organizational unit. """
        unit = get_object_or_404(OrgUnit, id=unit_id)
        new_manager = get_object_or_404(Employee, id=new_manager_id)

        current_role = new_manager.position_history.filter(is_current=True).first()
        
        if current_role and current_role.position.level not in [
            PositionLevel.MANAGER, 
            PositionLevel.DIRECTOR, 
            PositionLevel.EXECUTIVE
        ]:
            full_name = get_employee_full_name(new_manager)
            logger.warning(
                f"Leadership assignment: '{full_name}' holds a lower seniority level "
                f"({current_role.position.level})."
            )

        unit.manager = new_manager
        unit.save()

        full_name = get_employee_full_name(new_manager)
        logger.info(f"Leadership for '{unit.name}' transferred to {full_name}")
        return unit

    @transaction.atomic
    def assign_employee_to_unit(
        self,
        employee_id: UUID,
        org_unit_id: UUID,
        position_id: Optional[UUID] = None
    ) -> EmployeePositionHistory:
        """Assigns an employee to an organizational unit with optional position."""
        employee = get_object_or_404(Employee, id=employee_id)
        org_unit = get_object_or_404(OrgUnit, id=org_unit_id)

        # Validate headcount limit
        current_count = EmployeePositionHistory.objects.filter(
            org_unit=org_unit,
            is_current=True
        ).count()
        
        if org_unit.authorized_headcount > 0 and current_count >= org_unit.authorized_headcount:
            raise ValueError(
                f"Cannot assign employee: unit '{org_unit.name}' has reached its authorized headcount "
                f"({current_count}/{org_unit.authorized_headcount})."
            )

        # Close any current position history for this employee
        EmployeePositionHistory.objects.filter(
            employee=employee,
            is_current=True
        ).update(is_current=False, end_date=timezone.now().date())

        # Create new position history entry
        position = None
        if position_id:
            position = get_object_or_404(Position, id=position_id)

        history_entry = EmployeePositionHistory.objects.create(
            employee=employee,
            org_unit=org_unit,
            position=position,
            is_current=True,
            start_date=timezone.now().date()
        )

        # Invalidate cache
        self._invalidate_assignment_cache()

        full_name = get_employee_full_name(employee)
        logger.info(f"Employee '{full_name}' assigned to unit '{org_unit.name}'")
        return history_entry

    @transaction.atomic
    def unassign_employee_from_unit(self, employee_id: UUID) -> None:
        """Removes an employee from their current organizational unit."""
        employee = get_object_or_404(Employee, id=employee_id)

        # Close current position history
        current_history = EmployeePositionHistory.objects.filter(
            employee=employee,
            is_current=True
        ).first()

        if current_history:
            current_history.is_current = False
            current_history.end_date = timezone.now().date()
            current_history.save()

            # Invalidate cache
            self._invalidate_assignment_cache()

            full_name = get_employee_full_name(employee)
            logger.info(f"Employee '{full_name}' unassigned from unit '{current_history.org_unit.name}'")
        else:
            logger.warning(f"Employee {employee_id} has no current assignment to unassign")

    def _invalidate_assignment_cache(self):
        """Invalidate all related caches when employee assignment changes."""
        # Invalidate API response cache
        JobsCacheService.clear_employee_list_api_cache()
        JobsCacheService.clear_org_tree_api_cache()

        # Invalidate cacheops model cache
        invalidate_model(Employee)
        invalidate_model(OrgUnit)
        invalidate_model(EmployeePositionHistory)
        invalidate_model(Position)

        logger.info("[Cache] Invalidated all assignment-related caches")

