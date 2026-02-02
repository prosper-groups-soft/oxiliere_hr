from typing               import List, Dict
from decimal              import Decimal
from uuid                 import UUID
from datetime             import date
from ninja                import Schema, ModelSchema, FilterSchema
from pydantic             import Field
from hr.employees.schemas import EmployeeOut

from .models import (
    PayrollConfiguration,
    EmployeeContract,
    PayrollAdjustment,
    EmployeeAdjustment,
    PayrollRun,
    PayslipLine,
    EmployeePayslip,    
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


# ---------------- PAYROLL CONFIGURATION SCHEMAS  -------------------
class ConfigurePayrollIn(ModelSchema):
    """Input schema for creating/updating payroll configuration."""
    class Meta:
        model = PayrollConfiguration
        fields = [
            "currency",
            "default_payment_method",
            "work_hours_per_month",
            "housing_allowance_min_percentage",
            "family_allowance_min_amount",
            "family_allowance_smig_divider",
            "overtime_multiplier",
            "include_leaves_in_payroll",
            "leave_deduction_divisor",
            "use_theoretical_days_from_attendance",
            "fixed_deduction_per_absent_day",
            "exchange_rate_usd_cdf",
            "exchange_rate_source",
        ]


class PayrollConfigurationOut(ModelSchema):
    """Output schema for retrieving payroll configuration."""
    class Meta:
        model = PayrollConfiguration
        fields = [
            "id",
            "currency",
            "default_payment_method",
            "work_hours_per_month",
            "housing_allowance_min_percentage",
            "family_allowance_min_amount",
            "family_allowance_smig_divider",
            "overtime_multiplier",
            "include_leaves_in_payroll",
            "leave_deduction_divisor",
            "use_theoretical_days_from_attendance",
            "fixed_deduction_per_absent_day",
            "exchange_rate_usd_cdf",
            "exchange_rate_source",
            "created_at",
            "updated_at",
        ]


class PayrollConfigurationUpdateIn(ModelSchema):
    """Schema for partial updates to payroll configuration."""
    class Meta:
        model = PayrollConfiguration
        fields = [
            "currency",
            "default_payment_method",
            "work_hours_per_month",
            "housing_allowance_min_percentage",
            "family_allowance_min_amount",
            "family_allowance_smig_divider",
            "overtime_multiplier",
            "include_leaves_in_payroll",
            "leave_deduction_divisor",
            "use_theoretical_days_from_attendance",
            "fixed_deduction_per_absent_day",
            "exchange_rate_usd_cdf",
            "exchange_rate_source",
        ]
        fields_optional = "__all__"


# ----------------  EMPLOYEE CONTRACT SCHEMAS  -------------------
class EmployeeContractCreateIn(ModelSchema):
    """Input schema for creating an employee contract."""
    class Meta:
        model = EmployeeContract
        fields = [
            "employee",
            "remuneration_type",
            "payment_period",
            "contract_type",
            "base_salary",
            "salary_base_type",
            "hourly_rate",
            "currency",
            "start_date",
            "end_date",
            "is_active",
        ]


class EmployeeContractOut(ModelSchema):
    """Output schema for retrieving employee contract details."""
    employee: EmployeeOut

    class Meta:
        model = EmployeeContract
        fields = [
            "id",
            "employee",
            "remuneration_type",
            "payment_period",
            "contract_type",
            "base_salary",
            "salary_base_type",
            "hourly_rate",
            "currency",
            "start_date",
            "end_date",
            "is_active",
            "created_at",
            "updated_at",
        ]


class EmployeeContractUpdateIn(ModelSchema):
    """Schema for updating employee contract (all fields optional)."""
    class Meta:
        model = EmployeeContract
        fields = [
            "remuneration_type",
            "payment_period",
            "contract_type",
            "base_salary",
            "salary_base_type",
            "hourly_rate",
            "currency",
            "start_date",
            "end_date",
            "is_active",
        ]
        fields_optional = "__all__"


# ----------------  PAYROLL ADJUSTMENT SCHEMAS  -------------------
class PayrollAdjustmentCreateIn(ModelSchema):
    """Input schema for defining a payroll adjustment template."""
    class Meta:
        model = PayrollAdjustment
        fields = [
            "name",
            "adjustment_type",
            "calculation_mode",
            "amount",
            "percentage",
            "is_mandatory",
            "is_active",
        ]


class PayrollAdjustmentOut(ModelSchema):
    """Output schema for retrieving payroll adjustment details."""
    class Meta:
        model = PayrollAdjustment
        fields = [
            "id",
            "name",
            "adjustment_type",
            "calculation_mode",
            "amount",
            "percentage",
            "is_mandatory",
            "is_active",
            "created_at",
            "updated_at",
        ]


class PayrollAdjustmentUpdateIn(ModelSchema):
    """Schema for updating payroll adjustment."""
    class Meta:
        model = PayrollAdjustment
        fields = [
            "name",
            "adjustment_type",
            "calculation_mode",
            "amount",
            "percentage",
            "is_mandatory",
            "is_active",
        ]
        fields_optional = "__all__"


class EmployeeAdjustmentCreateIn(ModelSchema):
    """Input schema for assigning an adjustment to an employee."""
    class Meta:
        model = EmployeeAdjustment
        fields = [
            "employee",
            "adjustment",
            "start_date",
            "end_date",
            "custom_amount",
            "is_active",
        ]


class EmployeeAdjustmentOut(ModelSchema):
    """Output schema for retrieving employee adjustment assignments."""
    adjustment: PayrollAdjustmentOut

    class Meta:
        model = EmployeeAdjustment
        fields = [
            "id",
            "employee",
            "adjustment",
            "start_date",
            "end_date",
            "custom_amount",
            "is_active",
            "created_at",
            "updated_at",
        ]


class EmployeeAdjustmentUpdateIn(ModelSchema):
    """Schema for updating employee adjustment assignments."""
    class Meta:
        model = EmployeeAdjustment
        fields = [
            "start_date",
            "end_date",
            "custom_amount",
            "is_active",
        ]
        fields_optional = "__all__"


# ----------------  PAYROLL RUN SCHEMAS  -------------------
class PayrollRunCreateIn(ModelSchema):
    """Input schema for creating a payroll run."""
    class Meta:
        model = PayrollRun
        fields = [
            "start_date",
            "end_date",
        ]


class PayrollRunOut(ModelSchema):
    """Output schema for retrieving payroll run details."""
    total_payslips: int

    class Meta:
        model = PayrollRun
        fields = [
            "id",
            "code",
            "start_date",
            "end_date",
            "status",
            "exchange_rate_applied",
            "created_at",
            "updated_at",
        ]


class PayrollRunDetailOut(ModelSchema):
    """Detailed output schema for payroll run with summary statistics."""
    total_payslips: int
    processed_payslips: int
    pending_payslips: int
    total_gross_amount: Decimal
    total_net_amount: Decimal
    total_deductions: Decimal

    class Meta:
        model = PayrollRun
        fields = [
            "id",
            "code",
            "start_date",
            "end_date",
            "status",
            "exchange_rate_applied",
            "created_at",
            "updated_at",
        ]


class PayrollRunUpdateIn(ModelSchema):
    """Schema for updating payroll run status."""
    class Meta:
        model = PayrollRun
        fields = [
            "status",
            "exchange_rate_applied",
        ]
        fields_optional = "__all__"


# ----------------  PAYSLIP LINE SCHEMAS  -------------------
class PayslipLineOut(ModelSchema):
    """Output schema for payslip detail lines."""
    class Meta:
        model = PayslipLine
        fields = [
            "id",
            "label",
            "amount",
            "adjustment_type",
        ]


class PayslipLineCreateIn(ModelSchema):
    """Input schema for creating payslip lines."""
    class Meta:
        model = PayslipLine
        fields = [
            "label",
            "amount",
            "adjustment_type",
        ]


# ----------------  EMPLOYEE PAYSLIP SCHEMAS  -------------------
class EmployeePayslipOut(ModelSchema):
    """Output schema for complete payslip details."""
    class Meta:
        model = EmployeePayslip
        fields = [
            "id",
            "payroll_run",
            "contract",
            "base_salary_snapshot",
            "gross_amount",
            "cnss_amount",
            "onem_amount",
            "inpp_amount",
            "ipr_amount",
            "family_allowance",
            "housing_allowance",
            "transport_allowance",
            "total_adjustments",
            "net_amount",
            "worked_days",
            "worked_hours",
            "overtime_hours",
            "paid_leave_days",
            "unpaid_leave_days",
            "contract_currency",
            "exchange_rate_used",
            "currency",
            "payment_method",
            "paid_at",
            "created_at",
            "updated_at",
        ]


class EmployeePayslipDetailOut(ModelSchema):
    """Detailed payslip output with computed fields."""
    lines: List[PayslipLineOut] = []
    employee_name: str = ""
    employee_id: int = 0
    net_after_advances: Decimal = Decimal('0.00')

    class Meta:
        model = EmployeePayslip
        fields = [
            "id",
            "payroll_run",
            "contract",
            "base_salary_snapshot",
            "gross_amount",
            "cnss_amount",
            "onem_amount",
            "inpp_amount",
            "ipr_amount",
            "family_allowance",
            "housing_allowance",
            "transport_allowance",
            "total_adjustments",
            "net_amount",
            "worked_days",
            "worked_hours",
            "overtime_hours",
            "paid_leave_days",
            "unpaid_leave_days",
            "contract_currency",
            "exchange_rate_used",
            "currency",
            "payment_method",
            "paid_at",
        ]


class EmployeePayslipSummaryOut(ModelSchema):
    """Summary payslip output (minimal fields)."""
    class Meta:
        model = EmployeePayslip
        fields = [
            "id",
            "payroll_run",
            "gross_amount",
            "total_adjustments",
            "net_amount",
            "payment_method",
            "paid_at",
        ]


# ----------------  SALARY ADVANCE SCHEMAS  -------------------
class SalaryAdvanceCreateIn(ModelSchema):
    """
    Schema for creating a new salary advance with flexible deduction configuration.
    """
    class Meta:
        model = SalaryAdvance
        fields = [
            "employee",
            "amount",
            "repayment_percentage",
            "salary_base_for_deduction",
            "tax_timing",
            "deduction_window",
            "deduction_start_date",
            "deduction_end_date",
        ]


class SalaryAdvanceOut(ModelSchema):
    """
    Schema for retrieving salary advance details with remaining balance.
    """
    remaining_balance: Decimal = Decimal('0.00')

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


class SalaryAdvanceUpdateIn(ModelSchema):
    """Schema for updating a salary advance."""
    class Meta:
        model = SalaryAdvance
        fields = [
            "amount",
            "repayment_percentage",
            "salary_base_for_deduction",
            "tax_timing",
            "deduction_window",
            "deduction_start_date",
            "deduction_end_date",
            "is_closed",
        ]
        fields_optional = "__all__"


class SalaryAdvanceDetailOut(ModelSchema):
    """Detailed advance output with repayment history."""
    remaining_balance: Decimal
    total_repaid: Decimal = Decimal('0.00')
    repayment_count: int = 0

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


# ----------------  ADVANCE DEDUCTION CONFIGURATION SCHEMAS  -------------------
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


class AdvanceDeductionConfigurationCreateIn(ModelSchema):
    """
    Schema for creating advance deduction configuration.
    
    Manages priority order for deducting multiple advances from the same employee.
    """
    class Meta:
        model = AdvanceDeductionConfiguration
        fields = [
            "employee",
            "advance",
            "priority_order",
            "is_active",
        ]


class AdvanceDeductionConfigurationOut(ModelSchema):
    """
    Schema for retrieving advance deduction configuration with related data.
    """
    advance: SalaryAdvanceOut

    class Meta:
        model = AdvanceDeductionConfiguration
        fields = [
            "id",
            "employee",
            "advance",
            "priority_order",
            "is_active",
            "created_at",
            "updated_at",
        ]


class AdvanceDeductionConfigurationUpdateIn(ModelSchema):
    """Schema for updating advance deduction configuration."""
    class Meta:
        model = AdvanceDeductionConfiguration
        fields = [
            "priority_order",
            "is_active",
        ]
        fields_optional = "__all__"


# ----------------  REPAYMENT RECORD SCHEMAS  -------------------
class RepaymentRecordOut(ModelSchema):
    """Output schema for salary advance repayment records."""
    class Meta:
        model = RepaymentRecord
        fields = [
            "id",
            "salary_advance",
            "payslip",
            "amount",
            "repayment_date",
            "created_at",
        ]


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


# ----------------  WORKED DAYS RECORD SCHEMAS  -------------------
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
            "overtime_hours_holiday",
            "absence_days",
        ]
        fields_optional = "__all__"


# ----------------  SMIG CONFIGURATION SCHEMAS  -------------------
class SMIGConfigurationCreateIn(ModelSchema):
    """Input schema for creating SMIG configuration."""
    class Meta:
        model = SMIGConfiguration
        fields = [
            "daily_rate",
            "effective_date",
            "is_active",
        ]


class SMIGConfigurationOut(ModelSchema):
    """Output schema for retrieving SMIG configuration."""
    weekly_rate: Decimal = Decimal('0.00')
    monthly_rate: Decimal = Decimal('0.00')
    annual_rate: Decimal = Decimal('0.00')

    class Meta:
        model = SMIGConfiguration
        fields = [
            "id",
            "daily_rate",
            "effective_date",
            "is_active",
            "created_at",
        ]


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


# ----------------  SOCIAL CONTRIBUTION RATE SCHEMAS  -------------------
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


class SocialContributionRateOut(ModelSchema):
    """Output schema for retrieving social contribution rates."""
    class Meta:
        model = SocialContributionRate
        fields = [
            "id",
            "contribution_type",
            "rate_percentage",
            "employee_portion",
            "employer_portion",
            "company_size_min",
            "company_size_max",
            "ceiling_amount",
            "effective_date",
            "is_active",
            "created_at",
            "updated_at",
        ]


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


# ----------------  OVERTIME RULE SCHEMAS  -------------------
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


# ---------------- LEGAL ALLOWANCE SCHEMAS  -------------------
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


class LegalAllowanceOut(ModelSchema):
    """Output schema for retrieving legal allowances."""
    class Meta:
        model = LegalAllowance
        fields = [
            "id",
            "allowance_type",
            "calculation_mode",
            "base_amount",
            "formula_description",
            "is_taxable",
            "taxable_threshold_percentage",
            "is_active",
            "created_at",
            "updated_at",
        ]


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


# ----------------  TAX BRACKET SCHEMAS  -------------------
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


class TaxBracketOut(ModelSchema):
    """Output schema for retrieving tax brackets."""
    class Meta:
        model = TaxBracket
        fields = [
            "id",
            "label",
            "lower_limit",
            "upper_limit",
            "rate_percentage",
            "min_tax_amount",
            "max_tax_percentage",
            "applies_to_taxable_base",
            "is_active",
            "created_at",
            "updated_at",
        ]


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


# ---------------- FILTER SCHEMAS  -------------------
class EmployeeContractListFilterIn(FilterSchema):
    """Filter schema for employee contracts listing."""
    employee_id: UUID | None = Field(None, q="employee_id")
    is_active: bool | None = Field(None, q="is_active")
    remuneration_type: str | None = Field(None, q="remuneration_type")
    contract_type: str | None = Field(None, q="contract_type")
    start_date_from: date | None = Field(None, q="start_date__gte")
    start_date_to: date | None = Field(None, q="start_date__lte")
    end_date_from: date | None = Field(None, q="end_date__gte")
    end_date_to: date | None = Field(None, q="end_date__lte")


class PayrollRunListFilterIn(FilterSchema):
    """Filter schema for payroll runs listing."""
    status: str | None = Field(None, q="status")
    period_start_from: date | None = Field(None, q="period_start__gte")
    period_start_to: date | None = Field(None, q="period_start__lte")
    period_end_from: date | None = Field(None, q="period_end__gte")
    period_end_to: date | None = Field(None, q="period_end__lte")


class AdvanceListFilterIn(FilterSchema):
    """Filter schema for salary advances listing."""
    employee_id: UUID | None = Field(None, q="employee_id")
    status: str | None = Field(None, q="status")
    advance_type: str | None = Field(None, q="advance_type")
    requested_date_from: date | None = Field(None, q="requested_date__gte")
    requested_date_to: date | None = Field(None, q="requested_date__lte")


class AdjustmentListFilterIn(FilterSchema):
    """Filter schema for payroll adjustments listing."""
    adjustment_type: str | None = Field(None, q="adjustment_type")
    is_mandatory: bool | None = Field(None, q="is_mandatory")
    is_active: bool | None = Field(None, q="is_active")


class EmployeeAdjustmentListFilterIn(FilterSchema):
    """Filter schema for employee adjustments listing."""
    employee_id: UUID | None = Field(None, q="employee_id")
    adjustment_type: str | None = Field(None, q="adjustment__adjustment_type")
    is_active: bool | None = Field(None, q="is_active")
    effective_date_from: date | None = Field(None, q="start_date__gte")
    effective_date_to: date | None = Field(None, q="start_date__lte")


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


# ----------------  CONFIGURATION SCHEMAS  -------------------
class SMIGConfigurationListFilterIn(FilterSchema):
    """Filter schema for SMIG rates listing."""
    effective_date_from: date | None = Field(None, q="effective_date__gte")
    effective_date_to: date | None = Field(None, q="effective_date__lte")
    currency: str | None = Field(None, q="currency")
    min_amount: bool | None = Field(None, q="amount__gte")


class SocialContributionRateListFilterIn(FilterSchema):
    """Filter schema for contribution rates listing."""
    contribution_type: str | None = Field(None, q="contribution_type")
    is_active: bool | None = Field(None, q="is_active")


class OvertimeRuleListFilterIn(FilterSchema):
    """Filter schema for overtime rules listing."""
    rule_type: str | None = Field(None, q="rule_type")


class TaxBracketListFilterIn(FilterSchema):
    """Filter schema for tax brackets listing."""
    fiscal_year: int | None = Field(None, q="fiscal_year")
    min_amount_from: Decimal | None = Field(None, q="min_amount__gte")
    min_amount_to: Decimal | None = Field(None, q="min_amount__lte")


class LegalAllowanceListFilterIn(FilterSchema):
    """Filter schema for legal allowances listing."""
    allowance_type: str | None = Field(None, q="allowance_type")
    is_mandatory: bool | None = Field(None, q="is_mandatory")
    calculation_method: str | None = Field(None, q="calculation_method")


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


# ----------------  PAYROLL SUMMARY SCHEMAS  -------------------
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
