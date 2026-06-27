/** Performance Review status */
export type ReviewStatus = 'DRAFT' | 'SUBMITTED' | 'ACKNOWLEDGED';

/** Goal type */
export type PerformanceGoalType = 'OBJECTIVE' | 'KPI';

/** Goal in a review */
export interface Goal {
	description: string;
	type: PerformanceGoalType;
	rating?: number;
}

/** Skill assessment */
export interface Skill {
	name: string;
	level: number;
}

/** Raw response from the backend (snake_case) */
export interface PerformanceReviewBackendResponse {
	id: string;
	employee: { id: string; [key: string]: unknown };
	reviewer?: { id: string; [key: string]: unknown } | null;
	employee_name: string;
	reviewer_name: string;
	review_period_label: string;
	review_period_start: string;
	review_period_end: string;
	status: ReviewStatus;
	goals: Goal[];
	skills: Skill[];
	employee_comment: string;
	reviewer_comment: string;
	overall_rating?: number | null;
	created_at: string;
	updated_at: string;
}

/** Normalized frontend model (camelCase) */
export interface PerformanceReview {
	id: string;
	employeeId: string;
	employeeName: string;
	reviewerId?: string;
	reviewerName?: string;
	reviewPeriodLabel: string;
	reviewPeriodStart: string;
	reviewPeriodEnd: string;
	status: ReviewStatus;
	goals: Goal[];
	skills: Skill[];
	employeeComment: string;
	reviewerComment: string;
	overallRating?: number;
	createdAt: string;
}

/** Filters for listing reviews */
export interface PerformanceReviewFilters {
	search?: string;
	status?: ReviewStatus;
	employeeId?: string;
}
