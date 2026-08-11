import type {
	PayrollRun, PayrollStep, PayrollStatus,
	RunListItem, CycleListFilters,
	PayrollRunApiOut, PayrollRunDetailApiOut, PayrollRunSummaryApiOut
} from '../../types/types';
import {
	PAYROLL_STEPS,
	backendToRunListStatus,
	backendToPayrollStatus,
	periodLabelFromDates,
	availablePeriodFromDates,
	currentMonthKey
} from '../../types/types';
import { payrollRunApiStore } from './payrollRun.api.svelte';
import { payrollConfigStore } from '../configuration/payrollConfigStore.svelte';


export class PayrollRunStore {
	currentPeriod = $state<string>(currentMonthKey());
	availablePeriods = $state<string[]>([]);
	error = $state<string | null>(null);

	payrollRuns = $state<PayrollRun[]>([]);

	currentRun = $state<PayrollRun | null>(null);

	// --- Run List (S1) ---
	runList = $state<RunListItem[]>([]);
	runListTotalCount = $state<number>(0);

	cycleFilters = $state<CycleListFilters>({
		status: 'all',
		period: '',
		search: '',
		orgUnit: ''
	});

	cycleListPage = $state<number>(1);
	cycleListPerPage = $state<number>(10);
	sortBy = $state<'period' | 'status' | 'employeeCount' | 'grossTotal'>('period');
	sortOrder = $state<'asc' | 'desc'>('desc');

	// Wizard steps
	currentStep = $state<PayrollStep>('preparation');
	steps = $state<PayrollStep[]>(PAYROLL_STEPS);

	filteredRunList = $derived.by(() => {
		let items = [...this.runList];

		if (this.cycleFilters.status !== 'all') {
			items = items.filter(r => r.status === this.cycleFilters.status);
		}

		if (this.cycleFilters.period) {
			items = items.filter(r => r.periodLabel === this.cycleFilters.period);
		}

		if (this.cycleFilters.search) {
			const q = this.cycleFilters.search.toLowerCase();
			items = items.filter(r => r.periodLabel.toLowerCase().includes(q));
		}

		if (this.cycleFilters.orgUnit) {
			items = items.filter(r => r.orgUnits?.includes(this.cycleFilters.orgUnit));
		}

		items.sort((a, b) => {
			let cmp = 0;
			switch (this.sortBy) {
				case 'period':
					cmp = a.periodLabel.localeCompare(b.periodLabel);
					break;
				case 'status':
					cmp = a.status.localeCompare(b.status);
					break;
				case 'employeeCount':
					cmp = a.employeeCount - b.employeeCount;
					break;
				case 'grossTotal':
					cmp = a.grossTotal - b.grossTotal;
					break;
			}
			return this.sortOrder === 'asc' ? cmp : -cmp;
		});

		return items;
	});

	paginatedRunList = $derived.by(() => {
		const start = (this.cycleListPage - 1) * this.cycleListPerPage;
		return this.filteredRunList.slice(start, start + this.cycleListPerPage);
	});

	runListTotalPages = $derived(
		Math.ceil(this.filteredRunList.length / this.cycleListPerPage) || 1
	);

	runListTotalItems = $derived(this.filteredRunList.length);

	/** Périodes disponibles dérivées des runs réels (dédupliquées, triées desc). */
	runListPeriods = $derived(
		['Toutes les périodes', ...new Set(this.runList.map(r => r.periodLabel))]
	);

	activeCycleFiltersCount = $derived(
		(this.cycleFilters.status !== 'all' ? 1 : 0) +
		(this.cycleFilters.period ? 1 : 0) +
		(this.cycleFilters.orgUnit ? 1 : 0)
	);

	currentStepIndex = $derived(
		this.steps.indexOf(this.currentStep)
	);

	canGoNext = $derived(
		this.currentStepIndex < this.steps.length - 1 && this.currentRun !== null
	);

	canGoPrev = $derived(
		this.currentStepIndex > 0
	);

	isLastStep = $derived(
		this.currentStepIndex === this.steps.length - 1
	);

	maxAccessibleStepIndex = $derived.by(() => {
		if (!this.currentRun) return -1;
		const statusToIndex: Record<PayrollStatus, number> = {
			'draft': 0,
			'calculated': 1,
			'reviewed': 2,
			'approved': 3,
			'paid': 4,
			'closed': 5,
			'archived': 6
		};
		return statusToIndex[this.currentRun.status] ?? 0;
	});

	canAccessStep(stepIndex: number) {
		return stepIndex <= this.maxAccessibleStepIndex || stepIndex === this.currentStepIndex;
	}

	setCycleFilter<K extends keyof CycleListFilters>(key: K, value: CycleListFilters[K]) {
		this.cycleFilters = { ...this.cycleFilters, [key]: value };
		this.cycleListPage = 1;
	}

	resetCycleFilters() {
		this.cycleFilters = { status: 'all', period: '', search: '', orgUnit: '' };
		this.cycleListPage = 1;
	}

	// --- Mapping helpers ---

	/** Convertit un PayrollRunApiOut (liste/création) en RunListItem. */
	toRunListItem(run: PayrollRunApiOut): RunListItem {
		return {
			id: run.id,
			periodLabel: run.period_label ?? periodLabelFromDates(run.start_date, run.end_date),
			status: backendToRunListStatus(run.status),
			employeeCount: run.employee_count ?? 0,
			totalEmployeeCount: run.employee_count ?? 0,
			grossTotal: Number(run.gross_total ?? 0),
			closedAt: run.closed_at ?? undefined
		};
	}

	/** Convertit le dict de détail backend en PayrollRun enrichi (wizard). */
	detailToPayrollRun(detail: PayrollRunDetailApiOut, summary?: PayrollRunSummaryApiOut | null): PayrollRun {
		const status = backendToPayrollStatus(detail.status);
		const periodLabel = periodLabelFromDates(detail.start_date, detail.end_date);
		const exchangeRate = Number(detail.exchange_rate ?? payrollConfigStore.exchangeRate ?? 1);

		return {
			id: detail.id,
			cycleId: detail.id,
			period: periodLabel,
			type: 'monthly',
			status,
			currency: 'USD',
			exchangeRate,
			periodStart: detail.start_date,
			periodEnd: detail.end_date,
			fiscalVersion: 'fv-1',
			totalGross: Number(detail.financials.gross_total ?? 0),
			totalNet: Number(detail.financials.net_total ?? 0),
			totalContributions: Number(detail.financials.total_tax_deductions ?? 0),
			totalTaxes: Number(detail.financials.total_tax_deductions ?? 0),
			totalAllocations: 0,
			employeeCount: detail.stats.total_count ?? 0,
			totalEmployeeCount: detail.stats.total_count ?? 0,
			createdAt: detail.created_at,
			calculatedAt: detail.status === 'VALIDATED' || detail.status === 'REVIEWED' || detail.status === 'APPROVED' || detail.status === 'PAID' ? detail.updated_at : undefined,
			reviewedAt: detail.status === 'REVIEWED' || detail.status === 'APPROVED' || detail.status === 'PAID' ? detail.updated_at : undefined,
			approvedAt: detail.status === 'APPROVED' || detail.status === 'PAID' ? detail.updated_at : undefined,
			paidAt: detail.status === 'PAID' ? detail.updated_at : undefined
		};
	}

	// --- Actions ---

	async fetchRunList() {
		try {
			const res = await payrollRunApiStore.fetchRunList(this.cycleFilters);
			if (res?.results) {
				this.runList = res.results.map(r => this.toRunListItem(r));
				this.runListTotalCount = res.count ?? this.runList.length;
				// availablePeriods dérivé des runs réels (YYYY-MM, triés desc)
				this.availablePeriods = [...new Set(
					res.results
						.map(r => availablePeriodFromDates(r.start_date))
				)].sort((a, b) => b.localeCompare(a));
				// currentPeriod par défaut : le plus récent s'il existe
				if (!this.currentPeriod && this.availablePeriods.length > 0) {
					this.currentPeriod = this.availablePeriods[0];
				}
			} else {
				this.runList = [];
				this.runListTotalCount = 0;
			}
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors du chargement des runs';
			throw err;
		}
	}

	async fetchRunDetail(runId: string) {
		try {
			const run = await payrollRunApiStore.fetchRunDetail(runId);
			if (run) {
				const summary = await payrollRunApiStore.fetchRunSummary(runId);
				this.currentRun = this.detailToPayrollRun(run, summary);
			}
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors du chargement du run';
			throw err;
		}
	}

	/** Crée un run via l'API (période YYYY-MM → start/end dates), puis charge le détail. */
	async createPayrollRun(period: string): Promise<PayrollRun | null> {
		const [year, month] = period.split('-').map(Number);
		if (!year || !month) {
			this.error = `Période invalide : ${period}`;
			return null;
		}
		const startDate = `${period}-01`;
		const endDate = new Date(year, month, 0).toISOString().slice(0, 10); // dernier jour du mois

		return this.createPayrollRunFromDates(startDate, endDate, payrollConfigStore.exchangeRate ?? null);
	}

	/** Crée un run via l'API avec des dates explicites, puis charge le détail. */
	async createPayrollRunFromDates(startDate: string, endDate: string, exchangeRate: number | null = null): Promise<PayrollRun | null> {
		if (!startDate || !endDate || startDate >= endDate) {
			this.error = 'Date de début et de fin invalides';
			return null;
		}

		const created = await payrollRunApiStore.createRun({
			start_date: startDate,
			end_date: endDate,
			exchange_rate_applied: exchangeRate
		});
		if (!created) {
			this.error = this.error ?? 'Échec de la création du run';
			return null;
		}

		// Rafraîchit la liste (le run créé apparaît) puis charge le détail
		await this.fetchRunList();
		await this.fetchRunDetail(created.id);
		return this.currentRun;
	}

	/** Calcule la paie (lance le traitement backend : DRAFT → PROCESSING → VALIDATED). */
	async calculatePayroll(): Promise<boolean> {
		if (!this.currentRun) return false;
		const result = await payrollRunApiStore.processRun(this.currentRun.id);
		if (!result) return false;
		await this.fetchRunDetail(this.currentRun.id);
		await this.fetchRunList();
		return true;
	}

	/** Révision de la paie (VALIDATED → REVIEWED). */
	async reviewPayroll(): Promise<boolean> {
		if (!this.currentRun) return false;
		const result = await payrollRunApiStore.reviewRun(this.currentRun.id);
		if (!result) return false;
		await this.fetchRunDetail(this.currentRun.id);
		await this.fetchRunList();
		return true;
	}

	/** Approbation de la paie (REVIEWED → APPROVED). */
	async approvePayroll(): Promise<boolean> {
		if (!this.currentRun) return false;
		const result = await payrollRunApiStore.approveRun(this.currentRun.id);
		if (!result) return false;
		await this.fetchRunDetail(this.currentRun.id);
		await this.fetchRunList();
		return true;
	}

	/** Paiement / clôture de la paie (VALIDATED/REVIEWED/APPROVED → PAID). */
	async processPayment(): Promise<boolean> {
		if (!this.currentRun) return false;
		const result = await payrollRunApiStore.completeRun(this.currentRun.id);
		if (!result) return false;
		await this.fetchRunDetail(this.currentRun.id);
		await this.fetchRunList();
		return true;
	}

	setSort(by: typeof this.sortBy) {
		if (this.sortBy === by) {
			this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
		} else {
			this.sortBy = by;
			this.sortOrder = 'desc';
		}
		this.cycleListPage = 1;
	}

	setCycleListPage(page: number) {
		this.cycleListPage = Math.max(1, Math.min(page, this.runListTotalPages));
	}

	nextStep() {
		if (this.canGoNext) {
			this.currentStep = this.steps[this.currentStepIndex + 1];
		}
	}

	prevStep() {
		if (this.canGoPrev) {
			this.currentStep = this.steps[this.currentStepIndex - 1];
		}
	}

	goToStep(step: PayrollStep) {
		this.currentStep = step;
	}

	resetSteps() {
		this.currentStep = 'preparation';
	}
}


export const payrollRunStore = new PayrollRunStore();

