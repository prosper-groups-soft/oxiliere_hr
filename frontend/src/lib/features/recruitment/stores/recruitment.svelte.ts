import type {
	Candidate,
	Interview,
	JobOffer,
	RecruitmentFilters,
	PipelineColumn,
	PipelineMetrics,
	CreateCandidateInput,
	UpdateCandidateInput,
	CreateInterviewInput,
	CreateJobOfferInput,
	CandidateStage,
	RecruitmentCampaign
} from '../types/types';
import { format, differenceInDays } from 'date-fns';

// Shared configuration of stages
export const stageConfig: Record<
	string,
	{
		label: string;
		color: string;
		bgColor: string;
		borderColor: string;
		icon: string;
	}
> = {
	SCREENING: {
		label: 'Tri',
		color: 'bg-blue-50 text-blue-700 border-blue-100',
		bgColor: 'bg-blue-50',
		borderColor: 'border-blue-200',
		icon: 'filter'
	},
	SHORTLIST: {
		label: 'Shortlist',
		color: 'bg-amber-50 text-amber-700 border-amber-100',
		bgColor: 'bg-amber-50',
		borderColor: 'border-amber-200',
		icon: 'star'
	},
	INTERVIEW: {
		label: 'Entretien',
		color: 'bg-purple-50 text-purple-700 border-purple-100',
		bgColor: 'bg-purple-50',
		borderColor: 'border-purple-200',
		icon: 'users'
	},
	OFFER: {
		label: 'Offre',
		color: 'bg-emerald-50 text-emerald-700 border-emerald-100',
		bgColor: 'bg-emerald-50',
		borderColor: 'border-emerald-200',
		icon: 'send'
	},
	REJECTED: {
		label: 'Rejeté',
		color: 'bg-red-50 text-red-700 border-red-100',
		bgColor: 'bg-red-50',
		borderColor: 'border-red-200',
		icon: 'x'
	}
};

// Mock Data
const MOCK_CAMPAIGNS: RecruitmentCampaign[] = [
	{
		id: 'camp_1',
		title: 'Développeur Frontend Senior',
		jobName: 'Ingénierie',
		location: 'Paris, France (Hybride)',
		type: 'FULL_TIME',
		status: 'OPEN',
		openDate: '2026-02-15',
		hiringManagerId: 'e2',
		hiringManagerName: 'Marie Martin',
		targetHires: 1,
		description: 'Nous recherchons un développeur Frontend Senior pour rejoindre notre équipe.',
		metrics: { totalCandidates: 2, inPipeline: 2, interviews: 1, offersSent: 0 }
	},
	{
		id: 'camp_2',
		title: 'Développeur Backend Node.js',
		jobName: 'Ingénierie',
		location: 'Lyon, France',
		type: 'FULL_TIME',
		status: 'OPEN',
		openDate: '2026-02-20',
		hiringManagerId: 'e1',
		hiringManagerName: 'Jean Dupont',
		targetHires: 2,
		description: 'Rejoignez notre équipe pour construire des APIs robustes.',
		metrics: { totalCandidates: 3, inPipeline: 2, interviews: 1, offersSent: 1 }
	}
];

const MOCK_CANDIDATES: Candidate[] = [
	{
		id: 'c1',
		firstName: 'Alice',
		lastName: 'Martin',
		email: 'alice.martin@email.com',
		phone: '0612345678',
		currentStage: 'SCREENING',
		priority: 'HIGH',
		source: 'LINKEDIN',
		appliedDate: '2026-03-01',
		lastStageChange: '2026-03-01',
		score: 85,
		positionId: 'p1',
		location: 'Paris, France',
		position: 'Développeur Frontend',
		experience: '5 ans',
		summary:
			'Développeur frontend passionnée avec une forte expertise en React et TypeScript. Autonome et curieuse, je cherche à rejoindre une équipe innovante.',
		skills: ['React', 'TypeScript', 'JavaScript', 'CSS', 'HTML', 'Git', 'Agile'],
		technicalScore: 90,
		experienceScore: 85,
		communicationScore: 80,
		cultureScore: 85,
		inPipeline: true,
		campaignId: 'camp_1'
	},
	{
		id: 'c2',
		firstName: 'Bob',
		lastName: 'Dupont',
		email: 'bob.dupont@email.com',
		phone: '0623456789',
		currentStage: 'SHORTLIST',
		priority: 'MEDIUM',
		source: 'CAREER_SITE',
		appliedDate: '2026-02-28',
		lastStageChange: '2026-03-02',
		score: 78,
		positionId: 'p2',
		location: 'Lyon, France',
		position: 'Développeur Backend',
		experience: '3 ans',
		summary:
			'Développeur backend spécialisé Node.js avec une bonne compréhension des architectures microservices.',
		skills: ['Node.js', 'Express', 'MongoDB', 'PostgreSQL', 'Docker', 'AWS', 'REST API'],
		technicalScore: 75,
		experienceScore: 70,
		communicationScore: 85,
		cultureScore: 80,
		inPipeline: true,
		campaignId: 'camp_2'
	},
	{
		id: 'c3',
		firstName: 'Claire',
		lastName: 'Durand',
		email: 'claire.durand@email.com',
		phone: '0634567890',
		currentStage: 'INTERVIEW',
		priority: 'HIGH',
		source: 'REFERRAL',
		appliedDate: '2026-02-25',
		lastStageChange: '2026-03-03',
		score: 92,
		positionId: 'p1',
		inPipeline: true,
		campaignId: 'camp_1'
	},
	{
		id: 'c4',
		firstName: 'David',
		lastName: 'Leroy',
		email: 'david.leroy@email.com',
		phone: '0645678901',
		currentStage: 'OFFER',
		priority: 'MEDIUM',
		source: 'DIRECT',
		appliedDate: '2026-02-20',
		lastStageChange: '2026-03-04',
		score: 88,
		positionId: 'p3',
		inPipeline: true,
		campaignId: 'camp_2'
	},
	{
		id: 'c5',
		firstName: 'Eva',
		lastName: 'Petit',
		email: 'eva.petit@email.com',
		phone: '0656789012',
		currentStage: 'REJECTED',
		priority: 'LOW',
		source: 'LINKEDIN',
		appliedDate: '2026-02-10',
		lastStageChange: '2026-02-15',
		score: 45,
		positionId: 'p2',
		inPipeline: false,
		campaignId: 'camp_2'
	}
];

const MOCK_INTERVIEWS: Interview[] = [
	{
		id: 'i1',
		candidateId: 'c1',
		interviewerId: 'e1',
		interviewer: 'Jean Dupont',
		type: 'PHONE',
		scheduledDate: '2026-03-05T10:00:00',
		duration: 30,
		status: 'COMPLETED',
		feedback: {
			rating: 4,
			strengths: ['Bonne communication', 'Solide technique'],
			weaknesses: ["Manque d'expérience en équipe"],
			notes: 'Bon candidat, à poursuivre',
			wouldHire: true,
			feedback:
				'Entretien téléphonique très positif. Alice démontre une bonne maîtrise des concepts frontend et une excellente communication.',
			nextSteps: "Proposer un entretien technique avec l'équipe"
		},
		description: 'Entretien téléphonique de présélection'
	},
	{
		id: 'i2',
		candidateId: 'c2',
		interviewerId: 'e2',
		interviewer: 'Marie Martin',
		type: 'TECHNICAL',
		scheduledDate: '2026-03-08T14:00:00',
		duration: 90,
		videoLink: 'https://meet.google.com/xyz789',
		status: 'SCHEDULED',
		description: 'Entretien technique backend avec exercices pratiques'
	},
	{
		id: 'i3',
		candidateId: 'c3',
		interviewerId: 'e1',
		interviewer: 'Jean Dupont',
		type: 'VIDEO',
		scheduledDate: '2026-03-10T14:00:00',
		duration: 60,
		videoLink: 'https://meet.google.com/abc123',
		status: 'SCHEDULED',
		description: 'Entretien comportemental et culture fit'
	}
];

const MOCK_OFFERS: JobOffer[] = [
	{
		id: 'o1',
		candidateId: 'c4',
		positionId: 'p3',
		salary: {
			min: 45000,
			max: 55000,
			currency: 'EUR'
		},
		startDate: '2026-04-01',
		status: 'SENT',
		sentDate: '2026-03-05'
	}
];


class RecruitmentStore {
	campaigns = $state<RecruitmentCampaign[]>([]);
	activeCampaignId = $state<string | null>(null);

	candidates = $state<Candidate[]>([]);
	interviews = $state<Interview[]>([]);
	offers = $state<JobOffer[]>([]);
	filters = $state<RecruitmentFilters>({
		search: '',
		stage: [],
		source: [],
		priority: []
	});
	isLoading = $state(false);
	error = $state<string | null>(null);

	// Campaign-specific state
	searchQuery = $state('');
	campaignFilters = $state<{
		status: string[];
		jobName: string[];
		type: string[];
	}>({
		status: [],
		jobName: [],
		type: []
	});
	sortBy = $state('title');
	sortOrder = $state<'asc' | 'desc'>('asc');
	currentPage = $state(1);
	perPage = $state(8);

	constructor() {
		this.initializeMockData();
	}

	private initializeMockData() {
		this.campaigns = [...MOCK_CAMPAIGNS];
		this.candidates = [...MOCK_CANDIDATES];
		this.interviews = [...MOCK_INTERVIEWS];
		this.offers = [...MOCK_OFFERS];
	}

	// Getters
	get filteredCampaigns(): RecruitmentCampaign[] {
		let filtered = [...this.campaigns];

		// Filter by search query
		if (this.searchQuery) {
			const search = this.searchQuery.toLowerCase();
			filtered = filtered.filter((campaign) =>
				campaign.title.toLowerCase().includes(search) ||
				campaign.jobName.toLowerCase().includes(search) ||
				campaign.location.toLowerCase().includes(search)
			);
		}

		// Filter by status
		if (this.campaignFilters.status.length > 0) {
			filtered = filtered.filter((campaign) =>
				this.campaignFilters.status.includes(campaign.status)
			);
		}

		// Filter by jobName
		if (this.campaignFilters.jobName.length > 0) {
			filtered = filtered.filter((campaign) =>
				this.campaignFilters.jobName.includes(campaign.jobName)
			);
		}

		// Filter by type
		if (this.campaignFilters.type.length > 0) {
			filtered = filtered.filter((campaign) =>
				this.campaignFilters.type.includes(campaign.type)
			);
		}

		// Sort campaigns
		filtered.sort((a, b) => {
			let aValue: any = a[this.sortBy as keyof RecruitmentCampaign];
			let bValue: any = b[this.sortBy as keyof RecruitmentCampaign];

			if (typeof aValue === 'string') {
				aValue = aValue.toLowerCase();
				bValue = bValue.toLowerCase();
			}

			if (this.sortOrder === 'asc') {
				return aValue > bValue ? 1 : -1;
			} else {
				return aValue < bValue ? 1 : -1;
			}
		});

		return filtered;
	}

	get paginatedCampaigns(): RecruitmentCampaign[] {
		const startIndex = (this.currentPage - 1) * this.perPage;
		const endIndex = startIndex + this.perPage;
		return this.filteredCampaigns.slice(startIndex, endIndex);
	}

	get totalCount(): number {
		return this.filteredCampaigns.length;
	}

	get totalPages(): number {
		return Math.ceil(this.totalCount / this.perPage);
	}

	get activeFiltersCount(): number {
		return (
			(this.searchQuery ? 1 : 0) +
			this.campaignFilters.status.length +
			this.campaignFilters.jobName.length +
			this.campaignFilters.type.length
		);
	}

	get activeCandidateFiltersCount(): number {
		return (
			(this.filters.search ? 1 : 0) +
			(this.filters.stage?.length || 0) +
			(this.filters.source?.length || 0) +
			(this.filters.priority?.length || 0) +
			(this.filters.positionId?.length || 0)
		);
	}
  
	get filteredCandidates(): Candidate[] {
		let filtered = [...this.candidates];

		// Filter by active campaign if set
		if (this.activeCampaignId) {
			filtered = filtered.filter((c: Candidate) => c.campaignId === this.activeCampaignId);
		}

		// Filter by stage
		if (this.filters.stage && this.filters.stage.length > 0) {
			filtered = filtered.filter((c: Candidate) => this.filters.stage!.includes(c.currentStage));
		}

		// Filter by source
		if (this.filters.source && this.filters.source.length > 0) {
			filtered = filtered.filter((c: Candidate) => this.filters.source!.includes(c.source));
		}

		// Filter by priority
		if (this.filters.priority && this.filters.priority.length > 0) {
			filtered = filtered.filter((c: Candidate) => this.filters.priority!.includes(c.priority));
		}

		// Filter by search
		if (this.filters.search) {
			const search = this.filters.search.toLowerCase();
			filtered = filtered.filter(
				(c: Candidate) =>
					c.firstName.toLowerCase().includes(search) ||
					c.lastName.toLowerCase().includes(search) ||
					c.email.toLowerCase().includes(search)
			);
		}

		// Filter by position
		if (this.filters.positionId && this.filters.positionId.length > 0) {
			filtered = filtered.filter(
				(c: Candidate) => c.positionId && this.filters.positionId!.includes(c.positionId)
			);
		}

		return filtered;
	}

	get pipelineData(): PipelineColumn[] {
		const stages: CandidateStage[] = ['SCREENING', 'SHORTLIST', 'INTERVIEW', 'OFFER'];

		return stages.map((stage) => ({
			stage,
			title: this.getStageTitle(stage),
			candidates: this.filteredCandidates.filter(
				(c: Candidate) => c.currentStage === stage && c.inPipeline !== false
			)
		}));
	}

	get metrics(): PipelineMetrics {
		const candidates = this.filteredCandidates;
		const totalCandidates = candidates.length;

		const stageCounts: Record<CandidateStage, number> = {
			SCREENING: 0,
			SHORTLIST: 0,
			INTERVIEW: 0,
			OFFER: 0,
			REJECTED: 0
		};

		const averageTimeInStage: Record<CandidateStage, number> = {
			SCREENING: 0,
			SHORTLIST: 0,
			INTERVIEW: 0,
			OFFER: 0,
			REJECTED: 0
		};

		// Calculate stage counts and average times
		candidates.forEach((candidate: Candidate) => {
			stageCounts[candidate.currentStage]++;

			const daysInStage = differenceInDays(new Date(), new Date(candidate.lastStageChange));
			averageTimeInStage[candidate.currentStage] += daysInStage;
		});

		// Calculate averages
		Object.keys(averageTimeInStage).forEach((stage) => {
			const count = stageCounts[stage as CandidateStage];
			averageTimeInStage[stage as CandidateStage] =
				count > 0 ? Math.round(averageTimeInStage[stage as CandidateStage] / count) : 0;
		});

		return {
			totalCandidates,
			stageCounts,
			averageTimeInStage
		};
	}

	// Actions
	async addCandidate(data: CreateCandidateInput) {
		this.isLoading = true;
		this.error = null;

		try {
			const newCandidate: Candidate = {
				id: `c${Date.now()}`,
				currentStage: 'SCREENING',
				priority: 'MEDIUM',
				appliedDate: format(new Date(), 'yyyy-MM-dd'),
				lastStageChange: format(new Date(), 'yyyy-MM-dd'),
				...data,
				campaignId: this.activeCampaignId || data.campaignId // Ensure it uses active campaign or the one provided
			};

			this.candidates = [...this.candidates, newCandidate];
			return newCandidate;
		} catch (error) {
			this.error = error instanceof Error ? error.message : "Erreur lors de l'ajout du candidat";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async updateCandidate(id: string, data: UpdateCandidateInput) {
		this.isLoading = true;
		this.error = null;

		try {
			this.candidates = this.candidates.map((c) => (c.id === id ? { ...c, ...data } : c));
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
			this.candidates = this.candidates.map((c) =>
				c.id === candidateId
					? {
							...c,
							currentStage: newStage,
							lastStageChange: format(new Date(), 'yyyy-MM-dd')
						}
					: c
			);
		} catch (error) {
			this.error =
				error instanceof Error ? error.message : 'Erreur lors de la mise à jour du statut';
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async deleteCandidate(id: string) {
		this.isLoading = true;
		this.error = null;

		try {
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

	async addToPipeline(candidateId: string) {
		this.isLoading = true;
		this.error = null;

		try {
			this.candidates = this.candidates.map((c) =>
				c.id === candidateId
					? {
							...c,
							inPipeline: true,
							currentStage: 'SCREENING',
							lastStageChange: format(new Date(), 'yyyy-MM-dd')
						}
					: c
			);
		} catch (error) {
			this.error = error instanceof Error ? error.message : "Erreur lors de l'ajout au pipeline";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async removeFromPipeline(candidateId: string) {
		this.isLoading = true;
		this.error = null;

		try {
			this.candidates = this.candidates.map((c) =>
				c.id === candidateId
					? {
							...c,
							inPipeline: false,
							currentStage: 'REJECTED',
							lastStageChange: format(new Date(), 'yyyy-MM-dd')
						}
					: c
			);
		} catch (error) {
			this.error = error instanceof Error ? error.message : 'Erreur lors du retrait du pipeline';
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async scheduleInterview(data: CreateInterviewInput) {
		this.isLoading = true;
		this.error = null;

		try {
			const newInterview: Interview = {
				id: `i${Date.now()}`,
				status: 'SCHEDULED',
				...data
			};

			this.interviews = [...this.interviews, newInterview];
			return newInterview;
		} catch (error) {
			this.error =
				error instanceof Error ? error.message : "Erreur lors de la programmation de l'entretien";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async updateInterview(id: string, data: Partial<Interview>) {
		this.isLoading = true;
		this.error = null;

		try {
			this.interviews = this.interviews.map((i) => (i.id === id ? { ...i, ...data } : i));
		} catch (error) {
			this.error =
				error instanceof Error ? error.message : "Erreur lors de la mise à jour de l'entretien";
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
				salary: {
					min: data.salaryMin,
					max: data.salaryMax,
					currency: data.currency
				},
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
	setFilters(filters: Partial<RecruitmentFilters>) {
		this.filters = { ...this.filters, ...filters };
	}

	toggleFilter(key: keyof RecruitmentFilters, value: any) {
		const currentValues = (this.filters[key] as any[]) || [];
		if (currentValues.includes(value)) {
			(this.filters as any)[key] = currentValues.filter((v: any) => v !== value);
		} else {
			(this.filters as any)[key] = [...currentValues, value];
		}
	}

	resetFilters() {
		this.filters = {
			search: '',
			stage: [],
			source: [],
			priority: [],
			positionId: []
		};
	}

	// Utility methods
	private getStageTitle(stage: CandidateStage): string {
		const titles: Record<CandidateStage, string> = {
			SCREENING: 'Tri',
			SHORTLIST: 'Shortlist',
			INTERVIEW: 'Entretien',
			OFFER: 'Offre',
			REJECTED: 'Rejeté'
		};
		return titles[stage];
	}

	getCandidateById(id: string): Candidate | undefined {
		return this.candidates.find((c) => c.id === id);
	}

	getCampaignById(id: string): RecruitmentCampaign | undefined {
		return this.campaigns.find((c) => c.id === id);
	}

	// Campaign-specific actions
	async addCampaign(data: Partial<RecruitmentCampaign>) {
		this.isLoading = true;
		try {
			const newCampaign: RecruitmentCampaign = {
				id: `camp_${Date.now()}`,
				title: data.title || 'Nouvelle Campagne',
				jobName: data.jobName || '',
				location: data.location || '',
				type: data.type || 'FULL_TIME',
				status: 'DRAFT',
				openDate: format(new Date(), 'yyyy-MM-dd'),
				hiringManagerId: data.hiringManagerId || '',
				hiringManagerName: data.hiringManagerName || '',
				targetHires: data.targetHires || 1,
				description: data.description || '',
				metrics: { totalCandidates: 0, inPipeline: 0, interviews: 0, offersSent: 0 },
				...data
			};
			this.campaigns = [newCampaign, ...this.campaigns];
			return newCampaign;
		} catch (error) {
			this.error = "Erreur lors de l'ajout de la campagne";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async updateCampaign(id: string, data: Partial<RecruitmentCampaign>) {
		this.isLoading = true;
		try {
			this.campaigns = this.campaigns.map(c => c.id === id ? { ...c, ...data } : c);
		} catch (error) {
			this.error = "Erreur lors de la mise à jour de la campagne";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	async deleteCampaign(id: string) {
		this.isLoading = true;
		try {
			this.campaigns = this.campaigns.filter(c => c.id !== id);
			// Also cleanup candidates/interviews related to this campaign
			this.candidates = this.candidates.filter(c => c.campaignId !== id);
		} catch (error) {
			this.error = "Erreur lors de la suppression de la campagne";
			throw error;
		} finally {
			this.isLoading = false;
		}
	}

	setSearchQuery(query: string) {
		this.searchQuery = query;
		this.currentPage = 1; // Reset to first page when searching
	}

	setCampaignFilters(filters: Partial<typeof this.campaignFilters>) {
		this.campaignFilters = { ...this.campaignFilters, ...filters };
		this.currentPage = 1; // Reset to first page when filtering
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
			jobName: [],
			type: []
		};
		this.searchQuery = '';
		this.currentPage = 1;
	}

	setSort(sortBy: string) {
		this.sortBy = sortBy;
	}

	toggleSortOrder() {
		this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
	}

	setPage(page: number) {
		this.currentPage = page;
	}

	setPerPage(perPage: number) {
		this.perPage = perPage;
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

	setActiveCampaign(campaignId: string | null) {
		this.activeCampaignId = campaignId;
	}

	get activeCampaign(): RecruitmentCampaign | undefined {
		if (!this.activeCampaignId) return undefined;
		return this.getCampaignById(this.activeCampaignId);
	}

	getInterviewsByCandidate(candidateId: string): Interview[] {
		return this.interviews.filter((i) => i.candidateId === candidateId);
	}

	getOfferByCandidate(candidateId: string): JobOffer | undefined {
		return this.offers.find((o) => o.candidateId === candidateId);
	}
}


export const recruitmentStore = new RecruitmentStore();
