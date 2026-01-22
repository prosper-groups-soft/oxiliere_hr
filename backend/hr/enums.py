from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _

"""
Common enums used across the project.
"""


class GenderStatus(TextChoices):
    """Gender identity for civil status."""
    MALE = "MALE", _('Male')
    FEMALE = "FEMALE", _('Female')
    NOT_SPECIFIED = "NOT_SPECIFIED", _('Not specified')


class WorkerType(TextChoices):
    """Nature of the worker relationship with the company."""
    PERMANENT = "PERMANENT", _('Permanent Worker')
    COLLABORATOR = "COLLABORATOR", _('Internal Collaborator')
    CONSULTANT = "CONSULTANT", _('External Consultant')
    INTERN = "INTERN", _('Intern')
    FREELANCE = "FREELANCE", _('Freelance / Contractor')
    TEMPORARY = "TEMPORARY", _('Temporary Worker')


class CountryCode(TextChoices):
    """ISO Country codes for nationalities and addresses."""
    DRC = "CD", _("Congo (Democratic Republic of the Congo)")
    FRANCE = "FR", _("France")
    BELGIUM = "BE", _("Belgium")
    UNITED_STATES = "US", _("United States")
    CANADA = "CA", _("Canada")
    UNITED_KINGDOM = "GB", _("United Kingdom")
    GERMANY = "DE", _("Germany")
    

class WeekdayEnum(TextChoices):
    MONDAY = "MONDAY", _("Monday")
    TUESDAY = "TUESDAY", _("Tuesday")
    WEDNESDAY = "WEDNESDAY", _("Wednesday")
    THURSDAY = "THURSDAY", _("Thursday")
    FRIDAY = "FRIDAY", _("Friday")
    SATURDAY = "SATURDAY", _("Saturday")
    SUNDAY = "SUNDAY", _("Sunday")
    
    
class Currency(TextChoices):
    CDF = "CDF", _('Congolese Franc')      # Congolese Franc
    USD = "USD", _('US Dollar')            # US Dollar
    EUR = "EUR", _('Euro')                 # Euro

