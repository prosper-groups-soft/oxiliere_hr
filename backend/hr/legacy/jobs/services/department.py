from typing import Optional
from django.db import transaction
from django.core.exceptions import ValidationError
from hr.jobs.models import Department
from hr.employees.models import Employee


# -----------------------------------------------------------------
# Department Reader / Writer
# -----------------------------------------------------------------
class DepartmentWriterService:
    """
    Writer for Department: create, update, assign/unassign manager, delete.
    Business rules:
      - A single employee cannot manage more than one department.
    """

    @staticmethod
    @transaction.atomic
    def create(
        name: str, 
        description: str = "", 
        manager: Optional[Employee] = None
    ) -> Department:
        """
        Create a Department. If a manager is provided, ensure they don't 
        already manage another department.
        """
        if manager and Department.objects.filter(manager=manager).exists():
            raise ValidationError(
                f"Employee {manager.id} already manages another department."
            )
        dept = Department(
            name=name.strip().title(), 
            description=description, 
            manager=manager
        )
        dept.full_clean()
        dept.save()
        return dept

    @staticmethod
    @transaction.atomic
    def update(dept_id: int, **kwargs) -> Department:
        """
        Update Department fields. Validates manager uniqueness when manager is updated.
        """
        try:
            dept = Department.objects.get(id=dept_id)
        except Department.DoesNotExist:
            raise ValueError(f"Department {dept_id} not found")

        if "name" in kwargs and kwargs["name"]:
            kwargs["name"] = kwargs["name"].strip().title()

        manager = kwargs.get("manager", None)
        if manager:
            if Department.objects.exclude(id=dept_id).filter(manager=manager).exists():
                raise ValidationError(
                    f"Employee {manager.id} already manages another department."
                )

        for field, value in kwargs.items():
            if hasattr(dept, field):
                setattr(dept, field, value)

        dept.full_clean()
        dept.save()
        return dept

    @staticmethod
    @transaction.atomic
    def assign_manager(dept_id: int, manager: Employee) -> Department:
        """
        Assign a manager to a department after checking uniqueness.
        """
        if Department.objects.exclude(id=dept_id).filter(manager=manager).exists():
            raise ValidationError(
                f"Employee {manager.id} already manages another department."
            )
        dept = Department.objects.get(id=dept_id)
        dept.manager = manager
        dept.save()
        return dept

    @staticmethod
    @transaction.atomic
    def unassign_manager(dept_id: int) -> Department:
        """
        Remove manager assignment from a department.
        """
        dept = Department.objects.get(id=dept_id)
        dept.manager = None
        dept.save()
        return dept

    @staticmethod
    @transaction.atomic
    def delete(dept_id: int) -> None:
        dept = Department.objects.get(id=dept_id)
        dept.delete()


class DepartmentReaderService:
    """
    Reader for Department: single retrieval, listing and searching.
    """

    @staticmethod
    def get(dept_id: int) -> Optional[Department]:
        return Department.objects.filter(id=dept_id).select_related("manager").first()

    @staticmethod
    def list_all():
        return Department.objects.select_related("manager").all()

    @staticmethod
    def search(name: str):
        return Department.objects.filter(name__icontains=name.strip())

