from typing import List, Optional
from uuid import UUID
from ninja.errors import HttpError
from ninja.pagination import paginate
from ninja_extra import (
    api_controller, 
    ControllerBase, 
    route
)
from hr.employees.schemas import (
    EmployeeCreateIn, 
    EmployeeUpdateIn, 
    EmployeeDetailOut,
    EmployeeFullProfileOut,
    EmployeeAddressDetailOut,
    EmployeeListOut,
    EmployeeAddressUpdateIn,
)
from hr.employees.services import (
    EmployeeWriterService, 
    EmployeeReaderService,
    EmployeeAddressService
)
from hr.employees.models import Employee, EmployeeAddress
from hr.cursor_pagination import CursorPagination



@api_controller("/employees", tags=["Employee"])
class EmployeeAPI(ControllerBase):
    """API for employee"""
    
    @route.post("/", response=EmployeeDetailOut)
    def create_employee(self, payload: EmployeeCreateIn):
        employee = EmployeeWriterService.create_employee(**payload.dict(exclude_unset=True))
        return employee

    @route.put("/{employee_id}", response=EmployeeDetailOut)
    def update_employee(self, employee_id: UUID, payload: EmployeeUpdateIn):
        try:
            employee = EmployeeWriterService.update_employee(
                employee_id, 
                **payload.dict(exclude_unset=True)
            )
            return employee
        except Employee.DoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.patch("/{employee_id}/activate")
    def activate_employee(self, employee_id: UUID):
        try:
            employee = EmployeeWriterService.activate_employee(employee_id)
            return {"success": True, "id": employee.id}
        except Employee.DoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.patch("/{employee_id}/deactivate")
    def deactivate_employee(self, employee_id: UUID):
        try:
            employee = EmployeeWriterService.deactivate_employee(employee_id)
            return {"success": True, "id": employee.id}
        except Employee.DoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.get("/", response=List[EmployeeListOut])
    @paginate(CursorPagination)
    def get_employees(self, search: str | None = None, active_only: Optional[bool] = None):

        return EmployeeReaderService.get_employees(
            search=search,
            active_only=active_only,
        )

    @route.get("/{employee_id}", response=EmployeeDetailOut)
    def get_employee(self, employee_id: UUID):
        try:
            employee = EmployeeReaderService.get_employee_detail(employee_id)
            return employee
        except Employee.DoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.get("/{employee_id}/profile", response=EmployeeFullProfileOut)
    def get_employee_profile(self, employee_id: UUID):
        try:
            employee = EmployeeReaderService.get_employee_full_profile(employee_id)
            return employee
        except Employee.DoesNotExist:
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
        except EmployeeAddress.DoesNotExist:
            raise HttpError(404, "Employee Address not found")

    @route.put("/", response=EmployeeAddressDetailOut)
    def update_address(self, employee_id: UUID, payload: EmployeeAddressUpdateIn):
        try:
            address = EmployeeAddressService.update_address(
                employee_id, 
                **payload.dict(exclude_unset=True)
            )
            return address
        except EmployeeAddress.DoesNotExist:
            raise HttpError(404, "Employee Address not found")

