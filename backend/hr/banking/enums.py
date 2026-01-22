from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class AccountType(TextChoices):
    CHECKING = "CHECKING", _('Checking account')    # Checking account
    SAVINGS = "SAVINGS", _('Savings account')       # Savings account
    SALARY = "SALARY", _('Salary account')          # Salary account
    OTHER = "OTHER", _('Other')                     # Other


class BankAccountAction(TextChoices):
    CREATED = "CREATED", _('Created')
    UPDATED = "UPDATED", _('Updated')
    VERIFIED = "VERIFIED", _('Verified')
    UNVERIFIED = "UNVERIFIED", _('Unverified')
    ACTIVATED = "ACTIVATED", _('Activated')
    DEACTIVATED = "DEACTIVATED", _('Deactivated')
    SET_PRIMARY = "SET_PRIMARY", _('Set Primary')
    DELETED = "DELETED", _('Deleted')

