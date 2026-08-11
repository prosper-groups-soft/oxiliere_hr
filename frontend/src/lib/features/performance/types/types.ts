/** Statut d'une campagne */
export type CampaignStatus = 'DRAFT' | 'ACTIVE' | 'CLOSED';

/** Type de campagne */
export type CampaignType = 'ANNUAL' | 'SEMESTRIAL' | 'TRIMESTRIAL' | 'PROBATION';

/** Statut d'une évaluation (5 états) */
export type ReviewStatus =
	| 'EMPLOYEE_DRAFT'
	| 'MANAGER_DRAFT'
	| 'SUBMITTED'
	| 'CALIBRATED'
	| 'ACKNOWLEDGED';

/** Type d'objectif */
export type PerformanceGoalType = 'OBJECTIVE' | 'KPI';

/** Catégorie de compétence */
export type SkillCategory = 'TECHNICAL' | 'BEHAVIORAL' | 'LEADERSHIP';


// ---------------------------------------
//  CAMPAIGN
// ---------------------------------------

export interface ParticipantPreview {
	id: string;
	name: string;
	last_name?: string;
	first_name?: string;
	middle_name?: string | null;
	lastName?: string;
	firstName?: string;
	middleName?: string | null;
	job_title: string | null;
	org_unit: string | null;
	jobTitle: string | null;
	orgUnit: string | null;
	profile_photo: string | null;
	avatarUrl: string | null;
}

export interface Campaign {
	id: string;
	name: string;
	description: string;
	campaign_type: CampaignType;
	start_date: string;
	end_date: string;
	submission_deadline: string;
	status: CampaignStatus;
	goal_weight: number;
	skill_weight: number;
	default_goals: Goal[];
	default_skills: Skill[];
	participant_count: number;
	evaluator_count: number;
	participants_preview: ParticipantPreview[];
	evaluators_preview: ParticipantPreview[];
	created_at: string;
}


// ---------------------------------------
//  GOALS & SKILLS
// ---------------------------------------

/** Objectif (auto-évaluation employé + manager) */
export interface Goal {
	description: string;
	type: PerformanceGoalType;
	weight?: number;
	employee_rating?: number; // 1-5
	manager_rating?: number; // 1-5, saisi par le manager
	manager_comment?: string; // commentaire du manager sur cet objectif
	selected?: boolean; // utilisé en mode sélection (non-editable)
}

/** Compétence (auto-évaluation employé + manager) */
export interface Skill {
	name: string;
	category?: SkillCategory;
	weight?: number;
	employee_level?: number; // 1-5
	manager_level?: number; // 1-5, saisi par le manager
	selected?: boolean; // utilisé en mode sélection (non-editable)
}

/** Objectif (évaluation manager) */
export interface GoalManager {
	description: string;
	type: PerformanceGoalType;
	weight?: number;
	manager_rating?: number; // 1-5
	manager_comment?: string;
}

/** Compétence (évaluation manager) */
export interface SkillManager {
	name: string;
	category?: SkillCategory;
	weight?: number;
	manager_level?: number; // 1-5
}


// ---------------------------------------
//  PERFORMANCE REVIEW
// ---------------------------------------

/** Réponse backend brute (snake_case) */
export interface PerformanceReviewBackendResponse {
	id: string;
	campaign_id: string;
	campaign_name: string;
	campaign_goal_weight?: number | null;
	campaign_skill_weight?: number | null;
	employee_id: string;
	employee_name: string;
	employee_avatar?: string | null;
	employee_job_title?: string | null;
	employee_last_name?: string | null;
	employee_middle_name?: string | null;
	employee_first_name?: string | null;
	manager_id?: string | null;
	manager_name: string;
	manager_avatar?: string | null;
	manager_last_name?: string | null;
	manager_middle_name?: string | null;
	manager_first_name?: string | null;
	status: ReviewStatus;
	disputed: boolean;
	dispute_reason?: string | null;
	goals: Goal[];
	skills: Skill[];
	goals_manager: GoalManager[];
	skills_manager: SkillManager[];
	employee_comment: string;
	manager_comment: string;
	manager_overall_score?: number | null;
	overall_score?: number | null;
	calibrated_score?: number | null;
	employee_submitted_at?: string | null;
	manager_submitted_at?: string | null;
	acknowledged_at?: string | null;
	created_at: string;
	updated_at: string;
}

/** Modèle frontend normalisé (camelCase) */
export interface PerformanceReview {
	id: string;
	campaignId: string;
	campaignName: string;
	campaignGoalWeight?: number;
	campaignSkillWeight?: number;
	employeeId: string;
	employeeName: string;
	employeeAvatar?: string;
	employeeJobTitle?: string;
	employeeLastName?: string;
	employeeMiddleName?: string;
	employeeFirstName?: string;
	managerId?: string;
	managerName: string;
	managerAvatar?: string;
	managerLastName?: string;
	managerMiddleName?: string;
	managerFirstName?: string;
	status: ReviewStatus;
	disputed: boolean;
	disputeReason?: string;
	goals: Goal[];
	skills: Skill[];
	goalsManager: GoalManager[];
	skillsManager: SkillManager[];
	employeeComment: string;
	managerComment: string;
	managerOverallScore?: number;
	overallScore?: number;
	calibratedScore?: number;
	/** Score à afficher : calibrated si présent, sinon overall */
	displayScore?: number;
	/** Score moyen de l'auto-évaluation employé (calculé depuis les ratings) */
	employeeScore?: number;
	/** Score moyen de l'évaluation évaluateur (calculé depuis les ratings) */
	evaluatorScore?: number;
	employeeSubmittedAt?: string;
	managerSubmittedAt?: string;
	acknowledgedAt?: string;
	createdAt: string;
	updatedAt: string;
}


// ---------------------------------------
//  FILTERS
// ---------------------------------------

export interface PerformanceReviewFilters {
	search?: string;
	status?: ReviewStatus;
	campaignId?: string;
	employeeId?: string;
	managerId?: string;
}

export interface CampaignFilters {
	search?: string;
	status?: CampaignStatus;
	campaign_type?: CampaignType;
}
