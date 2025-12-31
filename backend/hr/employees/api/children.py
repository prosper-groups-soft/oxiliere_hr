from typing import List
from uuid import UUID
from ninja import Query
from ninja_extra import api_controller, ControllerBase, route
from ninja.errors import HttpError
from django.core.exceptions import ObjectDoesNotExist

from hr.employees.schemas import (
    EmployeeChildrenCreateIn,
    EmployeeChildrenUpdateIn,
    EmployeeChildrenDetailOut,
    EmployeeChildrenFilterIn
)
from hr.employees.services import (
    EmployeeChildrenWriterService,
    EmployeeChildrenReaderService
)


@api_controller(
    "/employees/{employee_id}/children", 
    tags=["Employee Children"]
)
class EmployeeChildrenAPI(ControllerBase):
    """
    API for managing employee's children records.
    """

    @route.get("/{child_id}", response=EmployeeChildrenDetailOut)
    def get_child(self, employee_id: UUID, child_id: UUID):
        """
        Retrieve a specific child record.
        """
        try:
            child = EmployeeChildrenReaderService.get_child(child_id)
            if child.parent_id != employee_id:
                raise HttpError(403, "Child does not belong to this employee")
            return child
        except ObjectDoesNotExist:
            raise HttpError(404, "Child not found")
    
    @route.get("/", response=List[EmployeeChildrenDetailOut])
    def get_children(
        self,
        employee_id: UUID,
        filters: EmployeeChildrenFilterIn = Query(...)
    ):
        try:
            return EmployeeChildrenReaderService.get_children(
                employee_id=employee_id,
                filters=filters,
            )
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")           
            
    @route.post("/", response=EmployeeChildrenDetailOut)
    def add_child(self, employee_id: UUID, payload: EmployeeChildrenCreateIn):
        """
        Create a new child record.
        """
        try:
            return EmployeeChildrenWriterService.add_child(
                employee_id, 
                **payload.dict(exclude_unset=True)
            )
        except ObjectDoesNotExist:
            raise HttpError(404, "Employee not found")

    @route.put("/{child_id}", response=EmployeeChildrenDetailOut)
    def update_child(self, employee_id: UUID, child_id: UUID, payload: EmployeeChildrenUpdateIn):
        """
        Update a child record.
        """
        try:
            child = EmployeeChildrenReaderService.get_child(child_id)
            if child.employee_id != employee_id:
                raise HttpError(403, "Child does not belong to this employee")
            
            return EmployeeChildrenWriterService.update_child(
                child_id, 
                **payload.dict(exclude_unset=True)
            )
        except ObjectDoesNotExist:
            raise HttpError(404, "Child not found")

    @route.delete("/{child_id}")
    def remove_child(self, employee_id: UUID, child_id: UUID):
        """
        Delete a child record.
        """
        try:
            child = EmployeeChildrenReaderService.get_child(child_id)
            if child.parent_id != employee_id:
                raise HttpError(403, "Child does not belong to this employee")
            
            EmployeeChildrenWriterService.remove_child(child_id)
            return {"success": True}
        except ObjectDoesNotExist:
            raise HttpError(404, "Child not found")
        
