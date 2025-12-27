from typing import List
from uuid import UUID
from django.core.exceptions import ObjectDoesNotExist
from ninja_extra import api_controller, ControllerBase, route
from ninja.errors import HttpError

from hr.employees.schemas import (
    EmployeeEducationCreateIn,
    EmployeeEducationUpdateIn,
    EmployeeEducationDetailOut
)
from hr.employees.services import (
    EmployeeEducationWriterService,
    EmployeeEducationReaderService
)


@api_controller("/employees/{employee_id}/education", tags=["Employee Education"])
class EmployeeEducationAPI(ControllerBase):
    """
    API for managing employee academic records.
    """

    @route.get("/", response=List[EmployeeEducationDetailOut])
    def get_educations(self, employee_id: UUID, institute: str | None = None):
        """
        List education records for an employee.
        """
        try:
            return EmployeeEducationReaderService.list_by_employee(
                employee_id=employee_id, 
                institute=institute
            )
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.post("/", response=EmployeeEducationDetailOut)
    def add_education(self, employee_id: UUID, payload: EmployeeEducationCreateIn):
        """
        Add a new education record.
        """
        try:
            return EmployeeEducationWriterService.add_education(
                employee_id, 
                **payload.dict(exclude_unset=True)
            )
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")
        except ValueError as e:
            raise HttpError(400, str(e))

    @route.get("/{education_id}", response=EmployeeEducationDetailOut)
    def get_education(self, employee_id: UUID, education_id: UUID):
        """
        Retrieve a specific education record.
        """
        try:
            edu = EmployeeEducationReaderService.get_education(education_id)
            if edu.employee_id != employee_id:
                raise HttpError(403, "Access denied: record belongs to another employee")
            return edu
        except ObjectDoesNotExist:
            raise HttpError(404, "Education record not found")

    @route.put("/{education_id}", response=EmployeeEducationDetailOut)
    def update_education(self, employee_id: UUID, education_id: UUID, payload: EmployeeEducationUpdateIn):
        """
        Update an education record.
        """
        try:
            edu = EmployeeEducationReaderService.get_education(education_id)
            if edu.employee_id != employee_id:
                raise HttpError(403, "Access denied")
            
            return EmployeeEducationWriterService.update_education(
                education_id, 
                **payload.dict(exclude_unset=True)
            )
        except ObjectDoesNotExist:
            raise HttpError(404, "Education record not found")
        except ValueError as e:
            raise HttpError(400, str(e))

    @route.delete("/{education_id}")
    def remove_education(self, employee_id: UUID, education_id: UUID):
        """
        Delete an education record.
        """
        try:
            edu = EmployeeEducationReaderService.get_education(education_id)
            if edu.employee_id != employee_id:
                raise HttpError(403, "Access denied")
            
            EmployeeEducationWriterService.remove_education(education_id)
            return {"success": True}
        except ObjectDoesNotExist:
            raise HttpError(404, "Education record not found")

