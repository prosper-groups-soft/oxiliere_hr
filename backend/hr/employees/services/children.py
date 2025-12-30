from uuid import UUID
from django.db.models import QuerySet, Q
from hr.employees.models import EmployeeChildren, Employee
from hr.employees.schemas import EmployeeChildrenFilterIn


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
    def get_children(
        *,
        employee_id: UUID,
        filters: EmployeeChildrenFilterIn,
    ) -> QuerySet[EmployeeChildren]:

        # Check employee existence
        Employee.objects.get(id=employee_id)

        qs = EmployeeChildren.objects.filter(parent_id=employee_id)

        # Text search
        if filters.search:
            qs = qs.filter(
                Q(first_name__icontains=filters.search) |
                Q(middle_name__icontains=filters.search) |
                Q(last_name__icontains=filters.search)
            )
            
        if filters.gender:
            qs = qs.filter(gender=filters.gender)


        return qs

