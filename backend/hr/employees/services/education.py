from uuid import UUID
from django.db import transaction, QuerySet
from django.db import models
from hr.employees.models import Employee, EmployeeEducation
from hr.employees.schemas import EmployeeEducationFilterIn
from hr.enums import DegreeEnum


class EmployeeEducationWriterService:
    """
    Handles creation, update, and deletion of employee academic records.
    """

    @staticmethod
    @transaction.atomic
    def add_education(employee_id: UUID, **data) -> EmployeeEducation:        
        """
        Adds a new academic record for the given employee.
        """
        degree = data.get("degree")
        if degree and degree not in DegreeEnum.values():
            raise ValueError(f"{degree!r} is not a valid DegreeEnum")
            
        # Ensure employee exists (raises Employee.DoesNotExist)
        employee = Employee.objects.get(id=employee_id)
        return EmployeeEducation.objects.create(employee=employee, **data)

    @staticmethod
    @transaction.atomic
    def update_education(education_id: UUID, **kwargs) -> EmployeeEducation:
        """
        Updates an existing academic record.
        Accepts kwargs corresponding to EmployeeEducation fields.
        """
        # raises EmployeeEducation.DoesNotExist if not found
        education = EmployeeEducation.objects.get(id=education_id)
        
        for field, value in kwargs.items():
            if hasattr(education, field):
                if field == "degree" and value not in DegreeEnum.values():
                    raise ValueError(f"Invalid degree: {value}")

                setattr(education, field, value)
        
        education.save()
        return education

    @staticmethod
    @transaction.atomic
    def remove_education(education_id: UUID) -> None:
        """
        Deletes an academic record.
        """
        education = EmployeeEducation.objects.get(id=education_id)
        education.delete()


class EmployeeEducationReaderService:
    """
    Handles retrieval and search of EmployeeEducation records.
    """

    @staticmethod
    def get_education(education_id: UUID) -> EmployeeEducation:
        """
        Retrieves a single academic record by its ID.
        """
        return EmployeeEducation.objects.get(id=education_id)

    @staticmethod
    def get_educations(*, employee_id: UUID, filters: EmployeeEducationFilterIn) -> QuerySet[EmployeeEducation]:
        
        # raises Employee.DoesNotExist if not found
        Employee.objects.get(id=employee_id)

        # Base queryset
        qs = EmployeeEducation.objects.filter(employee_id=employee_id)

        # Search text
        if filters.search:
            qs = qs.filter(
                models.Q(institute__icontains=filters.search)
                | models.Q(major__icontains=filters.search)
                | models.Q(location__icontains=filters.search)
            )

        # Search filters
        if filters.gender:
            qs = qs.filter(gender=filters.gender)
        
        if filters.degree:
            qs = qs.filter(degree=filters.degree)

        return qs

