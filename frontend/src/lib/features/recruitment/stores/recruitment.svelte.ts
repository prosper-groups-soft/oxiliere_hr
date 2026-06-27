import type {
	Candidate,
	Interview,
	JobOffer,
	RecruitmentFilters,
	PipelineColumn,
	PipelineApplicationItem,
	CreateCandidateInput,
	UpdateCandidateInput,
	CreateJobOfferInput,
	CandidateStage,
	RecruitmentCampaign
} from '../types/types';
import { recruitmentService } from '../services/recruitmentService';


class RecruitmentStore {
	campaigns = $state<RecruitmentCampaign[]>([]);
	activeCampaignId = $state<string | null>(null);
	currentCampaign = $state<RecruitmentCampaign | undefined>(undefined);

	candidates = $state<Candidate[]>([]);
	interviews = $state<Interview[]>([]);
	offers = $state<JobOffer[]>([]);
	candidatePerPage = $state(8);
	candidateCurrentPage = $state(1);
	profileSheetOpen = $state(false);
	profileSheetCandidateId = $state('');
	filters = $state<RecruitmentFilters>({
		search: '',
		stage: [],
		source: [],
		priority: [],
		positionId: []
	});
	pipelinePositionIds = $state<string[]>([]);
	isLoading = $state(false);
	error = $state<string | null>(null);

	// Campaign-specific state
	searchQuery = $state('');
	campaignFilters = $state<{
		status: string[];
		jobNames: string[];
		type: string[];
	}>({
		status: [],
		jobNames: [],
		type: []
	});
	sortBy = $state('title');
	sortOrder = $state<'asc' | 'desc'>('asc');
	currentPage = $state(1);
	perPage = $state(8);

	// Métadonnées de pagination du serveur
	serverTotalCount = $state(0);
	serverTotalPages = $state(1);

	// Version du pipeline pour forcer le refresh visuel (DnD rollback)
	private _pipelineVersion = $state(0);

	// Getters

	/**
	 * Rafraîchit le pipeline en forçant une re-dérivation des données
	 * Utile pour les rollbacks lors de Drag & Drop
	 */
	refreshPipeline() {
		this._pipelineVersion += 1;
	}

	get activeFiltersCount(): number {
		return (
			(this.searchQuery ? 1 : 0) +
			this.campaignFilters.status.length +
			this.campaignFilters.jobNames.length +
			this.campaignFilters.type.length
		);
	}

	get activeCandidateFiltersCount(): number {
		return (
			(this.filters.search ? 1 : 0) +
			(this.filters.stage?.length || 0) +
			(this.filters.source?.length || 0) +
			(this.filters.priority?.length || 0) +
			(this.filters.positionId?.length || 0) +
			(this.filters.gender?.length || 0)
		);
	}

	get pipelineData(): PipelineColumn[] {
		const stages: CandidateStage[] = ['SCREENING', 'SHORTLIST', 'INTERVIEW', 'OFFER'];

		return stages.map((stage) => ({
			stage,
			title: this.getStageTitle(stage),
			candidates: this.candidates.filter(
				(c: Candidate) => c.currentStage === stage && (!c.applications || c.applications.length === 0 ? true : c.applications.some(a => a.inPipeline !== false && a.currentStage !== 'REJECTED'))
			),
			applications: [],
		}));
	}

	/**
	 * Pipeline affiché par Applications (pas par Candidats).
	 * Chaque application d'un candidat devient une carte distincte dans sa colonne de stage.
	 */
	get pipelineApplications(): PipelineColumn[] {
		// Read _pipelineVersion so refreshPipeline() triggers re-derivation (DnD rollback)
		void this._pipelineVersion;
		const stages: CandidateStage[] = ['SCREENING', 'SHORTLIST', 'INTERVIEW', 'OFFER', 'ACCEPTED', 'REJECTED'];

		const allItems: PipelineApplicationItem[] = [];
		for (const c of this.candidates) {
			if (!c.applications || c.applications.length === 0) continue;
			for (const app of c.applications) {
				if (app.inPipeline === false) continue;
				allItems.push({ id: app.applicationId, candidate: c, application: app });
			}
		}

		return stages.map((stage) => ({
			stage,
			title: this.getStageTitle(stage),
			candidates: [],
			applications: allItems.filter(item => item.application.currentStage === stage),
		}));
	}

	get activeCampaign(): RecruitmentCampaign | undefined {
		if (this.currentCampaign && this.currentCampaign.id === this.activeCampaignId) {
			return this.currentCampaign;
		}
		if (!this.activeCampaignId) return undefined;
		return undefined;
	}

	// Actions

	/**
	 * Met à jour les données depuis le serveur
	 * Appelé par les queries après un fetch
	 */
	setJobOffers(data: RecruitmentCampaign[], total?: number, pages?: number) {
		this.campaigns = data;
		if (total !== undefined) {
			this.serverTotalCount = total;
		}
		if (pages !== undefined) {
			this.serverTotalPages = pages;
		}
	}

	setLoading(loading: boolean) {
		this.isLoading = loading;
	}

	setError(err: string | null) {
		this.error = err;
	}

	async addCandidate(data: CreateCandidateInput) {
		this.isLoading = true;
		this.error = null;

		try {
			const newCandidate = await recruitmentService.create(data);
			if (newCandidate) {
				this.candidates = [...this.candidates, newCandidate];
			}
			return newCandidate;
		} catch (error) {
			this.error = error instanceof Error ? error.message : "Erreur lors de l'ajout du candidat";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async updateEvaluation(applicationId: string, data: {
		scores?: Record<string, number>;
		evaluationNotes?: string;
	}) {
		this.isLoading = true;
		this.error = null;

		try {
			await recruitmentService.updateApplicationEvaluation(applicationId, data);
			// Update local candidate data if needed
			this.candidates = this.candidates.map((c) => ({
				...c,
				applications: c.applications?.map(a =>
					a.applicationId === applicationId
						? { ...a, evaluationNotes: data.evaluationNotes, scores: data.scores }
						: a
				) || []
			}));
		} catch (error) {
			this.error =
				error instanceof Error ? error.message : 'Erreur lors de la mise à jour de l\'évaluation';
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async updateCandidate(id: string, data: UpdateCandidateInput) {
		this.isLoading = true;
		this.error = null;

		try {
			const updated = await recruitmentService.update(id, data);
			if (updated) {
				this.candidates = this.candidates.map((c) => (c.id === id ? { ...c, ...updated } : c));
			}
		} catch (error) {
			this.error =
				error instanceof Error ? error.message : 'Erreur lors de la mise à jour du candidat';
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async updateCandidateStage(candidateId: string, newStage: CandidateStage) {
		this.isLoading = true;
		this.error = null;

		try {
			const updated = await recruitmentService.updateStage(candidateId, newStage);
			if (updated) {
				this.candidates = this.candidates.map((c) => (c.id === candidateId ? { ...c, ...updated } : c));
			}
		} catch (error) {
			this.error =
				error instanceof Error ? error.message : 'Erreur lors de la mise à jour du statut';
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	/**
	 * Met à jour le stage d'une application spécifique via le backend.
	 * Utilisé par le pipeline (DnD) pour changer le stage d'une Application, pas du Candidat.
	 */
	async updateApplicationStage(applicationId: string, newStage: CandidateStage) {
		this.isLoading = true;
		this.error = null;

		// Sauvegarder l'état pour rollback en cas d'échec API
		let rollbackCandidateId: string | null = null;
		let rollbackOldStage: CandidateStage | null = null;
		for (const c of this.candidates) {
			if (!c.applications) continue;
			const app = c.applications.find(a => a.applicationId === applicationId);
			if (app) {
				rollbackCandidateId = c.id;
				rollbackOldStage = app.currentStage;
				break;
			}
		}

		// 1. Mise à jour optimiste locale → la carte se déplace IMMÉDIATEMENT
		this.candidates = this.candidates.map((c) => {
			if (!c.applications) return c;
			const hasApp = c.applications.some(a => a.applicationId === applicationId);
			if (!hasApp) return c;
			return {
				...c,
				applications: c.applications.map(a =>
					a.applicationId === applicationId
						? { ...a, currentStage: newStage, lastStageChange: new Date().toISOString() }
						: a
				),
				currentStage: c.applications[0]?.applicationId === applicationId ? newStage : c.currentStage,
			};
		});

		// 2. Appel API en arrière-plan
		try {
			const backendStatus = this._candidateStageToApplicationStatus(newStage);
			await recruitmentService.updateApplicationStatus(applicationId, backendStatus);
		} catch (error) {
			// Rollback si l'API échoue
			if (rollbackCandidateId && rollbackOldStage) {
				this.candidates = this.candidates.map((c) => {
					if (c.id !== rollbackCandidateId) return c;
					if (!c.applications) return c;
					return {
						...c,
						applications: c.applications.map(a =>
							a.applicationId === applicationId
								? { ...a, currentStage: rollbackOldStage!, lastStageChange: new Date().toISOString() }
								: a
						),
						currentStage: c.applications[0]?.applicationId === applicationId ? rollbackOldStage! : c.currentStage,
					};
				});
			}
			this.error =
				error instanceof Error ? error.message : 'Erreur lors de la mise à jour du statut';
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	/** Mapping inverse: CandidateStage → ApplicationStatus pour le backend */
	private _candidateStageToApplicationStatus(stage: CandidateStage): string {
		const map: Record<string, string> = {
			SCREENING: 'PENDING',
			SHORTLIST: 'REVIEW',
			INTERVIEW: 'INTERVIEW',
			OFFER: 'OFFER',
			ACCEPTED: 'ACCEPTED',
			REJECTED: 'REJECTED',
		};
		return map[stage] || 'PENDING';
	}

	async deleteCandidate(id: string) {
		this.isLoading = true;
		this.error = null;

		try {
			await recruitmentService.delete(id);
			this.candidates = this.candidates.filter((c) => c.id !== id);
			this.interviews = this.interviews.filter((i) => i.candidateId !== id);
			this.offers = this.offers.filter((o) => o.candidateId !== id);
		} catch (error) {
			this.error =
				error instanceof Error ? error.message : 'Erreur lors de la suppression du candidat';
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async createJobOffer(data: CreateJobOfferInput) {
		this.isLoading = true;
		this.error = null;

		try {
			const newOffer: JobOffer = {
				id: `o${Date.now()}`,
				status: 'DRAFT',
				startDate: data.startDate,
				candidateId: data.candidateId,
				positionId: data.positionId
			};

			this.offers = [...this.offers, newOffer];

			// Update candidate stage to OFFER
			await this.updateCandidateStage(data.candidateId, 'OFFER');

			return newOffer;
		} catch (error) {
			this.error = error instanceof Error ? error.message : "Erreur lors de la création de l'offre";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	// Filter methods

	toggleFilter(filterType: 'stage' | 'source' | 'priority' | 'positionId' | 'gender', value: string) {
		const currentFilters = (this.filters[filterType] ?? []) as string[];
		if (currentFilters.includes(value)) {
			(this.filters as any)[filterType] = currentFilters.filter(f => f !== value);
		} else {
			(this.filters as any)[filterType] = [...currentFilters, value];
		}
		this.candidateCurrentPage = 1;
	}

	resetFilters() {
		this.filters = {
			search: '',
			stage: [],
			source: [],
			priority: [],
			positionId: [],
			gender: []
		};
		this.candidateCurrentPage = 1;
	}

	togglePipelinePositionFilter(positionId: string) {
		const current = this.pipelinePositionIds;
		if (current.includes(positionId)) {
			this.pipelinePositionIds = current.filter(id => id !== positionId);
		} else {
			this.pipelinePositionIds = [...current, positionId];
		}
	}

	resetPipelinePositionFilter() {
		this.pipelinePositionIds = [];
	}

	toggleCampaignFilter(filterType: keyof typeof this.campaignFilters, value: string) {
		const currentFilters = this.campaignFilters[filterType];
		if (currentFilters.includes(value)) {
			this.campaignFilters[filterType] = currentFilters.filter(f => f !== value);
		} else {
			this.campaignFilters[filterType] = [...currentFilters, value];
		}
		this.currentPage = 1;
	}

	resetCampaignFilters() {
		this.campaignFilters = {
			status: [],
			jobNames: [],
			type: []
		};
		this.searchQuery = '';
		this.currentPage = 1;
	}

	setActiveCampaign(campaignId: string | null) {
		this.activeCampaignId = campaignId;
		this.currentCampaign = undefined;
	}

	async getCampaignDetailsById(campaignId: string) {
		this.isLoading = true;
		this.error = null;
		this.currentCampaign = undefined;
		try {
			const campaign = await recruitmentService.getJobOfferById(campaignId);
			this.currentCampaign = campaign;
			const index = this.campaigns.findIndex(c => c.id === campaign.id);
			if (index !== -1) {
				this.campaigns[index] = campaign;
			} else {
				this.campaigns.push(campaign);
			}
		} catch (error) {
			this.error = error instanceof Error ? error.message : "Erreur lors du chargement de la campagne";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	// Utility methods
	getStageTitle(stage: CandidateStage): string {
		const titles: Record<CandidateStage, string> = {
			SCREENING: 'Tri',
			SHORTLIST: 'Shortlist',
			INTERVIEW: 'Entretien',
			OFFER: 'Offre',
			ACCEPTED: 'Acceptée',
			REJECTED: 'Rejeté'
		};
		return titles[stage];
	}
}


export const recruitmentStore = new RecruitmentStore();
