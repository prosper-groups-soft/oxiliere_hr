import logging
from uuid import UUID
from decimal import Decimal
from typing import Optional
from datetime import date

from django.shortcuts import get_object_or_404
from django.utils import timezone

# Models
from hr.employees.models import Employee
from hr.jobs.models import Position, PositionSeniority, EmployeePositionHistory, EmployeeTransition
from hr.payroll.models import EmployeeContract


logger = logging.getLogger(__name__)


class EmployeeCareerService:
    """
    Service for managing employee career lifecycle.
    
    Handles:
    - Contract creation during onboarding
    - Position assignments and history
    - Career transitions (hire, promotion, transfer)
    """

    def create_onboarding_contract(
        self,
        employee: Employee,
        position_id: UUID,
        seniority_level_id: UUID,
        base_salary: Decimal,
        contract_type: str,
        remuneration_type: str,
        payment_period: str,
        salary_base_type: str,
        start_date: date,
        end_date: Optional[date] = None,
        currency: str = "CDF",
        is_active: bool = True,
    ) -> EmployeeContract:
        """
        Creates a complete employment contract during onboarding.
        
        This method:
        1. Creates an EmployeeContract (payroll)
        2. Creates an EmployeePositionHistory (current position assignment)
        3. Creates an EmployeeTransition (HIRE event)
        
        Args:
            employee: The employee to create the contract for
            position_id: UUID of the position
            seniority_level_id: UUID of the seniority level
            base_salary: Base salary amount
            contract_type: Type of contract (CDI, CDD, FREELANCE, INTERN)
            remuneration_type: Type of remuneration (FIXED, HOURLY, GROSS_UP)
            payment_period: Payment frequency (MONTHLY, BIWEEKLY, WEEKLY)
            salary_base_type: Salary base type (GROSS, NET)
            start_date: Contract start date
            end_date: Contract end date (optional, for CDD)
            currency: Currency code (default: CDF)
            is_active: Whether the contract is active
            
        Returns:
            The created EmployeeContract
            
        Raises:
            ValidationError: If validation fails
            DoesNotExist: If position or seniority level not found
        """
        logger.info(f"[CareerService] Creating onboarding contract for employee {employee.matricule}")
        
        # 1. Get position and seniority level
        position = get_object_or_404(Position, id=position_id)
        
        # Le frontend envoie l'ID du PositionSeniority, pas le seniority_level_id
        position_seniority = get_object_or_404(
            PositionSeniority, 
            id=seniority_level_id
        )
        seniority_level = position_seniority.seniority_level
        
        # 2. Create EmployeeContract (payroll)
        contract = EmployeeContract.objects.create(
            employee=employee,
            remuneration_type=remuneration_type,
            payment_period=payment_period,
            contract_type=contract_type,
            base_salary=base_salary,
            salary_base_type=salary_base_type,
            hourly_rate=None,  # Will be calculated if needed
            currency=currency,
            start_date=start_date,
            end_date=end_date,
            is_active=is_active,
        )
        
        logger.info(f"[CareerService] Created EmployeeContract {contract.id} for {employee.matricule}")
        
        # 3. Create EmployeePositionHistory (current assignment)
        # First, mark any existing current position as not current
        EmployeePositionHistory.objects.filter(
            employee=employee,
            is_current=True
        ).update(is_current=False, end_date=timezone.now().date())
        
        position_history = EmployeePositionHistory.objects.create(
            employee=employee,
            position=position,
            seniority_level=seniority_level,
            salary_at_assignment=int(base_salary),
            org_unit=position.org_unit,
            start_date=start_date,
            end_date=None,
            is_current=True,
            description=f"Embauche initiale. Type de contrat : {contract_type}"
        )
        
        logger.info(f"[CareerService] Created EmployeePositionHistory {position_history.id} for {employee.matricule}")
        
        # 4. Create EmployeeTransition (HIRE event)
        transition = EmployeeTransition.objects.create(
            employee=employee,
            transition_type='HIRE',
            from_position=None,
            from_seniority_level=None,
            to_position=position,
            to_seniority_level=seniority_level,
            date=start_date,
            reason=f'Embauche initiale poste {position.name} - {position_seniority.seniority_level.label}'
        )
        
        logger.info(f"[CareerService] Created EmployeeTransition {transition.id} (HIRE) for {employee.matricule}")
        
        logger.info(
            f"[CareerService] Onboarding contract created successfully",
            extra={
                "contract_id": str(contract.id),
                "employee_matricule": employee.matricule,
                "position_id": str(position_id),
                "seniority_level_id": str(seniority_level_id),
                "transition_id": str(transition.id),
                "position_history_id": str(position_history.id),
            }
        )
        
        return contract
