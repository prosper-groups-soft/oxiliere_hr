from django.db import transaction
from hr.employees.models import Employee, EmployeeEducation
from hr.enums import DegreeEnum


class EmployeeEducationWriterService:
    """
    Handles creation, update, and deletion of employee academic records.
    """

    @staticmethod
    @transaction.atomic
    def add_education(
        employee_id: int, 
        institute: str, 
        degree: str, 
        major: str,
        start_year, 
        end_year, 
        location: str
    ) -> EmployeeEducation:
        """
        Adds a new academic record for the given employee.
        """
        if degree not in [d[0] for d in DegreeEnum.choices]:
            raise ValueError(f"Invalid degree value: {degree}")

        employee = Employee.objects.get(id=employee_id)
        return EmployeeEducation.objects.create(
            employee=employee,
            institute=institute,
            degree=degree,
            major=major,
            start_year=start_year,
            end_year=end_year,
            location=location
        )

    @staticmethod
    @transaction.atomic
    def update_education(education_id: int, **kwargs) -> EmployeeEducation:
        """
        Updates an existing academic record.
        Accepts kwargs corresponding to EmployeeEducation fields.
        """
        education = EmployeeEducation.objects.get(id=education_id)
        for field, value in kwargs.items():
            if hasattr(education, field):
                if field == "degree" and value not in [d[0] for d in DegreeEnum.choices]:
                    raise ValueError(f"Invalid degree value: {value}")
                setattr(education, field, value)
        education.save()
        return education

    @staticmethod
    @transaction.atomic
    def remove_education(education_id: int) -> None:
        """
        Deletes an academic record.
        """
        EmployeeEducation.objects.filter(id=education_id).delete()


class EmployeeEducationReaderService:
    """
    Handles retrieval and search of EmployeeEducation records.
    """

    @staticmethod
    def list_educations(employee_id: int):
        """
        Returns all academic records for a given employee.
        """
        return EmployeeEducation.objects.filter(employee_id=employee_id)

    @staticmethod
    def get_education(education_id: int) -> EmployeeEducation | None:
        """
        Retrieves a single academic record by its ID.
        """
        try:
            return EmployeeEducation.objects.get(id=education_id)
        except EmployeeEducation.DoesNotExist:
            return None

    @staticmethod
    def search_educations(
        employee_id: int = None, 
        institute: str = None, 
        major: str = None
    ):
        """
        Searches academic records with optional filters.
        """
        queryset = EmployeeEducation.objects.all()
        if employee_id:
            queryset = queryset.filter(employee_id=employee_id)
        if institute:
            queryset = queryset.filter(institute__icontains=institute)
        if major:
            queryset = queryset.filter(major__icontains=major)
        return queryset