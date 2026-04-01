import type {
	TaxConfig,
	IPRBracket,
	IPRCalculationResult
} from '../types/tax.types';
import { DEFAULT_TAX_CONFIG } from '../types/tax.types';

export class TaxSettingsStore {
	// --- Reactive State ---
	config = $state<TaxConfig>({ ...DEFAULT_TAX_CONFIG });
	isLoading = $state(false);
	isSaving = $state(false);
	error = $state<string | null>(null);
	hasChanges = $state(false);

	// Editing state
	editingBracketId = $state<string | null>(null);
	bracketEditForm = $state<Partial<IPRBracket>>({});

	// Calculator state
	calculatorSalary = $state<number>(1000);
	calculatorChildren = $state<number>(2);
	showCalculator = $state(false);

	// --- Derived State ---
	iprBrackets = $derived(this.config.iprBrackets);
	familyDeduction = $derived(this.config.familyDeduction);
	cnssConfig = $derived(this.config.cnss);
	inssConfig = $derived(this.config.inss);

	maxIPRRate = $derived(Math.max(...this.config.iprBrackets.map(b => b.rate)));
	totalBrackets = $derived(this.config.iprBrackets.length);

	// Validation
	isValid = $derived.by(() => {
		// Check brackets are properly ordered
		for (let i = 0; i < this.config.iprBrackets.length - 1; i++) {
			const current = this.config.iprBrackets[i];
			const next = this.config.iprBrackets[i + 1];
			if (current.max !== next.min) {
				return false;
			}
		}
		return true;
	});

	// Calculator result
	calculatorResult = $derived.by((): IPRCalculationResult | null => {
		if (!this.showCalculator || this.calculatorSalary <= 0) return null;
		return this.calculateIPR(this.calculatorSalary, this.calculatorChildren);
	});

	// --- Actions ---
	updateIPRBracket(id: string, updates: Partial<IPRBracket>) {
		const index = this.config.iprBrackets.findIndex(b => b.id === id);
		if (index !== -1) {
			this.config.iprBrackets[index] = { ...this.config.iprBrackets[index], ...updates };
			// Recalculate labels
			this.updateBracketLabels();
			this.hasChanges = true;
		}
	}

	updateBracketLabels() {
		this.config.iprBrackets = this.config.iprBrackets.map((b, index) => ({
			...b,
			label: `Tranche ${index + 1} (${b.min} - ${b.max ?? '∞'} ${this.config.currency})`
		}));
	}

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

	updateIPRConfig(updates: Partial<typeof this.config.iprConfig>) {
		this.config.iprConfig = { ...this.config.iprConfig, ...updates };
		this.hasChanges = true;
	}

	setCurrency(currency: 'USD' | 'CDF') {
		this.config.currency = currency;
		this.updateBracketLabels();
		this.hasChanges = true;
	}

	startEditingBracket(id: string) {
		const bracket = this.config.iprBrackets.find(b => b.id === id);
		if (bracket) {
			this.editingBracketId = id;
			this.bracketEditForm = { ...bracket };
		}
	}

	saveBracketEdit() {
		if (this.editingBracketId && this.bracketEditForm) {
			this.updateIPRBracket(this.editingBracketId, this.bracketEditForm);
			this.editingBracketId = null;
			this.bracketEditForm = {};
		}
	}

	cancelBracketEdit() {
		this.editingBracketId = null;
		this.bracketEditForm = {};
	}

	resetToDefaults() {
		this.config = { ...DEFAULT_TAX_CONFIG };
		this.hasChanges = true;
	}

	async saveSettings() {
		this.isSaving = true;
		this.error = null;
		try {
			await new Promise(resolve => setTimeout(resolve, 800));
			this.hasChanges = false;
			return true;
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors de la sauvegarde';
			return false;
		} finally {
			this.isSaving = false;
		}
	}

	async loadSettings() {
		this.isLoading = true;
		this.error = null;
		try {
			await new Promise(resolve => setTimeout(resolve, 500));
			this.hasChanges = false;
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors du chargement';
		} finally {
			this.isLoading = false;
		}
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

export const taxSettingsStore = new TaxSettingsStore();
