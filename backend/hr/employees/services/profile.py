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
from hr.enums import EmployeeStatus
from hr.utils import update_instance
from .query import EmployeeQueryService


logger = logging.getLogger(__name__)


class EmployeeProfileService:
    """
    Service handling the core identity and lifecycle events.
    Ensures data normalization and collision-proof identification.
    """
    
    @inject
    def __init__(self, query_service: EmployeeQueryService):
        self.query_service = query_service

    def _get_matricule_seq_key(self) -> str:
        """
        Generates a year-specific key for the sequence counter.
        Example: 'employee_matricule_2026'
        """
        year = timezone.now().year
        return f"employee_matricule_{year}"

    def _format_matricule(self, number: int, prefix: str = "EMP") -> str:
        """
        Formats the final matricule string. 
        Override this method to change the naming convention (e.g., adding branch codes).
        """
        year = timezone.now().year
        return f"{prefix}-{year}-{number:05d}"

    def _generate_matricule_value(self) -> str:
        """
        Generates a unique matricule using database-level locking.
        Ensures no duplicates even under heavy concurrent onboarding.
        """
        number = get_next_value(self._get_matricule_seq_key())
        return self._format_matricule(number)

    @transaction.atomic
    def onboard_employee(self, data: Dict[str, Any], actor: Any = None) -> Employee:
        """
        BUSINESS: Formal onboarding with mandatory initial probation period.
        """
        email = data.get("email", "").strip().lower()
        
        if Employee.objects.filter(email=email).exists():
            logger.warning(f"Onboarding failed: Email {email} already exists.")
            raise ValidationError({"email": "This email address is already assigned."})

        # Data normalization
        first_name = data.get("first_name", "")
        last_name = data.get("last_name", "")

        employee = Employee.objects.create(
            matricule=self._generate_matricule_value(),
            first_name=first_name,
            middle_name=data.get("middle_name", "") if data.get("middle_name") else None,
            last_name=last_name,
            email=email,
            phone=data.get("phone"),
            gender=data.get("gender"),
            birthdate=data.get("birthdate"),
            nationality=data.get("nationality"),
            marital_status=data.get("marital_status"),
            hire_date=data.get("hire_date", timezone.now().date()),
            created_by=actor
        )

        # Initial status track
        StatusHistory.objects.create(
            employee=employee,
            status=EmployeeStatus.PROBATION,
            start_date=employee.hire_date,
            reason="Intégration initiale.",
            created_by=actor
        )

        logger.info(f"[PROFILE] Onboarded: {employee.matricule} by {actor}")
        return employee

    @transaction.atomic
    def update_personal_info(self, employee: Employee, data: Dict[str, Any], actor: Any = None) -> Employee:
        """
        TECHNICAL: Partial updates with audit tracking.
        """
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
        """
        Technical Intent: Single-query retrieval of the complete employee dossier.
        """
        if not employee_id and not matricule:
            raise ValueError("Either employee_id or matricule must be provided")

        if employee_id and matricule:
            raise ValueError("Provide only one identifier")

        if employee_id:
            return self.query_service.get_employee_by_id(employee_id)

        return self.query_service.get_employee_by_matricule(matricule)

    @transaction.atomic
    def assign_user_account(self, employee_id: UUID, user_id: int, actor: Any = None) -> Employee:
        User = get_user_model()
        employee = get_object_or_404(Employee, id=employee_id)
        new_user = get_object_or_404(User, id=user_id)

        # 1. Validation: The target user must not already be taken elsewhere
        if Employee.objects.filter(user=new_user).exclude(id=employee.id).exists():
            raise ValidationError(
                f"User {new_user.username} is already used by another employee ID."
            )

        # 2. Replacement logic (Optional but recommended)
        if employee.user and employee.user != new_user:
            logger.info(
                f"[PROFILE] Replacing account {employee.user.username} "
                f"with {new_user.username} for {employee.matricule}"
            )
            # Here, you could deactivate flags on the old user if necessary

        # 3. Application
        employee.user = new_user
        employee.can_connect = True
        employee.updated_by = actor
        employee.save(update_fields=['user', 'can_connect', 'updated_by', 'updated_at'])

        return employee

    @transaction.atomic
    def unlink_user_account(self, employee_id: UUID, actor: Any = None) -> Employee:
        """
        Releases the link between an employee and their user account.
        Useful for suspending portal access.
        """
        employee = get_object_or_404(Employee, id=employee_id)
        
        if not employee.user:
            return employee # Already unlinked

        old_username = employee.user.username
        employee.user = None
        employee.can_connect = False
        employee.updated_by = actor
        employee.save(update_fields=['user', 'can_connect', 'updated_by', 'updated_at'])

        logger.warning(
            f"[PROFILE] Access revoked for {employee.matricule} (former account: {old_username}) by {actor}"
        )
        return employee

