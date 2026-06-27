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
    FIXED = "FIXED", _('Salaire Fixe')
    HOURLY = "HOURLY", _('Taux Horaire')
    GROSS_UP = "GROSS_UP", _('Brutage (Net à Brut)')


class SalaryBaseType(TextChoices):
    """Determines if the base salary is expressed as Gross or Net."""
    GROSS = "GROSS", _('Salaire Brut')
    NET = "NET", _('Salaire Net')


class ContractType(TextChoices):
    """Employment contract categories (Aligned with DRC Labor Law)."""
    CDI = "CDI", _('CDI (Indéterminé)')
    CDD = "CDD", _('CDD (Durée Déterminée)')
    INTERNSHIP = "INTERNSHIP", _('Stage Professionnel')
    FREELANCE = "FREELANCE", _('Consultance / Freelance')
    PROBATION = "PROBATION", _('Période d\'Essai')
    TEMPORARY = "TEMPORARY", _('Journalier / Temporaire')


class PayrollStatus(TextChoices):
    """Processing stages for a payroll run."""
    DRAFT = "DRAFT", _('Draft')
    VALIDATED = "VALIDATED", _('Validated')
    PAID = "PAID", _('Paid')
    CANCELED = "CANCELED", _('Canceled')
    PROCESSING = "PROCESSING", _('Processing')


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
    DAILY = "DAILY", _('Journalier')
    WEEKLY = "WEEKLY", _('Hebdomadaire')
    BIWEEKLY = "BIWEEKLY", _('Quinzaine / Bi-mensuel')
    MONTHLY = "MONTHLY", _('Mensuel')
    PER_TASK = "PER_TASK", _('À la tâche / Forfaitaire')


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
    FIRST_TIER = "FIRST_TIER", _('First 6 hours beyond 45h/week (130%)')
    SUBSEQUENT_HOURS = "SUBSEQUENT_HOURS", _('Subsequent hours (160%)')
    WEEKEND = "WEEKEND", _('Weekend/Rest day (200%)')
    HOLIDAY = "HOLIDAY", _('Public holiday (200%)')


class LegalAllowanceType(TextChoices):
    """Types of legal allowances in DRC."""
    FAMILY = "FAMILY", _('Family Allowance (Allocation Familiale)')
    HOUSING = "HOUSING", _('Housing Allowance (Contre-valeur Logement)')
    TRANSPORT = "TRANSPORT", _('Transport Allowance (Allocation de Transport)')
    MEAL = "MEAL", _('Meal Allowance (Panier)')
    RISK_PREMIUM = "RISK_PREMIUM", _('Risk Premium (Prime de Risque)')
    DIRTY_WORK = "DIRTY_WORK", _('Dirty Work Allowance (Prime de Salissure)')


class ExchangeRateSource(TextChoices):
    """Source for fetching currency exchange rates."""
    MANUAL = "MANUAL", _('Manual Entry')
    BCC = "BCC", _('Banque Centrale du Congo (Official)')


class AdvanceDeductionBase(TextChoices):
    """Determines which salary base the advance deduction is calculated on."""
    GROSS = "GROSS", _('Gross Salary (Brut)')
    NET = "NET", _('Net Salary (After deductions)')


class AdvanceTaxTiming(TextChoices):
    """Determines if the advance deduction affects tax calculations."""
    BEFORE_TAX = "BEFORE_TAX", _('Before Tax Calculation (Reduces taxable base)')
    AFTER_TAX = "AFTER_TAX", _('After Tax Calculation (No tax impact)')


class AdvanceDeductionWindow(TextChoices):
    """Determines the time period during which deductions are applied."""
    ALL_MONTHS = "ALL_MONTHS", _('All Months (Until fully repaid)')
    CUSTOM_PERIOD = "CUSTOM_PERIOD", _('Custom Period (Between defined dates)')

