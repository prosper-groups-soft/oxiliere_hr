import type {
	TaxConfig,
	IPRCalculationResult,
	LegalAllowance,
	OvertimeRule
} from '../types/tax.types';
import { TaxConfigValidationSchema } from '../schemas/tax.schemas';
import { CURRENCIES } from '@/constants/finance';
import { fromCDF, toCDF, setExchangeRate } from '@/utilities/common/currency';
import type {
	PayrollConfigResponse,
	TaxBracketResponse,
	SocialContributionResponse,
	PayrollConfigUpdate,
	TaxBracketUpdate,
	SocialContributionUpdate
} from '../schemas/tax.schemas';


// Helper to create empty config (values come from backend)
function createEmptyTaxConfig(): TaxConfig {
	return {
		iprBrackets: [],
		iprConfig: {
			globalCapRate: 0.30, // Default 30% per RDC law
			professionalAllowanceRate: 0.20, // Default 20%
			include13thMonth: true,
			includeBonuses: true
		},
		familyDeduction: {
			enabled: false,
			ratePerChild: 0,
			maxChildren: 9
		},
		cnss: {
			enabled: true, // Mandatory
			employerRate: 0.13,
			employeeRate: 0.05,
			salaryCap: 250000,
			includeInGross: true
		},
		inss: {
			enabled: false,
			rate: 0,
			salaryCap: null
		},
		inpp: [],
		onem: {
			enabled: true, // Mandatory
			rate: 0.002 // 0.2%
		},
		currency: CURRENCIES.USD,
		// General config defaults
		workHoursPerMonth: 200,
		workHoursPerDay: 8,
		workDaysPerWeek: 5,
		workHoursPerWeek: 45,
		housingAllowanceMinPercentage: 0.25, // 25%
		familyAllowanceMinAmount: 300,
		familyAllowanceSmigDivider: 27,
		overtimeMultiplier: 1.5,
		leaveDeductionDivisor: 26,
		exchangeRateUsdCdf: 2850,
		exchangeRateSource: 'MANUAL',
		defaultPaymentMethod: 'CASH',
		includeLeavesInPayroll: true,
		useTheoreticalDaysFromAttendance: false,
		fixedDeductionPerAbsentDay: null
	};
}

export class TaxSettingsStore {
	// --- Reactive State ---
	config = $state<TaxConfig>(createEmptyTaxConfig());
	isLoading = $state(false);
	hasLoaded = $state(false);
	hasChanges = $state(false);
	validationErrors = $state<Record<string, string>>({});

	// Legal allowances and overtime rules (loaded separately)
	legalAllowances = $state<LegalAllowance[]>([]);
	overtimeRules = $state<OvertimeRule[]>([]);

	// Calculator state
	calculatorSalary = $state<number>(1000);
	calculatorChildren = $state<number>(2);
	showCalculator = $state(false);

	// --- Private State (Tracking) ---
	// Note: Only tracking fields that are actually editable in TaxConfigPanel
	// IPR brackets, CNSS, INPP, ONEM, Family deductions are fixed by RDC law (read-only)
	#originalPayrollConfig = $state<{
		workHoursPerWeek: number;
		leaveDeductionDivisor: number;
		includeLeavesInPayroll: boolean;
		useTheoreticalDaysFromAttendance: boolean;
		exchangeRateUsdCdf: number;
		exchangeRateSource: 'MANUAL' | 'API';
		defaultPaymentMethod: 'BANK_TRANSFER' | 'CASH' | 'MOBILE_MONEY' | 'CHECK';
	} | null>(null);

	// Track original legal allowances for change detection
	#originalLegalAllowances = $state<LegalAllowance[]>([]);

	// Track original overtime rules for change detection
	#originalOvertimeRules = $state<OvertimeRule[]>([]);

	// --- Derived State ---
	iprBrackets = $derived(this.config.iprBrackets);
	familyDeduction = $derived(this.config.familyDeduction);
	cnssConfig = $derived(this.config.cnss);
	inssConfig = $derived(this.config.inss);

	maxIPRRate = $derived(Math.max(...this.config.iprBrackets.map(b => b.rate)));
	totalBrackets = $derived(this.config.iprBrackets.length);

	validationErrorsCount = $derived(Object.keys(this.validationErrors).length);
	isValid = $derived(this.validationErrorsCount === 0);

	// Calculator result
	calculatorResult = $derived.by((): IPRCalculationResult | null => {
		if (!this.showCalculator || this.calculatorSalary <= 0) return null;
		return this.calculateIPR(this.calculatorSalary, this.calculatorChildren);
	});

	// --- Actions ---
	updateFamilyDeduction(updates: Partial<typeof this.config.familyDeduction>) {
		this.config.familyDeduction = { ...this.config.familyDeduction, ...updates };
		this.hasChanges = true;
	}

	updateCNSS(updates: Partial<typeof this.config.cnss>) {
		this.config.cnss = { ...this.config.cnss, ...updates };
		this.hasChanges = true;
	}

	updateINSS(updates: Partial<typeof this.config.inss>) {
		this.config.inss = { ...this.config.inss, ...updates };
		this.hasChanges = true;
	}

	updateONEM(updates: Partial<typeof this.config.onem>) {
		this.config.onem = { ...this.config.onem, ...updates };
		this.hasChanges = true;
	}

	updateConfig(updates: Partial<Omit<TaxConfig, 'iprBrackets' | 'iprConfig' | 'familyDeduction' | 'cnss' | 'inss' | 'inpp' | 'onem'>>) {
		Object.assign(this.config, updates);
		this.hasChanges = true;
		// Run validation to show errors immediately
		this.validateConfig();
	}

	updateIPRConfig(updates: Partial<typeof this.config.iprConfig>) {
		this.config.iprConfig = { ...this.config.iprConfig, ...updates };
		this.hasChanges = true;
	}

	setCurrency(currency: 'USD' | 'CDF') {
		this.config.currency = currency;
		// Note: Don't mark hasChanges - this is just a display preference,
		// not a change to the actual data (values are always stored in CDF)
	}

	/**
	 * Get a monetary value converted from CDF (storage) to display currency
	 * All monetary values in config are stored in CDF
	 */
	getDisplayValue(valueInCDF: number | null | undefined): number {
		return fromCDF(valueInCDF, this.config.currency);
	}

	/**
	 * Update a monetary value - converts from display currency to CDF for storage
	 * Use this for all monetary inputs (familyAllowanceMinAmount, etc.)
	 */
	updateMonetaryValue(field: keyof TaxConfig, valueInDisplayCurrency: number) {
		const valueInCDF = toCDF(valueInDisplayCurrency, this.config.currency);
		// eslint-disable-next-line @typescript-eslint/no-explicit-any
		(this.config as any)[field] = valueInCDF;
		this.hasChanges = true;
		// Clear validation error for this field
		delete this.validationErrors[field as string];
	}

	/**
	 * Set exchange rate and update the global currency utility
	 */
	setExchangeRate(rate: number) {
		this.config.exchangeRateUsdCdf = rate;
		setExchangeRate(rate);
		this.hasChanges = true;
	}

	resetToDefaults() {
		this.config = createEmptyTaxConfig();
		this.legalAllowances = [];
		this.overtimeRules = [];
		this.#resetTrackingState();
		this.hasChanges = true;
		this.validationErrors = {};
	}

	/**
	 * Load legal allowances from API data
	 */
	loadLegalAllowances(allowances: LegalAllowance[]): void {
		this.legalAllowances = allowances;
		this.#originalLegalAllowances = JSON.parse(JSON.stringify(allowances)); // Deep copy for comparison
	}

	/**
	 * Update a legal allowance with validation
	 */
	updateLegalAllowance(id: string, updates: Partial<LegalAllowance>, rawValue?: string): void {
		const index = this.legalAllowances.findIndex(a => a.id === id);
		if (index === -1) return;

		const errorKey = `legalAllowance_${id}_base_amount`;

		// Validate base_amount if provided
		if (updates.base_amount !== undefined && updates.base_amount !== null) {
			const num = parseFloat(updates.base_amount);
			if (rawValue === '' || Number.isNaN(num) || num < 0) {
				this.validationErrors[errorKey] = 'Montant invalide';
				return;
			}
			if (num > 10000000) {
				this.validationErrors[errorKey] = 'Maximum 10 000 000 FC';
				return;
			}
			delete this.validationErrors[errorKey];
		}

		this.legalAllowances[index] = { ...this.legalAllowances[index], ...updates };
		this.hasChanges = true;
	}

	/**
	 * Load overtime rules from API data
	 */
	loadOvertimeRules(rules: OvertimeRule[]): void {
		this.overtimeRules = rules;
		this.#originalOvertimeRules = JSON.parse(JSON.stringify(rules)); // Deep copy for comparison
	}

	/**
	 * Update an overtime rule (is_active or multiplier)
	 */
	updateOvertimeRule(ruleId: string, updates: Partial<OvertimeRule>): void {
		const index = this.overtimeRules.findIndex(r => r.id === ruleId);
		if (index === -1) return;

		// Validate multiplier if present
		if (updates.multiplier !== undefined) {
			const multiplier = parseFloat(updates.multiplier as string);
			if (isNaN(multiplier) || multiplier < 1) {
				this.validationErrors[`overtimeRule_${ruleId}_multiplier`] = 'Le multiplicateur doit être ≥ 1.0';
				return;
			}
			if (multiplier > 5) {
				this.validationErrors[`overtimeRule_${ruleId}_multiplier`] = 'Le multiplicateur ne peut pas dépasser 5.0';
				return;
			}
			delete this.validationErrors[`overtimeRule_${ruleId}_multiplier`];
		}

		this.overtimeRules[index] = { ...this.overtimeRules[index], ...updates };
		this.hasChanges = true;
	}

	/**
	 * Load settings from pre-fetched data (TanStack Query integration)
	 */
	loadFromData(
		config: PayrollConfigResponse,
		brackets: TaxBracketResponse[],
		contributions: SocialContributionResponse[]
	): void {
		
		// Reset all tracking state first
		this.#resetTrackingState();

		// Helper to convert string to number
		const toNum = (val: number | string | null | undefined): number => {
			if (val === null || val === undefined) return 0;
			return typeof val === 'string' ? parseFloat(val) : val;
		};

		// Map backend data to frontend format
		this.config.currency = config.currency;

		// IPR Config - handle optional fields and string numbers
		// Note: global_ipr_cap_rate (30%) and professional_allowance_rate (20%) 
		// are fixed by RDC labor code, use defaults if not in API
		this.config.iprConfig = {
			globalCapRate: toNum(config.global_ipr_cap_rate || 30) / 100, // Default 30%
			professionalAllowanceRate: toNum(config.professional_allowance_rate || 20) / 100, // Default 20%
			include13thMonth: config.include_13th_month ?? true,
			includeBonuses: config.include_bonuses ?? true,
		};

		// Map tax brackets - convert rate_percentage (0-100) to rate (0-1)
		// Note: IPR brackets are fixed by RDC labor code (Ordonnance 69-102)
		this.config.iprBrackets = (brackets || []).map((b, index) => ({
			id: `bracket-${index}`,
			min: toNum(b.lower_limit),
			max: b.upper_limit === null ? null : toNum(b.upper_limit),
			rate: toNum(b.rate_percentage) / 100, // Convert percentage to decimal
			label: b.label || `Tranche ${index + 1} (${toNum(b.lower_limit)} - ${b.upper_limit === null ? '∞' : toNum(b.upper_limit)} ${config.currency})`,
			readOnly: true, // Fixed by law
		}));

		// Ensure inpp is at least an empty array (not undefined)
		if (!this.config.inpp) {
			this.config.inpp = [];
		}

		// Map CNSS from contributions - use correct backend field names
		const cnssContribution = contributions?.find(c => c.contribution_type === 'CNSS');
		if (cnssContribution) {
			this.config.cnss = {
				enabled: cnssContribution.is_active,
				employerRate: toNum(cnssContribution.employer_portion) / 100,
				employeeRate: toNum(cnssContribution.employee_portion) / 100,
				salaryCap: cnssContribution.ceiling_amount ? toNum(cnssContribution.ceiling_amount) : null,
				includeInGross: true,
			};
		}

		// Map INSS from AMO contribution
		const inssContribution = contributions?.find(c => c.contribution_type === 'AMO');
		if (inssContribution) {
			this.config.inss = {
				enabled: inssContribution.is_active,
				rate: toNum(inssContribution.employee_portion) / 100,
				salaryCap: inssContribution.ceiling_amount ? toNum(inssContribution.ceiling_amount) : null,
			};
		}

		// Map INPP rates (multiple entries based on company size)
		const inppContributions = contributions?.filter(c => c.contribution_type === 'INPP') || [];
		const inppRates = inppContributions.map(c => ({
			id: c.id,
			rate: toNum(c.employee_portion) / 100,
			companySizeMin: c.company_size_min,
			companySizeMax: c.company_size_max,
		}));

		// Assign all at once to ensure reactivity
		this.config.inpp = inppRates;

		// Map ONEM
		const onemContribution = contributions?.find(c => c.contribution_type === 'ONEM');
		if (onemContribution) {
			this.config.onem = {
				enabled: onemContribution.is_active,
				rate: toNum(onemContribution.employee_portion) / 100,
			};
		}

		// Family deduction from config
		const familyRate = toNum(config.family_deduction_rate_per_child);
		this.config.familyDeduction = {
			enabled: familyRate > 0,
			ratePerChild: familyRate / 100,
			maxChildren: toNum(config.family_deduction_max_children) || 9,
		};

		// Additional payroll configuration
		this.config.workHoursPerWeek = toNum(config.work_hours_per_week) || 45;
		this.config.workHoursPerMonth = toNum(config.work_hours_per_month) || 195;
		this.config.workHoursPerDay = toNum(config.work_hours_per_day) || 8;
		this.config.workDaysPerWeek = toNum(config.work_days_per_week) || 5;
		this.config.housingAllowanceMinPercentage = toNum(config.housing_allowance_min_percentage) / 100;
		this.config.familyAllowanceMinAmount = toNum(config.family_allowance_min_amount);
		this.config.familyAllowanceSmigDivider = toNum(config.family_allowance_smig_divider);
		this.config.overtimeMultiplier = toNum(config.overtime_multiplier);
		this.config.leaveDeductionDivisor = toNum(config.leave_deduction_divisor);
		const exchangeRate = toNum(config.exchange_rate_usd_cdf) || 2850;
		this.config.exchangeRateUsdCdf = exchangeRate;
		setExchangeRate(exchangeRate); // Initialize global rate
		this.config.exchangeRateSource = config.exchange_rate_source || 'MANUAL';
		this.config.defaultPaymentMethod = (config.default_payment_method || 'CASH') as typeof this.config.defaultPaymentMethod;
		this.config.includeLeavesInPayroll = config.include_leaves_in_payroll ?? true;
		this.config.useTheoreticalDaysFromAttendance = config.use_theoretical_days_from_attendance ?? false;
		this.config.fixedDeductionPerAbsentDay = config.fixed_deduction_per_absent_day ? toNum(config.fixed_deduction_per_absent_day) : null;

		// Track editable payroll/attendance config values
		this.#originalPayrollConfig = {
			workHoursPerWeek: this.config.workHoursPerWeek ?? 45,
			leaveDeductionDivisor: this.config.leaveDeductionDivisor ?? 26,
			includeLeavesInPayroll: this.config.includeLeavesInPayroll ?? true,
			useTheoreticalDaysFromAttendance: this.config.useTheoreticalDaysFromAttendance ?? false,
			exchangeRateUsdCdf: this.config.exchangeRateUsdCdf ?? 2200,
			exchangeRateSource: this.config.exchangeRateSource ?? 'MANUAL',
			defaultPaymentMethod: this.config.defaultPaymentMethod ?? 'CASH',
		};

		this.hasChanges = false;
		this.validationErrors = {};
		this.hasLoaded = true;
	}

	/**
	 * Get pending changes for mutation
	 * Only returns editable fields from TaxConfigPanel:
	 * - leaveDeductionDivisor, includeLeavesInPayroll, useTheoreticalDaysFromAttendance
	 * - exchangeRateUsdCdf, exchangeRateSource, defaultPaymentMethod
	 * - LegalAllowances (is_active, base_amount)
	 * - OvertimeRules (is_active, multiplier)
	 */
	getPendingChanges(): {
		configUpdates: Partial<PayrollConfigUpdate>;
		bracketUpdates: Array<{ id: string; data: Partial<TaxBracketUpdate> }>;
		contributionUpdates: Array<{ id: string; data: Partial<SocialContributionUpdate> }>;
		legalAllowanceUpdates: Array<{ id: string; data: Partial<LegalAllowance> }>;
		overtimeRuleUpdates: Array<{ id: string; data: Partial<OvertimeRule> }>;
	} | null {
		// Validate first
		if (!this.validateConfig()) {
			return null;
		}

		const configUpdates: Partial<PayrollConfigUpdate> = {};
		const bracketUpdates: Array<{ id: string; data: Partial<TaxBracketUpdate> }> = [];
		const contributionUpdates: Array<{ id: string; data: Partial<SocialContributionUpdate> }> = [];
		const legalAllowanceUpdates: Array<{ id: string; data: Partial<LegalAllowance> }> = [];
		const overtimeRuleUpdates: Array<{ id: string; data: Partial<OvertimeRule> }> = [];

		// Only check editable fields from TaxConfigPanel
		// IPR brackets, CNSS, INPP, ONEM, Family deductions are fixed by RDC law (read-only)
		if (this.#originalPayrollConfig) {
			if (this.#originalPayrollConfig.workHoursPerWeek !== this.config.workHoursPerWeek) {
				configUpdates.work_hours_per_week = this.config.workHoursPerWeek ?? undefined;
			}
			if (this.#originalPayrollConfig.leaveDeductionDivisor !== this.config.leaveDeductionDivisor) {
				configUpdates.leave_deduction_divisor = this.config.leaveDeductionDivisor;
			}
			if (this.#originalPayrollConfig.includeLeavesInPayroll !== this.config.includeLeavesInPayroll) {
				configUpdates.include_leaves_in_payroll = this.config.includeLeavesInPayroll;
			}
			if (this.#originalPayrollConfig.useTheoreticalDaysFromAttendance !== this.config.useTheoreticalDaysFromAttendance) {
				configUpdates.use_theoretical_days_from_attendance = this.config.useTheoreticalDaysFromAttendance;
			}
			if (this.#originalPayrollConfig.exchangeRateUsdCdf !== this.config.exchangeRateUsdCdf) {
				configUpdates.exchange_rate_usd_cdf = this.config.exchangeRateUsdCdf;
			}
			if (this.#originalPayrollConfig.exchangeRateSource !== this.config.exchangeRateSource) {
				configUpdates.exchange_rate_source = this.config.exchangeRateSource;
			}
			if (this.#originalPayrollConfig.defaultPaymentMethod !== this.config.defaultPaymentMethod) {
				configUpdates.default_payment_method = this.config.defaultPaymentMethod;
			}
		}

		// Note: Currency is just a display preference, not persisted
		// Note: IPR brackets, CNSS, INPP, ONEM are fixed by RDC law - no updates needed

		// Check for legal allowance changes
		for (const current of this.legalAllowances) {
			const original = this.#originalLegalAllowances.find(a => a.id === current.id);
			if (original) {
				const changes: Partial<LegalAllowance> = {};
				if (original.is_active !== current.is_active) {
					changes.is_active = current.is_active;
				}
				if (original.base_amount !== current.base_amount) {
					changes.base_amount = current.base_amount;
				}
				if (Object.keys(changes).length > 0) {
					legalAllowanceUpdates.push({ id: current.id, data: changes });
				}
			}
		}

		// Check for overtime rule changes
		for (const current of this.overtimeRules) {
			const original = this.#originalOvertimeRules.find(r => r.id === current.id);
			if (original) {
				const changes: Partial<OvertimeRule> = {};
				if (original.is_active !== current.is_active) {
					changes.is_active = current.is_active;
				}
				if (original.multiplier !== current.multiplier) {
					changes.multiplier = current.multiplier;
				}
				if (Object.keys(changes).length > 0) {
					overtimeRuleUpdates.push({ id: current.id, data: changes });
				}
			}
		}

		return {
			configUpdates,
			bracketUpdates,
			contributionUpdates,
			legalAllowanceUpdates,
			overtimeRuleUpdates,
		};
	}

	/**
	 * Commit changes after successful save
	 * Only tracks editable payroll/attendance fields
	 */
	commitChanges(): void {
		// Update original values to match current (only editable fields)
		this.#originalPayrollConfig = {
			workHoursPerWeek: this.config.workHoursPerWeek ?? 45,
			leaveDeductionDivisor: this.config.leaveDeductionDivisor ?? 26,
			includeLeavesInPayroll: this.config.includeLeavesInPayroll ?? true,
			useTheoreticalDaysFromAttendance: this.config.useTheoreticalDaysFromAttendance ?? false,
			exchangeRateUsdCdf: this.config.exchangeRateUsdCdf ?? 2850,
			exchangeRateSource: this.config.exchangeRateSource ?? 'MANUAL',
			defaultPaymentMethod: this.config.defaultPaymentMethod ?? 'CASH',
		};

		// Update original legal allowances to match current
		this.#originalLegalAllowances = JSON.parse(JSON.stringify(this.legalAllowances));

		// Update original overtime rules to match current
		this.#originalOvertimeRules = JSON.parse(JSON.stringify(this.overtimeRules));

		this.hasChanges = false;
		this.validationErrors = {};
	}

	/**
	 * Validate current configuration
	 */
	validateConfig(): boolean {
		// Only validate editable fields from TaxConfigPanel
		// Read-only fields (IPR brackets, CNSS, INPP, etc.) are fixed by RDC law
		const result = TaxConfigValidationSchema.safeParse({
			// Payroll/Attendance settings (editable)
			workHoursPerWeek: this.config.workHoursPerWeek,
			leaveDeductionDivisor: this.config.leaveDeductionDivisor,
			includeLeavesInPayroll: this.config.includeLeavesInPayroll,
			useTheoreticalDaysFromAttendance: this.config.useTheoreticalDaysFromAttendance,
			// Currency/Exchange settings (editable)
			exchangeRateUsdCdf: this.config.exchangeRateUsdCdf,
			exchangeRateSource: this.config.exchangeRateSource,
			defaultPaymentMethod: this.config.defaultPaymentMethod,
		});

		if (!result.success) {
			const errors: Record<string, string> = {};
			const zodError = result.error;
			zodError.issues.forEach((err) => {
				const path = err.path.map(String).join('.');
				errors[path] = err.message;
			});
			this.validationErrors = errors;
			return false;
		}

		this.validationErrors = {};
		return true;
	}

	// Private reset tracking
	#resetTrackingState(): void {
		this.#originalPayrollConfig = null;
		this.#originalLegalAllowances = [];
		this.#originalOvertimeRules = [];
	}

	// IPR Calculation
	calculateIPR(grossSalary: number, childrenCount: number = 0): IPRCalculationResult {
		const { iprConfig, familyDeduction, iprBrackets } = this.config;

		// 1. Professional allowance
		const professionalAllowance = grossSalary * iprConfig.professionalAllowanceRate;

		// 2. CNSS/INSS deductions (simplified)
		const cnssAmount = this.config.cnss.enabled ? grossSalary * this.config.cnss.employeeRate : 0;
		const inssAmount = this.config.inss.enabled ? grossSalary * this.config.inss.rate : 0;
		const socialDeductions = cnssAmount + inssAmount;

		// 3. Taxable base
		const taxableBase = Math.max(0, grossSalary - professionalAllowance - socialDeductions);

		// 4. Calculate tax per bracket
		const bracketCalculations = iprBrackets.map(bracket => {
			let amountInBracket = 0;

			if (taxableBase > bracket.min) {
				const maxInBracket = bracket.max ?? taxableBase;
				amountInBracket = Math.min(taxableBase, maxInBracket) - bracket.min;
			}

			return {
				bracket,
				amountInBracket,
				taxInBracket: amountInBracket * bracket.rate
			};
		});

		// 5. Total tax before deductions
		const totalTaxBeforeDeductions = bracketCalculations.reduce(
			(sum, calc) => sum + calc.taxInBracket, 0
		);

		// 6. Family deduction
		const applicableChildren = familyDeduction.enabled
			? Math.min(childrenCount, familyDeduction.maxChildren)
			: 0;
		const familyDeductionAmount = totalTaxBeforeDeductions *
			(applicableChildren * familyDeduction.ratePerChild);

		// 7. Final tax
		let finalTax = Math.max(0, totalTaxBeforeDeductions - familyDeductionAmount);

		// 8. Apply global cap (30%)
		const maxTax = grossSalary * iprConfig.globalCapRate;
		const globalCapApplied = finalTax > maxTax;
		if (globalCapApplied) {
			finalTax = maxTax;
		}

		// 9. Effective rate
		const effectiveRate = grossSalary > 0 ? finalTax / grossSalary : 0;

		return {
			grossSalary,
			professionalAllowance,
			taxableBase,
			brackets: bracketCalculations,
			totalTaxBeforeDeductions,
			familyDeduction: familyDeductionAmount,
			finalTax,
			globalCapApplied,
			effectiveRate
		};
	}

	// Calculator actions
	setCalculatorSalary(salary: number) {
		this.calculatorSalary = Math.max(0, salary);
	}

	setCalculatorChildren(count: number) {
		this.calculatorChildren = Math.max(0, Math.min(count, 15));
	}

	toggleCalculator() {
		this.showCalculator = !this.showCalculator;
	}
}


/**
 * Tax UI Store - Gestion de l'état UI pour la configuration fiscale
 * Persistance session pour la bannière (n'apparaît qu'une fois par session)
 */
class TaxUiStore {
  // Bannière légale - n'apparaît qu'une fois par session
  bannerSeen = $state(false);

  constructor() {
	this.bannerSeen = false;
  }

  markBannerSeen() {
	this.bannerSeen = true;
  }

  resetBanner() {
	this.bannerSeen = false;
  }
}


export const taxUiStore = new TaxUiStore();
export const taxSettingsStore = new TaxSettingsStore();

