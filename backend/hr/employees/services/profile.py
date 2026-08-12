from __future__ import annotations
import logging
from typing import Any, Dict, Optional
from uuid import UUID

from django.db import transaction
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from sequences import get_next_value
from injector import inject

from hr.employees.models import Employee, StatusHistory, WorkSite
from hr.employees.enums import EmployeeStatus
from hr.utils.core import update_instance
from .query import EmployeeQueryService
from .address import EmployeeAddressService

from hr.jobs.services import CareerService
from hr.payroll.services.contracts import EmployeeContractService


logger = logging.getLogger(__name__)


class EmployeeProfileService:
    """ Core service for employee identity and lifecycle management. """
    
    @inject
    def __init__(
        self, 
        query_service: EmployeeQueryService, 
        address_service: EmployeeAddressService,
        career_service: CareerService,
        contract_service: EmployeeContractService
    ):
        self.query_service = query_service
        self.address_service = address_service
        self.career_service = career_service
        self.contract_service = contract_service

    def _get_matricule_seq_key(self) -> str:
        """ Key for yearly sequence counter. """
        year = timezone.now().year
        return f"employee_matricule_{year}"

    def _format_matricule(self, number: int, prefix: str = "EMP") -> str:
        """ Formats final staff ID string. """
        year = timezone.now().year
        return f"{prefix}-{year}-{number:05d}"

    def _generate_matricule_value(self) -> str:
        """ Thread-safe generation of unique staff IDs. """
        number = get_next_value(self._get_matricule_seq_key())
        return self._format_matricule(number)

    @transaction.atomic
    def onboard_employee(self, data: Dict[str, Any], actor: Any = None) -> Employee:
        """ Formal onboarding with probation initiation and optional user account. """
        email = data.get("email", "").strip().lower()
        create_account = data.get("create_account", False)
        group_slug = data.get("group_slug")
        
        if Employee.objects.filter(email=email).exists():
            logger.warning(f"Onboarding failed: {email} exists.")
            raise ValidationError({
                "email": "Email already assigned.",
                "code": "EMAIL_ALREADY_EXISTS",
                "message": f"Un employé avec l'email '{email}' existe déjà dans le système."
            })

        # Generate matricule
        matricule = self._generate_matricule_value()

        # Prepare work_site if provided
        work_site_id = data.get("work_site_id")
        work_site = None
        if work_site_id:
            try:
                work_site = WorkSite.objects.get(id=work_site_id)
            except WorkSite.DoesNotExist:
                logger.warning(f"WorkSite {work_site_id} not found, creating employee without work site.")

        # Create main profile
        employee = Employee.objects.create(
            matricule=matricule,
            first_name=data.get("first_name", ""),
            middle_name=data.get("middle_name") or None,
            last_name=data.get("last_name", ""),
            email=email,
            phone=data.get("phone"),
            gender=data.get("gender"),
            birthdate=data.get("birthdate"),
            nationality=data.get("nationality"),
            marital_status=data.get("marital_status"),
            work_site=work_site,
            hire_date=data.get("hire_date", timezone.now().date()),
            created_by=actor
        )

        # Set initial status (PROBATION, ACTIVE or PENDING)
        initial_status = data.get("initial_status", "PROBATION")
        if initial_status == "PROBATION":
            status_value = EmployeeStatus.PROBATION
            reason = "Intégration initiale."
        elif initial_status == "PENDING":
            status_value = EmployeeStatus.PENDING
            reason = "En attente de début."
        else:
            status_value = EmployeeStatus.ACTIVE
            reason = "Embauche directe."

        StatusHistory.objects.create(
            employee=employee,
            status=status_value,
            start_date=employee.hire_date,
            reason=reason,
            created_by=actor
        )

        # Optional: User Account Creation
        if create_account:
            User = get_user_model()
            if User.objects.filter(email=email).exists():
                logger.warning(f"User account creation skipped: {email} already has a system user.")
            else:
                # Create user with matricule as default password
                user = User.objects.create_user(
                    email=email,
                    password=matricule,
                    first_name=employee.first_name,
                    last_name=employee.last_name,
                )
                employee.user = user
                employee.can_connect = True
                employee.save(update_fields=['user', 'can_connect'])

                # Assign permission group
                if group_slug:
                    from oxutils.permissions.utils import assign_group
                    try:
                        assign_group(user, group_slug)
                        logger.info(f"Assigned group '{group_slug}' to new user {email}")
                    except Exception as e:
                        logger.error(f"Failed to assign group {group_slug} to {email}: {e}")

        logger.info(f"[PROFILE] Onboarded: {employee.matricule} by {actor}")
        return employee

    @transaction.atomic
    def update_personal_info(self, employee: Employee, data: Dict[str, Any], actor: Any = None) -> Employee:
        """ Updates core personal identification data, work site and address. """
        allowed_fields = [
            "first_name", "middle_name", "last_name", 
            "gender", "marital_status", "phone", "email",
            "birthdate", "nationality", "description"
        ]

        # Handle work_site_id separately
        work_site_id = data.get("work_site_id")
        if work_site_id:
            try:
                employee.work_site = WorkSite.objects.get(id=work_site_id)
            except WorkSite.DoesNotExist:
                logger.warning(f"WorkSite {work_site_id} not found during update.")

        # Handle address separately
        address_data = data.get("address")
        if address_data:
            current_address = employee.addresses.filter(is_current=True).first()
            
            # Check if any field has changed
            changed = False
            if not current_address:
                changed = True
            else:
                for field in ["number", "street", "municipality", "city", "province", "country_code"]:
                    if address_data.get(field) != getattr(current_address, field, None):
                        changed = True
                        break
            
            if changed:
                self.address_service.register_move(
                    employee=employee,
                    data=address_data,
                    actor=actor
                )

        update_instance(
            instance=employee,
            allowed_fields=allowed_fields,
            data=data
        )

        employee.updated_by = actor
        employee.save()
        
        return employee

    def get_full_profile(
        self,
        *,
        employee_id: Optional[UUID] = None,
        matricule: Optional[str] = None
    ) -> Optional[Employee]:
        """ Retrieves complete dossier by ID or Staff ID. """
        if not employee_id and not matricule:
            raise ValueError("ID or matricule required.")

        if employee_id and matricule:
            raise ValueError("Provide only one identifier.")

        if employee_id:
            return self.query_service.get_employee_by_id(employee_id)

        return self.query_service.get_employee_by_matricule(matricule)

    @transaction.atomic
    def assign_user_account(self, employee_id: UUID, user_id: int, actor: Any = None) -> Employee:
        """ Links a system user profile for portal access. """
        User = get_user_model()
        employee = get_object_or_404(Employee, id=employee_id)
        new_user = get_object_or_404(User, id=user_id)

        # Ensure user isn't linked elsewhere
        if Employee.objects.filter(user=new_user).exclude(id=employee.id).exists():
            raise ValidationError("User account already assigned.")

        employee.user = new_user
        employee.can_connect = True
        employee.updated_by = actor
        employee.save(update_fields=['user', 'can_connect', 'updated_by', 'updated_at'])

        return employee

    @transaction.atomic
    def unlink_user_account(self, employee_id: UUID, actor: Any = None) -> Employee:
        """ Revokes system access and portal link. """
        employee = get_object_or_404(Employee, id=employee_id)
        
        if not employee.user:
            return employee

        employee.user = None
        employee.can_connect = False
        employee.updated_by = actor
        employee.save(update_fields=['user', 'can_connect', 'updated_by', 'updated_at'])

        logger.warning(f"[PROFILE] Link revoked for {employee.matricule}")
        return employee

    @transaction.atomic
    def update_profile_photo(self, employee: Employee, file: Any, actor: Any = None) -> Employee:
        """ Updates the profile photo and records the change. """
        employee.profile_photo = file
        employee.updated_by = actor
        employee.save(update_fields=['profile_photo', 'updated_by', 'updated_at'])
        
        logger.info(f"[PROFILE] Photo updated for {employee.matricule}")
        return employee

    @transaction.atomic
    def delete_employee(self, employee: Employee) -> bool:
        """ 
        Completely deletes an employee profile and its associated user account. 
        Returns True if successful.
        """
        try:
            # Delete associated user if exists
            if employee.user:
                employee.user.delete()
            
            # Delete employee profile
            matricule = employee.matricule
            employee.delete()
            
            logger.warning(f"[PROFILE] Permanently deleted: {matricule}")
            return True
        except Exception as e:
            logger.error(f"[PROFILE] Failed to delete {employee.matricule}: {e}")
            raise ValidationError(f"Failed to delete employee: {str(e)}")

    @transaction.atomic
    def update_contract_and_career(self, employee: Employee, data: Dict[str, Any], actor: Any = None) -> Employee:
        """ Orchestrates the update of career positioning and contract terms. """
        from hr.jobs.models import Position, OrgUnit, SeniorityLevel
        from hr.payroll.models import EmployeeContract
        from datetime import date

        # 1. Update Position & Career if needed
        position_id = data.get('position_id')
        seniority_level_id = data.get('seniority_level_id')
        org_unit_id = data.get('org_unit_id')
        effective_date = data.get('effective_date') or data.get('hire_date')
        description = data.get('description')

        if position_id or seniority_level_id or org_unit_id:
            current_pos = employee.position_history.filter(is_current=True).first()
            
            should_move = False
            if position_id and (not current_pos or str(current_pos.position_id) != str(position_id)):
                should_move = True
            if seniority_level_id and (not current_pos or str(current_pos.seniority_level_id) != str(seniority_level_id)):
                should_move = True
            if org_unit_id and (not current_pos or str(current_pos.org_unit_id) != str(org_unit_id)):
                should_move = True
            
            if should_move:
                target_position_id = position_id or (current_pos.position_id if current_pos else None)
                if not target_position_id:
                    raise ValidationError("Position is required for a career move.")
                    
                new_position = get_object_or_404(Position, id=target_position_id)
                
                new_org_unit = None
                if org_unit_id:
                    new_org_unit = get_object_or_404(OrgUnit, id=org_unit_id)
                elif current_pos:
                    new_org_unit = current_pos.org_unit
                    
                new_seniority = None
                if seniority_level_id:
                    new_seniority = get_object_or_404(SeniorityLevel, id=seniority_level_id)
                elif current_pos:
                    new_seniority = current_pos.seniority_level
                    
                self.career_service.move_employee(
                    employee=employee,
                    new_position=new_position,
                    new_seniority_level=new_seniority,
                    new_org_unit=new_org_unit,
                    effective_date=effective_date,
                    description=description or "Mise à jour Contrat/Poste"
                )

        # 2. Update Contract Terms
        contract = self.contract_service.get_latest_contract(employee.id)
        if contract:
            contract_fields = [
                'contract_type', 'remuneration_type', 'base_salary', 
                'hourly_rate', 'salary_base_type', 'currency', 
                'hire_date', 'end_date', 'is_active', 'contractual_clauses'
            ]
            
            contract_update_data = {
                k: data[k] for k in contract_fields if k in data
            }
            
            if contract_update_data:
                self.contract_service.update_contract(
                    contract_id=contract.id,
                    data=contract_update_data,
                    actor=actor
                )
        else:
            logger.warning(f"No active contract found for employee {employee.matricule}")

        return employee

