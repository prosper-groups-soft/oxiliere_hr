from uuid import UUID
import logging
from datetime import date
from typing import Any, Dict
from django.db import transaction

from hr.employees.models import EmployeeAddress, Employee
from hr.utils.core import update_instance


logger = logging.getLogger(__name__)


class EmployeeAddressService:
    """ Manages employee residency and location history. """

    @transaction.atomic
    def register_move(
        self, 
        employee: Employee, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeAddress:
        """ Records a change of residence and archives old address. """
        move_date = data.get('move_in_date') or date.today()

        # Archive old address
        current_address = employee.addresses.filter(is_current=True).first()
        if current_address:
            current_address.is_current = False
            current_address.move_out_date = move_date
            current_address.save(update_fields=['is_current', 'move_out_date'])

        # Create new address
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

        logger.info(f"[MOVE] {employee.matricule} moved to {new_address.city}")
        return new_address

    @transaction.atomic
    def correct_address(
        self, 
        address_id: UUID, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeAddress:
        """ Performs administrative corrections on address data. """
        address = EmployeeAddress.objects.get(id=address_id)
        
        allowed_fields = [
            'number', 'street', 'municipality', 'city', 'province', 
            'country', 'country_code', 'move_out_date', 'move_in_date'
        ]
        
        update_instance(
            instance=address,
            allowed_fields=allowed_fields,
            data=data
        )
        
        address.updated_by = actor
        address.save()
        
        logger.info(f"[CORRECTION] Address {address.id} updated")
        return address

