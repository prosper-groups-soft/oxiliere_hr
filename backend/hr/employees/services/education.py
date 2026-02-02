import logging
from typing import Any, Dict
from django.db import transaction
from django.core.exceptions import ValidationError
from django.db import IntegrityError

from hr.employees.models import Employee, EmployeeEducation
from hr.utils.core import update_instance


logger = logging.getLogger(__name__)


class EmployeeEducationService:
    """ Manages employee academic backgrounds and qualifications. """

    @transaction.atomic
    def add_education(
        self, 
        employee: Employee, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeEducation:
        """ Registers a new academic degree or certification. """
        institute = data.get('institute', '')
        major = data.get('major', '') or None

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
            
            logger.info(f"[EDU] Added: {education.degree} for {employee.matricule}")
            return education

        except IntegrityError:
            raise ValidationError({
                "degree": f"Degree already recorded for this institute."
            })

    @transaction.atomic
    def update_education(
        self, 
        education: EmployeeEducation, 
        data: Dict[str, Any], 
        actor: Any = None
    ) -> EmployeeEducation:
        """ Updates details of an existing academic record. """
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
        
        logger.info(f"[EDU] Updated: {education.id}")
        return education

    @transaction.atomic
    def remove_education(self, education: EmployeeEducation, actor: Any = None) -> None:
        """ Removes an education record from the profile. """
        education.updated_by = actor
        education.delete()
        logger.warning(f"[EDU] Removed: {education.id}")
        
