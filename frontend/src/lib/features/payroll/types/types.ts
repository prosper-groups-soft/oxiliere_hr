/** Supported currencies for payroll (USD for expats, CDF for local employees) */
export type Currency = 'USD' | 'CDF';

/** Steps in the payroll processing workflow */
export type PayrollStep = 'preparation' | 'calculation' | 'review' | 'approval' | 'payment';

/** Status of a payroll run throughout its lifecycle */
export type PayrollStatus = 'draft' | 'calculated' | 'reviewed' | 'approved' | 'paid' | 'closed' | 'archived';

/** Backend statuses returned by the payroll API (Django-Ninja PayrollStatus) */
export type BackendPayrollRunStatus = 'DRAFT' | 'REVIEWED' | 'APPROVED' | 'VALIDATED' | 'PAID' | 'CANCELED' | 'PROCESSING';

/** Simplified status for the payroll run list view (condensed from PayrollStatus) */
export type RunListStatus = 'draft' | 'processing' | 'closed' | 'error';

/** Lifecycle status of a payroll cycle (a monthly/closure period) */
export type PayrollCycleStatus = 'open' | 'closed' | 'archived';

/** Status of an individual employee payslip */
export type PayslipStatus = 'draft' | 'calculated' | 'paid';

/** Status of a salary advance request */
export type AdvanceStatus = 'DRAFT' | 'PENDING' | 'APPROVED' | 'REJECTED' | 'ACTIVE' | 'CLOSED';

/** Maps a backend PayrollRun status to the condensed list status used by the UI. */
export function backendToRunListStatus(status: BackendPayrollRunStatus | string): RunListStatus {
	switch (status) {
		case 'DRAFT':
		case 'CANCELED':
			return 'draft';
		case 'PROCESSING':
			return 'processing';
		case 'VALIDATED':
		case 'REVIEWED':
		case 'APPROVED':
		case 'PAID':
			return 'closed';
		default:
			return 'error';
	}
}

/** Maps a backend PayrollRun status to the rich wizard status. */
export function backendToPayrollStatus(status: BackendPayrollRunStatus | string): PayrollStatus {
	switch (status) {
		case 'DRAFT': return 'draft';
		case 'PROCESSING': return 'calculated';
		case 'VALIDATED': return 'reviewed';
		case 'REVIEWED': return 'reviewed';
		case 'APPROVED': return 'approved';
		case 'PAID': return 'paid';
		case 'CANCELED': return 'closed';
		default: return 'draft';
	}
}

/** Formats a YYYY-MM period into a French month/year label (e.g. 2026-03 → 'Mars 2026'). */
export function formatPeriodLabel(period: string): string {
	const d = new Date(`${period}-01T00:00:00`);
	if (Number.isNaN(d.getTime())) return period;
	return d.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
}

/** Converts backend start/end dates (YYYY-MM-DD) into the display period label. */
export function periodLabelFromDates(startDate: string, endDate: string): string {
	const start = new Date(`${startDate}T00:00:00`);
	const end = new Date(`${endDate}T00:00:00`);
	if (Number.isNaN(start.getTime()) || Number.isNaN(end.getTime())) return `${startDate} - ${endDate}`;
	if (start.getMonth() === end.getMonth() && start.getFullYear() === end.getFullYear()) {
		return start.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
	}
	return `${start.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })} - ${end.toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}`;
}

/** Derives the YYYY-MM available-period key from backend dates. */
export function availablePeriodFromDates(startDate: string): string {
	const start = new Date(`${startDate}T00:00:00`);
	if (Number.isNaN(start.getTime())) return startDate.slice(0, 7);
	return `${start.getFullYear()}-${String(start.getMonth() + 1).padStart(2, '0')}`;
}

/** Returns the current month as YYYY-MM (used as default current period). */
export function currentMonthKey(): string {
	const now = new Date();
	return `${now.getFullYear()}-${String(now.getMonth() + 1).padStart(2, '0')}`;
}

/** Risk level of a salary advance (backend persisted) */
export type AdvanceRiskLevel = 'LOW' | 'MEDIUM' | 'HIGH';

/** Base salary the advance deduction is calculated on (GROSS | NET). */
export type AdvanceDeductionBase = 'GROSS' | 'NET';

/** Timing of the advance deduction relative to tax (BEFORE_TAX | AFTER_TAX). */
export type AdvanceTaxTiming = 'BEFORE_TAX' | 'AFTER_TAX';

/** Time window during which advance deductions are applied. */
export type AdvanceDeductionWindow = 'ALL_MONTHS' | 'CUSTOM_PERIOD';

/** Human-readable labels for advance deduction base (French UI). */
export const ADVANCE_DEDUCTION_BASE_LABELS: Record<AdvanceDeductionBase, string> = {
	GROSS: 'Salaire brut',
	NET: 'Salaire net',
};

/** Human-readable labels for tax timing (French UI). */
export const ADVANCE_TAX_TIMING_LABELS: Record<AdvanceTaxTiming, string> = {
	BEFORE_TAX: 'Avant impôt (réduit le taxable)',
	AFTER_TAX: 'Après impôt (sans impact fiscal)',
};

/** Human-readable labels for deduction window (French UI). */
export const ADVANCE_DEDUCTION_WINDOW_LABELS: Record<AdvanceDeductionWindow, string> = {
	ALL_MONTHS: 'Tous les mois (jusqu\'à remboursement)',
	CUSTOM_PERIOD: 'Période personnalisée',
};

/** Mode exclusif de déduction des absences non payées (RDC) */
export type LeaveDeductionMode = 'DISABLED' | 'DAILY_RATE' | 'CALENDAR_DAYS' | 'ATTENDANCE_DAYS' | 'FIXED_AMOUNT';

/** Global payroll configuration (mirrors PayrollConfigurationOut in backend schemas.py) */
export interface PayrollConfiguration {
	id: string;
	currency: string;
	default_payment_method: string;
	work_hours_per_week: number;
	work_hours_per_month: number;
	housing_allowance_min_percentage: number;
	include_leaves_in_payroll: boolean;
	leave_deduction_divisor: number;
	leave_deduction_mode: LeaveDeductionMode;
	fixed_deduction_per_absent_day: number | null;
	exchange_rate_usd_cdf: number;
	created_at: string;
	updated_at: string;
}

/** Partial update payload for the payroll configuration */
export type PayrollConfigurationUpdate = Partial<Omit<PayrollConfiguration, 'id' | 'created_at' | 'updated_at'>>;

/** SMIG rate with history (mirrors SMIGConfigurationOut) */
export interface SMIGConfiguration {
	id: string;
	daily_rate: number;
	effective_date: string;
	is_active: boolean;
	weekly_rate: number;
	monthly_rate: number;
	annual_rate: number;
	created_at: string;
}

/** Progressive income tax bracket (mirrors TaxBracketOut) */
export interface TaxBracketConfig {
	id: string;
	label: string;
	lower_limit: number;
	upper_limit: number | null;
	rate_percentage: number;
	min_tax_amount: number | null;
	max_tax_percentage: number | null;
	applies_to_taxable_base: boolean;
	is_active: boolean;
	created_at: string;
}

/** Payroll adjustment template from the master catalog (mirrors PayrollAdjustmentOut) */
export interface PayrollAdjustmentConfig {
	id: string;
	/** Code normalisé du catalogue (ex. IND_LOG, ALLOC_REPAS) — écran S10 */
	code?: string | null;
	name: string;
	adjustment_type: string;
	calculation_mode: string;
	amount: number | null;
	percentage: number | null;
	is_mandatory: boolean;
	is_active: boolean;
	is_taxable: boolean;
	is_cnss_subject: boolean;
	formula_description: string;
	created_at: string;
	updated_at: string;
}

/** Allocation légale (Logement, Transport) — mirrors LegalAllowanceOut backend */
export type LegalAllowanceType = 'HOUSING' | 'TRANSPORT';

export interface LegalAllowanceConfig {
	id: string;
	allowance_type: LegalAllowanceType;
	calculation_mode: string;
	base_amount: number | null;
	formula_description: string;
	is_taxable: boolean;
	taxable_threshold_percentage: number | null;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}

/** Règle d'heures supplémentaires RDC (mirrors OvertimeRuleOut backend).
 *  Palier progressif : 130 % (6 premières h), 160 % (au-delà), 200 % (week-end/férié), 150 % (nuit). */
export interface OvertimeRule {
	id: string;
	rule_type: 'FIRST_TIER' | 'SUBSEQUENT_HOURS' | 'WEEKEND' | 'HOLIDAY' | 'NIGHT';
	multiplier: number;
	description: string;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}


/* ─── Pay Code (semantic catalog) ─── */

/**
 * Semantic catalog of all payroll line item codes.
 * Each code represents a specific earning or deduction that can appear on a payslip.
 * Codes prefixed with OT_ refer to overtime (heures supplémentaires).
 */
export type PayCode =
	| 'BASE_SALARY' | 'PARTIAL_SALARY' | 'SENIORITY'
	| 'PERF_BONUS' | 'FUNCTION_BONUS' | 'RISK_BONUS' | 'HOUSING_BONUS' | 'MEAL_BONUS' | 'COMMISSION'
	| 'OT_30' | 'OT_60' | 'OT_HOLIDAY' | 'NIGHT_OT'
	| 'HOUSING_ALLOWANCE' | 'TRANSPORT_ALLOWANCE' | 'MISSION_ALLOWANCE' | 'FUNCTIONAL_HOUSING' | 'COMPANY_CAR'
	| 'THIRTEENTH_MONTH' | 'EXCEPTIONAL_BONUS'
	| 'SALARY_BACKPAY' | 'PAID_LEAVE' | 'SEVERANCE_NOTICE' | 'SEVERANCE_PAY'
	| 'SALARY_ADVANCE' | 'GARNISHMENT'
	| 'CNSS_EMPLOYEE' | 'IPR' | 'IRPP' | 'CNSS_EMPLOYER' | 'INPP' | 'ONEM' | 'MUTUAL_CONTRIBUTION';

/** Category grouping for pay elements on the payslip */
export type PayElementCategory = 'base_salary' | 'bonus' | 'overtime' | 'allowance' | 'gratuity' | 'benefit_in_kind' | 'other';

/** Calculation method for a pay element: fixed amount, hourly rate, daily rate, or formula-based */
export type PayElementModeCalcul = 'fixed' | 'hourly_rate' | 'daily' | 'formula';


/* ─── Pay element (catalog) ─── */

/**
 * A pay element template from the master catalog.
 * Defines how a given PayCode should be calculated by default.
 */
export interface PayElement {
	/** The unique pay code this element refers to */
	code: PayCode;
	/** Display label shown on the payslip */
	label: string;
	/** Functional category for grouping */
	category: PayElementCategory;
	/** How the amount is derived — fixed, hourly, daily, or formula */
	modeCalcul: PayElementModeCalcul;
	/** Nominal amount or hourly rate depending on modeCalcul */
	amount: number;
	/** For hourly_rate (hours worked) or daily (days worked) */
	quantity?: number;
	/** Rate used when modeCalcul is 'formula' */
	rate?: number;
	/** Calculated formula expression (e.g. "amount * quantity") */
	formula?: string;
	/** Whether this element contributes to the taxable net (net imposable) */
	isTaxable: boolean;
	/** Whether this element is subject to CNSS (social security) contributions */
	subjectToCnss: boolean;
	/** Whether this element is subject to INPP (occupational risk) contributions */
	subjectToInpp: boolean;
	/** Whether this element is subject to ONEM (employment) contributions */
	subjectToOnem: boolean;
	/** Exempt from housing benefit calculation */
	housingExempt: boolean;
	/** Exempt from transport benefit calculation */
	transportExempt: boolean;
	/** Display order on the payslip — lower values appear first */
	displayOrder: number;
}


/* ─── Pay element assigned to a contract ─── */

/**
 * A pay element overridden for a specific employee contract.
 * Allows per-contract customisation of amounts, rates, and active period.
 */
export interface ContractPayElement {
	/** The employee contract this override applies to */
	contractId: string;
	/** The pay element code from the catalog */
	elementCode: PayCode;
	/** Overridden amount (nullable to inherit from catalog default) */
	amount?: number;
	/** Overridden rate (nullable to inherit from catalog default) */
	rate?: number;
	/** Overridden formula (nullable to inherit from catalog default) */
	formula?: string;
	/** Date from which this override is effective */
	startDate: string;
	/** Optional end date — if omitted, the override is indefinite */
	endDate?: string;
	/** Whether this override is currently active */
	isActive: boolean;
}


/* ─── S10 — Élément de paie du contrat (API) ─── */

/**
 * Ligne de l'écran S10 — un élément de paie assigné à un contrat.
 * Réponse de GET /payroll/contracts/{id}/pay-elements (PayElementOut backend).
 */
export interface ContractPayElementItem {
	/** Identifiant de l'assignation (ContractAdjustment) */
	id: string;
	/** Code catalogue de l'élément (ex. IND_LOG, PRIME_RISQUE) */
	catalog_code?: string | null;
	/** Libellé affiché */
	label: string;
	/** Mode de calcul : FIXED | PERCENTAGE | HOURLY_RATE | DAILY */
	value_type: string;
	/** Montant effectif (custom_amount ?? catalogue.amount) */
	amount: number | null;
	/** Montant négocié au contrat */
	custom_amount: number | null;
	/** Taux négocié au contrat (%) */
	custom_percentage: number | null;
	/** Actif/inactif (toggle S10) */
	is_active: boolean;
	/** Imposable IRPP (affichage 🛡️) */
	is_taxable: boolean;
	/** Récurrence (monthly par défaut) */
	recurrence: string;
	/** Début d'application */
	start_period: string;
	/** Fin d'application (null = indéfini) */
	end_period: string | null;
}

/**
 * Réponse complète S10 : éléments de paie d'un contrat + résumé brut estimé.
 * (ContractPayElementListOut backend)
 */
export interface ContractPayElementSummary {
	contract_id: string;
	employee: {
		id: string;
		matricule?: string;
		first_name?: string;
		last_name?: string;
		full_name?: string;
	};
	contract_type: string;
	base_salary: number | null;
	elements: ContractPayElementItem[];
	estimated_gross: number;
}


/**
 * Payload de création/assignation d'un élément de paie à un contrat (S10).
 * (ContractAdjustmentCreateIn backend)
 */
export interface ContractPayElementInput {
	/** ID du PayrollAdjustment (catalogue) */
	adjustment: string;
	custom_amount: number | null;
	custom_percentage: number | null;
	start_period: string;
	end_period?: string | null;
	is_active: boolean;
}


/* ─── Tax bracket ─── */

/** A progressive tax bracket with lower/upper bounds and marginal rate */
export interface TaxBracket {
	/** Minimum taxable amount for this bracket */
	lowerBound: number;
	/** Maximum taxable amount for this bracket (Infinity for the top bracket) */
	upperBound: number;
	/** Marginal tax rate applied within this bracket (e.g. 0.3 for 30%) */
	rate: number;
}

/** Type of tax version — IRPP (progressive income tax) or IPR (simplified professional tax) */
export type TaxVersionType = 'irpp' | 'ipr';

/**
 * A versioned set of tax brackets for a given tax type.
 * The DRC applies either IRPP (10 brackets) or IPR (4 brackets).
 */
export interface TaxVersion {
	/** Unique identifier */
	id: string;
	/** Human-readable label (e.g. "IRPP 2026 — 10 tranches") */
	label: string;
	/** Tax type */
	type: TaxVersionType;
	/** The set of progressive brackets for this version */
	brackets: TaxBracket[];
	/** Effective start date for this tax version */
	startDate: string;
	/** Optional end date — if omitted, this version is current */
	endDate?: string;
	/** Whether this is the default tax version for new employees */
	isDefault: boolean;
}


/* ─── Payroll cycle ─── */

/** A payroll cycle representing a monthly or closure period */
export interface PayrollCycle {
	/** Unique identifier */
	id: string;
	/** Display label for the period (e.g. "Juin 2026") */
	period: string;
	/** monthly = regular month, closure = end-of-contract closure */
	type: 'monthly' | 'closure';
	/** Current lifecycle status */
	status: PayrollCycleStatus;
	/** IDs of payroll runs associated with this cycle */
	runs: string[];
	/** Sum of gross pay across all runs in this cycle */
	totalGross: number;
	/** Sum of net pay across all runs */
	totalNet: number;
	/** Number of employees included */
	employeeCount: number;
	/** Creation timestamp */
	createdAt: string;
	/** Closure timestamp — set when the cycle is closed */
	closedAt?: string;
	/** Archive timestamp — set when the cycle is archived */
	archivedAt?: string;
}


/* ─── Organism contributions (CNSS, INPP, ONEM) ─── */

/** Configuration for a social/statutory contribution collected by an external organism */
export interface OrganismContribution {
	/** Contribution code (e.g. 'CNSS', 'INPP', 'ONEM') */
	code: string;
	/** Display label */
	label: string;
	/** Employee share percentage */
	employeeRate: number;
	/** Employer share percentage */
	employerRate: number;
	/** Contribution ceiling (salary cap above which the contribution no longer applies) */
	ceiling?: number;
	/** Optional description */
	description?: string;
}

/** Taux de cotisation sociale (CNSS, ONEM, INPP) — mirrors SocialContributionRateOut backend */
export interface SocialContributionRate {
	id: string;
	contribution_type: 'CNSS' | 'ONEM' | 'INPP' | string;
	rate_percentage: number;
	employee_portion: number;
	employer_portion: number;
	company_size_min: number | null;
	company_size_max: number | null;
	ceiling_amount: number | null;
	effective_date: string;
	is_active: boolean;
	created_at: string;
	updated_at: string;
}


/* ─── Payroll run (enriched) ─── */

/** A fully enriched payroll run with computed totals and timestamps */
export interface PayrollRun {
	/** Unique identifier */
	id: string;
	/** The payroll cycle this run belongs to */
	cycleId: string;
	/** Display label for the period */
	period: string;
	/** monthly (regular) or closure */
	type: 'monthly' | 'closure';
	/** Current processing status */
	status: PayrollStatus;
	/** Base currency for the run */
	currency: Currency;
	/** Exchange rate (CDF per USD) if currency is USD */
	exchangeRate: number;
	/** ISO date string for the period start */
	periodStart: string;
	/** ISO date string for the period end */
	periodEnd: string;
	/** Tax version applied to this run (reference to TaxVersion.id) */
	fiscalVersion: string;
	/** Sum of all gross pay amounts */
	totalGross: number;
	/** Sum of all net pay amounts */
	totalNet: number;
	/** Sum of all social contributions (employee + employer) */
	totalContributions: number;
	/** Sum of all income taxes (IPR / IRPP) */
	totalTaxes: number;
	/** Sum of all social allocations */
	totalAllocations: number;
	/** Number of employees included in this run */
	employeeCount: number;
	/** Total number of employees eligible */
	totalEmployeeCount: number;
	/** Creation timestamp */
	createdAt: string;
	/** Timestamp when payroll was calculated */
	calculatedAt?: string;
	/** Timestamp when payroll was reviewed */
	reviewedAt?: string;
	/** Timestamp when payroll was approved */
	approvedAt?: string;
	/** Timestamp when payment was processed */
	paidAt?: string;
}


/* ─── Run list item ─── */

/** Lightweight payroll run summary for list/table views */
export interface RunListItem {
	/** Unique identifier */
	id: string;
	/** Display label for the period */
	periodLabel: string;
	/** Condensed status for list display */
	status: RunListStatus;
	/** Number of employees included */
	employeeCount: number;
	/** Total number of eligible employees */
	totalEmployeeCount: number;
	/** Sum of gross amounts */
	grossTotal: number;
	/** Closure timestamp */
	closedAt?: string;
	/** Organisational units included in this run */
	orgUnits?: string[];
}

/* ─── Payroll run (API) ─── */

/** Raw payroll run as returned by the backend list/create endpoints (PayrollRunOut). */
export interface PayrollRunApiOut {
	id: string;
	code: string;
	start_date: string;
	end_date: string;
	status: BackendPayrollRunStatus;
	exchange_rate_applied: number | null;
	created_at: string;
	updated_at: string;
	total_payslips: number;
	gross_total: number;
	employee_count: number;
	closed_at: string | null;
	period_label: string | null;
}

/** Shape returned by GET /runs/{id} (service dict, not PayrollRunOut). */
export interface PayrollRunDetailApiOut {
	id: string;
	code: string;
	status: BackendPayrollRunStatus;
	period: string;
	start_date: string;
	end_date: string;
	exchange_rate: number | null;
	created_at: string;
	updated_at: string;
	stats: {
		total_count: number;
		processed_count: number;
		pending_count: number;
	};
	financials: {
		gross_total: number;
		net_total: number;
		total_tax_deductions: number;
		employer_liability: number;
	};
}

/** Shape returned by GET /runs/{id}/summary (PayrollRunSummaryOut). */
export interface PayrollRunSummaryApiOut {
	payroll_run: {
		id: string;
		code: string;
		period: string;
		status: BackendPayrollRunStatus;
	};
	summary: {
		total_employees: number;
		total_gross_salary: number;
		total_net_salary: number;
		total_ipr_to_pay: number;
		total_cnss_employee: number;
		total_cnss_employer: number;
		total_inpp: number;
		total_onem: number;
		total_employer_liabilities: number;
		total_cost_to_company: number;
	};
	adjustments: Record<string, { label: string; amount: number; type: string }>;
}

/** Filters for the payroll run list view */
export interface CycleListFilters {
	/** Filter by run status, or 'all' to show everything */
	status: RunListStatus | 'all';
	/** Filter by period label */
	period: string;
	/** Search term across employee names / IDs */
	search: string;
	/** Filter by organisational unit */
	orgUnit: string;
}


/* ─── Payslip line audit details ─── */

/** Full tax computation audit trail, e.g. for IPR / IRPP progressive brackets */
export interface PayslipLineAuditDetails {
	/** Taxable base amount */
	base: number;
	/** Progressive tax brackets applied */
	brackets: Array<{
		/** Bracket lower bound (inclusive) */
		from: number;
		/** Bracket upper bound (inclusive) */
		to: number;
		/** Marginal tax rate for this bracket */
		rate: number;
		/** Tax amount generated within this bracket */
		amount: number;
	}>;
	/** Cap rate applied (max marginal rate) */
	capRate: number;
	/** Maximum tax amount before capping */
	capAmount: number;
	/** Gross tax before family deductions */
	grossTax: number;
	/** Family deduction rate applied per dependent */
	familyDeductionRate: number;
	/** Number of dependents used for family deduction */
	familyDeductionCount: number;
	/** Final tax after all deductions and caps */
	finalTax: number;
}


/* ─── Payslip line (enriched) ─── */

/** A single line item on a payslip — either an earning or a deduction */
export interface PayslipLine {
	/** Pay code identifying this line */
	code: PayCode;
	/** Human-readable label */
	label: string;
	/** Base amount before applying the rate */
	baseAmount: number;
	/** Currency of the base amount (e.g. "USD" when base is in USD) */
	baseCurrency?: Currency;
	/** Rate applied (percentage or multiplier) */
	rate: number;
	/** Computed amount (positive for earnings, negative for deductions) */
	amount: number;
	/** Currency of the computed amount (e.g. "CDF" after conversion) */
	currency?: Currency;
	/** Whether this line adds to gross pay or subtracts from it */
	type: 'earning' | 'deduction';
	/** Display order on the payslip */
	displayOrder: number;
	/** Formula expression explaining how amount was computed */
	formula?: string;
	/** Full tax computation audit trail (progressive brackets, caps, deductions) */
	auditDetails?: PayslipLineAuditDetails;
}


/* ─── Payslip (enriched) ─── */

/** A complete employee payslip with all line items and summary totals */
/* ─── Employee Info ─── */

/** Employee information displayed on the payslip header */
export interface EmployeeInfo {
	/** Unique employee identifier */
	id: number;
	/** Employee matriculation number (matricule) */
	matricule: string;
	/** Employee full name */
	fullName: string;
	/** Employee organisational unit (department / service) */
	orgUnit: string;
	/** Employee entry date into the company (YYYY-MM-DD) */
	entryDate?: string;
}

/* ─── Contract Info ─── */

/** Contract details attached to the payslip */
export interface ContractInfo {
	/** Contract type: CDI (permanent), CDD (fixed-term), CTR (contractor) */
	type: 'CDI' | 'CDD' | 'CTR';
	/** Professional / job classification category (e.g. "Classe 4") */
	professionalCategory: string;
	/** Grade / échelon within the category */
	grade: string;
	/** Currency the contract is denominated in */
	currency: Currency;
	/** Contractual base salary */
	baseSalary: number;
	/** Work regime: full-time or part-time */
	workRegime: 'TEMPS_PLEIN' | 'TEMPS_PARTIEL';
}

/* ─── Period Info ─── */

/** Pay period covered by the payslip */
export interface PeriodInfo {
	/** Period start date (YYYY-MM-DD) */
	start: string;
	/** Period end date (YYYY-MM-DD) */
	end: string;
	/** Number of calendar days in the period */
	calendarDays: number;
}

/* ─── Exchange Rate ─── */

/** Exchange rate metadata for currency conversion (USD → CDF) */
export interface ExchangeRateInfo {
	/** The conversion rate value */
	rate: number;
	/** Source of the rate (e.g. "bcc" for Banque Centrale du Congo) */
	source: string;
	/** Timestamp when the rate was fetched */
	fetchedAt: string;
	/** Whether the rate is locked for the period (prevents revaluation) */
	isLocked: boolean;
}

/* ─── Payslip Section ─── */

/** A grouped section of payslip lines (earnings or deductions) */
export interface PayslipSection {
	/** Section code: "GAINS" | "DEDUCTIONS" */
	code: string;
	/** Human-readable section label */
	label: string;
	/** Line items belonging to this section */
	lines: PayslipLine[];
	/** Section total amount */
	total: number;
	/** Section category: earning (gain) or deduction (retenue) */
	sectionType: 'earning' | 'deduction';
}

/* ─── Payslip Summary ─── */

/** Aggregated summary of the payslip amounts */
export interface PayslipSummary {
	/** Total gross salary before any deductions */
	grossSalary: number;
	/** Total standard deductions (social contributions, taxes) */
	totalDeductions: number;
	/** Post-net deductions (e.g. salary advance repayments, garnishments) */
	postNetDeductions: number;
	/** Final net pay after all deductions */
	netPay: number;
	/** Total employer-side contributions */
	employerCosts: number;
	/** Grand total cost borne by the employer (grossSalary + employerCosts) */
	totalEmployerCost: number;
}

/* ─── Immutable Snapshot ─── */

/** Cryptographic snapshot for audit trail — frozen parameters at generation time */
export interface ImmutableSnapshot {
	/** Timestamp when the snapshot was signed */
	signedAt: string;
	/** SHA-256 hash of the payslip data for integrity verification */
	sha256: string;
	/** Frozen parameter values used during payslip calculation */
	parametersFrozen: {
		/** Legal minimum wage (SMIG) at the time of calculation */
		smig: number;
		/** CNSS contribution rate applied */
		cnssRate: number;
		/** IPR progressive tax brackets applied */
		iprBrackets: Array<{ from: number; to: number; rate: number }>;
		/** Exchange rate used for the calculation */
		exchangeRate: number;
	};
}

/* ─── Payslip ─── */

/** Full payslip document — the core output of a payroll run */
export interface Payslip {
	/** Unique payslip identifier */
	id: string;
	/** Payroll cycle this payslip belongs to */
	cycleId: string;
	/** Currency used for all amounts on the payslip */
	currency: Currency;
	/** Processing status */
	status: PayslipStatus;
	/** Payment timestamp */
	paidAt?: string;

	/** Employee information (embedded object) */
	employee: EmployeeInfo;
	/** Contract details (embedded object) */
	contract: ContractInfo;
	/** Pay period covered (embedded object) */
	period: PeriodInfo;
	/** Exchange rate used for USD→CDF conversion (embedded object) */
	exchangeRate: ExchangeRateInfo;

	/** Grouped payslip sections (earnings / deductions) */
	sections: PayslipSection[];
	/** Aggregated summary of all amounts */
	summary: PayslipSummary;

	/** Immutable audit snapshot (optional — present after calculation is finalised) */
	immutableSnapshot?: ImmutableSnapshot;
}


/* ─── Advance ─── */

export interface AdvanceEmployee {
	/** Employee UUID */
	id: string;
	/** Matricule (e.g. EMP-2026-00045) */
	matricule?: string;
	first_name?: string;
	middle_name?: string;
	last_name?: string;
	/** Full name (computed server-side) */
	full_name?: string;
	email?: string;
	phone?: string;
	/** Current job title (from position history) */
	job_title?: string | null;
	/** Current organisational unit name */
	org_unit?: string | null;
	/** Current organisational unit id */
	org_unit_id?: string | null;
	/** Profile photo URL */
	avatar_url?: string | null;
	is_active?: boolean;
}

/**
 * A salary advance (avance sur salaire) requested by an employee.
 * Mirrors SalaryAdvanceOut in backend schemas.py.
 */
export interface Advance {
	/** Unique identifier (UUID) */
	id: string;
	/** Employee snapshot (enriched object) */
	employee: AdvanceEmployee;
	/** Employee full name (kept for display compatibility) */
	employee_name: string;
	/** Total advance amount */
	amount: number;
	/** Percentage of salary deducted for repayment */
	repayment_percentage: number;
	/** Deduction base (GROSS | NET) */
	salary_base_for_deduction?: string;
	/** Tax timing (BEFORE_TAX | AFTER_TAX) */
	tax_timing?: string;
	/** Deduction window (ALL_MONTHS | CUSTOM_PERIOD) */
	deduction_window?: string;
	/** Deduction period (CUSTOM_PERIOD) */
	deduction_start_date?: string;
	deduction_end_date?: string;
	/** Current lifecycle status */
	status: AdvanceStatus;
	/** Advance type (NORMAL) */
	advance_type?: string;
	/** Reason for the advance request */
	reason: string;
	/** Date of the advance request */
	requested_date: string;
	/** Date the advance was approved */
	approved_date?: string;
	/** Date the advance was rejected */
	rejected_date?: string;
	/** Why the advance was rejected */
	rejection_reason?: string;
	/** Cumulative amount already deducted */
	deducted_amount: number;
	/** Risk assessment for reimbursement (backend persisted) */
	risk_level: AdvanceRiskLevel;
	/** Whether the advance is fully repaid */
	is_closed: boolean;
	/** Remaining balance to be reimbursed (computed) */
	remaining_balance: number;
	/** Currency of the advance amount (CDF or USD) */
	currency?: string;
	/** USD→CDF rate frozen at creation time for auditability */
	exchange_rate_used?: number | null;
	/** Creation timestamp */
	created_at: string;
	updated_at: string;
}

/** Payload for creating an advance (mirrors SalaryAdvanceCreateIn) */
export interface AdvanceCreatePayload {
	employee: string | number;
	amount: number;
	reason: string;
	repayment_percentage?: number;
	salary_base_for_deduction?: AdvanceDeductionBase;
	tax_timing?: AdvanceTaxTiming;
	deduction_window?: AdvanceDeductionWindow;
	deduction_start_date?: string;
	deduction_end_date?: string;
	currency?: string;
	/** true = soumission immédiate (PENDING), false/absent = brouillon (DRAFT) */
	submit?: boolean;
}

/** Payload for updating an advance's deduction config at approval (PATCH /payroll/advances/:id) */
export interface AdvanceUpdatePayload {
	repayment_percentage?: number;
	salary_base_for_deduction?: AdvanceDeductionBase;
	tax_timing?: AdvanceTaxTiming;
	deduction_window?: AdvanceDeductionWindow;
	deduction_start_date?: string;
	deduction_end_date?: string;
}

/* ─── Filters ─── */

/** Filters available on the main payslip list view */
export interface PayrollFilters {
	/** Search term */
	search: string;
	/** Filter by one or more payroll statuses */
	status: PayrollStatus[];
	/** Filter by organisational unit(s) */
	orgUnit: string[];
	/** Filter by period */
	period: string;
}

/** An employee excluded from a payroll run, with the exclusion reason */
export interface ExcludedEmployee {
	employeeName: string;
	reason: string;
	orgUnit: string;
}


/* ═══════════════════════════════════════════════
   Constants
   ═══════════════════════════════════════════════ */

/** Human-readable labels for run list statuses (displayed in French UI) */
export const RUN_LIST_STATUS_LABELS: Record<RunListStatus, string> = {
	draft: 'Brouillon',
	processing: 'En cours',
	closed: 'Clôturé',
	error: 'Anomalie'
};

/** Colour tokens for run list status badges */
export const RUN_LIST_STATUS_COLORS: Record<RunListStatus, { bg: string; text: string; dot: string }> = {
	draft:      { bg: 'bg-slate-100',    text: 'text-slate-700',    dot: 'bg-slate-500' },
	processing: { bg: 'bg-blue-50',      text: 'text-blue-700',     dot: 'bg-blue-500' },
	closed:     { bg: 'bg-emerald-50',   text: 'text-emerald-700',  dot: 'bg-emerald-500' },
	error:      { bg: 'bg-rose-50',      text: 'text-rose-700',     dot: 'bg-rose-500' }
};

/** Human-readable labels for payroll statuses */
export const PAYROLL_STATUS_LABELS: Record<PayrollStatus, string> = {
	draft: 'Brouillon',
	calculated: 'Calculé',
	reviewed: 'Révisé',
	approved: 'Approuvé',
	paid: 'Payé',
	closed: 'Clôturé',
	archived: 'Archivé'
};

/** Colour tokens for payroll status badges */
export const PAYROLL_STATUS_COLORS: Record<PayrollStatus, { bg: string; text: string; dot: string }> = {
	draft:      { bg: 'bg-slate-100',    text: 'text-slate-700',    dot: 'bg-slate-500' },
	calculated: { bg: 'bg-blue-50',      text: 'text-blue-700',     dot: 'bg-blue-500' },
	reviewed:   { bg: 'bg-amber-50',     text: 'text-amber-700',    dot: 'bg-amber-500' },
	approved:   { bg: 'bg-emerald-50',   text: 'text-emerald-700',  dot: 'bg-emerald-500' },
	paid:       { bg: 'bg-purple-50',    text: 'text-purple-700',   dot: 'bg-purple-500' },
	closed:     { bg: 'bg-indigo-50',    text: 'text-indigo-700',   dot: 'bg-indigo-500' },
	archived:   { bg: 'bg-neutral-100',  text: 'text-neutral-600',  dot: 'bg-neutral-500' }
};

/** Human-readable labels for cycle lifecycle statuses */
export const CYCLE_STATUS_LABELS: Record<PayrollCycleStatus, string> = {
	open: 'Ouvert',
	closed: 'Clôturé',
	archived: 'Archivé'
};

/** Colour tokens for cycle status badges */
export const CYCLE_STATUS_COLORS: Record<PayrollCycleStatus, { bg: string; text: string; dot: string }> = {
	open:     { bg: 'bg-emerald-50',   text: 'text-emerald-700',  dot: 'bg-emerald-500' },
	closed:   { bg: 'bg-indigo-50',    text: 'text-indigo-700',   dot: 'bg-indigo-500' },
	archived: { bg: 'bg-neutral-100',  text: 'text-neutral-600',  dot: 'bg-neutral-500' }
};

/** Human-readable labels for advance request statuses */
export const ADVANCE_STATUS_LABELS: Record<AdvanceStatus, string> = {
	DRAFT:    'Brouillon',
	PENDING:  'En attente',
	APPROVED: 'Approuvé',
	REJECTED: 'Rejeté',
	ACTIVE:   'Actif',
	CLOSED:   'Soldé'
};

/** Colour tokens for advance status badges */
export const ADVANCE_STATUS_COLORS: Record<AdvanceStatus, { bg: string; text: string }> = {
	DRAFT:     { bg: 'bg-slate-100',   text: 'text-slate-600' },
	PENDING:   { bg: 'bg-amber-100',   text: 'text-amber-700' },
	APPROVED:  { bg: 'bg-emerald-100', text: 'text-emerald-700' },
	REJECTED:  { bg: 'bg-rose-100',    text: 'text-rose-700' },
	ACTIVE:    { bg: 'bg-blue-100',    text: 'text-blue-700' },
	CLOSED:    { bg: 'bg-slate-100',   text: 'text-slate-700' }
};

/** Human-readable labels for advance risk levels */
export const ADVANCE_RISK_LABELS: Record<AdvanceRiskLevel, string> = {
	LOW:    'Faible',
	MEDIUM: 'Moyen',
	HIGH:   'Élevé'
};

/** Ordered workflow steps for payroll processing */
export const PAYROLL_STEPS: PayrollStep[] = ['preparation', 'calculation', 'review', 'approval', 'payment'];


/** Human-readable labels for each payroll processing step */
export const PAYROLL_STEP_LABELS: Record<PayrollStep, string> = {
	preparation: 'Préparation',
	calculation: 'Calcul',
	review:      'Révision',
	approval:    'Approbation',
	payment:     'Paiement'
};

/** Short descriptions for each payroll step shown in the step wizard */
export const PAYROLL_STEP_DESCRIPTIONS: Record<PayrollStep, string> = {
	preparation: 'Sélectionnez la période et les employés à inclure dans cette paie',
	calculation: 'Visualisez les calculs et formules appliquées à chaque employé',
	review:      'Contrôlez et modifiez les fiches de paie avant validation',
	approval:    'Confirmez les montants et approuvez la paie',
	payment:     'Finalisez le paiement et générez les justificatifs'
};


/* ─── PayCode helpers ─── */

/** Human-readable French labels for every PayCode value */
export const PAY_CODE_LABELS: Record<PayCode, string> = {
	BASE_SALARY: 'Salaire de base',
	PARTIAL_SALARY: 'Salaire de base (temps partiel)',
	SENIORITY: "Prime d'ancienneté",
	PERF_BONUS: 'Prime de performance',
	FUNCTION_BONUS: 'Prime de fonction',
	RISK_BONUS: 'Prime de risque / salissure',
	HOUSING_BONUS: 'Prime de logement',
	MEAL_BONUS: 'Prime de panier',
	COMMISSION: 'Commissions sur ventes',
	OT_30: 'Heures supplémentaires 30%',
	OT_60: 'Heures supplémentaires 60%',
	OT_HOLIDAY: 'Heures supplémentaires jours fériés',
	NIGHT_OT: 'Heures de nuit',
	HOUSING_ALLOWANCE: 'Indemnité de logement',
	TRANSPORT_ALLOWANCE: 'Indemnité de transport',
	MISSION_ALLOWANCE: 'Indemnité de mission / déplacement',
	FUNCTIONAL_HOUSING: 'Logement de fonction',
	COMPANY_CAR: 'Véhicule de fonction',
	THIRTEENTH_MONTH: '13e mois',
	EXCEPTIONAL_BONUS: 'Gratification exceptionnelle',
	SALARY_BACKPAY: 'Rappel de salaire',
	PAID_LEAVE: 'Indemnité de congés payés',
	SEVERANCE_NOTICE: "Indemnité de préavis",
	SEVERANCE_PAY: 'Indemnité de licenciement',
	SALARY_ADVANCE: 'Avance sur salaire',
	GARNISHMENT: 'Saisie-arrêt',
	CNSS_EMPLOYEE: 'CNSS part salariale',
	IPR: 'Impôt Professionnel sur les Rémunérations',
	IRPP: 'Impôt sur le Revenu des Personnes Physiques',
	CNSS_EMPLOYER: 'CNSS part patronale',
	INPP: 'Contribution INPP',
	ONEM: 'Contribution ONEM',
	MUTUAL_CONTRIBUTION: 'Cotisation mutuelle / prévoyance'
};


/** French labels for tax version types (IRPP has 10 brackets, IPR has 4) */
export const TAX_VERSION_LABELS: Record<TaxVersionType, string> = {
	irpp: 'IRPP 2026 (10 tranches)',
	ipr: 'IPR (4 tranches)'
};
