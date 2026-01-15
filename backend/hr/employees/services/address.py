from uuid import UUID
import logging
from datetime import date
from typing import Any, Dict
from django.db import transaction

from hr.employees.models import EmployeeAddress, Employee
from hr.utils import update_instance


logger = logging.getLogger(__name__)


class EmployeeAddressService:
    """
    Service managing residency history.
    Ensures that only one address is marked as 'current' at any given time.
    """

    @transaction.atomic
    def register_move(
        self, 
        employee: Employee, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeAddress:
        """
        Business Intent: Record a change of residence (Move).
        
        Logic:
        1. Archives the previous address by setting is_current=False.
        2. Creates a new record and marks it as the current address.
        """
        # Retrieve the move date from data or fallback to today's date
        move_date = data.get('move_in_date') or date.today()

        # 1. Archive the old current address if it exists
        current_address = employee.addresses.filter(is_current=True).first()
        if current_address:
            current_address.is_current = False
            current_address.move_out_date = move_date
            current_address.save(update_fields=['is_current', 'move_out_date'])

        # 2. Create the new address record
        new_address = EmployeeAddress.objects.create(
            employee=employee,
            is_current=True,
            number=data.get('number'),
            street=data.get('street'),
            municipality=data.get('municipality'),
            city=data.get('city'),
            province=data.get('province'),
            country=data.get('country', 'DRC'),
            country_code=data.get('country_code', 'CD'),
            move_in_date=move_date,
            created_by=actor
        )

        logger.info(f"[MOVE] Employee {employee.matricule} moved to {new_address.city} (ID: {new_address.id})")
        return new_address

    @transaction.atomic
    def correct_address(
        self, 
        address_id: UUID, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeAddress:
        """
        Business Intent: Administrative correction (fixing typos).
        Does NOT trigger a history break or change the 'current' status.
        """
        address = EmployeeAddress.objects.get(id=address_id)
        
        allowed_fields = [
            'number', 'street', 'municipality', 'city', 'province', 
            'country', 'country_code', 'move_out_date', 'move_in_date'
        ]
        
        # Apply partial updates using the utility helper
        update_instance(
            instance=address,
            allowed_fields=allowed_fields,
            data=data
        )
        
        address.updated_by = actor
        address.save()
        
        logger.info(f"[CORRECTION] Address ID {address.id} updated by {actor}")
        return address

