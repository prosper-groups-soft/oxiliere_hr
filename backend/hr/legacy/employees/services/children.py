from hr.employees.models import EmployeeChildren, Employee


class EmployeeChildrenWriterService:
    """
    Handles creation, update, and deletion of employee children records.
    """

    @staticmethod
    def add_child(employee: Employee, **data) -> EmployeeChildren:
        """
        Adds a new child record for the given employee.
        """
        child = EmployeeChildren.objects.create(employee=employee, **data)
        return child

    @staticmethod
    def update_child(child_id: int, **data) -> EmployeeChildren:
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
    def remove_child(child_id: int) -> None:
        """
        Deletes a child record.
        """
        EmployeeChildren.objects.filter(id=child_id).delete()


class EmployeeChildrenReaderService:
    """
    Handles retrieval and search of EmployeeChildren records.
    """

    @staticmethod
    def get_child(child_id: int) -> EmployeeChildren:
        """
        Retrieves a single child record by its ID.
        """
        return EmployeeChildren.objects.get(id=child_id)

    @staticmethod
    def get_for_employee(employee_id: int):
        """
        Returns all children records for a given employee.
        """
        return EmployeeChildren.objects.filter(employee_id=employee_id)

    @staticmethod
    def search(employee_id: int = None, name: str = None, **filters):
        """
        Searches for children records based on given criteria.
        """
        qs = EmployeeChildren.objects.all()
        if employee_id:
            qs = qs.filter(employee_id=employee_id)
        if name:
            qs = qs.filter(name__icontains=name)

        return qs.filter(**filters)
