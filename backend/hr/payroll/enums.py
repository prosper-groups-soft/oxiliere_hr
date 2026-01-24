from django.db.models         import TextChoices
from django.utils.translation import gettext_lazy as _


class PaymentMethod(TextChoices):
    """Methods used for processing payments."""
    BANK_TRANSFER = 'BANK_TRANSFER', _('Bank Transfer')
    CASH = 'CASH', _('Cash')
    MOBILE_MONEY = 'MOBILE_MONEY', _('Mobile Money')
    CHECK = 'CHECK', _('Check')


class RemunerationType(TextChoices):
    """Calculation method for employee compensation."""
    FIXED = "FIXED", _('Fixed Salary')
    HOURLY = "HOURLY", _('Hourly Rate')


class SalaryBaseType(TextChoices):
    """Determines if the base salary is expressed as Gross or Net."""
    GROSS = "GROSS", _('Gross (Brut)')
    NET = "NET", _('Net (Brutage)')


class ContractType(TextChoices):
    """Employment contract categories."""
    CDI = "CDI", _('CDI (Indefinite Contract)')
    CDD = "CDD", _('CDD (Fixed-term Contract)')
    INTERNSHIP = "INTERNSHIP", _('Internship')
    FREELANCE = "FREELANCE", _('Freelance / Service Agreement')
    TEMPORARY = "TEMPORARY", _('Temporary / Interim')


class PayrollStatus(TextChoices):
    """Processing stages for a payroll run."""
    DRAFT = "DRAFT", _('Draft')
    VALIDATED = "VALIDATED", _('Validated')
    PAID = "PAID", _('Paid')
    CANCELED = "CANCELED", _('Canceled')


class AdjustmentType(TextChoices):
    """Categories of payroll adjustments."""
    BONUS = "BONUS", _('Bonus')
    CONTRIBUTION = "CONTRIBUTION", _('Contribution/Deduction')


class CalculationMode(TextChoices):
    """Methods for calculating adjustment amounts."""
    FIXED = "FIXED", _('Fixed Amount')
    PERCENTAGE = "PERCENTAGE", _('Percentage')


class BonusTypes(TextChoices):
    """Specific types of predefined bonuses and allowances."""
    TRANSPORT_ALLOWANCE = 'TRANSPORT_ALLOWANCE', _('Transport allowance')
    HOUSING_ALLOWANCE = 'HOUSING_ALLOWANCE', _('Housing allowance')
    REMOTE_WORK_ALLOWANCE = 'REMOTE_WORK_ALLOWANCE', _('Remote work allowance')
    MEAL_ALLOWANCE = 'MEAL_ALLOWANCE', _('Meal allowance')
    COMPANY_HEALTH_INSURANCE = 'COMPANY_HEALTH_INSURANCE', _('Company health insurance')
    DISABILITY_INSURANCE = 'DISABILITY_INSURANCE', _('Disability insurance')
    TRAVEL_EXPENSES = 'TRAVEL_EXPENSES', _('Travel expenses')
    BACK_TO_SCHOOL_ALLOWANCE = 'BACK_TO_SCHOOL_ALLOWANCE', _('Back to school allowance')
    CHILDCARE_ALLOWANCE = 'CHILDCARE_ALLOWANCE', _('Childcare allowance')
    HOUSING_AID = 'HOUSING_AID', _('Housing aid')
    THIRTEENTH_MONTH = 'THIRTEENTH_MONTH', _('13th month')
    HEALTH_INSURANCE = 'HEALTH_INSURANCE', _('Health insurance')
    TRANSPORT_BONUS = 'TRANSPORT_BONUS', _('Transport bonus')
    SENIORITY_BONUS = 'SENIORITY_BONUS', _('Seniority bonus')
    OTHER = 'OTHER', _('Other')


class PaymentPeriod(TextChoices):
    """Payroll frequency cycles."""
    DAILY = "DAILY", _('Daily')
    PER_TASK = "PER_TASK", _('Per Task')
    MONTHLY = "MONTHLY", _('Monthly')


class PayslipStatus(TextChoices):
    """Status of the payslip processing cycle."""
    REVIEW = "REVIEW", _('Under Review')
    CONFIRMED = "CONFIRMED", _('Confirmed')
    PAID = "PAID", _('Paid')
    CANCELED = "CANCELED", _('Canceled')


class SocialContributionType(TextChoices):
    """Types of social contributions in DRC."""
    CNSS = "CNSS", _('CNSS (Caisse Nationale de Sécurité Sociale)')
    ONEM = "ONEM", _('ONEM (Office National de l\'Emploi)')
    INPP = "INPP", _('INPP (Institut National de Préparation Professionnelle)')


class OvertimeRuleType(TextChoices):
    """Types of overtime calculation rules."""
    FIRST_TWO_HOURS = "FIRST_TWO_HOURS", _('First 2 hours beyond 45h/week (130%)')
    SUBSEQUENT_HOURS = "SUBSEQUENT_HOURS", _('Subsequent hours (160%)')
    WEEKEND = "WEEKEND", _('Weekend/Rest day (200%)')
    HOLIDAY = "HOLIDAY", _('Public holiday (200%)')


class LegalAllowanceType(TextChoices):
    """Types of legal allowances in DRC."""
    FAMILY = "FAMILY", _('Family Allowance (Allocation Familiale)')
    HOUSING = "HOUSING", _('Housing Allowance (Contre-valeur Logement)')
    TRANSPORT = "TRANSPORT", _('Transport Allowance (Allocation de Transport)')


class ExchangeRateSource(TextChoices):
    """Source for fetching currency exchange rates."""
    MANUAL = "MANUAL", _('Manual Entry')
    BCC = "BCC", _('Banque Centrale du Congo (Official)')

