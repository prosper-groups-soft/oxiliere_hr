from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from hr.models.base import BaseAuditableModel
from .utils import generate_payroll_run_code
from .enums import (
    PaymentMethod,
    ContractType,
    PaymentPeriod,
    RemunerationType,
    AdjustmentType,
    CalculationMode,
    PayrollStatus,
    SocialContributionType,
    OvertimeRuleType,
    OvertimeRuleType,
    LegalAllowanceType,
    SalaryBaseType,
    ExchangeRateSource
)
from hr.enums import Currency


class PayrollConfiguration(BaseAuditableModel):
    """
    Stores global payroll settings and constants for the organization.
    """
    currency = models.CharField(
        max_length=3, 
        default="CDF",
        help_text=_("The default currency code (ISO 4217) for all payroll calculations.")
    )
    default_payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices, 
        default=PaymentMethod.CASH,
        help_text=_("The standard payment method used if not specified otherwise.")
    )
    work_hours_per_month = models.PositiveIntegerField(
        default=195,
        help_text=_("Standard number of working hours in a month for calculation purposes.")
    )
    housing_allowance_min_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=30.0,
        help_text=_("Minimum housing allowance as a percentage of base salary.")
    )
    family_allowance_min_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0,
        help_text=_("Absolute minimum daily amount per child (e.g. 262 FC).")
    )
    family_allowance_smig_divider = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=27.0,
        help_text=_("The factor used to calculate family allowance from SMIG (Daily SMIG / Divider).")
    )
    overtime_multiplier = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=1.5,
        help_text=_("Coefficient applied to the hourly rate for overtime compensation.")
    )
    include_leaves_in_payroll = models.BooleanField(
        default=True,
        help_text=_("If enabled, approved leaves from the Leaves module will be imported and processed.")
    )
    leave_deduction_divisor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=26.0,
        help_text=_("Standard divisor used if dynamic calculation is disabled.")
    )
    use_theoretical_days_from_attendance = models.BooleanField(
        default=False,
        help_text=_("If enabled, the divisor for deductions will be the exact number of working days scheduled in Attendance.")
    )
    fixed_deduction_per_absent_day = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("If set, this fixed amount will be deducted for each unpaid absence day, overriding pro-rata.")
    )
    exchange_rate_usd_cdf = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=2850.0000,
        help_text=_("Exchange rate for USD to CDF conversion (e.g., 2850). Used if pay rule requires conversion.")
    )
    exchange_rate_source = models.CharField(
        max_length=15, 
        choices=ExchangeRateSource.choices, 
        default=ExchangeRateSource.MANUAL,
        help_text=_("Source of the exchange rate. Select BCC for live Central Bank rates.")
    )

    class Meta:
        db_table = "pyrl_payroll_configuration"


class EmployeeContract(BaseAuditableModel):
    """
    Defines the compensation structure and operational rules for an employee's contract.
    """
    employee = models.ForeignKey(
        'hr_employees.Employee', 
        on_delete=models.CASCADE, 
        related_name='contracts',
        help_text=_("Reference to the employee linked to this contract.")
    )
    remuneration_type = models.CharField(
        max_length=10, 
        choices=RemunerationType.choices,
        help_text=_("Defines how the compensation is calculated (Hourly vs Fixed salary).")
    )
    payment_period = models.CharField(
        max_length=10, 
        choices=PaymentPeriod.choices, 
        default=PaymentPeriod.MONTHLY,
        null=True, 
        blank=True,
        help_text=_("Frequency of payment calculation. Defaults to Monthly if not specified.")
    )
    contract_type = models.CharField(
        max_length=20, 
        choices=ContractType.choices,
        help_text=_("The type of employment contract (e.g., CDI, CDD, Internship).")
    )
    base_salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_("Monthly base salary amount (Gross or Net depending on type).")
    )
    salary_base_type = models.CharField(
        max_length=10,
        choices=SalaryBaseType.choices,
        default=SalaryBaseType.GROSS,
        help_text=_("Indicates if the provided base_salary is Gross or Net.")
    )
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_("Rate per hour for hourly remuneration types.")
    )
    currency = models.CharField(
        max_length=3, 
        choices=Currency.choices, 
        default=Currency.CDF, 
        verbose_name=_("Currency"),
        help_text=_("Currency of the contract (e.g. CDF, USD).")
    )
    start_date = models.DateField(help_text=_("Official start date of the contract."))
    end_date = models.DateField(
        null=True, 
        blank=True,
        help_text=_("Official end date of the contract, if applicable.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this contract is currently active.")
    )

    class Meta:
        db_table = "pyrl_employee_contract"
        constraints = [
            models.UniqueConstraint(
                fields=['employee'], 
                condition=models.Q(is_active=True), 
                name='unique_active_contract_per_employee'
            )
        ]

    def clean(self):
        if self.end_date and self.end_date < self.start_date:
            raise ValidationError(_("The end date cannot be earlier than the start date."))
        if self.remuneration_type == RemunerationType.FIXED and not self.base_salary:
            raise ValidationError(_("A fixed salary requires a base salary amount."))
        if self.remuneration_type == RemunerationType.HOURLY and not self.hourly_rate:
            raise ValidationError(_("An hourly salary requires an hourly rate."))
        
        # SMIG Validation
        if self.is_active:
            from .models import SMIGConfiguration
            smig = SMIGConfiguration.objects.filter(is_active=True).first()
            if smig:
                if self.remuneration_type == RemunerationType.FIXED:
                    if self.base_salary < smig.monthly_rate:
                        raise ValidationError(_(f"Base salary ({self.base_salary} FC) cannot be lower than the active monthly SMIG ({smig.monthly_rate} FC)."))
                elif self.remuneration_type == RemunerationType.HOURLY:
                    # Assuming 8 hours per day for hourly SMIG comparison
                    daily_smig = smig.daily_rate
                    hourly_smig = daily_smig / Decimal('8.0')
                    if self.hourly_rate < hourly_smig:
                        raise ValidationError(_(f"Hourly rate ({self.hourly_rate} FC) cannot be lower than the active hourly SMIG ({hourly_smig:.2f} FC)."))

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PayrollAdjustment(BaseAuditableModel):
    """
    Configuration for reusable bonuses, allowances, or deductions (e.g., Transport, Health Insurance).
    """
    name = models.CharField(
        max_length=100,
        help_text=_("The display name of the adjustment.")
    )
    adjustment_type = models.CharField(
        max_length=15, 
        choices=AdjustmentType.choices,
        help_text=_("Determines if this is a bonus (addition) or a contribution (deduction).")
    )
    calculation_mode = models.CharField(
        max_length=15, 
        choices=CalculationMode.choices,
        help_text=_("Specifies if the adjustment is a fixed amount or a percentage.")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_("The fixed amount for the adjustment, if applicable.")
    )
    percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        null=True, 
        blank=True, 
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("The percentage for the adjustment, if applicable.")
    )
    is_mandatory = models.BooleanField(
        default=False,
        help_text=_("If true, this adjustment is applied to all eligible employees by default.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this adjustment is currently available for use.")
    )

    class Meta:
        db_table = "pyrl_payroll_adjustment"

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class EmployeeAdjustment(BaseAuditableModel):
    """
    Specific assignment of a payroll adjustment to an individual employee with potential overrides.
    """
    employee = models.ForeignKey(
        'hr_employees.Employee', 
        on_delete=models.CASCADE,
        help_text=_("The employee to whom the adjustment is assigned.")
    )
    adjustment = models.ForeignKey(
        PayrollAdjustment, 
        on_delete=models.CASCADE,
        help_text=_("The source adjustment configuration.")
    )
    start_date = models.DateField(help_text=_("The date from which this adjustment becomes effective for the employee."))
    end_date = models.DateField(
        null=True, 
        blank=True,
        help_text=_("The date when this specific adjustment assignment expires.")
    )
    custom_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_("A custom amount to override the default configuration for this employee.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this specific assignment is currently active.")
    )

    class Meta:
        db_table = "pyrl_employee_adjustment"
        unique_together = ('employee', 'adjustment')


class PayrollRun(BaseAuditableModel):
    """
    Represents a payroll processing session for a defined period.
    """
    code = models.CharField(
        max_length=32, 
        unique=True, 
        default=generate_payroll_run_code,
        help_text=_("A unique identifier for the payroll processing run.")
    )
    start_date = models.DateField(help_text=_("The beginning date of the payroll period."))
    end_date = models.DateField(help_text=_("The ending date of the payroll period."))
    status = models.CharField(
        max_length=15, 
        choices=PayrollStatus.choices, 
        default=PayrollStatus.DRAFT,
        help_text=_("The current state of the payroll run (e.g., Draft, Validated, Paid).")
    )
    exchange_rate_applied = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        null=True, 
        blank=True,
        help_text=_("The USD/CDF exchange rate effective during this payroll run.")
    )

    class Meta:
        db_table = "pyrl_payroll_run"


class EmployeePayslip(BaseAuditableModel):
    """
    Summary record of an employee's earnings, deductions, and net pay for a specific payroll run.
    """
    payroll_run = models.ForeignKey(
        PayrollRun, 
        on_delete=models.CASCADE, 
        related_name='payslips',
        help_text=_("The payroll session this payslip belongs to.")
    )
    contract = models.ForeignKey(
        EmployeeContract, 
        on_delete=models.PROTECT,
        help_text=_("The contract version used for this payslip.")
    )
    
    base_salary_snapshot = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text=_("Record of the base salary at the time of calculation.")
    )
    gross_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text=_("Total earnings before any deductions.")
    )
    total_adjustments = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text=_("The net sum of all additions and subtractions applied.")
    )
    net_amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text=_("The final amount to be paid to the employee.")
    )
    
    # Work tracking fields
    worked_days = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of days actually worked during the period.")
    )
    worked_hours = models.FloatField(
        default=0,
        help_text=_("Total number of hours worked during the period.")
    )
    overtime_hours = models.FloatField(
        default=0,
        help_text=_("Total number of overtime hours worked during the period.")
    )
    paid_leave_days = models.FloatField(
        default=0,
        help_text=_("Number of paid leave days taken during the period.")
    )
    unpaid_leave_days = models.FloatField(
        default=0,
        help_text=_("Number of unpaid leave days taken during the period.")
    )
    
    # DRC-specific deductions
    cnss_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("CNSS contribution amount (employee portion).")
    )
    onem_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("ONEM contribution amount.")
    )
    inpp_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("INPP contribution amount.")
    )
    ipr_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("IPR (income tax) amount.")
    )
    
    # DRC-specific allowances
    family_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Paid family allowances.")
    )
    housing_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Paid housing allowance.")
    )
    transport_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Paid transport allowance.")
    )
    
    # Currency tracking
    contract_currency = models.CharField(
        max_length=3, 
        choices=Currency.choices, 
        default=Currency.CDF
    )
    exchange_rate_used = models.DecimalField(
        max_digits=10,
        decimal_places=4,
        default=1.0,
        help_text=_("Exchange rate used for this specific payslip calculation.")
    )
    
    # Tax calculation base
    taxable_base = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text=_("Taxable income base for IPR calculation (after CNSS deduction).")
    )
    
    payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices,
        help_text=_("The method used to process the payment.")
    )
    paid_at = models.DateTimeField(
        null=True, 
        blank=True,
        help_text=_("Timestamp when the payment was finalized.")
    )
    currency = models.CharField(
        max_length=3,
        help_text=_("The currency in which the payslip was calculated.")
    )


    class Meta:
        db_table = "pyrl_employee_payslip"
        unique_together = ('payroll_run', 'contract')


class PayslipLine(BaseAuditableModel):
    """
    Details of each individual component (bonus or deduction) that makes up the total adjustments of a payslip.
    """
    payslip = models.ForeignKey(
        EmployeePayslip, 
        on_delete=models.CASCADE, 
        related_name='lines',
        help_text=_("The summary payslip this detail line belongs to.")
    )
    adjustment = models.ForeignKey(
        PayrollAdjustment, 
        on_delete=models.SET_NULL, 
        null=True,
        help_text=_("The source configuration for this line item.")
    )
    label = models.CharField(
        max_length=100,
        help_text=_("The descriptive name of the line item as it appears on the payslip.")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text=_("The individual amount for this line item.")
    )
    adjustment_type = models.CharField(
        max_length=15, 
        choices=AdjustmentType.choices,
        help_text=_("Snapshot of the adjustment category (Bonus or Contribution).")
    )

    class Meta:
        db_table = "pyrl_payslip_line"


class SalaryAdvance(BaseAuditableModel):
    """
    Records a short-term financial advance granted to an employee to be repaid over time.
    """
    employee = models.ForeignKey(
        'hr_employees.Employee', 
        on_delete=models.PROTECT,
        help_text=_("The employee who received the advance.")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text=_("The total principal amount of the advance.")
    )
    repayment_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        help_text=_("Percentage of the net salary to be deducted for each repayment cycle.")
    )
    is_closed = models.BooleanField(
        default=False,
        help_text=_("Indicates if the advance has been fully settled.")
    )

    class Meta:
        db_table = "pyrl_salary_advance"


class RepaymentRecord(BaseAuditableModel):
    """
    Tracks each repayment transaction made against a salary advance, usually tied to a payslip.
    """
    salary_advance = models.ForeignKey(
        SalaryAdvance, 
        on_delete=models.CASCADE, 
        related_name='repayments',
        help_text=_("The specific advance this repayment is credited to.")
    )
    payslip = models.ForeignKey(
        EmployeePayslip, 
        on_delete=models.CASCADE, 
        related_name='advance_repayments',
        help_text=_("The payslip from which the repayment was deducted.")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        help_text=_("The specific amount repaid in this transaction.")
    )
    repayment_date = models.DateField(
        auto_now_add=True,
        help_text=_("The date when the repayment was processed.")
    )

    class Meta:
        db_table = "pyrl_repayment_record"


class SMIGConfiguration(BaseAuditableModel):
    """
    Tracks the SMIG (Salaire Minimum Interprofessionnel Garanti) over time.
    Allows for historical tracking as minimum wage changes.
    """
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text=_("Daily minimum wage rate in local currency (e.g., 7075 FC).")
    )
    effective_date = models.DateField(
        help_text=_("Date from which this SMIG rate becomes effective.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this is the current active SMIG rate.")
    )

    class Meta:
        db_table = "pyrl_smig_configuration"
        ordering = ['-effective_date']
        constraints = [
            models.UniqueConstraint(
                fields=['effective_date'],
                name='unique_smig_effective_date'
            )
        ]

    def __str__(self):
        return f"SMIG: {self.daily_rate} FC/day (effective {self.effective_date})"

    @property
    def weekly_rate(self):
        """Calculate weekly SMIG (daily_rate * 6)."""
        return self.daily_rate * 6

    @property
    def monthly_rate(self):
        """Calculate monthly SMIG (daily_rate * 26)."""
        return self.daily_rate * 26

    @property
    def annual_rate(self):
        """Calculate annual SMIG (daily_rate * 312)."""
        return self.daily_rate * 312


class SocialContributionRate(BaseAuditableModel):
    """
    Configurable social contribution rates (CNSS, ONEM, INPP).
    Supports company size-based rates (e.g., INPP varies by employee count).
    """
    contribution_type = models.CharField(
        max_length=10,
        choices=SocialContributionType.choices,
        help_text=_("Type of social contribution.")
    )
    rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Total contribution rate as a percentage.")
    )
    employee_portion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Percentage of the contribution paid by the employee.")
    )
    employer_portion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Percentage of the contribution paid by the employer.")
    )
    company_size_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Minimum company size (employee count) for this rate to apply. Used for INPP.")
    )
    company_size_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        help_text=_("Maximum company size (employee count) for this rate to apply. Used for INPP.")
    )
    ceiling_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Maximum base amount on which this contribution is calculated (e.g., CNSS ceiling).")
    )
    effective_date = models.DateField(
        help_text=_("Date from which this rate becomes effective.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this rate is currently active.")
    )

    class Meta:
        db_table = "pyrl_social_contribution_rate"
        ordering = ['contribution_type', '-effective_date']

    def __str__(self):
        size_info = ""
        if self.company_size_min or self.company_size_max:
            size_info = f" (size: {self.company_size_min or 0}-{self.company_size_max or '∞'})"
        return f"{self.contribution_type}: {self.rate_percentage}%{size_info}"

    def clean(self):
        if self.employee_portion + self.employer_portion != self.rate_percentage:
            raise ValidationError(
                _("Employee portion + Employer portion must equal the total rate percentage.")
            )
        if self.company_size_min and self.company_size_max:
            if self.company_size_min > self.company_size_max:
                raise ValidationError(
                    _("Minimum company size cannot be greater than maximum company size.")
                )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class OvertimeRule(BaseAuditableModel):
    """
    Defines overtime calculation rules with different multipliers.
    Examples: 130% for first 2 hours, 160% for subsequent, 200% for holidays.
    """
    rule_type = models.CharField(
        max_length=20,
        choices=OvertimeRuleType.choices,
        unique=True,
        help_text=_("Type of overtime rule.")
    )
    multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(1.0)],
        help_text=_("Multiplier applied to the base hourly rate (e.g., 1.30 for 130%).")
    )
    description = models.TextField(
        blank=True,
        help_text=_("Detailed description of when this rule applies.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this rule is currently active.")
    )

    class Meta:
        db_table = "pyrl_overtime_rule"
        ordering = ['multiplier']

    def __str__(self):
        return f"{self.get_rule_type_display()}: {self.multiplier}x"


class LegalAllowance(BaseAuditableModel):
    """
    Configures legal allowances required by DRC law.
    Examples: Family allowance (1/27 SMIG per child), Housing, Transport.
    """
    allowance_type = models.CharField(
        max_length=15,
        choices=LegalAllowanceType.choices,
        unique=True,
        help_text=_("Type of legal allowance.")
    )
    calculation_mode = models.CharField(
        max_length=15,
        choices=CalculationMode.choices,
        help_text=_("How the allowance amount is calculated.")
    )
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Fixed base amount for the allowance, if applicable.")
    )
    formula_description = models.TextField(
        blank=True,
        help_text=_("Description of the calculation formula (e.g., '1/27 of SMIG per child').")
    )
    is_taxable = models.BooleanField(
        default=False,
        help_text=_("Indicates if this allowance is subject to IPR taxation.")
    )
    taxable_threshold_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Percentage of gross salary above which this allowance becomes taxable (e.g., 30% for housing).")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this allowance is currently active.")
    )

    class Meta:
        db_table = "pyrl_legal_allowance"
        ordering = ['allowance_type']

    def __str__(self):
        return f"{self.get_allowance_type_display()}"


class WorkedDaysRecord(BaseAuditableModel):
    """
    Tracks actual work performed by an employee during a payroll period.
    Records regular days, overtime hours by tier, and absences.
    """
    employee = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.CASCADE,
        related_name='worked_days_records',
        help_text=_("The employee this record belongs to.")
    )
    payroll_run = models.ForeignKey(
        'PayrollRun',
        on_delete=models.CASCADE,
        related_name='worked_days_records',
        help_text=_("The payroll run this record is associated with.")
    )
    regular_days = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of regular working days completed.")
    )
    overtime_hours_first_tier = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Overtime hours at first tier rate (typically 130%).")
    )
    overtime_hours_second_tier = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Overtime hours at second tier rate (typically 160%).")
    )
    overtime_hours_holiday = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text=_("Overtime hours on holidays/rest days (typically 200%).")
    )
    absence_days = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of days absent during the period.")
    )

    class Meta:
        db_table = "pyrl_worked_days_record"
        unique_together = ('employee', 'payroll_run')

    def __str__(self):
        return f"{self.employee} - {self.payroll_run.code}: {self.regular_days} days"

    @property
    def total_overtime_hours(self):
        """Calculate total overtime hours across all tiers."""
        return (
            self.overtime_hours_first_tier +
            self.overtime_hours_second_tier +
            self.overtime_hours_holiday
        )


class TaxBracket(BaseAuditableModel):

    """
    Stores progressive tax brackets (e.g., IPR in DRC).
    Example: 0 to 1000 @ 0%, 1001 to 2500 @ 15%, etc.
    Enhanced with DRC IPR-specific constraints.
    """
    label = models.CharField(
        max_length=100,
        help_text=_("Descriptive name for this tax bracket.")
    )
    lower_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        help_text=_("Lower bound of the income range for this bracket.")
    )
    upper_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Upper bound of the income range. Leave blank for the highest bracket.")
    )
    rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        help_text=_("Tax rate percentage applied to income in this bracket.")
    )
    min_tax_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        help_text=_("Minimum tax amount (e.g., IPR minimum of 2000 FC).")
    )
    max_tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text=_("Maximum tax as percentage of taxable income (e.g., IPR max 30%).")
    )
    applies_to_taxable_base = models.BooleanField(
        default=True,
        help_text=_("If true, tax is calculated on base after CNSS deduction (IPR rule).")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this tax bracket is currently active.")
    )

    class Meta:
        db_table = "pyrl_tax_bracket"
        ordering = ['lower_limit']

    def __str__(self):
        return f"{self.label}: {self.rate_percentage}%"



# --- AUDIT LOG REGISTRATION ---

auditlog.register(PayrollConfiguration)
auditlog.register(EmployeeContract)
auditlog.register(PayrollAdjustment)
auditlog.register(EmployeeAdjustment)
auditlog.register(PayrollRun)
auditlog.register(EmployeePayslip)
auditlog.register(PayslipLine)
auditlog.register(SalaryAdvance)
auditlog.register(RepaymentRecord)
auditlog.register(SMIGConfiguration)
auditlog.register(SocialContributionRate)
auditlog.register(OvertimeRule)
auditlog.register(LegalAllowance)
auditlog.register(WorkedDaysRecord)
auditlog.register(TaxBracket)

