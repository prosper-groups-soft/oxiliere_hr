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
    CAMEROON = "CM", _("Cameroon")
    GABON = "GA", _("Gabon")
    ANGOLA = "AO", _("Angola")
    CONGO_BRAZZAVILLE = "CG", _("Congo-Brazzaville")
    IVORY_COAST = "CI", _("Côte d'Ivoire")
    ALGERIA = "DZ", _("Algeria")
    MOROCCO = "MA", _("Morocco")
    TUNISIA = "TN", _("Tunisia")
    SENEGAL = "SN", _("Senegal")
    MALI = "ML", _("Mali")
    BURKINA_FASO = "BF", _("Burkina Faso")
    NIGER = "NE", _("Niger")
    CHAD = "TD", _("Chad")
    CENTRAL_AFRICAN_REPUBLIC = "CF", _("Central African Republic")
    EQUATORIAL_GUINEA = "GQ", _("Equatorial Guinea")
    RWANDA = "RW", _("Rwanda")
    BURUNDI = "BI", _("Burundi")
    UGANDA = "UG", _("Uganda")
    KENYA = "KE", _("Kenya")
    TANZANIA = "TZ", _("Tanzania")
    MOZAMBIQUE = "MZ", _("Mozambique")
    ZAMBIA = "ZM", _("Zambia")
    ZIMBABWE = "ZW", _("Zimbabwe")
    BOTSWANA = "BW", _("Botswana")
    NAMIBIA = "NA", _("Namibia")
    ESCHWATINI = "SZ", _("Eswatini")
    LESOTHO = "LS", _("Lesotho")
    MALAWI = "MW", _("Malawi")
    GAMBIA = "GM", _("Gambia")
    SIERRA_LEONE = "SL", _("Sierra Leone")
    LIBERIA = "LR", _("Liberia")
    GHANA = "GH", _("Ghana")
    NIGERIA = "NG", _("Nigeria")
    SOUTH_AFRICA = "ZA", _("South Africa")
    EGYPT = "EG", _("Egypt")
    LIBYA = "LY", _("Libya")
    ETHIOPIA = "ET", _("Ethiopia")
    ERITREA = "ER", _("Eritrea")
    DJIBOUTI = "DJ", _("Djibouti")
    SOMALIA = "SO", _("Somalia")
    SUDAN = "SD", _("Sudan")
    SOUTH_SUDAN = "SS", _("South Sudan")
    COMOROS = "KM", _("Comoros")
    MAURITIUS = "MU", _("Mauritius")
    SEYCHELLES = "SC", _("Seychelles")
    MADAGASCAR = "MG", _("Madagascar")
    REUNION = "RE", _("Reunion")
    ITALY = "IT", _("Italy")
    SPAIN = "ES", _("Spain")
    NETHERLANDS = "NL", _("Netherlands")
    CHINA = "CN", _("China")
    INDIA = "IN", _("India")
    JAPAN = "JP", _("Japan")
    SOUTH_KOREA = "KR", _("South Korea")
    BRAZIL = "BR", _("Brazil")
    ARGENTINA = "AR", _("Argentina")
    MEXICO = "MX", _("Mexico")
    AUSTRALIA = "AU", _("Australia")
    NEW_ZEALAND = "NZ", _("New Zealand")
    FIJI = "FJ", _("Fiji")


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

