from ninja.orm import ModelSchema
from .models import Bank, BankAccount, BankAccountHistory 
from hr.employees.schemas import EmployeeDetailOut


# ----------------------- Bank ModelSchema -----------------------------
BANK_FIELDS = [
    "name", 
    "code", 
    "swift_code", 
    "country", 
    "country_code", 
    "is_active"
]
class BankCreateIn(ModelSchema):

    class Meta:
        model = Bank
        fields = BANK_FIELDS
        fields_optional = [
            "swift_code",
            "country",
            "country_code",
            "is_active",
        ]


class BankUpdateIn(ModelSchema):

    class Meta:
        model = Bank
        fields = BANK_FIELDS
        fields_optional = "__all__"


class BankDetailOut(ModelSchema):

    class Meta:
        model = Bank
        model_fields = "__all__"


# ----------------------- BankAccount ModelSchema  --------------------------------
BANK_ACCOUNT_FIELDS = [
    "account_number", 
    "account_name", 
    "account_type", 
    "iban", 
    "currency",
    "is_primary", 
    "verified", 
    "is_active",
    "notes"
]
class BankAccountCreateIn(ModelSchema):

    class Meta:
        model = BankAccount
        fields = [
            'employee_id',
            'bank_id',
            *BANK_ACCOUNT_FIELDS
        ]
        BANK_ACCOUNT_FIELDS
        fields_optional = [
            "account_type",
            "currency",
            "verified",
            "is_active",
            "notes",
        ]


class BankAccountUpdateIn(ModelSchema):

    class Meta:
        model = BankAccount
        fields = BANK_ACCOUNT_FIELDS
        model_fields_optional = "__all__"


class BankAccountDetailOut(ModelSchema):
    employee: EmployeeDetailOut
    bank: BankDetailOut

    class Meta:
        model = BankAccount
        fields = "__all__" 
    

# --------------------  BankAccountHistory ModelSchema  ------------------------
BANK_ACCOUNT_HISTORY_FIELDS = [ 
    "action", 
    "changed_fields", 
    "notes"
]
class BankAccountHistoryCreateIn(ModelSchema):
    
    class Meta:
        model = BankAccountHistory
        fields = [
            'bank_account_id',
            *BANK_ACCOUNT_HISTORY_FIELDS
        ]
        fields_optional = ["notes"]


class BankAccountHistoryUpdateIn(ModelSchema):
    
    class Meta:
        model = BankAccountHistory
        fields = BANK_ACCOUNT_HISTORY_FIELDS
        fields_optional = "__all__"


class BankAccountHistoryDetailOut(ModelSchema):
    bank_account: BankAccountDetailOut
    
    class Meta:
        model = BankAccountHistory
        fields = "__all__"

