import logging
from typing import Any, Dict
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from hr.employees.models import Employee, EmployeeEducation
from hr.utils.core import update_instance


logger = logging.getLogger(__name__)


class EmployeeEducationService:
    """
    Service managing academic backgrounds and qualifications.
    Ensures data aligns with DRC's LMD educational framework.
    """

    @transaction.atomic
    def add_education(
        self, 
        employee: Employee, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeEducation:
        """
        Business Intent: Register a new academic degree or certification.
        
        Rules:
        - Validates chronological consistency (via model.clean()).
        - Normalizes institute and major names.
        - Handles potential duplicates (Unique constraint).
        """
        # Normalization
        institute = data.get('institute', '')
        major = data.get('major', '') if data.get('major') else None

        try:
            education = EmployeeEducation.objects.create(
                employee=employee,
                institute=institute,
                degree=data.get('degree'),
                major=major,
                start_year=data.get('start_year'),
                end_year=data.get('end_year'),
                location=data.get('location', ''),
                created_by=actor
            )
            
            logger.info(f"[EDU] Education added for {employee.matricule}: {education.degree} at {institute}")
            return education

        except IntegrityError:
            # Handle the unique_together constraint (employee, degree, institute)
            raise ValidationError({
                "degree": f"This employee already has a {data.get('degree')} recorded for this institute."
            })

    @transaction.atomic
    def update_education(
        self, 
        education: EmployeeEducation, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeEducation:
        """
        Business Intent: Correct or update academic record details.
        """
        allowed_fields = [
            'institute', 'degree', 'major', 
            'start_year', 'end_year', 'location'
        ]

        update_instance(
            instance=education,
            allowed_fields=allowed_fields,
            data=data
        )
        
        education.updated_by = actor
        education.save(update_fields=['updated_by'])
        
        logger.info(f"[EDU] Education record {education.id} updated by {actor}")
        return education

    @transaction.atomic
    def remove_education(self, education: EmployeeEducation, actor: Any = None) -> None:
        """
        Business Intent: Remove an education record.
        Uses Soft Delete via BaseAuditableModel.
        """
        education.updated_by = actor
        education.delete()
        logger.warning(f"[EDU] Education record {education.id} deleted by {actor}")
        
