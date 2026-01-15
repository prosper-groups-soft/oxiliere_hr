from django.db.models import TextChoices
from django.utils.translation import gettext_lazy as _


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


class GenderStatus(TextChoices):
    """Gender identity for civil status."""
    MALE = "MALE", _('Male')
    FEMALE = "FEMALE", _('Female')
    NOT_SPECIFIED = "NOT_SPECIFIED", _('Not specified')


class MaritalStatus(TextChoices):
    """Legal marital status."""
    SINGLE = "SINGLE", _("Single")
    MARRIED = "MARRIED", _("Married")
    DIVORCED = "DIVORCED", _("Divorced")
    WIDOWED = "WIDOWED", _("Widowed")
    DOMESTIC_PARTNERSHIP = "DOMESTIC_PARTNERSHIP", _("Domestic Partnership")


class EmployeeStatus(TextChoices):
    """Employee lifecycle and activity status."""
    ACTIVE = "ACTIVE", _("Active")
    PROBATION = "PROBATION", _("Probation")
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
    OTHER = "OTHER", _("Other Document")


class WorkerType(TextChoices):
    """Nature of the worker relationship with the company."""
    PERMANENT = "PERMANENT", _('Permanent Worker')
    COLLABORATOR = "COLLABORATOR", _('Internal Collaborator')
    CONSULTANT = "CONSULTANT", _('External Consultant')
    INTERN = "INTERN", _('Intern')
    FREELANCE = "FREELANCE", _('Freelance / Contractor')
    TEMPORARY = "TEMPORARY", _('Temporary Worker')


class RelationshipType(TextChoices):
    """Type of kinship for emergency contacts or dependents."""
    PARENT = "PARENT", _('Parent')
    CHILD = "CHILD", _('Child')
    SIBLING = "SIBLING", _('Sibling')
    FRIEND = "FRIEND", _('Friend')
    SPOUSE = "SPOUSE", _('Spouse')
    PARTNER = "PARTNER", _("Partner")
    OTHER = "OTHER", _('Other')


class AttendanceStatus(TextChoices):
    """Daily attendance and time tracking statuses."""
    PRESENT = "PRESENT", _('Present')
    ABSENT = "ABSENT", _('Absent')
    LATE = "LATE", _('Late')
    EXCUSED = "EXCUSED", _('Excused Absence')
    HOLIDAY = "HOLIDAY", _('Holiday / Vacation')


class CalendarEventType(TextChoices):
    """Types of events for the HR calendar."""
    HOLIDAY = "HOLIDAY", _('Public Holiday / Time Off')
    MEETING = "MEETING", _('Meeting')
    TRAINING = "TRAINING", _('Training')
    BIRTHDAY = "BIRTHDAY", _('Birthday')
    DEADLINE = "DEADLINE", _('Deadline')
    OTHER = "OTHER", _('Other')


class PaymentType(TextChoices):
    """Remuneration calculation method."""
    FIXED = "FIXED", _('Fixed Salary')
    HOURLY = "HOURLY", _('Hourly Rate')


class ContractType(TextChoices):
    """Employment contract types."""
    CDI = "CDI", _('CDI (Indefinite Contract)')
    CDD = "CDD", _('CDD (Fixed-term Contract)')
    INTERNSHIP = "INTERNSHIP", _('Internship')
    FREELANCE = "FREELANCE", _('Freelance / Service Agreement')
    TEMPORARY = "TEMPORARY", _('Temporary / Interim')


class PaymentPeriod(TextChoices):
    """Payroll frequency."""
    DAILY = "DAILY", _('Daily')
    PER_TASK = "PER_TASK", _('Per Task')
    MONTHLY = "MONTHLY", _('Monthly')


class PayslipStatus(TextChoices):
    """Status of the payslip processing cycle."""
    REVIEW = "REVIEW", _('Under Review')
    CONFIRMED = "CONFIRMED", _('Confirmed')
    PAID = "PAID", _('Paid')
    CANCELED = "CANCELED", _('Canceled')


class CountryCode(TextChoices):
    """ISO Country codes for nationalities and addresses."""
    DRC = "CD", _("Congo (Democratic Republic of the Congo)")
    FRANCE = "FR", _("France")
    BELGIUM = "BE", _("Belgium")
    UNITED_STATES = "US", _("United States")
    CANADA = "CA", _("Canada")
    UNITED_KINGDOM = "GB", _("United Kingdom")
    GERMANY = "DE", _("Germany")
    

class LeaveCategory(TextChoices):
    """
    High-level legal category of leave.
    Determines if it's deductible from annual balance or managed separately.
    """
    ANNUAL = "ANNUAL", _("Annual Leave")              # Deducted from balance
    SICK = "SICK", _("Sick Leave")                    # Outside balance, justified
    CIRCUMSTANCE = "CIRCUMSTANCE", _("Special Leave") # Outside balance, fixed duration
    UNPAID = "UNPAID", _("Unpaid Leave")              # Outside balance
    OTHER = "OTHER", _("Other")



class LeaveStatus(TextChoices):
    """
    Lifecycle of a leave request.
    PENDING -> APPROVED or REJECTED
    APPROVED -> TAKEN (once start_date is passed) or CANCELLED
    """
    PENDING = "PENDING", _("Pending Approval")
    APPROVED = "APPROVED", _("Approved")
    REJECTED = "REJECTED", _("Rejected")
    CANCELLED = "CANCELLED", _("Cancelled")
    # TAKEN is useful for historical reporting once the leave period is over
    TAKEN = "TAKEN", _("Taken / Archived")


class CircumstanceType(TextChoices):
    """
    Specific events based on Labor Law.
    Common durations (for reference in policy config):
    - MARRIAGE_EMPLOYEE: 2-3 days
    - BIRTH_SPOUSE: 2-3 days
    - DEATH_1ST_DEGREE: 4 days (Spouse, Child, Parent)
    - DEATH_2ND_DEGREE: 2 days (Sibling, Grandparent)
    - CHILD_MARRIAGE: 1 day
    """
    MARRIAGE_EMPLOYEE = "MARRIAGE_EMPLOYEE", _("Employee's own marriage")
    BIRTH_SPOUSE = "BIRTH_SPOUSE", _("Birth of spouse's child")
    DEATH_FIRST_DEGREE = "DEATH_FIRST_DEGREE", _("Death of a 1st degree relative")
    DEATH_SECOND_DEGREE = "DEATH_SECOND_DEGREE", _("Death of a 2nd degree relative")
    CHILD_MARRIAGE = "CHILD_MARRIAGE", _("Marriage of employee's child")
    MOVING = "MOVING", _("Relocation / Moving")
    CHILD_HOSPITALIZATION = "CHILD_HOSPITALIZATION", _("Hospitalization of a child")
    OTHER = "OTHER", _("Other legal circumstance")


class WeekdayEnum(TextChoices):
    MONDAY = "MONDAY", _("Monday")
    TUESDAY = "TUESDAY", _("Tuesday")
    WEDNESDAY = "WEDNESDAY", _("Wednesday")
    THURSDAY = "THURSDAY", _("Thursday")
    FRIDAY = "FRIDAY", _("Friday")
    SATURDAY = "SATURDAY", _("Saturday")
    SUNDAY = "SUNDAY", _("Sunday")
    
    
class TimeSheetStatus(TextChoices):
    PRESENT = "PRESENT", _("Present")
    ABSENT = "ABSENT", _("Absent")
    LATE = "LATE", _("Late")
    PARTIAL = "PARTIAL", _("Partial Absence") # New: present but did not complete required hours
    EXCUSED = "EXCUSED", _("Excused")
    ON_LEAVE = "ON_LEAVE", _("On Leave")


class PunchType(TextChoices):
    WORK = "WORK", _("Work")
    BREAK = "BREAK", _("Break")
    MISSION = "MISSION", _("External Mission")  # E.g., client meeting
    PERSONAL = "PERSONAL", _("Personal Leave")  # For "Personal Reason"


class PositionLevel(TextChoices):
    """
    The `level` represents the seniority or career stage.
    """
    TRAINEE = "TRAINEE", _("Trainee")                 # Entry-level training or internship
    APPRENTICE = "APPRENTICE", _("Apprentice")        # Practical learning with mentoring
    JUNIOR = "JUNIOR", _("Junior")                    # First independent work experience
    INTERMEDIATE = "INTERMEDIATE", _("Intermediate")  # Solid experience, some autonomy
    SENIOR = "SENIOR", _("Senior")                    # Advanced expertise, mentoring others
    LEAD = "LEAD", _("Lead")                          # Leads a small team or project
    MANAGER = "MANAGER", _("Manager")                 # Manages a team or functional area
    DIRECTOR = "DIRECTOR", _("Director")              # Manages multiple teams or departments
    EXECUTIVE = "EXECUTIVE", _("Executive")           # Strategic leadership role


class ApplicationStatus(TextChoices):
    PENDING = 'PENDING', _('Pending')
    REVIEW = 'REVIEW', _('Under Review')
    INTERVIEW = 'INTERVIEW', _('Interviewing')
    OFFER = 'OFFER', _('Offer Made')
    ACCEPTED = 'ACCEPTED', _('Accepted')
    REJECTED = 'REJECTED', _('Rejected')
    WITHDRAWN = 'WITHDRAWN', _('Withdrawn')


class InterviewType(TextChoices):
    PHONE = 'PHONE', _('Phone Screen')
    VIDEO = 'VIDEO', _('Video Call')
    ONSITE = 'ONSITE', _('On-site Interview')
    TECHNICAL = 'TECHNICAL', _('Technical Assessment')


class AccountType(TextChoices):
    CHECKING = "CHECKING", _('Checking account')    # Checking account
    SAVINGS = "SAVINGS", _('Savings account')       # Savings account
    SALARY = "SALARY", _('Salary account')          # Salary account
    OTHER = "OTHER", _('Other')                     # Other


class Currency(TextChoices):
    CDF = "CDF", _('Congolese Franc')      # Congolese Franc
    USD = "USD", _('US Dollar')            # US Dollar
    EUR = "EUR", _('Euro')                 # Euro


class BankAccountAction(TextChoices):
    CREATED = "CREATED", _('Created')
    UPDATED = "UPDATED", _('Updated')
    VERIFIED = "VERIFIED", _('Verified')
    UNVERIFIED = "UNVERIFIED", _('Unverified')
    ACTIVATED = "ACTIVATED", _('Activated')
    DEACTIVATED = "DEACTIVATED", _('Deactivated')
    SET_PRIMARY = "SET_PRIMARY", _('Set Primary')
    DELETED = "DELETED", _('Deleted')


class CalendarEventType(TextChoices):
    PUBLIC_HOLIDAY = "PUBLIC_HOLIDAY", _("Public Holiday") # Holiday
    COMPANY_EVENT = "COMPANY_EVENT", _("Company Event")    # Event
    DEADLINE = "DEADLINE", _("Deadline")                   # Deadline
    ANNIVERSARY = "ANNIVERSARY", _("Anniversary")          # Anniversary
    LEAVE = "LEAVE", _("Leave/Absence")                    # Leave
    OTHER = "OTHER", _("Other")                            # Other


class CalendarEventStatus(TextChoices):
    PENDING = "PENDING", _("Pending")
    APPROVED = "APPROVED", _("Approved")
    REJECTED = "REJECTED", _("Rejected")
    CANCELLED = "CANCELLED", _("Cancelled")
    TAKEN = "TAKEN", _("Taken / Archived")


class CalendarEventRecurrence(TextChoices):
    NONE = "NONE", _("None")
    DAILY = "DAILY", _("Daily")
    WEEKLY = "WEEKLY", _("Weekly")
    MONTHLY = "MONTHLY", _("Monthly")
    YEARLY = "YEARLY", _("Yearly")

