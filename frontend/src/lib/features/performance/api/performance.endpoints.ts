import APIEndPoint from '@/utilities/http/rest';
import type { PaginatedResponse } from '@/types/pagination';
import type { PerformanceReviewBackendResponse } from '../types/types';


/**
 * API Endpoints for Performance Reviews
 * Base path: /api/performance
 */
export const performanceEndpoint = {
	/**
	 * GET /api/performance/reviews/employee/{employee_id}
	 * Lists performance reviews for an employee (paginated).
	 */
	listEmployeeReviews: async (
		employeeId: string,
		params?: { page?: number; search?: string; status?: string }
	): Promise<PaginatedResponse<PerformanceReviewBackendResponse>> => {
		const queryParams = new URLSearchParams();
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.search) queryParams.set('search', params.search);
		if (params?.status) queryParams.set('status', params.status);
		const queryString = queryParams.toString();
		const url = queryString
			? `/api/performance/reviews/employee/${employeeId}?${queryString}`
			: `/api/performance/reviews/employee/${employeeId}`;
		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	/**
	 * GET /api/performance/reviews/pending/{reviewer_id}
	 * Lists reviews pending for a reviewer (paginated).
	 */
	listPendingReviews: async (
		reviewerId: string,
		params?: { page?: number; search?: string }
	): Promise<PaginatedResponse<PerformanceReviewBackendResponse>> => {
		const queryParams = new URLSearchParams();
		if (params?.page) queryParams.set('page', params.page.toString());
		if (params?.search) queryParams.set('search', params.search);
		const queryString = queryParams.toString();
		const url = queryString
			? `/api/performance/reviews/pending/${reviewerId}?${queryString}`
			: `/api/performance/reviews/pending/${reviewerId}`;
		const endpoint = new APIEndPoint(url, url);
		return await endpoint.list();
	},

	/**
	 * POST /api/performance/reviews
	 * Creates a new performance review.
	 */
	createReview: async (data: {
		employee_id: string;
		reviewer_id?: string;
		review_period_start: string;
		review_period_end: string;
		goals?: { description: string; type: string; rating?: number }[];
		skills?: { name: string; level: number }[];
		employee_comment?: string;
	}): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint('/api/performance/reviews', '/api/performance/reviews');
		const response = await endpoint.create(data);
		return response[1] || response;
	},

	/**
	 * PATCH /api/performance/reviews/{review_id}
	 * Updates an existing performance review.
	 */
	updateReview: async (
		reviewId: string,
		data: {
			status?: string;
			goals?: { description: string; type: string; rating?: number }[];
			skills?: { name: string; level: number }[];
			reviewer_comment?: string;
			employee_comment?: string;
			overall_rating?: number;
		}
	): Promise<PerformanceReviewBackendResponse> => {
		const endpoint = new APIEndPoint(
			`/api/performance/reviews/${reviewId}`,
			`/api/performance/reviews/${reviewId}`
		);
		const response = await endpoint.partial_update(data);
		return response[1] || response;
	},
};
