from typing import Optional
from uuid import UUID
from django.db.models import QuerySet, Prefetch
from hr.employees.models import (
    Employee, 
    EmployeeAddress, 
    StatusHistory
)


class EmployeeQueryService:
    """ Optimized service for employee data retrieval and reporting. """

    def get_base_queryset(self) -> QuerySet:
        """ Returns optimized queryset with prefetched relations. """

        # Prefetch addresses
        all_addresses_prefetch = Prefetch(
            'addresses',
            queryset=EmployeeAddress.objects.all(),
            to_attr='prefetched_all_addresses'
        )
        current_address_prefetch = Prefetch(
            'addresses',
            queryset=EmployeeAddress.objects.filter(is_current=True),
            to_attr='prefetched_current_address'
        )

        # Prefetch status history
        all_status_prefetch = Prefetch(
            'status_history',
            queryset=StatusHistory.objects.order_by('created_at'),
            to_attr='prefetched_all_status_history'
        )
        current_status_prefetch = Prefetch(
            'status_history',
            queryset=StatusHistory.objects.order_by('-created_at'),
            to_attr='prefetched_current_status'
        )

        return Employee.objects.select_related('user').prefetch_related(
            "user",
            all_addresses_prefetch,
            current_address_prefetch,
            "documents",
            "educations",
            "children",
            "emergency_contacts",
            all_status_prefetch,
            current_status_prefetch,
        )

    def get_employee_by_id(self, employee_id: UUID) -> Optional[Employee]:
        """ Finds specific employee by database ID. """
        return self.get_base_queryset().filter(id=employee_id).first()

    def get_employee_by_matricule(self, matricule: str) -> Optional[Employee]:
        """ Finds employee profile by unique staff ID. """
        return self.get_base_queryset().filter(matricule=matricule).first()

    def list_active_employees(self) -> QuerySet:
        """ Returns all employees with active status. """
        return self.get_base_queryset().filter(is_active=True)

