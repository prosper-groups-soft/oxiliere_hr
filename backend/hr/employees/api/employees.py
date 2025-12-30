from typing import List
from uuid import UUID
from ninja import Query
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja_extra import (
    api_controller, 
    ControllerBase, 
    route
)
from django.core.exceptions import ObjectDoesNotExist

from hr.employees.schemas import (
    EmployeeCreateIn, 
    EmployeeUpdateIn, 
    EmployeeDetailOut,
    EmployeeFullProfileOut,
    EmployeeAddressDetailOut,
    EmployeeListOut,
    EmployeeAddressUpdateIn,
    EmployeeFilterIn,
)
from hr.employees.services import (
    EmployeeWriterService, 
    EmployeeReaderService,
    EmployeeAddressService
)
from hr.cursor_pagination import CursorPagination



@api_controller("/employees", tags=["Employee"])
class EmployeeAPI(ControllerBase):
    """API for employee"""

    @route.get("/{employee_id}", response=EmployeeDetailOut)
    def get_employee(self, employee_id: UUID):
        try:
            employee = EmployeeReaderService.get_employee_detail(employee_id)
            return employee
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.get("/{employee_id}/profile", response=EmployeeFullProfileOut)
    def get_employee_profile(self, employee_id: UUID):
        try:
            employee = EmployeeReaderService.get_employee_full_profile(employee_id)
            return employee
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")
    
    @route.get("/", response=List[EmployeeListOut])
    @paginate(CursorPagination)
    def get_employees(
        self,
        filters: EmployeeFilterIn = Query(...)
    ):
        return EmployeeReaderService.get_employees(filters=filters)
    
    @route.post("/", response=EmployeeDetailOut)
    def add_employee(self, payload: EmployeeCreateIn):
        employee = EmployeeWriterService.add_employee(**payload.dict(exclude_unset=True))
        return employee

    @route.put("/{employee_id}", response=EmployeeDetailOut)
    def update_employee(self, employee_id: UUID, payload: EmployeeUpdateIn):
        try:
            employee = EmployeeWriterService.update_employee(
                employee_id, 
                **payload.dict(exclude_unset=True)
            )
            return employee
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.patch("/{employee_id}/activate")
    def activate_employee(self, employee_id: UUID):
        try:
            employee = EmployeeWriterService.activate_employee(employee_id)
            return {"success": True, "id": employee.id}
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.patch("/{employee_id}/deactivate")
    def deactivate_employee(self, employee_id: UUID):
        try:
            employee = EmployeeWriterService.deactivate_employee(employee_id)
            return {"success": True, "id": employee.id}
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")
        
    @route.delete("/{employee_id}")
    def remove_employee(self, employee_id: UUID):
        try:
            EmployeeWriterService.remove_employee(employee_id)
            return {"success": True, "id": employee_id}
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")


@api_controller(
    "/employees/{employee_id}/address", 
    tags=["Employee Address"]
)
class EmployeeAddressAPI(ControllerBase):
    """API for employee address"""
    
    @route.get("/", response=EmployeeAddressDetailOut)
    def get_address(self, employee_id: UUID):
        try:
            address = EmployeeAddressService.get_address(employee_id)
            return address
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee Address not found")

    @route.put("/", response=EmployeeAddressDetailOut)
    def update_address(self, employee_id: UUID, payload: EmployeeAddressUpdateIn):
        try:
            address = EmployeeAddressService.update_address(
                employee_id, 
                **payload.dict(exclude_unset=True)
            )
            return address
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee Address not found")

