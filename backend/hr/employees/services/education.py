from uuid import UUID
from django.db import transaction
from hr.employees.models import Employee, EmployeeEducation
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
        if degree and degree not in [tag.value for tag in DegreeEnum]:
            raise ValueError(f"Invalid degree: {degree}")

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
                if field == "degree" and value not in [d[0] for d in DegreeEnum.choices]:
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
    def list_by_employee(employee_id: UUID, institute: str = None):
        """
        Merged search and list logic.
        """
        qs = EmployeeEducation.objects.filter(employee_id=employee_id)
        if institute:
            qs = qs.filter(institute__icontains=institute)
        return qs

    @staticmethod
    def get_education(education_id: UUID) -> EmployeeEducation:
        """
        Retrieves a single academic record by its ID.
        """
        return EmployeeEducation.objects.get(id=education_id)