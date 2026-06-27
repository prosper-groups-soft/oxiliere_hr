import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { recruitmentEndpoint } from '../api/recruitment.endpoints';
import type {
	Candidate, CandidateApplication, CandidateStage, Interview, InterviewStatus, 
	JobOffer, CreateCandidateInput, UpdateCandidateInput, CreateInterviewInput, 
	CreateJobOfferInput, RecruitmentCampaign, RecruitmentPosition, RecruitmentVacancy
} from '../types/types';
import type { JobOfferUpdate } from '../api/recruitment.endpoints';
import { mapApplicationStatusToCandidateStage } from '../constants/recruitment';


/**
 * Normalise les données PositionOut du backend vers RecruitmentPosition frontend
 */
function mapPositionToFrontend(pos: any): RecruitmentPosition {
	return {
		id: pos.id,
		name: pos.name,
		description: pos.description || undefined,
		requirements: pos.requirements || [],
		skills: pos.skills || [],
		jobFamily: pos.job_family ? { id: pos.job_family.id, name: pos.job_family.name } : undefined,
		orgUnit: pos.org_unit ? { id: pos.org_unit.id, name: pos.org_unit.name } : undefined
	};
}

/**
 * Normalise les données Vacancy du backend vers RecruitmentVacancy frontend
 */
function mapVacancyToFrontend(vacancy: any): RecruitmentVacancy {
	return {
		id: vacancy.id,
		positionId: vacancy.position_id || null,
		positionName: vacancy.position_name || null,
		slots: vacancy.slots || 1,
		priority: vacancy.priority || undefined,
		status: vacancy.status || undefined,
		openedDate: vacancy.opened_date || undefined,
		targetDate: vacancy.target_date || undefined,
		filledDate: vacancy.filled_date || null,
		reason: vacancy.reason || null
	};
}

/**
 * Normalise les données JobOffer du backend vers RecruitmentCampaign du frontend
 */
function mapJobOfferToCampaign(jobOffer: any, positions: RecruitmentPosition[] = []): RecruitmentCampaign {
	const positionNameMap: Record<string, string> = {};
	positions.forEach((p) => {
		positionNameMap[p.id] = p.name;
	});
	
	const vacancies = jobOffer.vacancies 
		? jobOffer.vacancies.map(mapVacancyToFrontend)
		: undefined;
	
	return {
		id: jobOffer.id,
		title: jobOffer.title,
		slug: jobOffer.slug || undefined,
		jobNames: jobOffer.position_names || [],
		jobIds: jobOffer.target_position_ids || [],
		positionSlots: jobOffer.position_slots || undefined,
		positionNameMap: Object.keys(positionNameMap).length > 0 ? positionNameMap : undefined,
		positions: positions.length > 0 ? positions : undefined,
		location: jobOffer.location || '',
		status: jobOffer.status || (jobOffer.is_published ? 'OPEN' : 'DRAFT'),
		openDate: jobOffer.published_at || undefined,
		closeDate: jobOffer.end_date || undefined,
		hiringManagerId: jobOffer.recruiter_id || '',
		hiringManagerName: jobOffer.recruiter_name || 'Non assigné',
		targetHires: jobOffer.slots || 1,
		description: jobOffer.description,
		requirements: Array.isArray(jobOffer.requirements) 
			? jobOffer.requirements 
			: (jobOffer.requirements ? [jobOffer.requirements] : []),
		isPublished: jobOffer.is_published || false,
		isActive: jobOffer.is_active !== undefined ? jobOffer.is_active : true,
		maxApplications: jobOffer.max_applications || undefined,
		vacancyIds: jobOffer.vacancy_ids || [],
		vacancies: vacancies,
		evaluationTemplate: jobOffer.evaluation_template || undefined,
		metrics: {
			totalCandidates: jobOffer.total_candidates || 0,
			inPipeline: jobOffer.in_pipeline || 0,
			interviews: jobOffer.interviews_count || 0,
			offersSent: jobOffer.offers_sent || 0,
			offersMade: jobOffer.offers_made || 0
		}
	};
}

/**
 * Normalise les données Application du backend vers Candidate du frontend
 */
function mapApplicationToCandidate(application: any): Candidate {
	const c = application.candidate;
	const stage = mapApplicationStatusToCandidateStage(application.status) as CandidateStage;
	
	// Build candidate profile (first application or update)
	const candidate: Candidate = {
		id: c.id.toString(),
		firstName: c.first_name,
		middleName: c.middle_name || '',
		lastName: c.last_name,
		email: c.email,
		phone: c.phone || '',
		avatarUrl: c.avatar_url || undefined,
		linkedinUrl: c.linkedin_profile || undefined,
		currentStage: stage,
		priority: application.priority || 'MEDIUM',
		source: c.source || 'DIRECT',
		gender: c.gender || 'NOT_SPECIFIED',
		appliedDate: application.applied_at,
		lastStageChange: application.applied_at,
		score: c.technical_score ?? undefined,
		resumeUrl: c.resume || undefined,
		notes: c.notes || application.cover_letter || c.summary || undefined,
		positionId: application.target_position_id || undefined,
		targetPositionName: application.target_position_name || undefined,
		location: c.location || undefined,
		position: application.job_offer_title || c.position || undefined,
		experience: c.experience || undefined,
		summary: c.summary || undefined,
		skills: c.skills || undefined,
		technicalScore: c.technical_score ?? undefined,
		experienceScore: c.experience_score ?? undefined,
		communicationScore: c.communication_score ?? undefined,
		cultureScore: c.culture_score ?? undefined,
		campaignId: application.job_offer_id?.toString() || '',
		applications: [buildCandidateApplication(application)],
	};
	return candidate;
}

/**
 * Construit une CandidateApplication depuis une Application backend
 */
function buildCandidateApplication(application: any): CandidateApplication {
	const stage = mapApplicationStatusToCandidateStage(application.status) as CandidateStage;
	return {
		applicationId: application.id?.toString() || '',
		positionId: application.target_position_id || undefined,
		targetPositionName: application.target_position_name || undefined,
		currentStage: stage,
		priority: application.priority || 'MEDIUM',
		appliedDate: application.applied_at,
		lastStageChange: application.applied_at,
		notes: application.cover_letter || undefined,
		score: application.candidate?.technical_score ?? application.technical_score ?? undefined,
		inPipeline: true,
		scores: application.scores || {},
		evaluationNotes: application.evaluation_notes || undefined,
		// Offer details
		salaryMin: application.salary_min ?? undefined,
		salaryMax: application.salary_max ?? undefined,
		salaryCurrency: application.salary_currency || undefined,
		offerStartDate: application.offer_start_date || undefined,
		campaignId: application.job_offer_id?.toString() || '',
	};
}

/**
 * Normalise un CandidateWithApplicationsOut du backend vers Candidate du frontend.
 * Les candidats arrivent déjà groupés avec leurs applications.
 */
function mapCandidateWithApplicationsToFrontend(data: any): Candidate {
	const apps: CandidateApplication[] = (data.applications || []).map(buildCandidateApplication);
	// La première application sert de source pour les infos de stage/date/priorité
	const firstApp = apps[0] || {} as CandidateApplication;
	// Récupère le campaignId depuis la première application (job_offer_id)
	const campaignId = firstApp.campaignId 
		|| (data.applications && data.applications.length > 0 
			? String(data.applications[0].job_offer_id || '') 
			: '');
	return {
		id: data.id.toString(),
		firstName: data.first_name,
		middleName: data.middle_name || '',
		lastName: data.last_name,
		email: data.email,
		phone: data.phone || '',
		avatarUrl: data.avatar_url || undefined,
		linkedinUrl: data.linkedin_profile || undefined,
		currentStage: firstApp.currentStage || 'SCREENING',
		priority: data.priority || 'MEDIUM',
		source: data.source || 'DIRECT',
		gender: data.gender || 'NOT_SPECIFIED',
		appliedDate: firstApp.appliedDate || '',
		lastStageChange: firstApp.lastStageChange || '',
		score: firstApp.score ?? undefined,
		resumeUrl: data.resume || undefined,
		notes: data.notes || undefined,
		positionId: firstApp.positionId || undefined,
		targetPositionName: firstApp.targetPositionName || undefined,
		location: data.location || undefined,
		position: data.position || undefined,
		experience: data.experience || undefined,
		summary: data.summary || undefined,
		skills: data.skills || undefined,
		technicalScore: data.technical_score ?? undefined,
		experienceScore: data.experience_score ?? undefined,
		communicationScore: data.communication_score ?? undefined,
		cultureScore: data.culture_score ?? undefined,
		campaignId: campaignId,
		applications: apps,
	};
}

/**
 * Regroupe les candidats par ID et fusionne leurs applications.
 * Si un candidat a postulé à plusieurs postes, on a 1 ligne avec N applications.
 */
function groupCandidateResults(applications: Candidate[]): Candidate[] {
	const map = new Map<string, Candidate>();
	
	for (const app of applications) {
		const existing = map.get(app.id);
		if (existing) {
			// Merge applications
			if (app.applications) {
				existing.applications = [...(existing.applications || []), ...app.applications];
			}
		} else {
			map.set(app.id, { ...app });
		}
	}
	
	return Array.from(map.values());
}

/**
 * Normalise les données Interview du backend vers Interview du frontend
 */
function mapInterviewToFrontend(interview: any): Interview {
	return {
		id: interview.id.toString(),
		candidateId: interview.candidate_id ?? '',
		candidateName: interview.candidate_name || undefined,
		positionName: interview.position_name || undefined,
		applicationId: interview.application_id?.toString() ?? '',
		interviewerId: interview.interviewer_id ?? '',
		interviewer: interview.interviewer_name,
		type: interview.interview_type as any,
		scheduledDate: interview.scheduled_at,
		duration: interview.duration_minutes || 60,
		location: interview.location || undefined,
		videoLink: interview.video_link || undefined,
		status: (interview.status as InterviewStatus) || 'SCHEDULED',
		feedback: interview.score ? {
			rating: interview.score,
			feedback: interview.feedback || undefined,
			strengths: interview.strengths || [],
			weaknesses: interview.weaknesses || [],
			wouldHire: interview.would_hire ?? undefined,
			nextSteps: interview.next_steps || undefined,
		} : undefined,
		notes: interview.notes || undefined,
		description: interview.feedback || undefined,
		cancellationReason: undefined,
		nextSteps: interview.next_steps || undefined
	};
}

/**
 * Service pour la gestion du recrutement
 * Utilise les endpoints dédiés dans le dossier api/
 */
class RecruitmentService {
	// ==========================================
	// JOB OFFERS
	// ==========================================

	async listJobOffers(
		page?: number,
		limit?: number,
		orgUnitId?: number,
		isActive?: boolean,
		search?: string,
		status?: string,
		jobNames?: string[],
		sortBy?: string,
		sortOrder?: string
	): Promise<{ results: RecruitmentCampaign[]; count: number }> {
		try {
			const response = await recruitmentEndpoint.listJobOffers({
				page,
				limit,
				org_unit_id: orgUnitId,
				is_active: isActive,
				search,
				status,
				job_names: jobNames,
				sort_by: sortBy,
				sort_order: sortOrder
			});
			return {
				results: (response.results || []).map((jobOffer) => mapJobOfferToCampaign(jobOffer)),
				count: response.count || 0
			};
		} catch (error: any) {
			console.error('[RecruitmentService] Error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async createJobOffer(data: any): Promise<RecruitmentCampaign> {
		try {
			const jobOffer = await recruitmentEndpoint.createJobOffer(data);
			notification.toast.success('Offre d\'emploi créée avec succès');
			return mapJobOfferToCampaign(jobOffer);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async publishJobOffer(offerId: string): Promise<RecruitmentCampaign> {
		try {
			const jobOffer = await recruitmentEndpoint.publishJobOffer(offerId);
			notification.toast.success('Offre publiée avec succès');
			return mapJobOfferToCampaign(jobOffer);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async closeJobOffer(offerId: string): Promise<RecruitmentCampaign> {
		try {
			const jobOffer = await recruitmentEndpoint.closeJobOffer(offerId);
			notification.toast.success('Offre fermée avec succès');
			return mapJobOfferToCampaign(jobOffer);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async updateJobOffer(offerId: string, data: JobOfferUpdate): Promise<RecruitmentCampaign> {
		try {
			const jobOffer = await recruitmentEndpoint.updateJobOffer(offerId, data);
			return mapJobOfferToCampaign(jobOffer);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async getJobOfferById(offerId: string): Promise<RecruitmentCampaign> {
		try {
			const [jobOffer, allPositions] = await Promise.all([
				recruitmentEndpoint.getJobOffer(offerId),
				recruitmentEndpoint.listPositions()
			]);

			const positionsRaw = Array.isArray(allPositions) ? allPositions : (allPositions as any).results || [];
			const targetIds = jobOffer.target_position_ids || [];
			const relevantPositions = positionsRaw
				.filter((p: any) => targetIds.includes(p.id))
				.map(mapPositionToFrontend);

			return mapJobOfferToCampaign(jobOffer, relevantPositions);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	// ==========================================
	// APPLICATIONS
	// ==========================================

	async listApplications(
		offerId: string,
		page?: number,
		limit?: number,
		search?: string,
		status?: string[],
		source?: string[],
		priority?: string[],
		positionId?: string[]
	): Promise<{ results: Candidate[]; count: number }> {
		try {
			const response = await recruitmentEndpoint.listApplications({
				offer_id: offerId,
				page,
				limit,
				search,
				status: status?.length ? status : undefined,
				source: source?.length ? source : undefined,
				priority: priority?.length ? priority : undefined,
				position_id: positionId?.length ? positionId : undefined
			});
			return {
				results: groupCandidateResults((response.results || []).map(mapApplicationToCandidate)),
				count: response.count || 0
			};
		} catch (error: any) {
			console.error('[RecruitmentService] Error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async listCandidatesWithApplications(
		offerId: string,
		page?: number,
		limit?: number,
		search?: string,
		status?: string[],
		source?: string[],
		priority?: string[],
		positionId?: string[],
		gender?: string[]
	): Promise<{ results: Candidate[]; count: number }> {
		try {
			const response = await recruitmentEndpoint.listCandidatesWithApplications({
				offer_id: offerId,
				page,
				limit,
				search,
				status: status?.length ? status : undefined,
				source: source?.length ? source : undefined,
				priority: priority?.length ? priority : undefined,
				position_id: positionId?.length ? positionId : undefined,
				gender: gender?.length ? gender : undefined
			});
			return {
				results: (response.results || []).map(mapCandidateWithApplicationsToFrontend),
				count: response.count || 0
			};
		} catch (error: any) {
			console.error('[RecruitmentService] Error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async updateApplicationStatus(applicationId: string, newStatus: string): Promise<Candidate> {
		try {
			const application = await recruitmentEndpoint.updateApplicationStatus(applicationId, newStatus);
			return mapApplicationToCandidate(application);
		} catch (error: any) {
			throw error;
		}
	}

	// ==========================================
	// INTERVIEWS
	// ==========================================

	async listInterviews(offerId?: string, page?: number, limit?: number): Promise<{ results: Interview[]; count: number }> {
		try {
			const response = await recruitmentEndpoint.listInterviews({ offer_id: offerId, page, limit });
			return {
				results: (response.results || []).map(mapInterviewToFrontend),
				count: response.count || 0
			};
		} catch (error: any) {
			console.error('[RecruitmentService] Error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async scheduleInterview(data: CreateInterviewInput): Promise<Interview> {
		try {
			const interview = await recruitmentEndpoint.scheduleInterview({
				application_id: data.applicationId,
				interviewer_id: data.interviewerId,
				scheduled_at: data.scheduledDate,
				interview_type: data.type,
				duration_minutes: data.duration,
				location: data.location,
				notes: data.description
			});
			return mapInterviewToFrontend(interview);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async submitInterviewFeedback(interviewId: string, data: { score: number; feedback?: string; strengths?: string[]; weaknesses?: string[]; wouldHire?: boolean; nextSteps?: string; status?: string }): Promise<Interview> {
		try {
			// Map camelCase from frontend to snake_case for backend
			const backendData = {
				score: data.score,
				feedback: data.feedback,
				strengths: data.strengths,
				weaknesses: data.weaknesses,
				would_hire: data.wouldHire,
				next_steps: data.nextSteps,
				status: data.status,
			};
			const interview = await recruitmentEndpoint.submitInterviewFeedback(interviewId, backendData);
			return mapInterviewToFrontend(interview);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async updateInterview(interviewId: string, data: Partial<Interview>): Promise<Interview> {
		try {
			const interview = await recruitmentEndpoint.updateInterview(interviewId, {
				interview_type: data.type,
				scheduled_at: data.scheduledDate,
				duration_minutes: data.duration,
				interviewer_id: data.interviewerId,
				location: data.location,
				notes: data.description,
				video_link: data.videoLink,
				status: data.status as string | undefined
			});
			return mapInterviewToFrontend(interview);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	// ==========================================
	// LEGACY METHODS (à migrer progressivement)
	// ==========================================

	async get(id: string) {
		// TODO: Implémenter getApplication
		console.log('get candidate:', id);
		return null;
	}

	async create(data: CreateCandidateInput): Promise<Candidate | null> {
		// Map campaignId to offer_id for the backend apply endpoint
		const payload = {
			first_name: data.firstName,
			middle_name: data.middleName,
			last_name: data.lastName,
			email: data.email,
			phone: data.phone,
			linkedin_profile: data.linkedinProfile,
			gender: data.gender,
			source: data.source,
			location: data.location,
			position: data.position,
			experience: data.experience,
			notes: data.notes,
		} as Record<string, any>;
		// Add target_position_ids if provided
		if (data.positionIds && data.positionIds.length > 0) {
			payload.target_position_ids = data.positionIds;
		}
		// Add per-position priorities if provided
		if (data.positionPriorities) {
			payload.position_priorities = data.positionPriorities;
		}
		// Submit via the application endpoint (POST .../{offer_id}/apply)
		const application = await recruitmentEndpoint.submitApplication(
			data.campaignId,
			payload,
			data.resumeFile
		);
		return mapApplicationToCandidate(application);
	}

	async updateApplicationEvaluation(applicationId: string, data: {
		scores?: Record<string, number>;
		evaluationNotes?: string;
	}): Promise<any> {
		const payload: Record<string, any> = {};
		if (data.scores !== undefined) payload.scores = data.scores;
		if (data.evaluationNotes !== undefined) payload.evaluation_notes = data.evaluationNotes;
		return await recruitmentEndpoint.updateApplicationEvaluation(applicationId, payload);
	}

	async updateApplicationOffer(applicationId: string, data: {
		salaryMin?: number;
		salaryMax?: number;
		salaryCurrency?: string;
		offerStartDate?: string;
	}): Promise<any> {
		const payload: Record<string, any> = {};
		if (data.salaryMin !== undefined) payload.salary_min = data.salaryMin;
		if (data.salaryMax !== undefined) payload.salary_max = data.salaryMax;
		if (data.salaryCurrency !== undefined) payload.salary_currency = data.salaryCurrency;
		if (data.offerStartDate !== undefined) payload.offer_start_date = data.offerStartDate;
		return await recruitmentEndpoint.updateApplicationOffer(applicationId, payload);
	}


	async update(id: string, data: UpdateCandidateInput) {
		// Map frontend fields to backend snake_case
		const payload: Record<string, any> = {};
		if (data.firstName !== undefined) payload.first_name = data.firstName;
		if (data.lastName !== undefined) payload.last_name = data.lastName;
		if (data.middleName !== undefined) payload.middle_name = data.middleName;
		if (data.email !== undefined) payload.email = data.email;
		if (data.phone !== undefined) payload.phone = data.phone;
		if (data.linkedinProfile !== undefined) payload.linkedin_profile = data.linkedinProfile;
		if (data.source !== undefined) payload.source = data.source;
		if (data.gender !== undefined) payload.gender = data.gender;
		if (data.priority !== undefined) payload.priority = data.priority;
		if (data.notes !== undefined) payload.notes = data.notes;
		if (data.location !== undefined) payload.location = data.location;
		if (data.position !== undefined) payload.position = data.position;
		if (data.experience !== undefined) payload.experience = data.experience;
		if (data.summary !== undefined) payload.summary = data.summary;
		if (data.skills !== undefined) payload.skills = data.skills;
		if (data.technicalScore !== undefined) payload.technical_score = data.technicalScore;
		if (data.experienceScore !== undefined) payload.experience_score = data.experienceScore;
		if (data.communicationScore !== undefined) payload.communication_score = data.communicationScore;
		if (data.cultureScore !== undefined) payload.culture_score = data.cultureScore;
		if (data.score !== undefined) payload.technical_score = data.score;

		if (data.offerId !== undefined) payload.offer_id = data.offerId;
		if (data.positionIds !== undefined) payload.position_ids = data.positionIds;
		if (data.positionPriorities !== undefined) payload.position_priorities = data.positionPriorities as Record<string, string>;

		const result = await recruitmentEndpoint.updateCandidateProfile(id, payload);
		return mapCandidateWithApplicationsToFrontend(result);
	}

	async uploadPhoto(id: string, file: File): Promise<any> {
		try {
			const result = await recruitmentEndpoint.uploadCandidatePhoto(id, file);
			return result;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async updateStage(id: string, stage: string) {
		// Utiliser updateApplicationStatus à la place
		return this.updateApplicationStatus(id, stage);
	}

	async delete(id: string) {
		// TODO: Implémenter avec API (endpoint à créer)
		console.log('delete candidate:', id);
	}

	async listInterviewsByCandidate(candidateId?: string, applicationId?: string): Promise<{ results: Interview[]; count: number }> {
		const response = await recruitmentEndpoint.listInterviews({ candidate_id: candidateId, application_id: applicationId });
		return {
			results: (response.results || []).map(mapInterviewToFrontend),
			count: response.count
		};
	}

	async createInterview(data: CreateInterviewInput) {
		return this.scheduleInterview(data);
	}

	async deleteInterview(id: string) {
		// TODO: Implémenter avec API (endpoint à créer)
		console.log('delete interview:', id);
	}

	async listOffers(candidateId?: string) {
		// Utiliser listJobOffers à la place
		return this.listJobOffers();
	}

	async createOffer(data: CreateJobOfferInput) {
		return this.createJobOffer(data);
	}

	async updateOffer(id: string, data: Partial<JobOffer>) {
		// TODO: Implémenter avec API (endpoint à créer)
		console.log('update offer:', id, data);
		return null;
	}

	async sendOffer(id: string) {
		// TODO: Implémenter avec API (endpoint à créer)
		console.log('send offer:', id);
		return null;
	}

	async uploadResume(candidateId: string, file: File) {
		try {
			const result = await recruitmentEndpoint.uploadCandidateResume(candidateId, file);
			return result;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async generateVideoLink(interviewData: {
		candidateId: string;
		interviewerId: string;
		scheduledDate: string;
	}) {
		// TODO: Implémenter avec API (endpoint à créer)
		console.log('generate video link:', interviewData);
		return null;
	}
}

export const recruitmentService = new RecruitmentService();
