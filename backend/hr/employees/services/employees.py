from typing import Any
from django.db import transaction, models
from django.utils import timezone
from django.core.exceptions import ObjectDoesNotExist
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
    def create_employee(
        first_name: str,
        last_name: str,
        birthdate,
        gender: str,
        email=None,
        phone=None,
        middle_name=None,
        marital_status=None,
        description=None,
        user: Any | None = None
    ) -> Employee:
        """
        Creates an employee with a primary address, generated matricule,
        and optional linkage to a system User.
        """
        # Création de l'adresse primaire
        address = create_unset_address(user=user, model=EmployeeAddress)
        marital_status = marital_status or Employee._meta.get_field('marital_status').default
        
        employee = Employee(
            first_name=first_name,
            middle_name=middle_name,
            last_name=last_name,
            birthdate=birthdate,
            gender=gender,
            email=email,
            phone=phone,
            marital_status=marital_status,
            description=description,
            address=address,
            user=user
        )

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
    def update_employee(employee_id: int, **kwargs) -> Employee:
        """
        Updates employee fields (excluding address, which is handled separately).
        Supports updating the linked user account.
        """
        try:
            employee = Employee.objects.get(id=employee_id)
        except ObjectDoesNotExist:
            raise ValueError(f"Employee {employee_id} does not exist")

        for field, value in kwargs.items():
            if hasattr(employee, field) and field != "address":
                setattr(employee, field, value)

        employee.save()
        return employee

    @staticmethod
    @transaction.atomic
    def link_user(employee_id: int, user: Any) -> Employee:
        """
        Links an existing User account to the Employee.
        """
        employee = Employee.objects.get(id=employee_id)
        employee.user = user
        employee.save()
        return employee

    @staticmethod
    @transaction.atomic
    def unlink_user(employee_id: int) -> Employee:
        """
        Unlinks the User account from the Employee without deleting the User.
        """
        employee = Employee.objects.get(id=employee_id)
        employee.user = None
        employee.save()
        return employee

    @staticmethod
    @transaction.atomic
    def deactivate_employee(employee_id: int) -> Employee:
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

    @staticmethod
    def get_employee_by_id(employee_id: int) -> Employee | None:
        """
        Retrieve a single employee by ID.
        Returns None if not found.
        """
        try:
            return Employee.objects.get(id=employee_id)
        except Employee.DoesNotExist:
            return None

    @staticmethod
    def list_employees(active_only: bool = True):
        """
        Returns a QuerySet of all employees.
        Can filter by active status if active_only is True.
        """
        queryset = Employee.objects.all()
        if active_only:
            queryset = queryset.filter(is_active=True)
        return queryset

    @staticmethod
    def search_employees(name: str = None, email: str = None, phone: str = None):
        """
        Flexible search across name, email, and phone.
        Returns a QuerySet to allow chaining additional filters.
        """
        queryset = Employee.objects.all()

        if name:
            queryset = queryset.filter(
                models.Q(first_name__icontains=name) |
                models.Q(last_name__icontains=name) |
                models.Q(middle_name__icontains=name)
            )

        if email:
            queryset = queryset.filter(email__icontains=email)

        if phone:
            queryset = queryset.filter(phone__icontains=phone)

        return queryset


class EmployeeAddressService:
    """
    Handles operations related to Employee addresses.
    Primary address creation is managed by EmployeeWriterService.
    """

    @staticmethod
    def get_address(employee_id: int) -> EmployeeAddress | None:
        """
        Retrieves the primary address of an employee.
        """
        try:
            employee = Employee.objects.get(id=employee_id)
            return employee.address
        except Employee.DoesNotExist:
            return None

    @staticmethod
    @transaction.atomic
    def update_address(employee_id: int, **kwargs) -> EmployeeAddress:
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
