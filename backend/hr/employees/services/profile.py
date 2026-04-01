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

from hr.employees.models import Employee, StatusHistory
from hr.employees.enums import EmployeeStatus
from hr.utils.core import update_instance
from .query import EmployeeQueryService


logger = logging.getLogger(__name__)


class EmployeeProfileService:
    """ Core service for employee identity and lifecycle management. """
    
    @inject
    def __init__(self, query_service: EmployeeQueryService):
        self.query_service = query_service

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
            raise ValidationError({"email": "Email already assigned."})

        # Generate matricule
        matricule = self._generate_matricule_value()

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
            hire_date=data.get("hire_date", timezone.now().date()),
            created_by=actor
        )

        # Set initial probation status
        StatusHistory.objects.create(
            employee=employee,
            status=EmployeeStatus.PROBATION,
            start_date=employee.hire_date,
            reason="Intégration initiale.",
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
                    username=email, # Assuming email is used as username
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
        """ Updates core personal identification data. """
        allowed_fields = [
            "first_name", "middle_name", "last_name", 
            "gender", "marital_status", "phone", 
            "birthdate", "nationality"
        ]

        update_instance(
            instance=employee,
            allowed_fields=allowed_fields,
            data=data
        )

        employee.updated_by = actor
        employee.save(update_fields=['updated_by', 'updated_at'])
        
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

