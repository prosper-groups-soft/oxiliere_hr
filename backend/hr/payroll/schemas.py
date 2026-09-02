from decimal  import Decimal
from typing   import List, Dict, Annotated, Optional, Literal, Any
from uuid     import UUID
from datetime import date, datetime
from django.db.models import Q
from ninja    import (
    Schema, 
    ModelSchema, 
    FilterSchema, 
    FilterLookup
)
from pydantic import Field, ConfigDict, AliasChoices
from .models import (
    PayrollConfiguration,
    EmployeeContract,
    PayrollAdjustment,
    ContractAdjustment,
    PayrollRun,
    PayslipLine,
    SalaryAdvance,
    AdvanceDeductionConfiguration,
    WorkedDaysRecord,
    RepaymentRecord,
    SMIGConfiguration,
    SocialContributionRate,
    OvertimeRule,
    LegalAllowance,
    TaxBracket,
)
from hr.employees.schemas import EmployeeOut
from hr.schemas import BaseFilter


# --- PAYROLL CONFIGURATION SCHEMAS  ---
class ConfigurePayrollIn(ModelSchema):
    """Input schema for creating/updating payroll configuration."""
    class Meta:
        model = PayrollConfiguration
        fields = [
            "currency",
            "default_payment_method",
            "work_hours_per_week",
            "housing_allowance_min_percentage",
            "include_leaves_in_payroll",
            "leave_deduction_divisor",
            "leave_deduction_mode",
            "fixed_deduction_per_absent_day",
            "exchange_rate_usd_cdf",
        ]


class PayrollConfigurationOut(Schema):
    """Output schema for retrieving payroll configuration."""
    id: UUID
    currency: str
    default_payment_method: str
    work_hours_per_week: int
    work_hours_per_month: int
    housing_allowance_min_percentage: Decimal
    include_leaves_in_payroll: bool
    leave_deduction_divisor: Decimal
    leave_deduction_mode: str
    fixed_deduction_per_absent_day: Decimal | None = None
    exchange_rate_usd_cdf: Decimal
    created_at: datetime
    updated_at: datetime


class PayrollConfigurationUpdateIn(ModelSchema):
    """Schema for partial updates to payroll configuration."""
    class Meta:
        model = PayrollConfiguration
        fields = [
            "currency",
            "default_payment_method",
            "work_hours_per_week",
            "housing_allowance_min_percentage",
            "include_leaves_in_payroll",
            "leave_deduction_divisor",
            "leave_deduction_mode",
            "fixed_deduction_per_absent_day",
            "exchange_rate_usd_cdf",
        ]
        fields_optional = "__all__"


# ---  EMPLOYEE CONTRACT SCHEMAS  ---
class EmployeeContractCreateIn(ModelSchema):
    """Input schema for creating an employee contract."""
    class Meta:
        model = EmployeeContract
        fields = [
            "employee",
            "remuneration_type",
            "contract_type",
            "base_salary",
            "salary_base_type",
            "hourly_rate",
            "currency",
            "start_date",
            "end_date",
            "contractual_clauses",
        ]


class EmployeeContractOut(Schema):
    """Output schema for retrieving employee contract details."""
    id: UUID
    employee: EmployeeOut
    remuneration_type: str
    contract_type: str
    base_salary: Decimal | None = None
    salary_base_type: str
    hourly_rate: Decimal | None = None
    currency: str
    start_date: date
    end_date: date | None = None
    is_active: bool = True
    contractual_clauses: str = ''
    created_at: datetime
    updated_at: datetime


class EmployeeContractUpdateIn(ModelSchema):
    """Schema for updating employee contract (all fields optional)."""
    class Meta:
        model = EmployeeContract
        fields = [
            "remuneration_type",
            "contract_type",
            "base_salary",
            "salary_base_type",
            "hourly_rate",
            "currency",
            "start_date",
            "end_date",
            "is_active",
            "contractual_clauses",
        ]
        fields_optional = "__all__"


# --- PAYROLL ADJUSTMENT SCHEMAS ---
class PayrollAdjustmentCreateIn(ModelSchema):
    """Input schema for defining a payroll adjustment template."""
    class Meta:
        model = PayrollAdjustment
        fields = [
            "code",
            "name",
            "adjustment_type",
            "calculation_mode",
            "amount",
            "percentage",
            "is_mandatory",
            "is_active",
            "is_taxable",
            "is_cnss_subject",
            "formula_description",
        ]


class PayrollAdjustmentOut(Schema):
    """Output schema for retrieving payroll adjustment details."""
    id: UUID
    code: str | None = None
    name: str
    adjustment_type: str
    calculation_mode: str
    amount: Decimal | None = None
    percentage: Decimal | None = None
    is_mandatory: bool
    is_active: bool
    is_taxable: bool
    is_cnss_subject: bool
    formula_description: str
    created_at: datetime
    updated_at: datetime


class PayrollAdjustmentUpdateIn(ModelSchema):
    """Schema for updating payroll adjustment."""
    class Meta:
        model = PayrollAdjustment
        fields = [
            "code",
            "name",
            "adjustment_type",
            "calculation_mode",
            "amount",
            "percentage",
            "is_mandatory",
            "is_active",
            "is_taxable",
            "is_cnss_subject",
            "formula_description",
        ]
        fields_optional = "__all__"


class ContractAdjustmentCreateIn(Schema):
    """Input schema for assigning a catalog element (PayrollAdjustment) to a contract.

    Le champ `contract` est requis (UUID) — `employee` est dérivé du contrat
    par le service (dénormalisation). `custom_percentage` permet de négocier
    un taux propre au contrat (S10).

    Compatible avec les deux formes de payload :
      - `adjustment`      (forme S10, utilisée par le frontend)
      - `adjustment_id`   (forme ModelSchema django-ninja)
    `contract` / `contract_id` sont optionnels car imposés par l'URL de la route.
    """
    model_config = ConfigDict(populate_by_name=True)

    contract: UUID | None = Field(default=None, validation_alias=AliasChoices("contract", "contract_id"))
    adjustment: UUID = Field(validation_alias=AliasChoices("adjustment", "adjustment_id"))
    start_date: date
    end_date: date | None = None
    custom_amount: Decimal | None = None
    custom_percentage: Decimal | None = None
    is_active: bool = True


class ContractAdjustmentOut(Schema):
    """Output schema for retrieving contract adjustment assignments (S10)."""
    id: UUID
    contract: UUID = Field(..., alias="contract_id")
    employee: UUID = Field(..., alias="employee_id")
    adjustment: PayrollAdjustmentOut
    start_date: date
    end_date: date | None = None
    custom_amount: Decimal | None = None
    custom_percentage: Decimal | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class ContractAdjustmentUpdateIn(ModelSchema):
    """Schema for updating contract adjustment assignments (all fields optional)."""
    class Meta:
        model = ContractAdjustment
        fields = [
            "start_date",
            "end_date",
            "custom_amount",
            "custom_percentage",
            "is_active",
        ]
        fields_optional = "__all__"


# --- S10 PAY ELEMENTS SCHEMAS ---
class PayElementOut(Schema):
    """Élément de paie d'un contrat — ligne de la liste S10."""
    id: UUID
    catalog_code: str | None = None
    label: str
    value_type: str
    amount: Decimal | None = None
    custom_amount: Decimal | None = None
    custom_percentage: Decimal | None = None
    is_active: bool
    is_taxable: bool = True
    recurrence: str = "monthly"
    start_period: date
    end_period: date | None = None


class ContractPayElementListOut(Schema):
    """Réponse complète S10 : éléments de paie d'un contrat + résumé brut estimé."""
    contract_id: UUID
    employee: EmployeeOut
    contract_type: str
    base_salary: Decimal | None = None
    elements: List[PayElementOut]
    estimated_gross: Decimal = Decimal('0.00')


# --- PAYROLL RUN SCHEMAS ---
class PayrollRunCreateIn(ModelSchema):
    """Input schema for creating a payroll run.

    - ``exchange_rate_applied`` : taux USD→CDF figé pour le run (None si CDF).
    - ``selection_scope``       : 'all' (tous les employés actifs),
                                  'org_units' (départements sélectionnés),
                                  'employees' (liste explicite d'employés).
    - ``org_unit_ids`` / ``employee_ids`` : IDs selon le scope.
    """
    exchange_rate_applied: Decimal | None = None
    selection_scope: Literal['all', 'org_units', 'employees'] = 'all'
    org_unit_ids: list[UUID] = []
    employee_ids: list[UUID] = []

    class Meta:
        model = PayrollRun
        fields = [
            "start_date",
            "end_date",
        ]


class PayrollRunOut(ModelSchema):
    """Output schema for retrieving payroll run details.

    The extra computed fields (total_payslips, gross_total, employee_count,
    closed_at, period_label) are resolved either from queryset annotations
    (list endpoint) or from the run detail dict (detail endpoint).

    `params_snapshot` est exposé pour permettre au frontend d'hydrater
    les steps avec la sélection employés (scope, org_unit_ids, employee_ids)
    et l'exchange rate.
    """
    total_payslips: int
    gross_total: Decimal = Decimal('0')
    employee_count: int = 0
    closed_at: datetime | None = None
    period_label: str | None = None
    params_snapshot: Dict[str, Any] = {}

    class Meta:
        model = PayrollRun
        fields = [
            "id",
            "code",
            "start_date",
            "end_date",
            "status",
            "exchange_rate_applied",
            "params_snapshot",
            "created_at",
            "updated_at",
        ]


class PayrollRunDetailOut(Schema):
    """Detailed output schema for payroll run (matches get_run_detail() dict)."""
    id: UUID
    code: str
    status: str
    period: str
    start_date: date
    end_date: date
    exchange_rate: Decimal | None = None
    created_at: datetime
    updated_at: datetime
    stats: Dict[str, int]
    financials: Dict[str, Decimal]


class PayrollRunUpdateIn(ModelSchema):
    """Schema for updating a payroll run (DRAFT only).

    Le client envoie uniquement les champs modifiés (exclude_unset côté
    service). On accepte `params_snapshot` pour permettre l'édition de
    la sélection employés (`selection.scope / org_unit_ids / employee_ids`).
    """
    class Meta:
        model = PayrollRun
        fields = [
            "status",
            "exchange_rate_applied",
            "params_snapshot",
        ]
        fields_optional = "__all__"


# --- PAYSLIP LINE SCHEMAS ---
class PayslipLineOut(Schema):
    """Output schema for payslip detail lines."""
    id: UUID
    label: str
    amount: Decimal
    adjustment_type: str


class PayslipLineCreateIn(ModelSchema):
    """Input schema for creating payslip lines."""
    class Meta:
        model = PayslipLine
        fields = [
            "label",
            "amount",
            "adjustment_type",
        ]


# --- EMPLOYEE PAYSLIP SCHEMAS ---
class EmployeePayslipOut(Schema):
    """Output schema for complete payslip details."""
    id: UUID
    payroll_run: UUID = Field(..., alias="payroll_run_id")
    contract: UUID = Field(..., alias="contract_id")
    base_salary_snapshot: Decimal
    gross_amount: Decimal
    cnss_amount: Decimal
    onem_amount: Decimal
    inpp_amount: Decimal
    ipr_amount: Decimal
    housing_allowance: Decimal
    transport_allowance: Decimal
    total_adjustments: Decimal
    net_amount: Decimal
    taxable_base: Decimal
    worked_days: int
    worked_hours: float
    overtime_hours: float
    paid_leave_days: float
    unpaid_leave_days: float
    contract_currency: str
    exchange_rate_used: Decimal
    currency: str
    payment_method: str
    paid_at: datetime | None = None
    created_at: datetime
    updated_at: datetime


class EmployeePayslipDetailOut(Schema):
    """Detailed payslip output with computed fields."""
    id: UUID
    payroll_run: UUID
    contract: UUID
    base_salary_snapshot: Decimal
    gross_amount: Decimal
    cnss_amount: Decimal
    onem_amount: Decimal
    inpp_amount: Decimal
    ipr_amount: Decimal
    housing_allowance: Decimal
    transport_allowance: Decimal
    total_adjustments: Decimal
    net_amount: Decimal
    taxable_base: Decimal
    worked_days: int
    worked_hours: float
    overtime_hours: float
    paid_leave_days: float
    unpaid_leave_days: float
    contract_currency: str
    exchange_rate_used: Decimal
    currency: str
    payment_method: str
    paid_at: datetime | None = None
    lines: List[PayslipLineOut] = []
    employee_name: str = ""
    employee_id: int = 0
    net_after_advances: Decimal = Decimal('0.00')


class EmployeePayslipSummaryOut(Schema):
    """Summary payslip output (minimal fields)."""
    id: UUID
    payroll_run: UUID
    gross_amount: Decimal
    total_adjustments: Decimal
    net_amount: Decimal
    payment_method: str
    paid_at: datetime | None = None


# ---  SALARY ADVANCE SCHEMAS ---
class SalaryAdvanceCreateIn(Schema):
    """
    Schema for creating a new salary advance request.
    The employee/HR fills the request; 'submit' controls whether the
    request is created as DRAFT (false) or submitted to PENDING (true).
    """
    employee: UUID
    amount: Decimal
    reason: str = ""
    repayment_percentage: Decimal | None = None
    salary_base_for_deduction: str | None = None
    tax_timing: str | None = None
    deduction_window: str | None = None
    deduction_start_date: date | None = None
    deduction_end_date: date | None = None
    currency: str | None = None
    submit: bool = False


class AdvanceEmployeeOut(Schema):
    """
    Lightweight employee snapshot embedded in salary advance responses.
    Provides the key identity/career fields without the full EmployeeOut cost.
    """
    id: UUID
    matricule: str = ""
    first_name: str = ""
    middle_name: str = ""
    last_name: str = ""
    full_name: str = ""
    email: str = ""
    phone: str = ""
    job_title: str | None = None
    org_unit: str | None = None
    org_unit_id: str | None = None
    avatar_url: str | None = None
    is_active: bool = True

    @staticmethod
    def _current_pos(obj):
        """Returns the current position history entry (prefetched or queried)."""
        hist = getattr(obj, 'position_history', None)
        if hist is None:
            return None
        # Support prefetch (list) or manager (queryset)
        if hasattr(hist, 'all'):
            return hist.filter(is_current=True).select_related('position', 'org_unit').first()
        for entry in hist:
            if entry.is_current:
                return entry
        return None

    @staticmethod
    def resolve_full_name(obj) -> str:
        """Employee.first_name + middle_name + last_name (pas de propriété full_name sur le modèle)."""
        parts = [
            p for p in (
                getattr(obj, 'last_name', '').upper(),
                getattr(obj, 'middle_name', '').upper() or '',
                getattr(obj, 'first_name', '').capitalize(),
            ) if p
        ]
        return " ".join(parts)

    @staticmethod
    def resolve_job_title(obj):
        pos = AdvanceEmployeeOut._current_pos(obj)
        return pos.position.name if pos and pos.position else None

    @staticmethod
    def resolve_org_unit(obj):
        pos = AdvanceEmployeeOut._current_pos(obj)
        return pos.org_unit.name if pos and pos.org_unit else None

    @staticmethod
    def resolve_org_unit_id(obj):
        pos = AdvanceEmployeeOut._current_pos(obj)
        return str(pos.org_unit.id) if pos and pos.org_unit else None

    @staticmethod
    def resolve_avatar_url(obj):
        return obj.profile_photo.url if getattr(obj, 'profile_photo', None) else None


class SalaryAdvanceOut(Schema):
    """Output schema for retrieving a salary advance."""
    id: UUID
    employee: AdvanceEmployeeOut = Field(..., alias="employee")
    employee_name: str = ""
    amount: Decimal
    repayment_percentage: Decimal
    salary_base_for_deduction: str
    tax_timing: str
    deduction_window: str
    deduction_start_date: date | None = None
    deduction_end_date: date | None = None
    status: str = "PENDING"
    advance_type: str = "NORMAL"
    reason: str = ""
    requested_date: date | None = None
    approved_date: datetime | None = None
    rejected_date: datetime | None = None
    rejection_reason: str = ""
    deducted_amount: Decimal = Decimal('0.00')
    risk_level: str = "LOW"
    is_closed: bool = False
    remaining_balance: Decimal = Decimal('0.00')
    currency: str = "CDF"
    exchange_rate_used: Decimal | None = None
    created_at: datetime
    updated_at: datetime


class SalaryAdvanceUpdateIn(ModelSchema):
    """Schema for updating a salary advance.
    Restricted to request-level fields: the deduction configuration
    (repayment_percentage, base, timing, window, dates) is managed
    exclusively via AdvanceDeductionConfigurationUpdateIn.
    """
    class Meta:
        model = SalaryAdvance
        fields = [
            "amount",
            "reason",
            "is_closed",
        ]
        fields_optional = "__all__"


# --- ADVANCE DEDUCTION CONFIGURATION SCHEMAS ---
class AdvanceDeductionConfigurationIn(ModelSchema):
    """
    Schema for configuring advance deduction priority and activation.
    """
    class Meta:
        model = AdvanceDeductionConfiguration
        fields = [
            "employee",
            "advance",
            "priority_order",
            "is_active",
        ]


class AdvanceDeductionConfigurationCreateIn(Schema):
    """
    Schema for creating advance deduction configuration.

    Manages how the advance will be repaid at activation:
    - repayment_percentage (monthly salary percentage)
    - salary_base_for_deduction (GROSS | NET)
    - tax_timing (BEFORE_TAX | AFTER_TAX)
    - deduction_window (ALL_MONTHS | CUSTOM_PERIOD)
    - deduction_start_date / deduction_end_date (CUSTOM_PERIOD)
    - priority_order & is_active (multi-advance priority)
    """
    employee: UUID
    advance: UUID
    priority_order: int = 1
    is_active: bool = True
    repayment_percentage: Decimal = Decimal('20')
    salary_base_for_deduction: str = "NET"
    tax_timing: str = "AFTER_TAX"
    deduction_window: str = "ALL_MONTHS"
    deduction_start_date: date | None = None
    deduction_end_date: date | None = None


class AdvanceDeductionConfigurationOut(Schema):
    """
    Schema for retrieving advance deduction configuration with related data.
    """
    id: UUID
    employee: AdvanceEmployeeOut = Field(..., alias="employee")
    advance: SalaryAdvanceOut
    priority_order: int
    is_active: bool
    created_at: datetime
    updated_at: datetime


class AdvanceDeductionConfigurationUpdateIn(Schema):
    """
    Schema for updating the deduction configuration of an advance.

    This is the SINGLE place where the repayment/deduction parameters
    are modified at approval time:
    - repayment_percentage (percentage of salary deducted monthly)
    - salary_base_for_deduction (GROSS | NET)
    - tax_timing (BEFORE_TAX | AFTER_TAX)
    - deduction_window (ALL_MONTHS | CUSTOM_PERIOD)
    - deduction_start_date / deduction_end_date (CUSTOM_PERIOD)
    - priority_order & is_active (multi-advance priority)
    """
    repayment_percentage: Decimal | None = None
    salary_base_for_deduction: str | None = None
    tax_timing: str | None = None
    deduction_window: str | None = None
    deduction_start_date: date | None = None
    deduction_end_date: date | None = None
    priority_order: int | None = None
    is_active: bool | None = None


# --- REPAYMENT RECORD SCHEMAS ---
class RepaymentRecordOut(Schema):
    """Output schema for salary advance repayment records."""
    id: UUID
    salary_advance: UUID = Field(..., alias="salary_advance_id")
    payslip: UUID = Field(..., alias="payslip_id")
    amount: Decimal
    repayment_date: date
    created_at: datetime


class RepaymentRecordCreateIn(ModelSchema):
    """Input schema for recording a repayment."""
    class Meta:
        model = RepaymentRecord
        fields = [
            "salary_advance",
            "payslip",
            "amount",
        ]


class RepaymentHistoryOut(Schema):
    """Output schema for advance repayment history (computed/aggregated)."""
    salary_advance: SalaryAdvanceOut
    repayments: List[RepaymentRecordOut] = []
    total_repaid: Decimal = Decimal('0.00')
    balance_remaining: Decimal = Decimal('0.00')


# ---  WORKED DAYS RECORD SCHEMAS  ---
class WorkedDaysRecordOut(ModelSchema):
    """Output schema for worked days and overtime tracking."""
    total_overtime_hours: float = 0.0

    class Meta:
        model = WorkedDaysRecord
        fields = [
            "id",
            "employee",
            "payroll_run",
            "regular_days",
            "overtime_hours_first_tier",
            "overtime_hours_second_tier",
            "overtime_hours_weekend",
            "overtime_hours_holiday",
            "absence_days",
            "created_at",
            "updated_at",
        ]


class WorkedDaysRecordCreateIn(ModelSchema):
    """Input schema for recording worked days."""
    class Meta:
        model = WorkedDaysRecord
        fields = [
            "employee",
            "payroll_run",
            "regular_days",
            "overtime_hours_first_tier",
            "overtime_hours_second_tier",
            "overtime_hours_weekend",
            "overtime_hours_holiday",
            "absence_days",
        ]


class WorkedDaysRecordUpdateIn(ModelSchema):
    """Schema for updating worked days record."""
    class Meta:
        model = WorkedDaysRecord
        fields = [
            "regular_days",
            "overtime_hours_first_tier",
            "overtime_hours_second_tier",
            "overtime_hours_weekend",
            "overtime_hours_holiday",
            "absence_days",
        ]
        fields_optional = "__all__"


# ---  SMIG CONFIGURATION SCHEMAS  ---
class SMIGConfigurationCreateIn(ModelSchema):
    """Input schema for creating SMIG configuration."""
    class Meta:
        model = SMIGConfiguration
        fields = [
            "daily_rate",
            "effective_date",
            "is_active",
        ]


class SMIGConfigurationOut(Schema):
    """Output schema for retrieving SMIG configuration."""
    id: UUID
    daily_rate: Decimal
    effective_date: date
    is_active: bool
    created_at: datetime
    weekly_rate: Decimal = Decimal('0.00')
    monthly_rate: Decimal = Decimal('0.00')
    annual_rate: Decimal = Decimal('0.00')


class SMIGConfigurationUpdateIn(ModelSchema):
    """Schema for updating SMIG configuration."""
    class Meta:
        model = SMIGConfiguration
        fields = [
            "daily_rate",
            "effective_date",
            "is_active",
        ]
        fields_optional = "__all__"


# --- SOCIAL CONTRIBUTION RATE SCHEMAS ---
class SocialContributionRateCreateIn(ModelSchema):
    """Input schema for creating social contribution rates."""
    class Meta:
        model = SocialContributionRate
        fields = [
            "contribution_type",
            "rate_percentage",
            "employee_portion",
            "employer_portion",
            "company_size_min",
            "company_size_max",
            "ceiling_amount",
            "effective_date",
            "is_active",
        ]


class SocialContributionRateOut(Schema):
    """Output schema for retrieving social contribution rates."""
    id: UUID
    contribution_type: str
    rate_percentage: Decimal
    employee_portion: Decimal
    employer_portion: Decimal
    company_size_min: int | None = None
    company_size_max: int | None = None
    ceiling_amount: Decimal | None = None
    effective_date: date
    is_active: bool
    created_at: datetime
    updated_at: datetime


class SocialContributionRateUpdateIn(ModelSchema):
    """Schema for updating social contribution rates."""
    class Meta:
        model = SocialContributionRate
        fields = [
            "rate_percentage",
            "employee_portion",
            "employer_portion",
            "company_size_min",
            "company_size_max",
            "ceiling_amount",
            "effective_date",
            "is_active",
        ]
        fields_optional = "__all__"


# ---  OVERTIME RULE SCHEMAS  ---
class OvertimeRuleCreateIn(ModelSchema):
    """Input schema for creating overtime rules."""
    class Meta:
        model = OvertimeRule
        fields = [
            "rule_type",
            "multiplier",
            "description",
            "is_active",
        ]


class OvertimeRuleOut(ModelSchema):
    """Output schema for retrieving overtime rules."""
    class Meta:
        model = OvertimeRule
        fields = [
            "id",
            "rule_type",
            "multiplier",
            "description",
            "is_active",
            "created_at",
            "updated_at",
        ]


class OvertimeRuleUpdateIn(ModelSchema):
    """Schema for updating overtime rules."""
    class Meta:
        model = OvertimeRule
        fields = [
            "multiplier",
            "description",
            "is_active",
        ]
        fields_optional = "__all__"


# ---  LEGAL ALLOWANCE SCHEMAS  ---
class LegalAllowanceCreateIn(ModelSchema):
    """Input schema for creating legal allowances."""
    class Meta:
        model = LegalAllowance
        fields = [
            "allowance_type",
            "calculation_mode",
            "base_amount",
            "formula_description",
            "is_taxable",
            "taxable_threshold_percentage",
            "is_active",
        ]


class LegalAllowanceOut(Schema):
    """Output schema for retrieving legal allowances."""
    id: UUID
    allowance_type: str
    calculation_mode: str
    base_amount: Decimal | None = None
    formula_description: str
    is_taxable: bool
    taxable_threshold_percentage: Decimal | None = None
    is_active: bool
    created_at: datetime
    updated_at: datetime


class LegalAllowanceUpdateIn(ModelSchema):
    """Schema for updating legal allowances."""
    class Meta:
        model = LegalAllowance
        fields = [
            "calculation_mode",
            "base_amount",
            "formula_description",
            "is_taxable",
            "taxable_threshold_percentage",
            "is_active",
        ]
        fields_optional = "__all__"


# ---  TAX BRACKET SCHEMAS  ---
class TaxBracketCreateIn(ModelSchema):
    """Input schema for creating tax brackets."""
    class Meta:
        model = TaxBracket
        fields = [
            "label",
            "lower_limit",
            "upper_limit",
            "rate_percentage",
            "min_tax_amount",
            "max_tax_percentage",
            "applies_to_taxable_base",
            "is_active",
        ]


class TaxBracketOut(Schema):
    """Output schema for retrieving tax brackets."""
    id: UUID
    label: str
    lower_limit: Decimal
    upper_limit: Decimal | None = None
    rate_percentage: Decimal
    min_tax_amount: Decimal | None = None
    max_tax_percentage: Decimal | None = None
    applies_to_taxable_base: bool
    is_active: bool
    created_at: datetime
    updated_at: datetime


class TaxBracketUpdateIn(ModelSchema):
    """Schema for updating tax brackets."""
    class Meta:
        model = TaxBracket
        fields = [
            "label",
            "lower_limit",
            "upper_limit",
            "rate_percentage",
            "min_tax_amount",
            "max_tax_percentage",
            "applies_to_taxable_base",
            "is_active",
        ]
        fields_optional = "__all__"


# ---  FILTER SCHEMAS  ---
class EmployeeContractListFilterIn(FilterSchema):
    """Filter schema for employee contracts listing."""
    employee_id: Annotated[UUID | None, FilterLookup("employee_id")] = None
    is_active: Annotated[bool | None, FilterLookup("is_active")] = None
    remuneration_type: Annotated[str | None, FilterLookup("remuneration_type")] = None
    contract_type: Annotated[str | None, FilterLookup("contract_type")] = None
    start_date_from: Annotated[date | None, FilterLookup("start_date__gte")] = None
    start_date_to: Annotated[date | None, FilterLookup("start_date__lte")] = None
    end_date_from: Annotated[date | None, FilterLookup("end_date__gte")] = None
    end_date_to: Annotated[date | None, FilterLookup("end_date__lte")] = None


class PayrollRunListFilterIn(FilterSchema):
    """Filter schema for payroll runs listing."""
    status: Annotated[str | None, FilterLookup("status")] = None
    search: Annotated[str | None, FilterLookup("code__icontains")] = None
    org_unit: Annotated[str | None, FilterLookup("payslips__contract__employee__position_history__org_unit__name__icontains")] = None
    period_start_from: Annotated[date | None, FilterLookup("start_date__gte")] = None
    period_start_to: Annotated[date | None, FilterLookup("start_date__lte")] = None
    period_end_from: Annotated[date | None, FilterLookup("end_date__gte")] = None
    period_end_to: Annotated[date | None, FilterLookup("end_date__lte")] = None


class AdvanceListFilterIn(BaseFilter):
    """Filter schema for salary advances listing.

    Supports server-side:
    - search: global text search (employee name, matricule, reason)
    - status: comma-separated statuses (PENDING, APPROVED, ACTIVE, ...)
    - risk_level: comma-separated risk levels (LOW, MEDIUM, HIGH)
    - advance_type, employee_id, date range
    """
    employee_id: Annotated[UUID | None, FilterLookup("employee_id")] = None
    status: Optional[str] = None
    risk_level: Optional[str] = None
    advance_type: Annotated[str | None, FilterLookup("advance_type")] = None
    requested_date_from: Annotated[date | None, FilterLookup("requested_date__gte")] = None
    requested_date_to: Annotated[date | None, FilterLookup("requested_date__lte")] = None

    def filter_search(self, value: str) -> Q:
        """Broad global search across employee identity and advance reason."""
        if not value:
            return Q()
        return (
            Q(employee__first_name__icontains=value)
            | Q(employee__middle_name__icontains=value)
            | Q(employee__last_name__icontains=value)
            | Q(employee__matricule__icontains=value)
            | Q(reason__icontains=value)
        )

    def filter_status(self, value: Optional[str]) -> Q:
        """Filter by status (supports comma-separated values)."""
        if not value:
            return Q()
        if ',' in value:
            statuses = [s.strip() for s in value.split(',') if s.strip()]
            return Q(status__in=statuses)
        return Q(status__iexact=value)

    def filter_risk_level(self, value: Optional[str]) -> Q:
        """Filter by risk level (supports comma-separated values)."""
        if not value:
            return Q()
        if ',' in value:
            levels = [r.strip() for r in value.split(',') if r.strip()]
            return Q(risk_level__in=levels)
        return Q(risk_level__iexact=value)


class AdjustmentListFilterIn(FilterSchema):
    """Filter schema for payroll adjustments listing."""
    adjustment_type: Annotated[str | None, FilterLookup("adjustment_type")] = None
    is_mandatory: Annotated[bool | None, FilterLookup("is_mandatory")] = None
    is_active: Annotated[bool | None, FilterLookup("is_active")] = None


class ContractAdjustmentListFilterIn(FilterSchema):
    """Filter schema for contract adjustments listing."""
    contract_id: Annotated[UUID | None, FilterLookup("contract_id")] = None
    employee_id: Annotated[UUID | None, FilterLookup("employee_id")] = None
    adjustment_type: Annotated[str | None, FilterLookup("adjustment__adjustment_type")] = None
    is_active: Annotated[bool | None, FilterLookup("is_active")] = None
    effective_date_from: Annotated[date | None, FilterLookup("start_date__gte")] = None
    effective_date_to: Annotated[date | None, FilterLookup("start_date__lte")] = None


class PayslipGenerationStatusOut(Schema):
    """Output schema for payslip generation status (async operation)."""
    task_id: str | None = None
    status: str
    total_employees: int
    processed_employees: int = 0
    failed_employees: int = 0
    progress_percentage: int = 0


class AdvanceBalanceOut(Schema):
    """Output schema for advance balance and repayment status."""
    total_amount: Decimal
    total_repaid: Decimal = Decimal('0.00')
    remaining_balance: Decimal = Decimal('0.00')
    repayment_progress: int = 0
    estimated_repayment_date: date | None = None


# ---  CONFIGURATION SCHEMAS  ---
class SMIGConfigurationListFilterIn(FilterSchema):
    """Filter schema for SMIG rates listing."""
    effective_date_from: Annotated[date | None, FilterLookup("effective_date__gte")] = None
    effective_date_to: Annotated[date | None, FilterLookup("effective_date__lte")] = None
    currency: Annotated[str | None, FilterLookup("currency")] = None
    min_amount: Annotated[bool | None, FilterLookup("amount__gte")] = None


class SocialContributionRateListFilterIn(FilterSchema):
    """Filter schema for contribution rates listing."""
    contribution_type: Annotated[str | None, FilterLookup("contribution_type")] = None
    is_active: Annotated[bool | None, FilterLookup("is_active")] = None


class OvertimeRuleListFilterIn(FilterSchema):
    """Filter schema for overtime rules listing."""
    rule_type: Annotated[str | None, FilterLookup("rule_type")] = None


class TaxBracketListFilterIn(FilterSchema):
    """Filter schema for tax brackets listing."""
    lower_limit_from: Annotated[Decimal | None, FilterLookup("lower_limit__gte")] = None
    lower_limit_to: Annotated[Decimal | None, FilterLookup("lower_limit__lte")] = None


class LegalAllowanceListFilterIn(FilterSchema):
    """Filter schema for legal allowances listing."""
    allowance_type: Annotated[str | None, FilterLookup("allowance_type")] = None
    is_mandatory: Annotated[bool | None, FilterLookup("is_mandatory")] = None
    calculation_method: Annotated[str | None, FilterLookup("calculation_method")] = None


class SalaryAdvanceDetailOut(ModelSchema):
    """Detailed salary advance output with configuration and repayment info."""
    remaining_balance: Decimal = Decimal('0.00')
    total_repaid: Decimal = Decimal('0.00')
    repayment_count: int = 0
    configuration: AdvanceDeductionConfigurationOut | None = None

    class Meta:
        model = SalaryAdvance
        fields = [
            "id",
            "employee",
            "amount",
            "repayment_percentage",
            "salary_base_for_deduction",
            "tax_timing",
            "deduction_window",
            "deduction_start_date",
            "deduction_end_date",
            "is_closed",
            "created_at",
            "updated_at",
        ]


# ---  PAYROLL SUMMARY SCHEMAS  ---
class PayrollRunSummaryNestedOut(Schema):
    id: UUID
    code: str
    period: str
    status: str

class PayrollFinancialSummaryOut(Schema):
    total_employees: int
    total_gross_salary: Decimal
    total_net_salary: Decimal
    total_ipr_to_pay: Decimal
    total_cnss_employee: Decimal
    total_cnss_employer: Decimal
    total_inpp: Decimal
    total_onem: Decimal
    total_employer_liabilities: Decimal
    total_cost_to_company: Decimal

class AdjustmentSummaryItem(Schema):
    total: Decimal
    count: int

class PayrollRunSummaryOut(Schema):
    """Full summary of a payroll run including DRC-specific financial breakdown."""
    payroll_run: PayrollRunSummaryNestedOut
    summary: PayrollFinancialSummaryOut
    adjustments: Dict[str, AdjustmentSummaryItem]


# ---  EMPLOYER CHARGE SCHEMAS ---
class EmployerChargeOut(Schema):
    """Output schema for employer charges."""
    id: UUID
    payslip_id: UUID
    contribution_type: str
    label: str
    amount: Decimal
    base_amount: Decimal

