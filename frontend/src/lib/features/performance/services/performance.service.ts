import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { performanceEndpoint } from '../api/performance.endpoints';
import type {
	PerformanceReview,
	PerformanceReviewBackendResponse,
	ReviewStatus,
	Campaign,
	Goal,
	Skill,
	GoalManager,
	SkillManager,
	ParticipantPreview,
} from '../types/types';


/**
 * Normalise une réponse backend PerformanceReview vers le modèle frontend (camelCase)
 */
function normalizeReview(rev: PerformanceReviewBackendResponse): PerformanceReview {
	return {
		id: rev.id,
		campaignId: rev.campaign_id,
		campaignName: rev.campaign_name,
		campaignGoalWeight: rev.campaign_goal_weight ?? 0.6,
		campaignSkillWeight: rev.campaign_skill_weight ?? 0.4,
		employeeId: rev.employee_id,
		employeeName: rev.employee_name,
		employeeAvatar: rev.employee_avatar ?? undefined,
		employeeJobTitle: rev.employee_job_title ?? undefined,
		employeeLastName: rev.employee_last_name ?? undefined,
		employeeMiddleName: rev.employee_middle_name ?? undefined,
		employeeFirstName: rev.employee_first_name ?? undefined,
		managerId: rev.manager_id ?? undefined,
		managerName: rev.manager_name,
		managerAvatar: rev.manager_avatar ?? undefined,
		managerLastName: rev.manager_last_name ?? undefined,
		managerMiddleName: rev.manager_middle_name ?? undefined,
		managerFirstName: rev.manager_first_name ?? undefined,
		status: rev.status as ReviewStatus,
		disputed: rev.disputed,
		disputeReason: rev.dispute_reason ?? undefined,
		goals: rev.goals as Goal[],
		skills: rev.skills as Skill[],
		goalsManager: rev.goals_manager as GoalManager[],
		skillsManager: rev.skills_manager as SkillManager[],
		employeeComment: rev.employee_comment,
		managerComment: rev.manager_comment,
		managerOverallScore: rev.manager_overall_score ?? undefined,
		overallScore: rev.overall_score ?? undefined,
		calibratedScore: rev.calibrated_score ?? undefined,
		displayScore: rev.calibrated_score ?? rev.overall_score ?? undefined,
		// Scores individuels calculés (même formule pondérée que le backend)
		employeeScore: (() => {
			const goalWeight = rev.campaign_goal_weight ?? 0.6;
			const skillWeight = rev.campaign_skill_weight ?? 0.4;
			const totalW = goalWeight + skillWeight;
			const gw = totalW > 0 ? goalWeight / totalW : 0.6;
			const sw = totalW > 0 ? skillWeight / totalW : 0.4;

			const goals = (rev.goals ?? []).filter(g => g.employee_rating != null);
			const gScore = goals.length > 0
				? goals.reduce((sum, g) => sum + (g.employee_rating ?? 0) * (g.weight ?? (1 / goals.length)), 0)
					/ goals.reduce((sum, g) => sum + (g.weight ?? (1 / goals.length)), 0)
				: null;

			const skills = (rev.skills ?? []).filter(s => s.employee_level != null);
			const sScore = skills.length > 0
				? skills.reduce((sum, s) => sum + (s.employee_level ?? 0) * (s.weight ?? (1 / skills.length)), 0)
					/ skills.reduce((sum, s) => sum + (s.weight ?? (1 / skills.length)), 0)
				: null;

			if (gScore == null && sScore == null) return undefined;
			return Math.round(((gScore ?? 0) * gw + (sScore ?? 0) * sw) * 100) / 100;
		})(),
		evaluatorScore: (() => {
			const goalWeight = rev.campaign_goal_weight ?? 0.6;
			const skillWeight = rev.campaign_skill_weight ?? 0.4;
			const totalW = goalWeight + skillWeight;
			const gw = totalW > 0 ? goalWeight / totalW : 0.6;
			const sw = totalW > 0 ? skillWeight / totalW : 0.4;

			const goals = (rev.goals_manager ?? []).filter(g => g.manager_rating != null);
			const gScore = goals.length > 0
				? goals.reduce((sum, g) => sum + (g.manager_rating ?? 0) * (g.weight ?? (1 / goals.length)), 0)
					/ goals.reduce((sum, g) => sum + (g.weight ?? (1 / goals.length)), 0)
				: null;

			const skills = (rev.skills_manager ?? []).filter(s => s.manager_level != null);
			const sScore = skills.length > 0
				? skills.reduce((sum, s) => sum + (s.manager_level ?? 0) * (s.weight ?? (1 / skills.length)), 0)
					/ skills.reduce((sum, s) => sum + (s.weight ?? (1 / skills.length)), 0)
				: null;

			if (gScore == null && sScore == null) return undefined;
			return Math.round(((gScore ?? 0) * gw + (sScore ?? 0) * sw) * 100) / 100;
		})(),
		employeeSubmittedAt: rev.employee_submitted_at ?? undefined,
		managerSubmittedAt: rev.manager_submitted_at ?? undefined,
		acknowledgedAt: rev.acknowledged_at ?? undefined,
		createdAt: rev.created_at,
		updatedAt: rev.updated_at,
	};
}


/**
 * Normalise un ParticipantPreview du backend (snake_case) vers camelCase avec les mêmes champs.
 * Les champs snake_case restent présents pour compatibilité.
 */
function normalizeParticipantPreview(p: any): any {
	if (!p) return p;
	return {
		...p,
		jobTitle: p.job_title ?? null,
		orgUnit: p.org_unit ?? null,
		lastName: p.last_name ?? undefined,
		firstName: p.first_name ?? undefined,
		middleName: p.middle_name ?? null,
		avatarUrl: p.profile_photo ?? null,
	};
}


/**
 * Service pour la gestion des campagnes et évaluations de performance.
 *
 * S'interface avec l'API /api/performance/*.
 * Suit le pattern employés.service.ts / leaveRequests.service.ts.
 */
class PerformanceService {

	// ═══════════════════════════════════════
	//  CAMPAIGNS
	// ═══════════════════════════════════════

	async listCampaigns(
		page: number = 1,
		filters?: { status?: string; campaign_type?: string; search?: string }
	): Promise<{ results: Campaign[]; count: number }> {
		try {
			const response = await performanceEndpoint.listCampaigns({
				page,
				status: filters?.status || undefined,
				campaign_type: filters?.campaign_type || undefined,
				search: filters?.search || undefined,
			});
			return {
				results: response.results || [],
				count: response.count || 0,
			};
		} catch (error: any) {
			console.error('[PerformanceService] listCampaigns error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async getCampaign(campaignId: string): Promise<Campaign> {
		try {
			return await performanceEndpoint.getCampaign(campaignId);
		} catch (error: any) {
			console.error('[PerformanceService] getCampaign error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async createCampaign(data: {
		name: string;
		description?: string;
		campaign_type: string;
		start_date: string;
		end_date: string;
		submission_deadline: string;
		goal_weight?: number;
		skill_weight?: number;
		default_goals?: { description: string; type: string; weight?: number; employee_rating?: number }[];
		default_skills?: { name: string; category?: string; weight?: number; employee_level?: number }[];
	}): Promise<Campaign> {
		try {
			return await performanceEndpoint.createCampaign(data);
		} catch (error: any) {
			console.error('[PerformanceService] createCampaign error:', error);
			throw error;
		}
	}

	async updateCampaign(
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
			default_goals: { description: string; type: string; weight?: number; employee_rating?: number }[];
			default_skills: { name: string; category?: string; weight?: number; employee_level?: number }[];
		}>
	): Promise<Campaign> {
		try {
			return await performanceEndpoint.updateCampaign(campaignId, data);
		} catch (error: any) {
			console.error('[PerformanceService] updateCampaign error:', error);
			throw error;
		}
	}

	async deleteCampaign(campaignId: string): Promise<void> {
		try {
			await performanceEndpoint.deleteCampaign(campaignId);
		} catch (error: any) {
			console.error('[PerformanceService] deleteCampaign error:', error);
			throw error;
		}
	}

	async activateCampaign(campaignId: string): Promise<Campaign> {
		try {
			return await performanceEndpoint.activateCampaign(campaignId);
		} catch (error: any) {
			console.error('[PerformanceService] activateCampaign error:', error);
			throw error;
		}
	}

	async closeCampaign(campaignId: string): Promise<Campaign> {
		try {
			return await performanceEndpoint.closeCampaign(campaignId);
		} catch (error: any) {
			console.error('[PerformanceService] closeCampaign error:', error);
			throw error;
		}
	}

	async addParticipant(campaignId: string, employeeId: string): Promise<void> {
		try {
			await performanceEndpoint.addParticipant(campaignId, employeeId);
		} catch (error: any) {
			console.error('[PerformanceService] addParticipant error:', error);
			throw error;
		}
	}

	async removeParticipant(campaignId: string, employeeId: string): Promise<void> {
		try {
			await performanceEndpoint.removeParticipant(campaignId, employeeId);
		} catch (error: any) {
			console.error('[PerformanceService] removeParticipant error:', error);
			throw error;
		}
	}

	async listParticipants(campaignId: string): Promise<{ employee_id: string }[]> {
		try {
			return await performanceEndpoint.listParticipants(campaignId);
		} catch (error: any) {
			console.error('[PerformanceService] listParticipants error:', error);
			throw error;
		}
	}

	async listParticipantsDetail(campaignId: string): Promise<ParticipantPreview[]> {
		try {
			const data = await performanceEndpoint.listParticipantsDetail(campaignId);
			return (data || []).map(normalizeParticipantPreview);
		} catch (error: any) {
			console.error('[PerformanceService] listParticipantsDetail error:', error);
			throw error;
		}
	}

	async listEvaluatorsDetail(campaignId: string): Promise<ParticipantPreview[]> {
		try {
			const data = await performanceEndpoint.listEvaluatorsDetail(campaignId);
			return (data || []).map(normalizeParticipantPreview);
		} catch (error: any) {
			console.error('[PerformanceService] listEvaluatorsDetail error:', error);
			throw error;
		}
	}

	async addEvaluator(campaignId: string, employeeId: string): Promise<void> {
		try {
			await performanceEndpoint.addEvaluator(campaignId, employeeId);
		} catch (error: any) {
			console.error('[PerformanceService] addEvaluator error:', error);
			throw error;
		}
	}

	async removeEvaluator(campaignId: string, employeeId: string): Promise<void> {
		try {
			await performanceEndpoint.removeEvaluator(campaignId, employeeId);
		} catch (error: any) {
			console.error('[PerformanceService] removeEvaluator error:', error);
			throw error;
		}
	}

	// ═══════════════════════════════════════
	//  REVIEWS
	// ═══════════════════════════════════════

	async getReview(reviewId: string): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.getReview(reviewId);
			return normalizeReview(response);
		} catch (error: any) {
			console.error('[PerformanceService] getReview error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async listReviews(
		employeeId: string,
		page: number = 1,
		filters?: { search?: string; status?: string }
	): Promise<{ results: PerformanceReview[]; count: number }> {
		try {
			const response = await performanceEndpoint.listEmployeeReviews(employeeId, {
				page,
				status: filters?.status || undefined,
			});
			return {
				results: (response.results || []).map(normalizeReview),
				count: response.count || 0,
			};
		} catch (error: any) {
			console.error('[PerformanceService] listReviews error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async listAllReviews(
		page: number = 1,
		filters?: { search?: string; status?: string; campaign_id?: string }
	): Promise<{ results: PerformanceReview[]; count: number }> {
		try {
			const response = await performanceEndpoint.listAllReviews({
				page,
				status: filters?.status || undefined,
				campaign_id: filters?.campaign_id || undefined,
				search: filters?.search || undefined,
			});
			return {
				results: (response.results || []).map(normalizeReview),
				count: response.count || 0,
			};
		} catch (error: any) {
			console.error('[PerformanceService] listAllReviews error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async listPendingReviews(
		reviewerId: string,
		page: number = 1
	): Promise<{ results: PerformanceReview[]; count: number }> {
		try {
			const response = await performanceEndpoint.listPendingReviews(reviewerId, { page });
			return {
				results: (response.results || []).map(normalizeReview),
				count: response.count || 0,
			};
		} catch (error: any) {
			console.error('[PerformanceService] listPendingReviews error:', error);
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async createReview(data: {
		campaign_id: string;
		employee_id: string;
		manager_id?: string;
		goals?: { description: string; type: string; weight?: number; employee_rating?: number }[];
		skills?: { name: string; category?: string; employee_level?: number }[];
		employee_comment?: string;
	}): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.createReview(data);
			return normalizeReview(response);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async updateEmployeeReview(
		reviewId: string,
		data: {
			goals?: { description: string; type: string; weight?: number; employee_rating?: number }[];
			skills?: { name: string; category?: string; employee_level?: number }[];
			employee_comment?: string;
		}
	): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.updateEmployeeReview(reviewId, data);
			return normalizeReview(response);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async updateManagerReview(
		reviewId: string,
		data: {
			goals_manager?: { description: string; type: string; weight?: number; manager_rating?: number; manager_comment?: string }[];
			skills_manager?: { name: string; category?: string; manager_level?: number }[];
			manager_comment?: string;
			manager_overall_score?: number;
		}
	): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.updateManagerReview(reviewId, data);
			return normalizeReview(response);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async deleteReview(reviewId: string): Promise<void> {
		try {
			await performanceEndpoint.deleteReview(reviewId);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async submitEmployeeReview(reviewId: string): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.submitEmployeeReview(reviewId);
			return normalizeReview(response);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async submitManagerReview(reviewId: string): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.submitManagerReview(reviewId);
			return normalizeReview(response);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async calibrateReview(
		reviewId: string,
		data: { calibrated_score: number; reason: string }
	): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.calibrateReview(reviewId, data);
			return normalizeReview(response);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async acknowledgeReview(reviewId: string): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.acknowledgeReview(reviewId);
			return normalizeReview(response);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	async disputeReview(reviewId: string, data?: { reason?: string }): Promise<PerformanceReview> {
		try {
			const response = await performanceEndpoint.disputeReview(reviewId, data);
			return normalizeReview(response);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}
}


export const performanceService = new PerformanceService();
