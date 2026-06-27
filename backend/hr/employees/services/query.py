from typing import Optional
from uuid import UUID
from django.db.models import QuerySet, Prefetch
from hr.employees.models import (
    Employee, 
    EmployeeAddress, 
    StatusHistory,
)
from hr.jobs.models import EmployeePositionHistory
from hr.payroll.models import EmployeeContract


def enrich_employee_data(employee: 'Employee') -> dict:
    """
    Enriches employee instance with career and contract information.
    Extracts data from prefetched relations to build the EmployeeOut representation.
    """
    data = {
        'job_title':     None,
        'org_unit':      None,
        'org_unit_id':   None,
        'org_unit_type': None,
        'position_id':   None,
        'contract_type': None,
        'work_site':     None,
        'location':      None,
        'status':        None,
    }
    
    # Get current position info from prefetched relations
    current_positions = getattr(employee, 'prefetched_current_position', [])
    if current_positions:
        current_pos = current_positions[0]
        if current_pos.position:
            data['job_title'] = current_pos.position.name
            data['position_id'] = str(current_pos.position.id)
        if current_pos.org_unit:
            data['org_unit'] = current_pos.org_unit.name
            data['org_unit_id'] = str(current_pos.org_unit.id)
            data['org_unit_type'] = getattr(current_pos.org_unit, 'unit_type', None)
    
    # Get current contract info from prefetched relations
    active_contracts = getattr(employee, 'prefetched_active_contracts', [])
    if active_contracts:
        contract = active_contracts[0]
        data['contract_type'] = contract.contract_type
    
    # Get work site
    if employee.work_site:
        data['work_site'] = employee.work_site.name
    
    # Get current address location
    current_addresses = getattr(employee, 'prefetched_current_address', [])
    if current_addresses:
        addr = current_addresses[0]
        city = addr.city or ''
        province = addr.province or ''
        data['location'] = f"{city}, {province}".strip(', ')
    
    # Determine employment status
    if employee.termination_date:
        data['status'] = 'inactive'
    elif employee.is_active:
        data['status'] = 'active'
    else:
        data['status'] = 'inactive'
    
    return data


class EmployeeQueryService:
    """ Optimized service for employee data retrieval and reporting. """

    def get_base_queryset(self) -> QuerySet:
        """ Returns optimized queryset with prefetched relations including career and contract info. """

        # Prefetch addresses
        all_addresses_prefetch = Prefetch(
            'addresses',
            queryset=EmployeeAddress.objects.all(),
            to_attr='prefetched_all_addresses'
        )
        current_address_prefetch = Prefetch(
            'addresses',
            queryset=EmployeeAddress.objects.order_by('-is_current', '-created_at'),
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
        
        # Prefetch current position history (career info)
        current_position_prefetch = Prefetch(
            'position_history',
            queryset=EmployeePositionHistory.objects.order_by('-is_current', '-start_date').select_related('position', 'org_unit', 'seniority_level'),
            to_attr='prefetched_current_position'
        )
        
        # Prefetch latest contract (active or suspended)
        current_contract_prefetch = Prefetch(
            'contracts',
            queryset=EmployeeContract.objects.order_by('-is_active', '-start_date'),
            to_attr='prefetched_latest_contract'
        )

        return Employee.objects.select_related('user', 'work_site').prefetch_related(
            "user",
            all_addresses_prefetch,
            current_address_prefetch,
            "documents",
            "educations",
            "children",
            "emergency_contacts",
            all_status_prefetch,
            current_status_prefetch,
            current_position_prefetch,
            current_contract_prefetch,
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

