from typing import Any, Optional
from uuid import UUID
from django.db import transaction, models
from django.db.models import QuerySet
from django.utils import timezone
from hr.employees.models import Employee, EmployeeAddress
from utils_mixins.fn import create_unset_address
from hr.utils import get_matricule_seq_key
from sequences import get_next_value


class EmployeeWriterService:
    """
    Handles creation, update, deactivation of Employee.
    Manages HR data, primary address, and optional linkage 
    to a User account.
    """
    
    @staticmethod
    @transaction.atomic
    def create_employee(**data) -> Employee:
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
    def set_employee_active_status(employee_id: UUID, status: bool) -> Employee:
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
        return EmployeeWriterService.set_employee_active_status(employee_id, status=True)

    @staticmethod
    def deactivate_employee(employee_id: UUID) -> Employee:
        """
        Desactive an employee
        """
        return EmployeeWriterService.set_employee_active_status(employee_id, status=False)

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
    def get_employee_by_id(employee_id: UUID) -> Employee | None:
        return Employee.objects.get(id=employee_id)
        

    @staticmethod
    def get_employees(
        search: str | None = None,
        active_only: Optional[bool] = None,
    ) -> QuerySet[Employee]:
        queryset = EmployeeReaderService.base_queryset()

        if active_only is not None :
            queryset = queryset.filter(is_active=active_only)

        if search:
            queryset = queryset.filter(
                models.Q(first_name__icontains=search)
                | models.Q(last_name__icontains=search)
                | models.Q(middle_name__icontains=search)
                | models.Q(email__icontains=search)
                | models.Q(phone__icontains=search)
            )

        return queryset

    @staticmethod
    def get_employee_detail(employee_id: UUID) -> Employee | None:
        return EmployeeReaderService.detail_queryset().filter(id=employee_id).first()

    @staticmethod
    def get_employee_full_profile(employee_id: UUID) -> Employee | None:
        return EmployeeReaderService.full_profile_queryset().filter(id=employee_id).first()


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
