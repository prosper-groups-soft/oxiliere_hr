from enum import Enum


class AccountType(str, Enum):
    CHECKING = "CHECKING"      # Checking account
    SAVINGS = "SAVINGS"        # Savings account
    SALARY = "SALARY"          # Salary account
    OTHER = "OTHER"            # Other


class Currency(str, Enum):
    CDF = "CDF"  # Congolese Franc
    USD = "USD"  # US Dollar
    EUR = "EUR"  # Euro


class BankAccountAction(str, Enum):
    CREATED = "CREATED"
    UPDATED = "UPDATED"
    VERIFIED = "VERIFIED"
    UNVERIFIED = "UNVERIFIED"
    ACTIVATED = "ACTIVATED"
    DEACTIVATED = "DEACTIVATED"
    SET_PRIMARY = "SET_PRIMARY"
