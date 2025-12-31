from uuid import UUID
from django.db import transaction
from django.db.models import QuerySet, Q 
from hr.employees.models import EmployeeChildren, Employee
from hr.employees.schemas import EmployeeChildrenFilterIn
from hr.utils.fn import update_instance


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
    @transaction.atomic
    def update_child(child_id: UUID, **data) -> EmployeeChildren:
        """
        Updates allowed fields of an employee's child record.
        """
        # Récupération de l'instance
        child = EmployeeChildren.objects.get(id=child_id)

        # Appel au helper générique
        return update_instance(
            instance=child,
            allowed_fields={
                "first_name",
                "middle_name",
                "last_name",
                "birth_date",
                "gender",
                "description",
            },
            data=data,
        )

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
        """
        Retrieve children for a specific employee with filtering.
        """
        Employee.objects.get(id=employee_id)

        qs = EmployeeChildren.objects.filter(parent_id=employee_id)

        return filters.filter(qs)

