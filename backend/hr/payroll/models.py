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
    PayrollStatus
)


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
        default=173,
        help_text=_("Standard number of working hours in a month for calculation purposes.")
    )
    overtime_multiplier = models.DecimalField(
        max_digits=4, 
        decimal_places=2, 
        default=1.5,
        help_text=_("Coefficient applied to the hourly rate for overtime compensation.")
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
        help_text=_("Monthly base salary amount for fixed remuneration types.")
    )
    hourly_rate = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        null=True, 
        blank=True,
        help_text=_("Rate per hour for hourly remuneration types.")
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
    
    worked_hours = models.FloatField(
        default=0,
        help_text=_("Total number of hours worked during the period.")
    )
    overtime_hours = models.FloatField(
        default=0,
        help_text=_("Total number of overtime hours worked during the period.")
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


class TaxBracket(BaseAuditableModel):
    """
    Stores progressive tax brackets (e.g., IPR in DRC).
    Example: 0 to 1000 @ 0%, 1001 to 2500 @ 15%, etc.
    """
    label = models.CharField(max_length=100)
    lower_limit = models.DecimalField(max_digits=12, decimal_places=2)
    upper_limit = models.DecimalField(max_digits=12, decimal_places=2, null=True, blank=True)
    rate_percentage = models.DecimalField(max_digits=5, decimal_places=2)
    is_active = models.BooleanField(default=True)

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
auditlog.register(TaxBracket)

