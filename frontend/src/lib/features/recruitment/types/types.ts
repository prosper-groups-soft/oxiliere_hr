export interface RecruitmentPosition {
	id: string;
	name: string;
	description?: string;
	requirements: string[];
	skills: { name: string; level: number }[];
	jobFamily?: { id: string; name: string };
	orgUnit?: { id: string; name: string };
}

export interface RecruitmentVacancy {
	id: string;
	positionId?: string | null;
	positionName?: string | null;
	slots: number;
	priority?: 'LOW' | 'MEDIUM' | 'HIGH';
	status?: 'OPEN' | 'FILLED' | 'CANCELLED';
	openedDate?: string;
	targetDate?: string;
	filledDate?: string | null;
	reason?: string | null;
}


export interface EvaluationCriterion {
	source: 'requirement' | 'skill';
	name: string;
	weight: number;
}

export interface RecruitmentCampaign {
	id: string;
	title: string;      // ex: "Développeur Frontend Senior"
	slug?: string;       // slug unique généré par le backend
	jobNames: string[]; // ex: ["Développeur Fullstack", "Développeur Backend"]
	jobIds: string[];  // IDs des positions
	positionSlots?: Record<string, number>; // position_id -> number of slots
	positionNameMap?: Record<string, string>; // position_id -> position_name
	positions?: RecruitmentPosition[]; // Données complètes des positions (requirements, skills)
	location: string;   // ex: "Paris" ou "Remote"
	status: 'DRAFT' | 'OPEN' | 'PAUSED' | 'CLOSED';
	openDate?: string;
	closeDate?: string;
	hiringManagerId: string;
	hiringManagerName?: string;
	targetHires: number;
	description?: string;
	requirements?: string[];
	isPublished?: boolean;
	isActive?: boolean;
	maxApplications?: number;
	vacancyIds?: string[]; // IDs des vacancies associées (legacy)
	vacancies?: RecruitmentVacancy[]; // Détails complets des vacancies associées
	evaluationTemplate?: Record<string, EvaluationCriterion[]>; // positionId -> critères
	metrics: {
		totalCandidates: number;
		inPipeline: number;
		interviews: number;
		offersSent: number;
		offersMade: number;
	};
}

export interface CandidateApplication {
	applicationId: string;
	positionId?: string;
	targetPositionName?: string;
	currentStage: CandidateStage;
	priority: 'LOW' | 'MEDIUM' | 'HIGH';
	appliedDate: string;
	lastStageChange: string;
	notes?: string;
	score?: number;
	inPipeline?: boolean;
	scores?: Record<string, number>;
	evaluationNotes?: string;
	campaignId?: string;
	// Offer details
	salaryMin?: number;
	salaryMax?: number;
	salaryCurrency?: string;
	offerStartDate?: string;
}

export interface Candidate {
	id: string;
	firstName: string;
	middleName: string;
	lastName: string;
	email: string;
	phone: string;
	avatarUrl?: string;
	linkedinUrl?: string;
	// Primary/default application info
	currentStage: CandidateStage;
	priority: 'LOW' | 'MEDIUM' | 'HIGH';
	source: CandidateSource;
	gender: GenderStatus;
	appliedDate: string;
	lastStageChange: string;
	score?: number;
	resumeUrl?: string;
	notes?: string;
	positionId?: string;
	targetPositionName?: string;

	// All applications for this candidate (when grouped)
	applications?: CandidateApplication[];

	// Additional fields for detailed profile
	location?: string;
	position?: string;
	experience?: string;
	summary?: string;
	skills?: string[];

	// Evaluation scores
	technicalScore?: number;
	experienceScore?: number;
	communicationScore?: number;
	cultureScore?: number;

	campaignId: string;
}

export type CandidateStage = 'SCREENING' | 'SHORTLIST' | 'INTERVIEW' | 'OFFER' | 'ACCEPTED' | 'REJECTED';
export type CandidateSource = 'LINKEDIN' | 'CAREER_SITE' | 'REFERRAL' | 'DIRECT';
export type GenderStatus = 'MALE' | 'FEMALE' | 'NOT_SPECIFIED';

export interface Interview {
	id: string;
	candidateId: string;
	candidateName?: string;
	positionName?: string;
	applicationId: string;
	interviewerId: string;
	interviewer?: string; // Name of interviewer
	type: InterviewType;
	scheduledDate: string;
	duration: number; // minutes
	location?: string;
	videoLink?: string;
	status: InterviewStatus;
	feedback?: InterviewFeedback;
	notes?: string;
	description?: string;
	cancellationReason?: string;
	nextSteps?: string;
}

export type InterviewType = 'PHONE' | 'VIDEO' | 'ONSITE' | 'TECHNICAL' | 'BEHAVIORAL';
export type InterviewStatus = 'SCHEDULED' | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW';

export interface InterviewFeedback {
	rating: number; // 1-5
	feedback?: string; // Qualitative feedback
	strengths: string[];
	weaknesses: string[];
	wouldHire?: boolean;
	nextSteps?: string;
}

export interface JobOffer {
	id: string;
	candidateId: string;
	positionId: string;
	startDate: string;
	status: OfferStatus;
	sentDate?: string;
}

export type OfferStatus = 'DRAFT' | 'SENT' | 'ACCEPTED' | 'DECLINED';

export interface RecruitmentFilters {
	stage?: CandidateStage[];
	source?: CandidateSource[];
	priority?: ('LOW' | 'MEDIUM' | 'HIGH')[];
	gender?: GenderStatus[];
	search: string;
	positionId?: string[];
}

export interface CreateCandidateInput {
	firstName: string;
	middleName?: string;
	lastName: string;
	email: string;
	phone: string;
	linkedinProfile?: string;
	source: CandidateSource;
	gender?: GenderStatus;
	location?: string;
	position?: string;
	experience?: string;
	positionId?: string;
	positionIds?: string[];
	positionPriorities?: Record<string, 'LOW' | 'MEDIUM' | 'HIGH'>;
	campaignId: string;
	resumeFile?: File;
	notes?: string;
	summary?: string;
	skills?: string[];
}

export interface UpdateCandidateInput {
	firstName?: string;
	middleName?: string;
	lastName?: string;
	email?: string;
	phone?: string;
	linkedinProfile?: string;
	source?: CandidateSource;
	gender?: GenderStatus;
	priority?: 'LOW' | 'MEDIUM' | 'HIGH';
	notes?: string;
	location?: string;
	position?: string;
	experience?: string;
	summary?: string;
	skills?: string[];
	technicalScore?: number;
	experienceScore?: number;
	communicationScore?: number;
	cultureScore?: number;
	score?: number;
	currentStage?: CandidateStage;
	// Application sync fields
	offerId?: string;
	positionIds?: string[];
	positionPriorities?: Record<string, 'LOW' | 'MEDIUM' | 'HIGH'>;
}

export interface CreateInterviewInput {
	applicationId: string;
	interviewerId: string;
	type: InterviewType;
	scheduledDate: string;
	duration: number;
	location?: string;
	description?: string;
}

export interface CreateJobOfferInput {
	candidateId: string;
	positionId: string;
	currency: string;
	startDate: string;
}

// Pipeline Data Structure
export interface PipelineColumn {
	stage: CandidateStage;
	title: string;
	/** @deprecated Use applications instead */
	candidates: Candidate[];
	applications: PipelineApplicationItem[];
}

/** Une application dans le pipeline, avec son candidat parent */
export interface PipelineApplicationItem {
	id: string;
	candidate: Candidate;
	application: CandidateApplication;
}

export interface PipelineMetrics {
	totalCandidates: number;
	stageCounts: Record<CandidateStage, number>;
	averageTimeInStage: Record<CandidateStage, number>; // in days
}
