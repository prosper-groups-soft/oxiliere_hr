from typing import Any, Optional
from uuid import UUID
from django.db import transaction, models
from django.db.models import QuerySet
from django.utils import timezone
from hr.employees.models import Employee, EmployeeAddress
from utils_mixins.fn import create_unset_address
from hr.utils import get_matricule_seq_key
from sequences import get_next_value
from hr.employees.schemas import EmployeeFilterIn


class EmployeeWriterService:
    """
    Handles creation, update, deactivation of Employee.
    Manages HR data, primary address, and optional linkage 
    to a User account.
    """
    
    @staticmethod
    @transaction.atomic
    def add_employee(**data) -> Employee:
        """
        Create an employee with:
        - optional user
        - optional address (auto-created if missing)
        - auto-generated matricule if not provided
        """

        user = data.pop("user", None)
        address = data.pop("address", None)
        matricule = data.pop("matricule", None)

        if not address:
            address = create_unset_address(
                user=user,
                model=EmployeeAddress,
            )

        if "marital_status" not in data:
            data["marital_status"] = Employee._meta.get_field(
                "marital_status"
            ).default

        employee = Employee(
            **data,
            user=user,
            address=address,
        )

        if matricule:
            employee.matricule = matricule
        else:
            EmployeeWriterService.generate_matricule(employee)

        employee.save()
        return employee

    @staticmethod
    def generate_matricule(employee: Employee) -> None:
        """
        Generates a unique matricule for the employee.
        Format: EMP-<year>-<sequence number>
        """
        year = timezone.now().year
        number = get_next_value(get_matricule_seq_key())
        employee.matricule = f"EMP-{year}-{number:05d}"

    @staticmethod
    @transaction.atomic
    def update_employee(employee_id: UUID, **kwargs) -> Employee:
        """
        Updates employee fields (excluding address, which is handled separately).
        Supports updating the linked user account.
        """
        employee = Employee.objects.get(id=employee_id)

        for field, value in kwargs.items():
            if hasattr(employee, field) and field != "address":
                setattr(employee, field, value)

        employee.save()
        return employee

    @staticmethod
    @transaction.atomic
    def link_user(employee_id: UUID, user: Any) -> Employee:
        """
        Links an existing User account to the Employee.
        """
        employee = Employee.objects.get(id=employee_id)
        employee.user = user
        employee.save()
        return employee

    @staticmethod
    @transaction.atomic
    def unlink_user(employee_id: UUID) -> Employee:
        """
        Unlinks the User account from the Employee without deleting the User.
        """
        employee = Employee.objects.get(id=employee_id)
        employee.user = None
        employee.save()
        return employee
    
    @staticmethod
    @transaction.atomic
    def set_employee_status_generic(employee_id: UUID, status: bool) -> Employee:
        """
        Generalization for activation and desactivation of an employee.
        """
        employee = Employee.objects.get(id=employee_id)
        employee.is_active = status
        
        if not status:
            employee.can_connect = False
        else:
            employee.can_connect = True 
            
        employee.save()
        return employee

    @staticmethod
    def activate_employee(employee_id: UUID) -> Employee:
        """
        Activate an amployee.
        """
        return EmployeeWriterService.set_employee_status_generic(employee_id, status=True)
    
    @staticmethod
    def deactivate_employee(employee_id: UUID) -> Employee:
        """
        Desactive an employee
        """
        return EmployeeWriterService.set_employee_status_generic(employee_id, status=False)

    @staticmethod
    @transaction.atomic
    def deactivate_employee(employee_id: UUID) -> Employee:
        """
        Soft delete / deactivate an employee.
        """
        employee = Employee.objects.get(id=employee_id)
        employee.is_active = False
        employee.can_connect = False
        employee.save()
        return employee

    @staticmethod
    def remove_employee(employee_id: UUID) -> None:
        """
        Deletes a employee record.
        """
        Employee.objects.get(id=employee_id).delete()


class EmployeeReaderService:
    """
    Handles retrieval and search of Employee records.
    Returns QuerySets for efficiency and allows pagination or chaining filters.
    """

    # ---------- Queryset factories ----------

    @staticmethod
    def base_queryset() -> QuerySet[Employee]:
        return Employee.objects.select_related("user")

    @staticmethod
    def detail_queryset() -> QuerySet[Employee]:
        return Employee.objects.select_related("user", "address")

    @staticmethod
    def full_profile_queryset() -> QuerySet[Employee]:
        return (
            Employee.objects
            .select_related("user", "address")
            .prefetch_related(
                "children",
                "educations",
                "emergency_contacts",
            )
        )

    # ---------- Read operations ----------

    @staticmethod
    def get_employee(employee_id: UUID) -> Employee | None:
        return Employee.objects.get(id=employee_id)

    @staticmethod
    def get_employee_detail(employee_id: UUID) -> Employee | None:
        return EmployeeReaderService.detail_queryset().filter(id=employee_id).first()

    @staticmethod
    def get_employee_full_profile(employee_id: UUID) -> Employee | None:
        return EmployeeReaderService.full_profile_queryset().filter(id=employee_id).first()

    @staticmethod
    def get_employees(*, filters: EmployeeFilterIn) -> QuerySet[Employee]:
        queryset = EmployeeReaderService.base_queryset()

        if filters.active_only is not None:
            queryset = queryset.filter(is_active=filters.active_only)

        if filters.search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=filters.search)
                | models.Q(last_name__icontains=filters.search)
                | models.Q(middle_name__icontains=filters.search)
                | models.Q(email__icontains=filters.search)
                | models.Q(phone__icontains=filters.search)
            )

        for field in ("gender", "marital_status"):
            value = getattr(filters, field)
            if value is not None:
                queryset = queryset.filter(**{field: value})

        if filters.born_before or filters.born_after:
            if filters.born_before:
                queryset = queryset.filter(date_of_birth__lte=filters.born_before)
            if filters.born_after:
                queryset = queryset.filter(date_of_birth__gte=filters.born_after)

        return queryset


class EmployeeAddressService:
    """
    Handles operations related to Employee addresses.
    Primary address creation is managed by EmployeeWriterService.
    """

    @staticmethod
    def get_address(employee_id: UUID) -> EmployeeAddress | None:
        """
        Retrieves the primary address of an employee.
        """
        employee = Employee.objects.get(id=employee_id)
        return employee.address

    @staticmethod
    @transaction.atomic
    def update_address(employee_id: UUID, **kwargs) -> EmployeeAddress:
        """
        Updates fields of the employee's primary address.
        Accepts kwargs corresponding to EmployeeAddress fields.
        """
        employee = Employee.objects.get(id=employee_id)
        address = employee.address
 
        for field, value in kwargs.items():
            if hasattr(address, field):
                setattr(address, field, value)

        address.save()
        return address
