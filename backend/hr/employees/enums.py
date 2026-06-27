from django.utils.translation import gettext_lazy as _
from django.db.models import TextChoices


class AcademicLevel(TextChoices):
    """
    Academic degrees and educational levels tailored 
    for French-speaking systems (DRC).
    """
    
    # Secondary Education
    TENASOSP = "TENASOSP", _('TENASOSP / Brevet')                         # New name for the patent after 8th grade in the DRC
    STATE_DIPLOMA = "STATE_DIPLOMA", _('State Diploma (Diplôme d\'État)') # Crucial in the DRC for hiring
    
    # Higher Education (LMD System)
    ASSOCIATE = "ASSOCIATE", _("Associate's Degree (Graduat/BTS)")
    BACHELOR = "BACHELOR", _("Bachelor's Degree (Licence LMD)")
    MASTER = "MASTER", _("Master's Degree (DEA)")
    DOCTORATE = "DOCTORATE", _('Doctorate (PhD)')
    
    # Professional
    VOCATIONAL = "VOCATIONAL", _("Vocational Training (Formation Professionnelle)")
    NOT_SPECIFIED = "NOT_SPECIFIED", _('Not specified')


class MaritalStatus(TextChoices):
    """Legal marital status."""
    SINGLE = "SINGLE", _("Single")
    MARRIED = "MARRIED", _("Married")
    DIVORCED = "DIVORCED", _("Divorced")
    WIDOWED = "WIDOWED", _("Widowed")
    DOMESTIC_PARTNERSHIP = "DOMESTIC_PARTNERSHIP", _("Domestic Partnership")


class RelationshipType(TextChoices):
    """Type of kinship for emergency contacts or dependents."""
    PARENT = "PARENT", _('Parent')
    CHILD = "CHILD", _('Child')
    SIBLING = "SIBLING", _('Sibling')
    FRIEND = "FRIEND", _('Friend')
    SPOUSE = "SPOUSE", _('Spouse')
    PARTNER = "PARTNER", _("Partner")
    OTHER = "OTHER", _('Other')


class EmployeeStatus(TextChoices):
    """Employee lifecycle and activity status."""
    ACTIVE = "ACTIVE", _("Active")
    PROBATION = "PROBATION", _("Probation")
    PENDING = "PENDING", _("Pending")
    SUSPENDED = "SUSPENDED", _("Suspended")
    MATERNITY_LEAVE = "MATERNITY_LEAVE", _("Maternity/Paternity Leave")
    SICK_LEAVE = "SICK_LEAVE", _("Long-term Sick Leave")
    SABBATICAL = "SABBATICAL", _("Sabbatical")
    TERMINATED = "TERMINATED", _("Terminated")
    RESIGNED = "RESIGNED", _("Resigned")
    RETIRED = "RETIRED", _("Retired")


class DocumentType(TextChoices):
    """Official and administrative document categories."""
    NATIONAL_ID = "NATIONAL_ID", _("National Identity Card")
    PASSPORT = "PASSPORT", _("Passport")
    VOTER_CARD = "VOTER_CARD", _("Voter Card")
    DRIVING_LICENSE = "DRIVING_LICENSE", _("Driving License")
    DIPLOMA = "DIPLOMA", _("Diploma / Degree")
    CERTIFICATE = "CERTIFICATE", _("Professional Certificate")
    RESIDENCE_PERMIT = "RESIDENCE_PERMIT", _("Residence Permit")
    CRIMINAL_RECORD = "CRIMINAL_RECORD", _("Criminal Record Check")
    PHOTO = "PHOTO", _("Profile Photo")
    OTHER = "OTHER", _("Other Document")

