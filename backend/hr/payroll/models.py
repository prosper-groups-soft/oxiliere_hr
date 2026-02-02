from decimal import Decimal
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from auditlog.registry import auditlog

from hr.models.base import BaseAuditableModel
from hr.utils.gen   import generate_payroll_run_code
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
    ExchangeRateSource,
    AdvanceDeductionBase,
    AdvanceTaxTiming,
    AdvanceDeductionWindow,
)
from hr.enums import Currency


class PayrollConfiguration(BaseAuditableModel):
    """ Global payroll settings and organizational constants. """
    currency = models.CharField(
        max_length=3, 
        default="CDF",
        help_text=_("Default currency (ISO 4217) for all payroll calculations.")
    )
    default_payment_method = models.CharField(
        max_length=20, 
        choices=PaymentMethod.choices, 
        default=PaymentMethod.CASH,
        verbose_name=_("Payment Method"),
        help_text=_("Standard method used for employee payments.")
    )
    work_hours_per_month = models.PositiveIntegerField(
        default=195,
        verbose_name=_("Work Hours/Month"),
        help_text=_("Standard monthly working hours for calculation purposes.")
    )
    housing_allowance_min_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=30.0,
        verbose_name=_("Min Housing Allowance %"),
        help_text=_("Minimum housing allowance as a percentage of base salary.")
    )
    family_allowance_min_amount = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0.0,
        verbose_name=_("Min Family Allowance"),
        help_text=_("Minimum daily allowance per child.")
    )
    family_allowance_smig_divider = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=27.0,
        verbose_name=_("Family Allowance Divider"),
        help_text=_("Factor for calculating family allowance from SMIG (Daily SMIG / Divider).")
    )
    overtime_multiplier = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=1.5,
        verbose_name=_("Overtime Multiplier"),
        help_text=_("Coefficient applied to the hourly rate for overtime.")
    )
    include_leaves_in_payroll = models.BooleanField(
        default=True,
        verbose_name=_("Include Leaves"),
        help_text=_("Import approved leaves for payroll processing.")
    )
    leave_deduction_divisor = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=26.0,
        verbose_name=_("Leave Divisor"),
        help_text=_("Divisor used for leave deductions.")
    )
    use_theoretical_days_from_attendance = models.BooleanField(
        default=False,
        verbose_name=_("Use Attendance Days"),
        help_text=_("Use the scheduled working days from Attendance for deductions.")
    )
    fixed_deduction_per_absent_day = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Fixed Absent Deduction"),
        help_text=_("Fixed amount deducted for each unpaid absence day.")
    )
    exchange_rate_usd_cdf = models.DecimalField(
        max_digits=10, 
        decimal_places=4, 
        default=2850.0000,
        verbose_name=_("USD/CDF Rate"),
        help_text=_("Standard USD to CDF exchange rate.")
    )
    exchange_rate_source = models.CharField(
        max_length=15, 
        choices=ExchangeRateSource.choices, 
        default=ExchangeRateSource.MANUAL,
        verbose_name=_("Rate Source"),
        help_text=_("Source of the exchange rate (e.g., Central Bank or Manual).")
    )

    class Meta:
        db_table = "pyrl_payroll_configuration"
        verbose_name = _("Payroll Configuration")


class EmployeeContract(BaseAuditableModel):
    """ Compensation structure and employment terms for an employee. """
    employee = models.ForeignKey(
        'hr_employees.Employee', 
        on_delete=models.CASCADE, 
        related_name='contracts',
        verbose_name=_("Employee")
    )
    remuneration_type = models.CharField(
        max_length=10, 
        choices=RemunerationType.choices,
        verbose_name=_("Remuneration Type"),
        help_text=_("Basis for compensation (e.g., Hourly or Fixed).")
    )
    payment_period = models.CharField(
        max_length=10, 
        choices=PaymentPeriod.choices, 
        default=PaymentPeriod.MONTHLY,
        null=True, 
        blank=True,
        verbose_name=_("Payment Period")
    )
    contract_type = models.CharField(
        max_length=20, 
        choices=ContractType.choices,
        verbose_name=_("Contract Type"),
        help_text=_("Legal form of employment (CDI, CDD, etc.).")
    )
    base_salary = models.DecimalField(
        max_digits=12, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_("Base Salary"),
        help_text=_("Standard salary amount.")
    )
    salary_base_type = models.CharField(
        max_length=10,
        choices=SalaryBaseType.choices,
        default=SalaryBaseType.GROSS,
        verbose_name=_("Salary Base Type"),
        help_text=_("Indicates if the salary is defined as Gross or Net.")
    )
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        verbose_name=_("Hourly Rate")
    )
    currency = models.CharField(
        max_length=3, 
        choices=Currency.choices, 
        default=Currency.CDF, 
        verbose_name=_("Currency")
    )
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        null=True, 
        blank=True,
        verbose_name=_("End Date")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        db_table = "pyrl_employee_contract"
        verbose_name = _("Employee Contract")
        verbose_name_plural = _("Employee Contracts")
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
                        raise ValidationError(
                            _(f"Base salary ({self.base_salary} FC) cannot be lower than the active monthly SMIG ({smig.monthly_rate} FC).")
                        )
                elif self.remuneration_type == RemunerationType.HOURLY:
                    # Assuming 8 hours per day for hourly SMIG comparison
                    daily_smig = smig.daily_rate
                    hourly_smig = daily_smig / Decimal('8.0')
                    if self.hourly_rate < hourly_smig:
                        raise ValidationError(
                            _(f"Hourly rate ({self.hourly_rate} FC) cannot be lower than the active hourly SMIG ({hourly_smig:.2f} FC).")
                        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PayrollAdjustment(BaseAuditableModel):
    """ Standard bonuses, allowances, or deductions used in payroll. """
    name = models.CharField(
        max_length=100,
        verbose_name=_("Name")
    )
    adjustment_type = models.CharField(
        max_length=15, 
        choices=AdjustmentType.choices,
        verbose_name=_("Type"),
        help_text=_("Categorizes the adjustment as a bonus or a contribution.")
    )
    calculation_mode = models.CharField(
        max_length=15, 
        choices=CalculationMode.choices,
        verbose_name=_("Calculation Mode"),
        help_text=_("Determines if the adjustment is a fixed amount or a percentage.")
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
        verbose_name=_("Is Mandatory"),
        help_text=_("Apply this adjustment to all eligible employees by default.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this adjustment is currently available for use.")
    )

    class Meta:
        db_table = "pyrl_payroll_adjustment"
        verbose_name = _("Payroll Adjustment")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class EmployeeAdjustment(BaseAuditableModel):
    """ Individual assignment of a payroll adjustment to an employee. """
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
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
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
        verbose_name=_("Custom Amount"),
        help_text=_("Override the standard amount for this employee.")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this specific assignment is currently active.")
    )

    class Meta:
        db_table = "pyrl_employee_adjustment"
        verbose_name = _("Employee Adjustment")
        unique_together = ('employee', 'adjustment')


class PayrollRun(BaseAuditableModel):
    """ Payroll processing session for a specific period. """
    code = models.CharField(
        max_length=32, 
        unique=True, 
        default=generate_payroll_run_code,
        help_text=_("A unique identifier for the payroll processing run.")
    )
    start_date = models.DateField(
        verbose_name=_("Start Date")
    )
    end_date = models.DateField(
        verbose_name=_("End Date")
    )
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
        verbose_name=_("Applied Exchange Rate")
    )

    class Meta:
        db_table = "pyrl_payroll_run"
        verbose_name = _("Payroll Run")


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
    
    #status = models.CharField(max_length=15, choices=EmployeePayslipStatus.choices, default=EmployeePayslipStatus.DRAFT) DRAFT, VALIDATED, PAID, CANCELED
    
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
        verbose_name = _("Payslip Line")


class SalaryAdvance(BaseAuditableModel):
    """ Short-term financial advance granted to an employee. """
    employee = models.ForeignKey(
        'hr_employees.Employee', 
        on_delete=models.PROTECT,
        help_text=_("The employee who received the advance.")
    )
    amount = models.DecimalField(
        max_digits=12, 
        decimal_places=2,
        verbose_name=_("Amount"),
        help_text=_("Total principal amount of the advance.")
    )
    repayment_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2,
        verbose_name=_("Repayment %"),
        help_text=_("Percentage of salary deducted for repayment.")
    )
    
    salary_base_for_deduction = models.CharField(
        max_length=10,
        choices=AdvanceDeductionBase.choices,
        default=AdvanceDeductionBase.NET,
        verbose_name=_("Deduction Base"),
        help_text=_("Deduction from Gross or Net salary.")
    )
    tax_timing = models.CharField(
        max_length=15,
        choices=AdvanceTaxTiming.choices,
        default=AdvanceTaxTiming.AFTER_TAX,
        verbose_name=_("Tax Timing"),
        help_text=_("Specifies if the deduction affects taxable income.")
    )
    deduction_window = models.CharField(
        max_length=15,
        choices=AdvanceDeductionWindow.choices,
        default=AdvanceDeductionWindow.ALL_MONTHS,
        verbose_name=_("Deduction Window")
    )
    deduction_start_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Deduction Start"),
        help_text=_("Required if window is CUSTOM_PERIOD.")
    )
    deduction_end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Deduction End"),
        help_text=_("Required if window is CUSTOM_PERIOD.")
    )
    is_closed = models.BooleanField(
        default=False,
        verbose_name=_("Is Settled"),
        help_text=_("Indicates if the advance has been fully repaid.")
    )

    class Meta:
        db_table = "pyrl_salary_advance"
        verbose_name = _("Salary Advance")
        verbose_name_plural = _("Salary Advances")


class AdvanceDeductionConfiguration(BaseAuditableModel):
    """ Priority and selection rules for salary advance deductions. """
    employee = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.CASCADE,
        related_name='advance_deduction_config',
        verbose_name=_("Employee")
    )
    advance = models.ForeignKey(
        SalaryAdvance,
        on_delete=models.CASCADE,
        related_name='deduction_configs',
        verbose_name=_("Advance")
    )
    priority_order = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Priority"),
        help_text=_("Order of deduction (lower numbers = higher priority).")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("If False, this advance will not be deducted in payroll calculations.")
    )
    
    class Meta:
        db_table = "pyrl_advance_deduction_config"
        verbose_name = _("Advance Deduction Setting")
        unique_together = ('employee', 'advance')
        ordering = ['priority_order']
        
    def __str__(self):
        return f"{self.employee} - Priority #{self.priority_order}"


class RepaymentRecord(BaseAuditableModel):
    """ Repayment transaction against a salary advance. """
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
        verbose_name=_("Repayment Date")
    )

    class Meta:
        db_table = "pyrl_repayment_record"
        verbose_name = _("Repayment Record")


class SMIGConfiguration(BaseAuditableModel):
    """
    Tracks the SMIG (Salaire Minimum Interprofessionnel Garanti) over time.
    Allows for historical tracking as minimum wage changes. 
    """
    daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name=_("Daily Rate"),
        help_text=_("Minimum daily wage in local currency.")
    )
    effective_date = models.DateField(
        verbose_name=_("Effective Date")
    )
    is_active = models.BooleanField(
        default=True,
        help_text=_("Indicates if this is the current active SMIG rate.")
    )

    class Meta:
        db_table = "pyrl_smig_configuration"
        verbose_name = _("SMIG Configuration")
        ordering = ['-effective_date']
        constraints = [
            models.UniqueConstraint(
                fields=['effective_date'],
                name='unique_smig_effective_date'
            )
        ]

    def __str__(self):
        return f"SMIG: {self.daily_rate} FC (from {self.effective_date})"

    @property
    def weekly_rate(self):
        return self.daily_rate * 6

    @property
    def monthly_rate(self):
        return self.daily_rate * 26

    @property
    def annual_rate(self):
        return self.daily_rate * 312


class SocialContributionRate(BaseAuditableModel):
    """ Social security and tax contribution rates (CNSS, ONEM, INPP). """
    contribution_type = models.CharField(
        max_length=10,
        choices=SocialContributionType.choices,
        verbose_name=_("Type")
    )
    rate_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Total Rate %")
    )
    employee_portion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Employee Portion %")
    )
    employer_portion = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Employer Portion %")
    )
    company_size_min = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Min Company Size")
    )
    company_size_max = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_("Max Company Size")
    )
    ceiling_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Ceiling Amount"),
        help_text=_("Maximum base amount for this contribution.")
    )
    effective_date = models.DateField(
        help_text=_("Date from which this rate becomes effective.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        db_table = "pyrl_social_contribution_rate"
        verbose_name = _("Contribution Rate")
        ordering = ['contribution_type', '-effective_date']

    def __str__(self):
        return f"{self.contribution_type}: {self.rate_percentage}%"

    def clean(self):
        if self.employee_portion + self.employer_portion != self.rate_percentage:
            raise ValidationError(
                _("Employee portion + Employer portion must equal total rate.")
            )
        if self.company_size_min and self.company_size_max:
            if self.company_size_min > self.company_size_max:
                raise ValidationError(
                    _("Min size cannot be greater than max size.")
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
        verbose_name=_("Rule Type")
    )
    multiplier = models.DecimalField(
        max_digits=4,
        decimal_places=2,
        validators=[MinValueValidator(1.0)],
        verbose_name=_("Multiplier"),
        help_text=_("Multiplier applied to the hourly rate (e.g., 1.5).")
    )
    description = models.TextField(
        blank=True,
        verbose_name=_("Description")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        db_table = "pyrl_overtime_rule"
        verbose_name = _("Overtime Rule")
        ordering = ['multiplier']

    def __str__(self):
        return f"{self.get_rule_type_display()}: {self.multiplier}x"


class LegalAllowance(BaseAuditableModel):
    """ Statutory allowances required by local regulations. """
    allowance_type = models.CharField(
        max_length=15,
        choices=LegalAllowanceType.choices,
        unique=True,
        verbose_name=_("Allowance Type")
    )
    calculation_mode = models.CharField(
        max_length=15,
        choices=CalculationMode.choices,
        verbose_name=_("Calculation Mode")
    )
    base_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Base Amount")
    )
    formula_description = models.TextField(
        blank=True,
        verbose_name=_("Formula Description")
    )
    is_taxable = models.BooleanField(
        default=False,
        verbose_name=_("Is Taxable")
    )
    taxable_threshold_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Taxable Threshold %"),
        help_text=_("% of gross salary above which the allowance is taxed.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        db_table = "pyrl_legal_allowance"
        verbose_name = _("Legal Allowance")
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
        verbose_name=_("Employee")
    )
    payroll_run = models.ForeignKey(
        'PayrollRun',
        on_delete=models.CASCADE,
        related_name='worked_days_records',
        verbose_name=_("Payroll Run")
    )
    regular_days = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of regular working days completed.")
    )
    overtime_hours_first_tier = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Overtime (Tier 1)")
    )
    overtime_hours_second_tier = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Overtime (Tier 2)")
    )
    overtime_hours_holiday = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Overtime (Holiday)")
    )
    absence_days = models.PositiveIntegerField(
        default=0,
        verbose_name=_("Absence Days")
    )

    class Meta:
        db_table = "pyrl_worked_days_record"
        verbose_name = _("Worked Days Record")
        unique_together = ('employee', 'payroll_run')

    def __str__(self):
        return f"{self.employee} - {self.payroll_run.code}"

    @property
    def total_overtime_hours(self):
        return (
            self.overtime_hours_first_tier +
            self.overtime_hours_second_tier +
            self.overtime_hours_holiday
        )


class TaxBracket(BaseAuditableModel):
    """ Income tax brackets and progressive rates (e.g., IPR in DRC). """
    label = models.CharField(
        max_length=100,
        verbose_name=_("Label")
    )
    lower_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name=_("Lower Limit")
    )
    upper_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Upper Limit")
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
        verbose_name=_("Min Tax Amount")
    )
    max_tax_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Max Tax % of Income")
    )
    applies_to_taxable_base = models.BooleanField(
        default=True,
        verbose_name=_("Tax Taxable Base"),
        help_text=_("Calculate tax on base after social deductions.")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Is Active")
    )

    class Meta:
        db_table = "pyrl_tax_bracket"
        verbose_name = _("Tax Bracket")
        ordering = ['lower_limit']

    def __str__(self):
        return f"{self.label}: {self.rate_percentage}%"


# --- Audit log registration ---
auditlog.register(PayrollConfiguration)
auditlog.register(EmployeeContract)
auditlog.register(PayrollAdjustment)
auditlog.register(EmployeeAdjustment)
auditlog.register(PayrollRun)
auditlog.register(EmployeePayslip)
auditlog.register(PayslipLine)
auditlog.register(SalaryAdvance)
auditlog.register(AdvanceDeductionConfiguration)
auditlog.register(RepaymentRecord)
auditlog.register(SMIGConfiguration)
auditlog.register(SocialContributionRate)
auditlog.register(OvertimeRule)
auditlog.register(LegalAllowance)
auditlog.register(WorkedDaysRecord)
auditlog.register(TaxBracket)

