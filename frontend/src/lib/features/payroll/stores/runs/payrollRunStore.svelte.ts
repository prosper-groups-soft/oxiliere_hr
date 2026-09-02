import type { 
  PayrollRun, PayrollStep, PayrollStatus,
  RunListItem, CycleListFilters, PayrollRunApiOut, 
  PayrollRunDetailApiOut, PayrollRunSummaryApiOut,
  PayrollRunSelection
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

	/**
	 * Vrai tant que l'utilisateur a démarré une nouvelle paie (KickoffStep)
	 * mais que le backend n'a pas encore créé le run DRAFT.
	 * Permet d'afficher l'onglet dynamique immédiatement.
	 */
	isStartingNewRun = $state(false);

	/** Clé localStorage pour l'ID du run actif (persiste à travers les rechargements). */
	private static readonly ACTIVE_RUN_KEY = 'payroll:activeRunId';
	/** Clé sessionStorage pour le démarrage d'une nouvelle paie (avant POST). */
	private static readonly STARTING_RUN_KEY = 'payroll:startingNewRun';

	/** Statuts finaux : l'onglet dynamique doit disparaître. */
	private isFinalStatus(status: string): boolean {
		return status === 'paid' || status === 'closed' || status === 'canceled' || status === 'archived';
	}

	constructor() {
		// Restaure le run actif après un rechargement de page (F5) :
		// le run est rechargé par son ID directement depuis l'API, indépendamment
		// du cache de liste (qui peut être périmé). L'onglet dynamique réapparaît
		// dès que currentRun est rechargé.
		this.restoreActiveRun();
	}

	/** Vrai si un run non finalisé est chargé (l'onglet dynamique doit rester visible). */
	get hasActiveRun(): boolean {
		return this.currentRun !== null && !this.isFinalStatus(this.currentRun.status);
	}

	/** Onglet dynamique : run backend actif OU démarrage client (KickoffStep). */
	get hasCurrentRunTab(): boolean {
		return this.hasActiveRun || this.isStartingNewRun;
	}

	/** Lit l'ID du run actif persisté (ou null). */
	private get persistedActiveRunId(): string | null {
		if (typeof localStorage === 'undefined') return null;
		return localStorage.getItem(PayrollRunStore.ACTIVE_RUN_KEY);
	}

	/** Persiste l'ID du run actif (localStorage). */
	private persistActiveRunId(runId: string | null) {
		if (typeof localStorage === 'undefined') return;
		if (runId) {
			localStorage.setItem(PayrollRunStore.ACTIVE_RUN_KEY, runId);
		} else {
			localStorage.removeItem(PayrollRunStore.ACTIVE_RUN_KEY);
		}
	}

	private persistStartingNewRun(value: boolean) {
		if (typeof sessionStorage === 'undefined') return;
		if (value) {
			sessionStorage.setItem(PayrollRunStore.STARTING_RUN_KEY, '1');
		} else {
			sessionStorage.removeItem(PayrollRunStore.STARTING_RUN_KEY);
		}
	}

	private clearActiveRun() {
		this.currentRun = null;
		this.persistActiveRunId(null);
		this.isStartingNewRun = false;
		this.persistStartingNewRun(false);
	}

	/** Au boot : recharge le run actif persisté par son ID. */
	private async restoreActiveRun() {
		const runId = this.persistedActiveRunId;
		if (!runId) {
			// Pas de run backend : éventuellement un démarrage de paie en cours (Kickoff).
			if (typeof sessionStorage !== 'undefined' && sessionStorage.getItem(PayrollRunStore.STARTING_RUN_KEY) === '1') {
				this.isStartingNewRun = true;
			}
			return;
		}
		try {
			await this.fetchRunDetail(runId);
			// Run introuvable (404) : fetchRunDetail retourne null au lieu de lever
			// une exception (le client API avale les erreurs HTTP). Sans ce garde,
			// l'ID persisté resterait en localStorage et le store retenterait de
			// fetcher un run fantôme à chaque rechargement — même si l'onglet
			// dynamique est visuellement masqué (currentRun === null).
			if (!this.currentRun) {
				this.clearActiveRun();
				return;
			}
			// Si le run persisté est finalisé (PAID/CANCELED), on libère l'onglet.
			if (this.isFinalStatus(this.currentRun.status)) {
				this.clearActiveRun();
			} else {
				// Run actif restauré → plus besoin du flag "starting".
				this.isStartingNewRun = false;
				this.persistStartingNewRun(false);
			}
		} catch {
			// Run introuvable (supprimé côté serveur) : on nettoie tout, y compris
			// un éventuel run fantôme resté en mémoire (sinon l'onglet pourrait
			// perdurer avec un run obsolète).
			this.clearActiveRun();
		}
	}

	/**
	 * Charge la liste et rattache le run actif backend à l'onglet dynamique.
	 * À appeler au montage du layout paie (même si la liste est déjà en cache).
	 */
	async syncActiveRunFromList() {
		await this.fetchRunList();
	}

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
	currentStep = $state<PayrollStep>('kickoff');
	steps = $state<PayrollStep[]>(PAYROLL_STEPS);

	/** Mappe le statut backend d'un run sur le step du wizard à afficher. */
	private static stepForStatus(status: PayrollStatus): PayrollStep {
		switch (status) {
			case 'draft': return 'preparation';
			case 'calculated': return 'calculation';
			case 'reviewed': return 'review';
			case 'approved': return 'approval';
			case 'paid':
			case 'closed':
			case 'archived': return 'payment';
		}
	}

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
		// Sans run backend mais en cours de démarrage (kickoff), seule l'étape 0
		// est accessible. Sinon, l'index suit le statut du run (décalé d'un cran
		// car l'index 0 est désormais réservé à kickoff).
		if (!this.currentRun) {
			return this.isStartingNewRun ? 0 : -1;
		}
		const statusToIndex: Record<PayrollStatus, number> = {
			'draft': 1,
			'calculated': 2,
			'reviewed': 3,
			'approved': 4,
			'paid': 5,
			'closed': 6,
			'archived': 7
		};
		return statusToIndex[this.currentRun.status] ?? 1;
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
		const paramsSnapshot = detail.params_snapshot ?? undefined;
		// Extrait la sélection depuis params_snapshot (clé `selection`) pour les steps.
		const selection = (paramsSnapshot?.['selection'] as PayrollRunSelection | undefined) ?? undefined;

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
			paramsSnapshot,
			selection,
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

				// Identifier le run actif (jamais PAID ni CANCELED).
				// Attention : la liste backend peut être servie depuis le cache (24 h) et
				// ne pas refléter un run récemment créé. On ne doit JAMAIS écraser un
				// currentRun existant — l'onglet dynamique "Paie en cours" disparaîtrait.
				const activeRun = res.results.find(r => r.status !== 'PAID' && r.status !== 'CANCELED');
				if (activeRun) {
					if (this.currentRun?.id !== activeRun.id) {
						await this.fetchRunDetail(activeRun.id);
					} else {
						this.isStartingNewRun = false;
						this.persistStartingNewRun(false);
					}
				} else if (this.currentRun && this.hasActiveRun) {
					// Aucun run actif dans la liste : on ne réinitialise currentRun que
					// si le run courant apparaît explicitement comme finalisé dans la
					// liste (protection contre le cache périmé qui ne contiendrait pas
					// encore le run récemment créé).
					const currentInList = res.results.find(r => r.id === (this.currentRun as PayrollRun).id);
					if (currentInList && ['PAID', 'CANCELED'].includes(currentInList.status)) {
						this.clearActiveRun();
					}
				}

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
				// Idem : on ne réinitialise PAS currentRun ici pour ne pas faire
				// disparaître l'onglet dynamique sur une réponse vide/cachée.
			}
		} catch (err) {
			this.error = err instanceof Error ? err.message : 'Erreur lors du chargement des runs';
			throw err;
		}
	}

	async fetchRunDetail(runId: string): Promise<PayrollRun | null> {
		try {
			const run = await payrollRunApiStore.fetchRunDetail(runId);
			if (!run) return null;
			const summary = await payrollRunApiStore.fetchRunSummary(runId);
			this.currentRun = this.detailToPayrollRun(run, summary);
			// Persiste l'ID du run dès qu'il est chargé (sauf s'il est déjà finalisé
			// — dans ce cas on retire la clé pour libérer l'onglet).
			if (['PAID', 'CANCELED'].includes(run.status)) {
				this.persistActiveRunId(null);
			} else {
				this.persistActiveRunId(runId);
				this.isStartingNewRun = false;
				this.persistStartingNewRun(false);
			}
			// Ré-affiche le step correspondant au statut du run. Un run restauré
			// (clic onglet / F5) doit ouvrir le step de son statut courant, pas
			// le kickoff. Un run actif n'a jamais kickoff pour step légitime :
			// si l'utilisateur y est encore, c'est qu'on vient de restaurer.
			// On ne touche PAS à la position s'il navigue déjà (préserve le
			// refresh de fin d'étape : pas de saut automatique vers l'avant).
			if (this.currentStep === 'kickoff') {
				this.currentStep = PayrollRunStore.stepForStatus(this.currentRun.status);
			}

			// Charge les bulletins de paie du run pour alimenter les steps
			// (preparation, calculation, review...). Import dynamique pour
			// éviter le cycle ESM : payslipsStore importe déjà payrollRunStore.
			// Le run reste chargé même si le fetch des bulletins échoue.
			try {
				const { payslipsStore } = await import('../payslips/payslipsStore.svelte');
				await payslipsStore.fetchPayslips(runId);
			} catch {
				// Silencieux : les steps afficheront les données du run uniquement.
			}

			return this.currentRun;
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
	async createPayrollRunFromDates(
		startDate: string,
		endDate: string,
		exchangeRate: number | null = null,
		selection: PayrollRunSelection = { scope: 'all' },
	): Promise<PayrollRun | null> {
		if (!startDate || !endDate || startDate >= endDate) {
			this.error = 'Date de début et de fin invalides';
			return null;
		}

		const created = await payrollRunApiStore.createRun({
			start_date: startDate,
			end_date: endDate,
			exchange_rate_applied: exchangeRate,
			selection_scope: selection.scope,
			org_unit_ids: selection.org_unit_ids ?? [],
			employee_ids: selection.employee_ids ?? [],
		});
		if (!created) {
			// L'API client avale les erreurs → on récupère le message du backend
			// (ex. « Une paie est déjà en cours ») pour le propager au formulaire.
			const apiError = payrollRunApiStore.getLastError('listState');
			this.error = apiError ?? 'Échec de la création du run';
			throw new Error(this.error);
		}

		// Initialisation immédiate du store avec les données de création
		// Cela permet à l'onglet "Cycle en cours" d'apparaître tout de suite
		this.currentRun = {
			id: created.id,
			cycleId: created.id,
			period: periodLabelFromDates(created.start_date, created.end_date),
			type: 'monthly',
			status: backendToPayrollStatus(created.status),
			currency: 'USD',
			exchangeRate: Number(created.exchange_rate_applied ?? 1),
			periodStart: created.start_date,
			periodEnd: created.end_date,
			fiscalVersion: 'fv-1',
			totalGross: 0,
			totalNet: 0,
			totalContributions: 0,
			totalTaxes: 0,
			totalAllocations: 0,
			employeeCount: 0,
			totalEmployeeCount: 0,
			createdAt: created.created_at
		};

		// Persistance et flag : immédiats, pour que l'onglet soit stable
		// dès le retour (même avant la fin des rafraîchissements en arrière-plan).
		this.persistActiveRunId(created.id);
		this.isStartingNewRun = false;
		this.persistStartingNewRun(false);

		// Rafraîchit la liste et charge le détail enrichi en ARRIÈRE-PLAN.
		// Ne pas `await` ici : le `currentRun` minimal ci-dessus suffit déjà à
		// afficher l'onglet dynamique et à naviguer. Attendre la liste + le
		// détail + le summary (3 requêtes séquentielles) retardait inutilement
		// la redirection du KickoffStep. `.catch` évite tout rejet non géré.
		void this.fetchRunList().catch(() => { /* erreur déjà consignée dans this.error */ });
		void this.fetchRunDetail(created.id).catch(() => { /* idem */ });

		return this.currentRun;
	}

	/** Signale que l'utilisateur a initié un nouveau cycle (avant soumission du formulaire).
	 *  Affiche l'onglet « Nouvelle paie » immédiatement. Le run DRAFT backend
	 *  est créé via `createPayrollRun*` à la soumission du KickoffStep.
	 *  Garde : no-op si un run est déjà en cours. */
	beginNewRun() {
		if (this.hasActiveRun) return;
		// Si un run finalisé est encore en mémoire (consultation historique),
		// on le libère pour afficher le KickoffStep.
		if (this.currentRun) {
			this.currentRun = null;
			this.persistActiveRunId(null);
		}
		this.isStartingNewRun = true;
		this.persistStartingNewRun(true);
		this.resetSteps();
	}

	/** Annule l'initiation d'un nouveau cycle (l'utilisateur a cliqué "Annuler"). */
	cancelNewRun() {
		this.isStartingNewRun = false;
		this.persistStartingNewRun(false);
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
		const id = this.currentRun.id;
		const result = await payrollRunApiStore.completeRun(id);
		if (!result) return false;
		// Re-synchroniser le détail depuis le backend et ne libérer l'onglet
		// que si le run est explicitement `PAID` côté serveur.
		try {
			await this.fetchRunDetail(id);
			if (this.currentRun && this.currentRun.status === 'paid') {
				this.clearActiveRun();
			}
			// Rafraîchit la liste en arrière-plan.
			await this.fetchRunList();
			return true;
		} catch (err) {
			// Si la récupération échoue, on ne supprime pas currentRun pour éviter
			// une disparition involontaire — l'UI restera visible jusqu'à la
			// prochaine synchronisation réussie.
			this.error = err instanceof Error ? err.message : 'Erreur lors de la synchronisation post-paiement';
			return false;
		}
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
		this.currentStep = 'kickoff';
	}
}


export const payrollRunStore = new PayrollRunStore();

