from django.utils import timezone
from decimal import Decimal
from django.db import models
from django.apps import apps
from django.core.validators import (
    MinValueValidator, 
    MaxValueValidator
)
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.conf import settings
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
    PayslipStatus,
    SocialContributionType,
    OvertimeRuleType,
    LegalAllowanceType,
    SalaryBaseType,
    AdvanceDeductionBase,
    AdvanceTaxTiming,
    AdvanceDeductionWindow,
    AdvanceStatus,
    AdvanceRiskLevel,
    LeaveDeductionMode,
    WorkRegime,
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
    work_hours_per_week = models.PositiveIntegerField(
        default=45,
        verbose_name=_("Work Hours/Week"),
        help_text=_("Standard weekly working hours (45h for RCD labor code). Monthly hours are calculated from this.")
    )
    work_hours_per_month = models.PositiveIntegerField(
        default=195,
        verbose_name=_("Work Hours/Month"),
        help_text=_("Calculated automatically: work_hours_per_week × 52 / 12")
    )
    housing_allowance_min_percentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        default=30.0,
        verbose_name=_("Min Housing Allowance %"),
        help_text=_("Minimum housing allowance as a percentage of base salary.")
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
    leave_deduction_mode = models.CharField(
        max_length=20,
        choices=LeaveDeductionMode.choices,
        default=LeaveDeductionMode.DISABLED,
        verbose_name=_("Leave Deduction Mode"),
        help_text=_(
            "Mode exclusif de déduction des absences non payées : "
            "DISABLED (aucune), DAILY_RATE (salaire ÷ diviseur), "
            "CALENDAR_DAYS (salaire ÷ jours calendaires du mois), "
            "ATTENDANCE_DAYS (salaire ÷ jours théoriques de présence du planning), "
            "FIXED_AMOUNT (montant forfaitaire par jour)."
        ),
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

    def save(self, *args, **kwargs):
        """Calculate work_hours_per_month from work_hours_per_week before saving."""
        if self.work_hours_per_week:
            # Standard calculation: weekly hours × 52 weeks / 12 months
            self.work_hours_per_month = round(self.work_hours_per_week * 52 / 12)
        super().save(*args, **kwargs)

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
        verbose_name=_("Active"),
        help_text=_("Whether this contract is currently active. Suspended/terminated contracts set this to False.")
    )
    # --- Payroll metamodel (metamodel.md L124-135) ---
    # Net salary negotiated in USD at hiring — converted at the period exchange rate.
    negotiated_salary_usd = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Salaire négocié (USD)"),
        help_text=_("Salaire net négocié en USD à l'embauche — montant que l'employé connaît comme « son salaire ». Converti en CDF au taux de la période. Cohérence Règle 5 du métamodèle.")
    )
    # Work regime (catalogue.md §7.2)
    work_regime = models.CharField(
        max_length=20,
        choices=WorkRegime.choices,
        default=WorkRegime.FULL_TIME,
        verbose_name=_("Régime de travail"),
        help_text=_("Temps plein, temps partiel (taux d'activité), expatriation.")
    )
    # Special / particular contract clauses
    contractual_clauses = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Clauses particulières"),
        help_text=_("Primes garanties, avantages contractuels spécifiques (métamodèle).")
    )

    class Meta:
        db_table = "pyrl_employee_contract"
        verbose_name = _("Employee Contract")
        verbose_name_plural = _("Employee Contracts")
        constraints = [
            models.UniqueConstraint(
                fields=['employee'],
                condition=models.Q(end_date__isnull=True, deleted__isnull=True),
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
        
        # SMIG Validation (only for currently active contracts)
        today = timezone.localdate()
        is_currently_active = (
            self.start_date and self.start_date <= today and
            (not self.end_date or self.end_date >= today)
        )
        if is_currently_active:
            # Deferred import to avoid circular dependency
            # SMIGConfiguration is defined later in this module
            SMIGConfiguration = apps.get_model('hr_payroll', 'SMIGConfiguration')
            smig = SMIGConfiguration.objects.filter(is_active=True).first()
            if smig:
                if self.remuneration_type == RemunerationType.FIXED:
                    base_amt = self.base_salary if self.base_salary else Decimal('0')
                    if base_amt < smig.monthly_rate:
                        raise ValidationError(
                            _(f"Base salary ({base_amt} FC) cannot be lower than the active monthly SMIG ({smig.monthly_rate} FC).")
                        )
                elif self.remuneration_type == RemunerationType.HOURLY:
                    # Assuming 8 hours per day for hourly SMIG comparison
                    daily_smig = smig.daily_rate if smig.daily_rate else Decimal('0')
                    hourly_smig = daily_smig / Decimal('8.0')
                    hourly_amt = self.hourly_rate if self.hourly_rate else Decimal('0')
                    if hourly_amt < hourly_smig:
                        raise ValidationError(
                            _(f"Hourly rate ({hourly_amt} FC) cannot be lower than the active hourly SMIG ({hourly_smig:.2f} FC).")
                        )

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class PayrollAdjustment(BaseAuditableModel):
    """ Standard bonuses, allowances, or deductions used in payroll. """
    code = models.CharField(
        max_length=30,
        null=True,
        blank=True,
        verbose_name=_("Code catalogue"),
        help_text=_("Code normalisé du catalogue (ex. IND_LOG, ALLOC_REPAS) — utilisé par l'écran S10 Éléments de paie du contrat.")
    )
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
    is_taxable = models.BooleanField(
        default=True,
        verbose_name=_("Imposable IRPP"),
        help_text=_("Inclu dans le revenu catégoriel IRPP (défaut : oui, conforme au Code du travail RDC).")
    )
    is_cnss_subject = models.BooleanField(
        default=True,
        verbose_name=_("Soumis à la CNSS"),
        help_text=_("Inclu dans la base CNSS (défaut : oui pour les primes conventionnelles).")
    )
    formula_description = models.TextField(
        blank=True,
        verbose_name=_("Description de la formule"),
        help_text=_("Explication lisible du calcul (ex. '10 % du salaire de base, versé chaque mois').")
    )

    class Meta:
        db_table = "pyrl_payroll_adjustment"
        verbose_name = _("Payroll Adjustment")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ContractAdjustment(BaseAuditableModel):
    """
    Élément de paie négocié et assigné à un contrat (S10 — Éléments de paie du contrat).
    
    Conforme au métamodèle : `Contrat de travail ──1──>* Élément de paie`.
    Le catalogue (PayrollAdjustment) définit les modèles ; cette table relie un
    élément du catalogue à un contrat spécifique avec ses paramètres négociés
    (montant/taux personnalisé, période d'application, actif/inactif).
    """
    contract = models.ForeignKey(
        EmployeeContract,
        on_delete=models.CASCADE,
        related_name='pay_elements',
        verbose_name=_("Contrat"),
        help_text=_("Le contrat auquel cet élément de paie est lié.")
    )
    # Dénormalisé pour les requêtes par employé et le calcul des bulletins
    employee = models.ForeignKey(
        'hr_employees.Employee',
        on_delete=models.CASCADE,
        verbose_name=_("Employé"),
        help_text=_("Employé du contrat (dénormalisé pour les requêtes par employé).")
    )
    adjustment = models.ForeignKey(
        PayrollAdjustment,
        on_delete=models.CASCADE,
        related_name='contract_assignments',
        verbose_name=_("Élément du catalogue"),
        help_text=_("L'élément de paie du catalogue (PayrollAdjustment).")
    )
    start_date = models.DateField(
        verbose_name=_("Début d'application")
    )
    end_date = models.DateField(
        null=True,
        blank=True,
        verbose_name=_("Fin d'application"),
        help_text=_("Désactive automatiquement l'élément au cycle concerné.")
    )
    custom_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name=_("Montant négocié"),
        help_text=_("Override du montant standard du catalogue (négocié au contrat).")
    )
    # Correction du bug : custom_percentage référencé mais absent
    custom_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        verbose_name=_("Taux négocié (%)"),
        help_text=_("Override du pourcentage standard du catalogue (négocié au contrat).")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Actif"),
        help_text=_("Permet de sélectionner/désélectionner l'élément pour ce contrat sans le supprimer (les allocations légales is_mandatory restent désactivables ici).")
    )

    class Meta:
        db_table = "pyrl_contract_adjustment"
        verbose_name = _("Élément de paie du contrat")
        verbose_name_plural = _("Éléments de paie du contrat")
        unique_together = ('contract', 'adjustment')

    def clean(self):
        if self.start_date and self.end_date and self.start_date > self.end_date:
            raise ValidationError(_("La date de début ne peut pas être après la date de fin."))

    def __str__(self):
        return f"{self.contract} — {self.adjustment.name}"


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
    
    # --- Correction 0.4 : Snapshot d'audit ---
    # Conforme à semantics.md L481-507
    # Capturé UNE FOIS par PayrollRun (pas par bulletin) pour éviter la duplication
    params_snapshot = models.JSONField(
        default=dict,
        blank=True,
        verbose_name=_("Audit Snapshot"),
        help_text=_(
            "Paramètres légaux et réglementaires en vigueur lors du calcul "
            "(SMIG, barème IRPP, taux CNSS, taux de change, etc.). "
            "Identique pour tous les bulletins du Run."
        ),
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
    
    # Correction 0.7 #8 : Statut du bulletin (DRAFT→CALCULATED→GENERATED→VALIDATED)
    status = models.CharField(
        max_length=15,
        choices=PayslipStatus.choices,
        default=PayslipStatus.REVIEW,
        verbose_name=_("Payslip Status"),
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
        default=Decimal('0.00'),
        help_text=_("CNSS contribution amount (employee portion).")
    )
    onem_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("ONEM contribution amount.")
    )
    inpp_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("INPP contribution amount.")
    )
    ipr_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("IPR (income tax) amount.")
    )
    
    # DRC-specific allowances
    housing_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text=_("Paid housing allowance.")
    )
    transport_allowance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
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
        default=Decimal('0.00'),
        help_text=_("Taxable income base for IPR calculation (after CNSS deduction).")
    )
    
    # --- Correction 0.4 : Signature SHA-256 du bulletin ---
    # Unique par bulletin (les montants diffèrent par employé)
    signature_hash = models.CharField(
        max_length=64,
        blank=True,
        default='',
        verbose_name=_("Signature SHA-256"),
        help_text=_(
            "Hash SHA-256 du bulletin (montants + identifiants). "
            "Permet de détecter toute altération après validation."
        ),
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


# Correction 0.7 #9 : Charges patronales persistées séparément
class EmployerCharge(BaseAuditableModel):
    """Employer social charges linked to a payslip (audit trail)."""
    payslip = models.ForeignKey(
        EmployeePayslip,
        on_delete=models.CASCADE,
        related_name='employer_charges',
    )
    contribution_type = models.CharField(
        max_length=10,
        choices=SocialContributionType.choices,
    )
    label = models.CharField(max_length=100)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    base_amount = models.DecimalField(max_digits=12, decimal_places=2)

    class Meta:
        db_table = "pyrl_employer_charge"
        verbose_name = _("Employer Charge")


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

    # ---- Workflow d'approbation (PENDING -> APPROVED/REJECTED -> ACTIVE -> CLOSED) ----
    status = models.CharField(
        max_length=15,
        choices=AdvanceStatus.choices,
        default=AdvanceStatus.PENDING,
        verbose_name=_("Status"),
        help_text=_("Lifecycle state of the advance request.")
    )
    advance_type = models.CharField(
        max_length=20,
        default='NORMAL',
        verbose_name=_("Advance Type")
    )
    reason = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Reason"),
        help_text=_("Motif de la demande d'avance.")
    )
    requested_date = models.DateField(
        default=timezone.localdate,
        verbose_name=_("Request Date"),
        help_text=_("Date when the advance was requested.")
    )
    requested_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_requested',
        verbose_name=_("Requested By"),
        help_text=_("User who submitted the advance request.")
    )
    approved_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_approved',
        verbose_name=_("Approved By"),
        help_text=_("User who approved the advance.")
    )
    approved_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Approved Date"),
        help_text=_("When the advance was approved.")
    )
    rejected_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='%(app_label)s_%(class)s_rejected',
        verbose_name=_("Rejected By"),
        help_text=_("User who rejected the advance.")
    )
    rejected_date = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_("Rejected Date"),
        help_text=_("When the advance was rejected.")
    )
    rejection_reason = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Rejection Reason"),
        help_text=_("Why the advance was rejected.")
    )

    # ---- Suivi financier ----
    deducted_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        verbose_name=_("Deducted Amount"),
        help_text=_("Cumulative amount already deducted from salary repayments.")
    )
    risk_level = models.CharField(
        max_length=10,
        choices=AdvanceRiskLevel.choices,
        default=AdvanceRiskLevel.LOW,
        verbose_name=_("Risk Level"),
        help_text=_("Reimbursement risk assessed at request time (LOW/MEDIUM/HIGH).")
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

    # ---- Devise & taux (audit financier) ----
    currency = models.CharField(
        max_length=3,
        default=Currency.CDF,
        verbose_name=_("Currency"),
        help_text=_("Currency of the advance amount (CDF or USD).")
    )
    
    exchange_rate_used = models.DecimalField(
        max_digits=12,
        decimal_places=4,
        null=True,
        blank=True,
        verbose_name=_("Exchange Rate Used"),
        help_text=_("USD→CDF rate frozen at creation time for auditability.")
    )

    @property
    def employee_name(self) -> str:
        """Full name of the employee (used by API serialization)."""
        return getattr(self.employee, 'full_name', '')

    @property
    def remaining_balance(self) -> Decimal:
        """Outstanding balance to be reimbursed."""
        return self.amount - self.deducted_amount

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
                condition=models.Q(deleted__isnull=True),
                name='unique_smig_effective_date'
            )
        ]

    def __str__(self):
        return f"SMIG: {self.daily_rate} FC (from {self.effective_date})"

    @property
    def weekly_rate(self):
        return self.daily_rate * 6 if self.daily_rate else Decimal('0')

    @property
    def monthly_rate(self):
        return self.daily_rate * 26 if self.daily_rate else Decimal('0')

    @property
    def annual_rate(self):
        return self.daily_rate * 312 if self.daily_rate else Decimal('0')


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
    overtime_hours_weekend = models.FloatField(
        default=0,
        validators=[MinValueValidator(0)],
        verbose_name=_("Overtime (Weekend)")
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
            self.overtime_hours_weekend +
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


class ProfessionalCategory(BaseAuditableModel):
    """
    Grille des catégories professionnelles (catalogue.md §6).

    7 classes x 4 échelons définies par le Décret n° 25/22 :
    - Classe 1 : Manœuvre ordinaire → Classe 7 : Cadre supérieur
    - Principe de tension salariale 1:10 : le salaire max de la grille
      (Classe 7, Échelon 4) = SMIG mensuel x 10.

    C'est le paramétrage légal de référence (S8). Les champs
    `classe`/`echelon` du module jobs y sont liés sémantiquement
    (libellés de la grille) — pas de FK pour rester découplé.
    """
    classe = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(7)],
        verbose_name=_("Classe"),
        help_text=_("Classe professionnelle RDC (1-7).")
    )
    echelon = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(4)],
        verbose_name=_("Échelon"),
        help_text=_("Échelon dans la classe (1-4).")
    )
    label = models.CharField(
        max_length=120,
        verbose_name=_("Libellé"),
        help_text=_("Libellé de la classe (ex. Manœuvre ordinaire, Cadre moyen).")
    )
    application = models.TextField(
        blank=True,
        default='',
        verbose_name=_("Application"),
        help_text=_("Profil de personnel concerné (ex. Personnel non qualifié).")
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name=_("Active"),
        help_text=_("La classe/échelon est applicable pour les nouveaux contrats.")
    )

    class Meta:
        db_table = "pyrl_professional_category"
        verbose_name = _("Catégorie professionnelle")
        verbose_name_plural = _("Catégories professionnelles")
        ordering = ['classe', 'echelon']
        constraints = [
            models.UniqueConstraint(
                fields=['classe', 'echelon'],
                condition=models.Q(deleted__isnull=True),
                name='unique_professional_category_class_echelon'
            )
        ]

    def __str__(self):
        return f"Classe {self.classe} — Échelon {self.echelon} ({self.label})"


# --- Audit log registration ---
auditlog.register(PayrollConfiguration)
auditlog.register(EmployeeContract)
auditlog.register(PayrollAdjustment)
auditlog.register(ContractAdjustment)
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
auditlog.register(EmployerCharge)
auditlog.register(ProfessionalCategory)

