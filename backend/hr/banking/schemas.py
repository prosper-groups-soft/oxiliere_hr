from hr.schemas import BaseFilter, LightUserOut
from django.db.models import Q
from typing import Optional
from ninja  import Field, Schema
from ninja.orm import ModelSchema
from uuid      import UUID

from .models import (
    Bank,
    BankAccount,
    BankAccountHistory 
)
from .enums import AccountStatus
from hr.employees.schemas import EmployeeOut


# ----------------------- Account Filter Schema -----------------------------

class BankAccountFilterIn(BaseFilter):
    """ Filtering criteria for bank accounts list. """
    currency: Optional[str] = None  # single currency to match against currencies list
    is_primary: Optional[bool] = None
    status: Optional[str] = Field(None, q="status")
    bank_id: Optional[str] = Field(None, q="bank__id__exact")

    def filter_search(self, value: str) -> Q:
        return (
            Q(account_name__icontains=value) |
            Q(account_number__icontains=value) |
            Q(employee__first_name__icontains=value) |
            Q(employee__last_name__icontains=value) |
            Q(bank__name__icontains=value) |
            Q(bank__code__icontains=value)
        )

    def filter_currency(self, value: str) -> Q:
        """Currency is a JSONField — use containment lookup."""
        return Q(currencies__contains=[value]) if value else Q()

    def apply_ordering(self, qs, ordering: Optional[str] = None):
        if not ordering:
            return qs.order_by('-created_at')
        ordering_map = {
            'account_name': ['account_name'],
            '-account_name': ['-account_name'],
            'created_at': ['created_at'],
            '-created_at': ['-created_at'],
            'employee_name': ['employee__first_name', 'employee__last_name'],
            '-employee_name': ['-employee__first_name', '-employee__last_name'],
        }
        order_fields = ordering_map.get(ordering, ['-created_at'])
        return qs.order_by(*order_fields)


# ----------------------- Bank Schemas -----------------------------

class BankCreateIn(Schema):
    """ Data required to register a new financial institution. """
    name: str
    code: str
    swift_code: Optional[str] = None
    is_mobile_money: bool = False
    country_code: Optional[str] = None
    is_active: bool = True



class BankUpdateIn(Schema):
    """ Schema for updating existing bank metadata. """
    name: Optional[str] = None
    code: Optional[str] = None
    swift_code: Optional[str] = None
    is_mobile_money: Optional[bool] = None
    country_code: Optional[str] = None
    is_active: Optional[bool] = None


class BankOut(ModelSchema):
    """ Public bank details for API responses. """
    id: UUID
    class Meta:
        model = Bank
        fields = ["id", "name", "code", "swift_code", "country_code", "logo", "is_mobile_money", "is_active", "created_at", "updated_at"]


class BankSeedInstitution(Schema):
    """ An institution available for seeding, from the fixture. """
    code: str
    name: str
    is_mobile_money: bool
    exists: bool = False


class BankSeedIn(Schema):
    """ Input for seeding banks — optional list of codes to seed only selected ones. """
    codes: Optional[list[str]] = None


class BankSeedOut(Schema):
    """ Response for the seed banks endpoint. """
    created: list[str]
    created_count: int
    skipped: list[str]
    skipped_count: int


# ----------------------- BankAccount Schemas --------------------------------

class BankAccountCreateIn(Schema):
    """ Input data for setting up a new employee payment account. """
    employee_id: UUID
    bank_id: UUID
    account_number: str
    account_name: str
    account_type: str = "CHECKING"
    currencies: list[str] = ["USD"]
    default_currency: str = "USD"
    branch_code: Optional[str] = None
    iban: Optional[str] = None
    is_primary: bool = False
    status: str = "PENDING"
    notes: Optional[str] = None

class BankAccountUpdateIn(Schema):
    """ Parameters for modifying employee bank account settings. """
    employee_id: Optional[UUID] = None
    bank_id: Optional[UUID] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    currencies: Optional[list[str]] = None
    default_currency: Optional[str] = None
    branch_code: Optional[str] = None
    iban: Optional[str] = None
    is_primary: Optional[bool] = None
    status: Optional[str] = None
    notes: Optional[str] = None

class BankAccountOut(ModelSchema):
    """ Detailed view of an employee's payment account. """
    id: UUID
    bank: BankOut
    employee: EmployeeOut
    currencies: list[str]
    default_currency: str

    class Meta:
        model = BankAccount
        fields = [
            "id", "employee", "bank", "account_number", "account_name", 
            "account_type", "currencies", "default_currency", "branch_code", "iban", 
            "is_primary", "status", "verified_at", "notes",
            "created_at", "updated_at"
        ]

# --------------------  BankAccountHistory Schemas ------------------------

class BankAccountHistoryOut(ModelSchema):
    """ Audit record for a specific bank account change. """
    id: UUID
    bank_account: BankAccountOut
    created_by: Optional[LightUserOut] = None
    
    class Meta:
        model = BankAccountHistory
        fields = [
            "id", "action", "changed_fields", "notes", 
            "created_at", "bank_account", "created_by"
        ]

