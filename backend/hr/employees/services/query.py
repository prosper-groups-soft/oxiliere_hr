from typing import Optional
from uuid import UUID
from django.db.models import QuerySet, Prefetch
from hr.employees.models import (
    Employee, 
    EmployeeAddress, 
    StatusHistory
)


class EmployeeQueryService:
    """
    Optimized service for reading employees.
    Prefetches all necessary relations and filtered versions for computed properties.
    Compatible with existing code.
    """

    def get_base_queryset(self) -> QuerySet:
        """
        Returns the optimized base queryset.
        Prefetches all necessary relations and filtered versions for properties.
        """

        # --- Addresses ---
        # Prefetch all addresses
        all_addresses_prefetch = Prefetch(
            'addresses',
            queryset=EmployeeAddress.objects.all(),
            to_attr='prefetched_all_addresses'
        )
        # Prefetch only the current address for current_address
        current_address_prefetch = Prefetch(
            'addresses',
            queryset=EmployeeAddress.objects.filter(is_current=True),
            to_attr='prefetched_current_address'
        )

        # --- Status History ---
        # Prefetch all status history for all_status_history
        all_status_prefetch = Prefetch(
            'status_history',
            queryset=StatusHistory.objects.order_by('created_at'),
            to_attr='prefetched_all_status_history'
        )
        # Prefetch the first status for current_status
        current_status_prefetch = Prefetch(
            'status_history',
            queryset=StatusHistory.objects.order_by('-created_at'),
            to_attr='prefetched_current_status'
        )

        # --- Final Queryset ---
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
        return self.get_base_queryset().filter(id=employee_id).first()

    def get_employee_by_matricule(self, matricule: str) -> Optional[Employee]:
        return self.get_base_queryset().filter(matricule=matricule).first()

    def list_active_employees(self) -> QuerySet:
        return self.get_base_queryset().filter(is_active=True)

