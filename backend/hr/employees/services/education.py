from uuid import UUID
<<<<<<< HEAD
from django.db import transaction
from django.db.models import QuerySet
=======
from django.db import transaction, models
>>>>>>> d9d914b (add: oxiliere tenant)
from hr.employees.models import Employee, EmployeeEducation
from hr.employees.schemas import EmployeeEducationFilterIn
from hr.choices import DegreeChoices
from hr.utils.fn import update_instance


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
        if degree and degree not in DegreeChoices.values:
            raise ValueError(f"{degree!r} is not a valid DegreeChoices")
            
        # Ensure employee exists (raises Employee.DoesNotExist)
        employee = Employee.objects.get(id=employee_id)
        return EmployeeEducation.objects.create(employee=employee, **data)

    @staticmethod
    @transaction.atomic
    def update_education(education_id: UUID, **kwargs) -> EmployeeEducation:
        """
        Updates allowed fields of an academic record.
        """
        education = EmployeeEducation.objects.get(id=education_id)

        if "degree" in kwargs and kwargs["degree"] not in DegreeChoices.values:
            raise ValueError(f"Invalid degree: {kwargs['degree']}")

        return update_instance(
            instance=education,
            allowed_fields={
                "institute",
                "degree",
                "major",
                "start_year",
                "end_year",
                "location",
            },
            data=kwargs,
        )

    @staticmethod
    @transaction.atomic
    def remove_education(education_id: UUID) -> None:
        """
        Deletes an academic record.
        """
        count, _ = EmployeeEducation.objects.filter(id=education_id).delete()
        if count == 0:
            raise EmployeeEducation.DoesNotExist()


class EmployeeEducationReaderService:
    """
    Handles retrieval and search of EmployeeEducation records.
    """

    @staticmethod
    def get_education(education_id: UUID) -> EmployeeEducation:
        return EmployeeEducation.objects.get(id=education_id)

    @staticmethod
<<<<<<< HEAD
    def get_educations(*, employee_id: UUID, filters: EmployeeEducationFilterIn) -> QuerySet[EmployeeEducation]:
=======
    def get_educations(*, employee_id: UUID, filters: EmployeeEducationFilterIn) -> models.QuerySet[EmployeeEducation]:
        
>>>>>>> d9d914b (add: oxiliere tenant)
        # raises Employee.DoesNotExist if not found
        Employee.objects.get(id=employee_id)

        qs = EmployeeEducation.objects.filter(employee_id=employee_id)

        return filters.filter(qs)
