import APIEndPoint from '@/hr/utilities/http/rest';
import type { PaginatedResponse } from '@/hr/utilities/common/types';


// Types backend (à aligner avec les schemas backend)
interface JobOfferOut {
	id: string;
	title: string;
	slug: string;
	location: string;
	description: string;
	requirements: string;
	published_at: string | null;
	end_date: string | null;
	slots: number;
	position_slots: Record<string, number>;
	max_applications: number | null;
	status: string;
	position_names: string[] | null;
	target_position_ids: string[] | null;
	vacancy_ids: string[] | null;
	vacancies?: Array<{
		id: string;
		position_id: string;
		position_name: string;
		slots: number;
	}>;
	total_candidates: number;
	in_pipeline: number;
	interviews_count: number;
	offers_sent: number;
	recruiter_id: string | null;
	recruiter_name: string | null;
}

export interface JobOfferCreateIn {
	title: string;
	target_position_ids: string[];
	position_slots?: Record<string, number>;
	vacancy_ids?: string[];
	recruiter_id?: string;
	description: string;
	requirements: string;
	location: string;
	end_date?: string;
	status?: string;
	is_published?: boolean;
	is_active?: boolean;
	published_at?: string;
	slots?: number;
	max_applications?: number | null;
	evaluation_template?: Record<string, any[]>;
}

export interface JobOfferUpdate {
	title?: string;
	target_position_ids?: string[];
	position_slots?: Record<string, number>;
	vacancy_ids?: string[];
	recruiter_id?: string;
	description?: string;
	requirements?: string;
	location?: string;
	end_date?: string;
	status?: string;
	is_published?: boolean;
	is_active?: boolean;
	published_at?: string;
	slots?: number;
	max_applications?: number | null;
	evaluation_template?: Record<string, any[]>;
}

interface ApplicationOut {
	id: number;
	status: string;
	applied_at: string;
	resume: string | null;
	cover_letter: string | null;
	priority: string;
	target_position_id: string | null;
	target_position_name: string | null;
	candidate: {
		id: number;
		first_name: string;
		middle_name: string;
		last_name: string;
		email: string;
		phone: string | null;
		linkedin_profile: string | null;
	};
	job_offer_title: string;
}

interface ApplicationBriefOut {
	id: number;
	status: string;
	priority: string;
	target_position_id: string | null;
	target_position_name: string | null;
	job_offer_id: string | null;
	scores: Record<string, number> | null;
	evaluation_notes: string | null;
	salary_min: number | null;
	salary_max: number | null;
	salary_currency: string | null;
	offer_start_date: string | null;
	applied_at: string;
	cover_letter: string | null;
	resume: string | null;
}

interface CandidateWithApplicationsOut {
	id: number;
	first_name: string;
	middle_name: string;
	last_name: string;
	email: string;
	phone: string | null;
	avatar_url: string | null;
	linkedin_profile: string | null;
	source: string;
	priority: string;
	location: string | null;
	position: string | null;
	experience: string | null;
	summary: string | null;
	skills: string[];
	applications: ApplicationBriefOut[];
}

interface InterviewOut {
	id: number;
	application_id: string;
	candidate_id: string;
	candidate_name: string | null;
	position_name: string | null;
	interviewer_id: string;
	interview_type: string;
	scheduled_at: string;
	duration_minutes: number;
	score: number | null;
	notes: string | null;
	interviewer_name: string;
	location: string | null;
	video_link: string | null;
	status: string;
}

interface InterviewScheduleIn {
	application_id: string;
	interviewer_id: string;
	scheduled_at: string;
	interview_type: string;
	duration_minutes: number;
	location?: string;
	notes?: string;
}

interface InterviewFeedbackIn {
	score: number;
	feedback?: string;
	strengths?: string[];
	weaknesses?: string[];
	would_hire?: boolean;
	next_steps?: string;
	status?: string;
}

interface InterviewUpdateIn {
	interviewer_id?: string;
	scheduled_at?: string;
	interview_type?: string;
	duration_minutes?: number;
	notes?: string;
	location?: string;
	video_link?: string;
	status?: string;
}

// Types pour positions et unités organisationnelles
interface PositionOut {
	id: string;
	name: string;
	description: string | null;
	requirements: string[];
	skills: { name: string; level: number }[];
	job_family: {
		id: string;
		name: string;
	};
	org_unit: {
		id: string;
		name: string;
	} | null;
}

interface OrgUnitOut {
	id: string;
	name: string;
	type: string;
}

/**
 * Endpoints API pour la gestion du recrutement
 * Base path: /api/recruitment
 */
export const recruitmentEndpoint = {
	// ==========================================
	// JOB OFFERS
	// ==========================================

	/**
	 * GET /api/recruitment/offers
	 * Liste toutes les offres d'emploi avec pagination
	 */
	listJobOffers: async (params?: {
		page?: number;
		limit?: number;
		org_unit_id?: number;
		is_active?: boolean;
		search?: string;
		status?: string;
		job_names?: string[];
		sort_by?: string;
		sort_order?: string;
	}): Promise<PaginatedResponse<JobOfferOut>> => {
		const queryParams = new URLSearchParams();
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.limit) queryParams.set('limit', params.limit.toString());
		if (params?.org_unit_id) queryParams.set('org_unit_id', params.org_unit_id.toString());
		if (params?.is_active !== undefined) queryParams.set('is_active', params.is_active.toString());
		if (params?.search) queryParams.set('search', params.search);
		if (params?.status) queryParams.set('status', params.status);
		if (params?.sort_by) queryParams.set('sort_by', params.sort_by);
		if (params?.sort_order) queryParams.set('sort_order', params.sort_order);
		if (params?.job_names && params.job_names.length > 0) {
			params.job_names.forEach(jobName => queryParams.append('job_names', jobName));
		}

		const queryString = queryParams.toString();
		const url = queryString ? `/api/recruitment/offers/?${queryString}` : '/api/recruitment/offers/';

		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	/**
	 * POST /api/recruitment/offers
	 * Crée une nouvelle offre d'emploi
	 */
	createJobOffer: async (data: JobOfferCreateIn): Promise<JobOfferOut> => {
		const endpoint = new APIEndPoint('/api/recruitment/offers/', '/api/recruitment/offers/');
		return await endpoint.create(data);
	},

	/**
	 * GET /api/recruitment/offers/{offer_id}
	 * Récupère les détails d'une offre d'emploi
	 */
	getJobOffer: async (offerId: string): Promise<JobOfferOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/offers/${offerId}`,
			`/api/recruitment/offers/${offerId}`
		);
		return await endpoint.retrieve();
	},

	/**
	 * PATCH /api/recruitment/offers/{offer_id}/publish
	 * Publie une offre d'emploi
	 */
	publishJobOffer: async (offerId: string): Promise<JobOfferOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/offers/${offerId}/publish`,
			`/api/recruitment/offers/${offerId}/publish`
		);
		return await endpoint.partial_update({});
	},

	/**
	 * PATCH /api/recruitment/offers/{offer_id}/close
	 * Ferme une offre d'emploi
	 */
	closeJobOffer: async (offerId: string): Promise<JobOfferOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/offers/${offerId}/close`,
			`/api/recruitment/offers/${offerId}/close`
		);
		return await endpoint.partial_update({});
	},

	/**
	 * PATCH /api/recruitment/offers/{offer_id}/
	 * Met à jour une offre d'emploi existante
	 */
	updateJobOffer: async (offerId: string, data: Partial<JobOfferCreateIn>): Promise<JobOfferOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/offers/${offerId}`,
			`/api/recruitment/offers/${offerId}`
		);
		return await endpoint.partial_update(data);
	},

	// ==========================================
	// APPLICATIONS
	// ==========================================

	/**
	 * GET /api/recruitment/applications
	 * Liste toutes les candidatures avec pagination
	 * Nécessite toujours l'offer_id pour filtrer par campagne
	 */
	listApplications: async (params: {
		offer_id: string;
		page?: number;
		limit?: number;
		search?: string;
		status?: string[];
		source?: string[];
		priority?: string[];
		position_id?: string[];
	}): Promise<PaginatedResponse<ApplicationOut>> => {
		const queryParams = new URLSearchParams();
		queryParams.set('offer_id', params.offer_id.toString());
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.limit) queryParams.set('limit', params.limit.toString());
		if (params?.search) queryParams.set('search', params.search);
		if (params?.status?.length) params.status.forEach(s => queryParams.append('status', s));
		if (params?.source?.length) params.source.forEach(s => queryParams.append('source', s));
		if (params?.priority?.length) params.priority.forEach(s => queryParams.append('priority', s));
		if (params?.position_id?.length) params.position_id.forEach(s => queryParams.append('position_id', s));

		const queryString = queryParams.toString();
		const url = queryString ? `/api/recruitment/applications/?${queryString}` : '/api/recruitment/applications/';

		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	/**
	 * GET /api/recruitment/applications/{application_id}
	 * Récupère les détails d'une candidature
	 */
	getApplication: async (applicationId: string): Promise<ApplicationOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/applications/${applicationId}`,
			`/api/recruitment/applications/${applicationId}`
		);
		return await endpoint.retrieve();
	},

	/**
	 * PATCH /api/recruitment/applications/{application_id}
	 * Met à jour les métadonnées d'une candidature (priorité, ...)
	 */
	updateApplication: async (applicationId: string, data: { priority?: string }): Promise<ApplicationOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/applications/${applicationId}`,
			`/api/recruitment/applications/${applicationId}`
		);
		return await endpoint.partial_update(data);
	},

	/**
	 * PATCH /api/recruitment/applications/{application_id}/status
	 * Met à jour le statut d'une candidature
	 */
	updateApplicationStatus: async (applicationId: string, newStatus: string): Promise<ApplicationOut> => {
		const url = `/api/recruitment/applications/${applicationId}/status?new_status=${encodeURIComponent(newStatus)}`;
		const endpoint = new APIEndPoint(url, url);
		return await endpoint.partial_update();
	},

	/**
	 * GET /api/recruitment/applications/candidates
	 * Liste les candidats groupés avec leurs applications (paginé par candidat)
	 */
	listCandidatesWithApplications: async (params: {
		offer_id: string;
		page?: number;
		limit?: number;
		search?: string;
		status?: string[];
		source?: string[];
		priority?: string[];
		position_id?: string[];
		gender?: string[];
	}): Promise<PaginatedResponse<CandidateWithApplicationsOut>> => {
		const queryParams = new URLSearchParams();
		queryParams.set('offer_id', params.offer_id.toString());
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.limit) queryParams.set('limit', params.limit.toString());
		if (params?.search) queryParams.set('search', params.search);
		if (params?.status?.length) params.status.forEach(s => queryParams.append('status', s));
		if (params?.source?.length) params.source.forEach(s => queryParams.append('source', s));
		if (params?.priority?.length) params.priority.forEach(s => queryParams.append('priority', s));
		if (params?.position_id?.length) params.position_id.forEach(s => queryParams.append('position_id', s));
		if (params?.gender?.length) params.gender.forEach(s => queryParams.append('gender', s));

		const queryString = queryParams.toString();
		const url = queryString ? `/api/recruitment/applications/candidates?${queryString}` : '/api/recruitment/applications/candidates';

		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	/**
	 * POST /api/recruitment/applications/{offer_id}/apply
	 * Soumet une nouvelle candidature pour une offre
	 */
	submitApplication: async (offerId: string, data: Record<string, any>, resumeFile?: File): Promise<ApplicationOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/applications/${offerId}/apply`,
			`/api/recruitment/applications/${offerId}/apply`
		);
		const formData = new FormData();
		Object.entries(data).forEach(([key, value]) => {
			if (value !== undefined && value !== null && value !== '') {
				if (Array.isArray(value)) {
					value.forEach(item => {
						formData.append(key, String(item));
					});
				} else if (typeof value === 'object') {
					formData.append(key, JSON.stringify(value));
				} else {
					formData.append(key, String(value));
				}
			}
		});
		if (resumeFile) {
			formData.append('resume', resumeFile);
		}
		return await endpoint.create(formData);
	},

	// ==========================================
	// CANDIDATE PROFILE (standalone, not via application)
	// ==========================================

	/**
	 * PATCH /api/recruitment/candidates/{candidate_id}
	 * Met à jour le profil d'un candidat
	 */
	updateCandidateProfile: async (candidateId: string, data: Record<string, any>): Promise<any> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/candidates/${candidateId}`,
			`/api/recruitment/candidates/${candidateId}`
		);
		return await endpoint.partial_update(data);
	},

	/**
	 * PATCH /api/recruitment/candidates/{candidate_id}/sync-applications
	 * Synchronise les applications d'un candidat (positions, priorités)
	 */
	/**
	 * PATCH /api/recruitment/applications/{application_id}/evaluation
	 * Met à jour les scores d'évaluation d'une candidature
	 */
	updateApplicationEvaluation: async (applicationId: string, data: Record<string, any>): Promise<any> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/applications/${applicationId}/evaluation`,
			`/api/recruitment/applications/${applicationId}/evaluation`
		);
		return await endpoint.partial_update(data);
	},

	/**
	 * PATCH /api/recruitment/applications/{application_id}/offer
	 * Met à jour les détails de l'offre d'une candidature
	 */
	updateApplicationOffer: async (applicationId: string, data: Record<string, any>): Promise<any> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/applications/${applicationId}/offer`,
			`/api/recruitment/applications/${applicationId}/offer`
		);
		return await endpoint.partial_update(data);
	},

	syncCandidateApplications: async (candidateId: string, offerId: string, positionIds: string[], positionPriorities?: Record<string, string>): Promise<any> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/candidates/${candidateId}/sync-applications`,
			`/api/recruitment/candidates/${candidateId}/sync-applications`
		);
		return await endpoint.partial_update({
			offer_id: offerId,
			position_ids: positionIds,
			position_priorities: positionPriorities || {},
		});
	},

	/**
	 * POST /api/recruitment/candidates/{candidate_id}/upload-resume
	 * Upload ou remplace le CV d'un candidat
	 */
	uploadCandidateResume: async (candidateId: string, file: File): Promise<any> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/candidates/${candidateId}/upload-resume`,
			`/api/recruitment/candidates/${candidateId}/upload-resume`
		);
		const formData = new FormData();
		formData.append('resume', file);
		return await endpoint.create(formData);
	},

	/**
	 * POST /api/recruitment/candidates/{candidate_id}/upload-photo
	 * Upload de la photo de profil
	 */
	uploadCandidatePhoto: async (candidateId: string, file: File): Promise<any> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/candidates/${candidateId}/upload-photo`,
			`/api/recruitment/candidates/${candidateId}/upload-photo`
		);
		const formData = new FormData();
		formData.append('file', file);
		return await endpoint.create(formData);
	},

	// ==========================================
	// INTERVIEWS
	// ==========================================

	/**
	 * GET /api/recruitment/interviews
	 * Liste les entretiens avec pagination, optionnellement filtrés par candidate_id
	 */
	listInterviews: async (params?: {
		page?: number;
		limit?: number;
		candidate_id?: string;
		application_id?: string;
		offer_id?: string;
	}): Promise<PaginatedResponse<InterviewOut>> => {
		const queryParams = new URLSearchParams();
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.limit) queryParams.set('limit', params.limit.toString());
		if (params?.candidate_id) queryParams.set('candidate_id', params.candidate_id);
		if (params?.application_id) queryParams.set('application_id', params.application_id);
		if (params?.offer_id) queryParams.set('offer_id', params.offer_id);

		const queryString = queryParams.toString();
		const url = queryString ? `/api/recruitment/interviews/?${queryString}` : '/api/recruitment/interviews/';

		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	/**
	 * POST /api/recruitment/interviews
	 * Planifie un nouvel entretien
	 */
	scheduleInterview: async (data: InterviewScheduleIn): Promise<InterviewOut> => {
		const endpoint = new APIEndPoint('/api/recruitment/interviews/', '/api/recruitment/interviews/');
		return await endpoint.create(data);
	},

	/**
	 * PATCH /api/recruitment/interviews/{interview_id}/feedback
	 * Soumet le feedback d'un entretien
	 */
	submitInterviewFeedback: async (interviewId: string, data: InterviewFeedbackIn): Promise<InterviewOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/interviews/${interviewId}/feedback`,
			`/api/recruitment/interviews/${interviewId}/feedback`
		);
		return await endpoint.partial_update(data);
	},

	/**
	 * PATCH /api/recruitment/interviews/{interview_id}
	 * Met à jour les champs modifiables d'un entretien
	 */
	updateInterview: async (interviewId: string, data: InterviewUpdateIn): Promise<InterviewOut> => {
		const endpoint = new APIEndPoint(
			`/api/recruitment/interviews/${interviewId}`,
			`/api/recruitment/interviews/${interviewId}`
		);
		return await endpoint.partial_update(data);
	},

	// ==========================================
	// POSITIONS & ORG UNITS (pour dropdowns)
	// ==========================================

	/**
	 * GET /api/jobs/positions
	 * Liste toutes les positions pour les dropdowns
	 */
	listPositions: async (): Promise<PositionOut[]> => {
		const endpoint = new APIEndPoint('/api/jobs/positions', '/api/jobs/positions');
		return await endpoint.list();
	},

	/**
	 * GET /api/organization/units
	 * Liste toutes les unités organisationnelles pour les dropdowns
	 */
	listOrgUnits: async (): Promise<OrgUnitOut[]> => {
		const endpoint = new APIEndPoint('/api/organization/units', '/api/organization/units');
		return await endpoint.list();
	},
};
