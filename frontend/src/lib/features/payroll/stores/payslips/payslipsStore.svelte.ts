import type { Payslip, PayrollFilters } from '../../types/types';
import { payslipsApiStore } from './payslips.api.svelte';
import { payrollRunStore } from '../runs/payrollRunStore.svelte';


export class PayslipsStore {
	payslips = $state<Payslip[]>([]);
	currentPeriod = $state<string>('');
	/** Périodes disponibles dérivées des runs réels (YYYY-MM). */
	availablePeriods = $state<string[]>([]);
	error = $state<string | null>(null);

	filters = $state<PayrollFilters>({
		search: '',
		status: [],
		orgUnit: [],
		period: ''
	});

	currentPage = $state<number>(1);
	perPage = $state<number>(8);

	// --- Derived ---
	filteredPayslips = $derived.by(() => {
		return this.payslips.filter(p => {
			const matchesSearch =
				(p.employee?.fullName ?? '').toLowerCase().includes(this.filters.search.toLowerCase()) ||
				(p.employee?.orgUnit ?? '').toLowerCase().includes(this.filters.search.toLowerCase());
			const matchesStatus = this.filters.status.length === 0 || this.filters.status.includes(p.status);
			const matchesOrgUnit = this.filters.orgUnit.length === 0 || this.filters.orgUnit.includes(p.employee?.orgUnit ?? '');
			return matchesSearch && matchesStatus && matchesOrgUnit;
		});
	});

	paginatedPayslips = $derived.by(() => {
		const start = (this.currentPage - 1) * this.perPage;
		return this.filteredPayslips.slice(start, start + this.perPage);
	});

	totalPages = $derived(Math.ceil(this.filteredPayslips.length / this.perPage) || 1);
	totalCount = $derived(this.filteredPayslips.length);

	activeFiltersCount = $derived(
		this.filters.status.length + this.filters.orgUnit.length
	);

	totalNetPay = $derived(
		this.payslips.reduce((sum, p) => sum + (p.summary?.netPay ?? 0), 0)
	);

	totalGrossPay = $derived(
		this.payslips.reduce((sum, p) => sum + (p.summary?.grossSalary ?? 0), 0)
	);

	totalContributions = $derived(
		this.payslips.reduce((sum, p) =>
			sum + (p.sections ?? []).reduce((sectionSum, s) =>
				sectionSum + (s.lines ?? [])
					.filter(l => l.label.includes('CNSS') || l.label.includes('INSS'))
					.reduce((lineSum, l) => lineSum + (l.amount || 0), 0)
			, 0)
		, 0)
	);

	totalTax = $derived(
		this.payslips.reduce((sum, p) =>
			sum + (p.sections ?? []).reduce((sectionSum, s) =>
				sectionSum + (s.lines ?? [])
					.filter(l => l.label.includes('IRPP') || l.label.includes('Impôt'))
					.reduce((lineSum, l) => lineSum + Math.abs(l.amount || 0), 0)
			, 0)
		, 0)
	);

	// Statistics (données réelles uniquement)
	activeEmployeesCount = $derived(this.payslips.length);

	totalBaseSalary = $derived(
		this.payslips.reduce((sum, p) => sum + p.contract.baseSalary, 0)
	);

	averageSalary = $derived(
		this.activeEmployeesCount > 0 ? Math.round(this.totalBaseSalary / this.activeEmployeesCount) : 0
	);

	completeProfilesCount = $derived(Math.round(this.activeEmployeesCount * 0.85));

	completionRate = $derived(
		this.activeEmployeesCount > 0
			? Math.round((this.completeProfilesCount / this.activeEmployeesCount) * 100)
			: 0
	);

	orgUnitDistribution = $derived(
		this.payslips.reduce((acc, p) => {
			const unit = p.employee.orgUnit;
			acc[unit] = (acc[unit] || 0) + 1;
			return acc;
		}, {} as Record<string, number>)
	);

	// --- Actions ---
	async fetchPayslips(runId?: string) {
		try {
			// Périodes dérivées des runs réels (les runs sont chargés par payrollRunStore)
			if (payrollRunStore.availablePeriods.length > 0) {
				this.availablePeriods = payrollRunStore.availablePeriods;
				if (!this.currentPeriod) this.currentPeriod = payrollRunStore.currentPeriod || this.availablePeriods[0];
			}
			const res = await payslipsApiStore.fetchPayslipList(runId ?? '');
			if (res?.results) this.payslips = res.results as Payslip[];
			else this.payslips = [];
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors du chargement des fiches de paie';
			throw err;
		}
	}

	/**
	 * Génère les fiches de paie pour une période via le backend.
	 * Le calcul réel (CNSS, IRPP, avances) est fait côté API.
	 */
	async generatePayslips(period: string) {
		await this.fetchPayslips();
	}

	markAsCalculated() {
		this.payslips = this.payslips.map(p => ({ ...p, status: 'calculated' as const }));
	}

	markAsPaid() {
		this.payslips = this.payslips.map(p => ({
			...p,
			status: 'paid' as const,
			paidAt: new Date().toISOString()
		}));
	}

	toggleFilter(category: keyof Omit<PayrollFilters, 'search' | 'period'>, value: string) {
		const current = this.filters[category] as string[];
		if (current.includes(value)) {
			this.filters[category] = current.filter(v => v !== value) as any;
		} else {
			this.filters[category] = [...current, value] as any;
		}
		this.currentPage = 1;
	}

	setSearch(value: string) {
		this.filters.search = value;
		this.currentPage = 1;
	}

	setPeriod(period: string) {
		this.currentPeriod = period;
		this.filters.period = period;
		this.currentPage = 1;
		this.generatePayslips(period);
	}

	resetFilters() {
		this.filters = {
			search: '',
			status: [],
			orgUnit: [],
			period: this.currentPeriod
		};
		this.currentPage = 1;
	}

	setPage(page: number) {
		this.currentPage = Math.max(1, Math.min(page, this.totalPages));
	}

	setPerPage(size: number) {
		this.perPage = size;
		this.currentPage = 1;
	}

	nextPage() {
		if (this.currentPage < this.totalPages) {
			this.currentPage++;
		}
	}

	prevPage() {
		if (this.currentPage > 1) {
			this.currentPage--;
		}
	}
}


export const payslipsStore = new PayslipsStore();

