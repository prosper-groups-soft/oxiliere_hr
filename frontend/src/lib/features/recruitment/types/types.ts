export interface RecruitmentCampaign {
	id: string;
	title: string; // ex: "Développeur Frontend Senior"
	jobName: string; // ex: "Développeur Fullstack"
	location: string; // ex: "Paris" ou "Remote"
	type: 'FULL_TIME' | 'PART_TIME' | 'CONTRACT' | 'INTERNSHIP';
	status: 'DRAFT' | 'OPEN' | 'PAUSED' | 'CLOSED';
	openDate?: string;
	closeDate?: string;
	hiringManagerId: string;
	hiringManagerName?: string;
	targetHires: number;
	description?: string;
	requirements?: string[];
	metrics: {
		totalCandidates: number;
		inPipeline: number;
		interviews: number;
		offersSent: number;
	};
}

export interface Candidate {
	id: string;
	firstName: string;
	lastName: string;
	email: string;
	phone: string;
	avatarUrl?: string;
	currentStage: CandidateStage;
	priority: 'LOW' | 'MEDIUM' | 'HIGH';
	source: CandidateSource;
	appliedDate: string;
	lastStageChange: string;
	score?: number;
	resumeUrl?: string;
	notes?: string;
	positionId?: string; // Link to position

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

	// Pipeline status
	inPipeline?: boolean; // Whether candidate is actively in recruitment process
	campaignId: string; // Campaign this candidate belongs to
}

export type CandidateStage = 'SCREENING' | 'SHORTLIST' | 'INTERVIEW' | 'OFFER' | 'REJECTED';
export type CandidateSource = 'LINKEDIN' | 'CAREER_SITE' | 'REFERRAL' | 'DIRECT';

export interface Interview {
	id: string;
	candidateId: string;
	interviewerId: string;
	interviewer?: string; // Name of interviewer
	type: InterviewType;
	scheduledDate: string;
	duration: number; // minutes
	location?: string;
	videoLink?: string;
	status: InterviewStatus;
	feedback?: InterviewFeedback;
	description?: string; // Interview description
	cancellationReason?: string; // Cancellation reason
	nextSteps?: string; // Next steps after interview
}

export type InterviewType = 'PHONE' | 'VIDEO' | 'ONSITE' | 'TECHNICAL' | 'BEHAVIORAL';
export type InterviewStatus = 'SCHEDULED' | 'COMPLETED' | 'CANCELLED' | 'NO_SHOW';

export interface InterviewFeedback {
	rating: number; // 1-5
	strengths: string[];
	weaknesses: string[];
	notes: string;
	wouldHire: boolean;
	feedback?: string; // Simplified text feedback
	nextSteps?: string; // Next steps
}

export interface JobOffer {
	id: string;
	candidateId: string;
	positionId: string;
	salary: {
		min: number;
		max: number;
		currency: string;
	};
	startDate: string;
	status: OfferStatus;
	sentDate?: string;
}

export type OfferStatus = 'DRAFT' | 'SENT' | 'ACCEPTED' | 'DECLINED';

export interface RecruitmentFilters {
	stage?: CandidateStage[];
	source?: CandidateSource[];
	priority?: ('LOW' | 'MEDIUM' | 'HIGH')[];
	search: string;
	positionId?: string[];
}

export interface CreateCandidateInput {
	firstName: string;
	lastName: string;
	email: string;
	phone: string;
	source: CandidateSource;
	positionId?: string;
	campaignId: string;
	resumeUrl?: string;
	notes?: string;
}

export interface UpdateCandidateInput {
	firstName?: string;
	lastName?: string;
	email?: string;
	phone?: string;
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
	inPipeline?: boolean;
	currentStage?: CandidateStage;
}

export interface CreateInterviewInput {
	candidateId: string;
	interviewerId: string;
	type: InterviewType;
	scheduledDate: string;
	duration: number;
	location?: string;
}

export interface CreateJobOfferInput {
	candidateId: string;
	positionId: string;
	salaryMin: number;
	salaryMax: number;
	currency: string;
	startDate: string;
}

// Pipeline Data Structure
export interface PipelineColumn {
	stage: CandidateStage;
	title: string;
	candidates: Candidate[];
}

export interface PipelineMetrics {
	totalCandidates: number;
	stageCounts: Record<CandidateStage, number>;
	averageTimeInStage: Record<CandidateStage, number>; // in days
}
