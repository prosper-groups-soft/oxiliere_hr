from uuid import UUID
from hr.employees.models import EmployeeChildren, Employee


class EmployeeChildrenWriterService:
    """
    Handles creation, update, and deletion of employee children records.
    """

    @staticmethod
    def add_child(employee_id: UUID, **data) -> EmployeeChildren:
        """
        Adds a new child record for the given employee.
        """
        employee = Employee.objects.get(id=employee_id)
        child = EmployeeChildren.objects.create(parent=employee, **data)
        return child

    @staticmethod
    def update_child(child_id: UUID, **data) -> EmployeeChildren:
        """
        Updates an existing child record.
        Accepts kwargs corresponding to EmployeeChildren fields.
        """
        child = EmployeeChildren.objects.get(id=child_id)
        for k, v in data.items():
            setattr(child, k, v)
        child.save()
        return child

    @staticmethod
    def remove_child(child_id: UUID) -> None:
        """
        Deletes a child record.
        """
        EmployeeChildren.objects.filter(id=child_id).delete()


class EmployeeChildrenReaderService:
    """
    Handles retrieval and search of EmployeeChildren records.
    """

    @staticmethod
    def get_child(child_id: UUID) -> EmployeeChildren:
        """
        Retrieves a single child record by its ID.
        """
        return EmployeeChildren.objects.get(id=child_id)

    @staticmethod
    def get_for_employee(employee_id: UUID):
        """
        Returns all children records for a given employee.
        """
        return EmployeeChildren.objects.filter(employee_id=employee_id)

    @staticmethod
    def search(employee_id: UUID = None, name: str = None, **filters):
        """
        Searches for children records based on given criteria.
        """
        # Ensure the employee exists first to avoid orphan searches
        Employee.objects.get(id=employee_id)
        qs = EmployeeChildren.objects.all()
        if employee_id:
            qs = qs.filter(parent_id=employee_id)
        if name:
            qs = qs.filter(name__icontains=name)

        return qs.filter(**filters)

