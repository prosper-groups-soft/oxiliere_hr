import APIEndPoint from '@/utilities/http/rest';
import type { PaginatedResponse } from '@/utilities/common/types';
import type {
	PerformanceReviewBackendResponse,
	Campaign,
	ParticipantPreview,
} from '../types/types';


/**
 * API Endpoints for Performance Module
 * Base path: /api/performance
 */
export const performanceEndpoint = {

	// ═══════════════════════════════════════
	//  CAMPAIGNS
	// ═══════════════════════════════════════

	listCampaigns: async (
		params?: { page?: number; status?: string; campaign_type?: string; search?: string }
	): Promise<PaginatedResponse<Campaign>> => {
		const queryParams = new URLSearchParams();
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.status) queryParams.set('status', params.status);
		if (params?.campaign_type) queryParams.set('campaign_type', params.campaign_type);
		if (params?.search) queryParams.set('search', params.search);
		const queryString = queryParams.toString();
		const url = queryString
			? `/api/performance/campaigns/?${queryString}`
			: `/api/performance/campaigns/`;
		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	getCampaign: async (campaignId: string): Promise<Campaign> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}`,
			`/api/performance/campaigns/${campaignId}`
		);
		return await endpoint.retrieve();
	},

	createCampaign: async (
		data: {
			name: string;
			description?: string;
			campaign_type: string;
			start_date: string;
			end_date: string;
			submission_deadline: string;
			goal_weight?: number;
			skill_weight?: number;
			participant_ids?: string[];
		}
	): Promise<Campaign> => {
		const endpoint = new APIEndPoint('/api/performance/campaigns/', '/api/performance/campaigns/');
		const response = await endpoint.create(data);
		return response[1] || response;
	},

	updateCampaign: async (
		campaignId: string,
		data: Partial<{
			name: string;
			description: string;
			campaign_type: string;
			start_date: string;
			end_date: string;
			submission_deadline: string;
			goal_weight: number;
			skill_weight: number;
			participant_ids: string[];
		}>
	): Promise<Campaign> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}`,
			`/api/performance/campaigns/${campaignId}`
		);
		return await endpoint.partial_update(data);
	},

	deleteCampaign: async (campaignId: string): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}`,
			`/api/performance/campaigns/${campaignId}`
		);
		await endpoint.destroy();
	},

	activateCampaign: async (campaignId: string): Promise<Campaign> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/activate`,
			`/api/performance/campaigns/${campaignId}/activate`
		);
		return await endpoint.create({});
	},

	closeCampaign: async (campaignId: string): Promise<Campaign> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/close`,
			`/api/performance/campaigns/${campaignId}/close`
		);
		return await endpoint.create({});
	},

	listParticipants: async (campaignId: string): Promise<{ employee_id: string }[]> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/participants`,
			`/api/performance/campaigns/${campaignId}/participants`
		);
		return await endpoint.list();
	},

	addParticipant: async (
		campaignId: string,
		employeeId: string
	): Promise<unknown> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/add-participant`,
			`/api/performance/campaigns/${campaignId}/add-participant`
		);
		return await endpoint.create({ employee_id: employeeId });
	},

	removeParticipant: async (
		campaignId: string,
		employeeId: string
	): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/remove-participant`,
			`/api/performance/campaigns/${campaignId}/remove-participant`
		);
		await endpoint.create({ employee_id: employeeId });
	},

	listParticipantsDetail: async (
		campaignId: string
	): Promise<ParticipantPreview[]> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/participants/detail`,
			`/api/performance/campaigns/${campaignId}/participants/detail`
		);
		return await endpoint.list();
	},

	// ═══════════════════════════════════════
	//  EVALUATORS
	// ═══════════════════════════════════════

	listEvaluatorsDetail: async (
		campaignId: string
	): Promise<ParticipantPreview[]> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/evaluators/detail`,
			`/api/performance/campaigns/${campaignId}/evaluators/detail`
		);
		return await endpoint.list();
	},

	addEvaluator: async (
		campaignId: string,
		employeeId: string
	): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/add-evaluator`,
			`/api/performance/campaigns/${campaignId}/add-evaluator`
		);
		return await endpoint.create({ employee_id: employeeId });
	},

	removeEvaluator: async (
		campaignId: string,
		employeeId: string
	): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/performance/campaigns/${campaignId}/remove-evaluator`,
			`/api/performance/campaigns/${campaignId}/remove-evaluator`
		);
		await endpoint.create({ employee_id: employeeId });
	},

	// ═══════════════════════════════════════
	//  REVIEWS
	// ═══════════════════════════════════════

	listAllReviews: async (
		params?: {
			page?: number;
			status?: string;
			campaign_id?: string;
			employee_id?: string;
			manager_id?: string;
			search?: string;
		}
	): Promise<PaginatedResponse<PerformanceReviewBackendResponse>> => {
		const queryParams = new URLSearchParams();
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.status) queryParams.set('status', params.status);
		if (params?.campaign_id) queryParams.set('campaign_id', params.campaign_id);
		if (params?.employee_id) queryParams.set('employee_id', params.employee_id);
		if (params?.manager_id) queryParams.set('manager_id', params.manager_id);
		if (params?.search) queryParams.set('search', params.search);
		const queryString = queryParams.toString();
		const url = queryString
			? `/api/performance/reviews/?${queryString}`
			: `/api/performance/reviews/`;
		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	getReview: async (
		reviewId: string
	): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}`,
			`/api/performance/reviews/${reviewId}`
		);
		return await endpoint.retrieve();
	},

	listEmployeeReviews: async (
		employeeId: string,
		params?: { page?: number; status?: string }
	): Promise<PaginatedResponse<PerformanceReviewBackendResponse>> => {
		const queryParams = new URLSearchParams();
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.status) queryParams.set('status', params.status);
		const queryString = queryParams.toString();
		const url = queryString
			? `/api/performance/reviews/employee/${employeeId}?${queryString}`
			: `/api/performance/reviews/employee/${employeeId}`;
		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	listPendingReviews: async (
		reviewerId: string,
		params?: { page?: number }
	): Promise<PaginatedResponse<PerformanceReviewBackendResponse>> => {
		const queryParams = new URLSearchParams();
		if (params?.page) queryParams.set('page', params.page.toString());
		const queryString = queryParams.toString();
		const url = queryString
			? `/api/performance/reviews/pending/${reviewerId}?${queryString}`
			: `/api/performance/reviews/pending/${reviewerId}`;
		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	createReview: async (data: {
		campaign_id: string;
		employee_id: string;
		manager_id?: string;
		goals?: { description: string; type: string; weight?: number; employee_rating?: number }[];
		skills?: { name: string; category?: string; employee_level?: number }[];
		employee_comment?: string;
	}): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint('/api/performance/reviews/', '/api/performance/reviews/');
		const response = await endpoint.create(data);
		return response[1] || response;
	},

	/** PATCH employee : goals, skills, employee_comment */
	updateEmployeeReview: async (
		reviewId: string,
		data: {
			goals?: { description: string; type: string; weight?: number; employee_rating?: number }[];
			skills?: { name: string; category?: string; employee_level?: number }[];
			employee_comment?: string;
		}
	): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}/employee`,
			`/api/performance/reviews/${reviewId}/employee`
		);
		return await endpoint.partial_update(data);
	},

	/** PATCH manager : goals_manager, skills_manager, manager_comment, manager_overall_score */
	updateManagerReview: async (
		reviewId: string,
		data: {
			goals_manager?: { description: string; type: string; weight?: number; manager_rating?: number; manager_comment?: string }[];
			skills_manager?: { name: string; category?: string; manager_level?: number }[];
			manager_comment?: string;
			manager_overall_score?: number;
		}
	): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}/manager`,
			`/api/performance/reviews/${reviewId}/manager`
		);
		return await endpoint.partial_update(data);
	},

	deleteReview: async (reviewId: string): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}`,
			`/api/performance/reviews/${reviewId}`
		);
		await endpoint.destroy();
	},

	submitEmployeeReview: async (reviewId: string): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}/submit-employee`,
			`/api/performance/reviews/${reviewId}/submit-employee`
		);
		return await endpoint.create({});
	},

	submitManagerReview: async (reviewId: string): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}/submit-manager`,
			`/api/performance/reviews/${reviewId}/submit-manager`
		);
		return await endpoint.create({});
	},

	calibrateReview: async (
		reviewId: string,
		data: { calibrated_score: number; reason: string }
	): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}/calibrate`,
			`/api/performance/reviews/${reviewId}/calibrate`
		);
		return await endpoint.create(data);
	},

	acknowledgeReview: async (reviewId: string): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}/acknowledge`,
			`/api/performance/reviews/${reviewId}/acknowledge`
		);
		return await endpoint.create({});
	},

	disputeReview: async (reviewId: string, data?: { reason?: string }): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}/dispute`,
			`/api/performance/reviews/${reviewId}/dispute`
		);
		return await endpoint.create(data ?? {});
	},
};

