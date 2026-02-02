from hr.schemas import LightUserOut
from typing import Optional
from ninja import Schema
from ninja.orm import ModelSchema
from uuid import UUID

from .models import (
    Bank,
    BankAccount,
    BankAccountHistory 
)
from hr.employees.schemas import EmployeeOut


# ----------------------- Bank Schemas -----------------------------

class BankCreateIn(ModelSchema):
    """ Data required to register a new financial institution. """
    class Meta:
        model = Bank
        fields = ["name", "code", "swift_code", "country_code", "is_mobile_money", "is_active"]
        fields_optional = ["swift_code", "country_code", "is_mobile_money", "is_active"]


class BankUpdateIn(ModelSchema):
    """ Schema for updating existing bank metadata. """
    class Meta:
        model = Bank
        fields = ["name", "code", "swift_code", "country_code", "is_mobile_money", "is_active"]
        fields_optional = "__all__"


class BankOut(ModelSchema):
    """ Public bank details for API responses. """
    id: UUID
    class Meta:
        model = Bank
        fields = ["id", "name", "code", "swift_code", "country_code", "is_mobile_money", "is_active", "created_at", "updated_at"]


# ----------------------- BankAccount Schemas --------------------------------

class BankAccountCreateIn(Schema):
    """ Input data for setting up a new employee payment account. """
    employee_id: UUID
    bank_id: UUID
    account_number: str
    account_name: str
    account_type: str = "CHECKING"
    currency: str = "CDF"
    branch_code: Optional[str] = None
    iban: Optional[str] = None
    is_primary: bool = False
    verified: bool = False
    document_proof: Optional[str] = None
    notes: Optional[str] = None

class BankAccountUpdateIn(Schema):
    """ Parameters for modifying employee bank account settings. """
    bank_id: Optional[UUID] = None
    account_number: Optional[str] = None
    account_name: Optional[str] = None
    account_type: Optional[str] = None
    currency: Optional[str] = None
    branch_code: Optional[str] = None
    iban: Optional[str] = None
    is_active: Optional[bool] = None
    notes: Optional[str] = None

class BankAccountOut(ModelSchema):
    """ Detailed view of an employee's payment account. """
    id: UUID
    bank: BankOut
    employee_id: EmployeeOut 
    
    class Meta:
        model = BankAccount
        fields = [
            "id", "employee", "bank", "account_number", "account_name", 
            "account_type", "currency", "branch_code", "iban", 
            "is_primary", "verified", "verified_at", "is_active", 
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

