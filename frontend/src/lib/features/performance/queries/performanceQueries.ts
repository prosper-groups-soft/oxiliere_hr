import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { performanceService } from '../services/performance.service';
import { campaignStore } from '../stores/campaigns.svelte';
import { reviewsStore } from '../stores/reviews.svelte';
import type { Campaign, PerformanceReview } from '../types/types';


// ===== QUERY KEYS =====
export const performanceQueryKeys = {
	all: ['performance'] as const,
	campaigns: ['performance', 'campaigns'] as const,
	campaignDetail: (campaignId: string) => ['performance', 'campaigns', campaignId] as const,
	detail: (reviewId: string) => ['performance', 'reviews', 'detail', reviewId] as const,
	employeeReviews: (employeeId: string, page: number, status?: string) =>
		['performance', 'reviews', 'employee', employeeId, page, status ?? ''] as const,
	pendingReviews: (reviewerId: string, page: number) =>
		['performance', 'reviews', 'pending', reviewerId, page] as const,
};

// ---------------------------------------
//  CAMPAIGN QUERIES
// ---------------------------------------

export function useCampaignsQuery(
	page: () => number = () => 1,
	filters: () => { status?: string; campaign_type?: string; search?: string } = () => ({})
) {
	return createQuery({
		get queryKey() { return [...performanceQueryKeys.campaigns, page(), filters()] as const; },
		queryFn: () => performanceService.listCampaigns(page(), filters()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		refetchOnWindowFocus: true,
	});
}

export function useCampaignDetailQuery(campaignId: () => string) {
	return createQuery({
		get queryKey() { return performanceQueryKeys.campaignDetail(campaignId()); },
		queryFn: () => performanceService.getCampaign(campaignId()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		enabled: () => !!campaignId(),
	});
}

export function useCampaignParticipantsQuery(campaignId: () => string) {
	return createQuery({
		get queryKey() { return ['performance', 'campaigns', campaignId(), 'participants'] as const; },
		queryFn: () => performanceService.listParticipantsDetail(campaignId()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		enabled: () => !!campaignId(),
	});
}

export function useCampaignEvaluatorsQuery(campaignId: () => string) {
	return createQuery({
		get queryKey() { return ['performance', 'campaigns', campaignId(), 'evaluators'] as const; },
		queryFn: () => performanceService.listEvaluatorsDetail(campaignId()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		enabled: () => !!campaignId(),
	});
}

// ---------------------------------------
//  REVIEW QUERIES
// ---------------------------------------

export function useReviewDetailQuery(reviewId: () => string) {
	return createQuery({
		get queryKey() { return performanceQueryKeys.detail(reviewId()); },
		queryFn: () => performanceService.getReview(reviewId()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		enabled: () => !!reviewId(),
	});
}

export function useEmployeeReviewsQuery(
	employeeId: () => string,
	page: () => number = () => 1,
	filters: () => { search?: string; status?: string } = () => ({})
) {
	return createQuery({
		get queryKey() { return performanceQueryKeys.employeeReviews(employeeId(), page(), filters().status); },
		queryFn: () => performanceService.listReviews(employeeId(), page(), filters()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		refetchOnWindowFocus: true,
		refetchOnReconnect: true,
		enabled: () => !!employeeId(),
	});
}

export function useAllReviewsQuery(
	page: () => number = () => 1,
	filters: () => { search?: string; status?: string; campaign_id?: string } = () => ({})
) {
	return createQuery({
		get queryKey() { return ['performance', 'reviews', 'all', page(), filters()] as const; },
		queryFn: () => performanceService.listAllReviews(page(), filters()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		refetchOnWindowFocus: true,
		refetchOnReconnect: true,
	});
}

export function usePendingReviewsQuery(
	reviewerId: () => string,
	page: () => number = () => 1
) {
	return createQuery({
		get queryKey() { return performanceQueryKeys.pendingReviews(reviewerId(), page()); },
		queryFn: () => performanceService.listPendingReviews(reviewerId(), page()),
		staleTime: 1000 * 60 * 2,
		gcTime: 1000 * 60 * 5,
		refetchOnWindowFocus: true,
		refetchOnReconnect: true,
		enabled: () => !!reviewerId(),
	});
}

// ---------------------------------------
//  CAMPAIGN MUTATIONS
// ---------------------------------------

export function useCreateCampaignMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (data: Parameters<typeof performanceService.createCampaign>[0]) =>
			performanceService.createCampaign(data),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.campaigns });
			notification.toast.success('Campagne créée avec succès');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useUpdateCampaignMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: ({ campaignId, data }: { campaignId: string; data: Parameters<typeof performanceService.updateCampaign>[1] }) =>
			performanceService.updateCampaign(campaignId, data),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.campaigns });
			notification.toast.success('Campagne mise à jour');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useActivateCampaignMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (campaignId: string) => performanceService.activateCampaign(campaignId),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Campagne activée');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useCloseCampaignMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (campaignId: string) => performanceService.closeCampaign(campaignId),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Campagne clôturée');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useDeleteCampaignMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (campaignId: string) => performanceService.deleteCampaign(campaignId),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.campaigns });
			notification.toast.success('Campagne supprimée');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

// --------------------------------------
//  REVIEW MUTATIONS
// --------------------------------------

export function useCreateReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (data: Parameters<typeof performanceService.createReview>[0]) =>
			performanceService.createReview(data),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Évaluation créée avec succès');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useUpdateEmployeeReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: ({ reviewId, data }: {
			reviewId: string;
			data: Parameters<typeof performanceService.updateEmployeeReview>[1];
		}) => performanceService.updateEmployeeReview(reviewId, data),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Auto-évaluation mise à jour');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useUpdateManagerReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: ({ reviewId, data }: {
			reviewId: string;
			data: Parameters<typeof performanceService.updateManagerReview>[1];
		}) => performanceService.updateManagerReview(reviewId, data),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Évaluation évaluateur mise à jour');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useDeleteReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (reviewId: string) => performanceService.deleteReview(reviewId),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: ['performance', 'reviews'] });
			notification.toast.success('Évaluation supprimée');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useSubmitEmployeeReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (reviewId: string) => performanceService.submitEmployeeReview(reviewId),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success("Auto-évaluation soumise à l'évaluateur");
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useSubmitManagerReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (reviewId: string) => performanceService.submitManagerReview(reviewId),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Évaluation soumise pour calibrage');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useCalibrateReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: ({ reviewId, data }: {
			reviewId: string;
			data: { calibrated_score: number; reason: string };
		}) => performanceService.calibrateReview(reviewId, data),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Évaluation calibrée');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useAcknowledgeReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (reviewId: string) => performanceService.acknowledgeReview(reviewId),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Évaluation approuvée');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

export function useDisputeReviewMutation() {
	const queryClient = useQueryClient();
	return createMutation({
		mutationFn: (args: { reviewId: string; reason?: string }) =>
			performanceService.disputeReview(args.reviewId, { reason: args.reason }),
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: performanceQueryKeys.all });
			notification.toast.success('Évaluation contestée — RH notifié');
		},
		onError: (error) => { notification.toast.error(getFriendlyErrorMessage(error)); },
	});
}

/**
 * Helper pour synchroniser le store des campagnes avec les données de la query.
 * À utiliser DANS un $effect dans un composant .svelte.
 *
 * Exemple :
 * ```svelte
 * $effect(() => {
 *   syncCampaignsStore($campaignsQuery);
 * });
 * ```
 */
export function syncCampaignsStore(query: any) {
	const data = query.data as { results: Campaign[]; count: number } | undefined;
	if (data) {
		const perPage = campaignStore.perPage;
		const totalPages = Math.ceil(data.count / perPage) || 1;
		campaignStore.setMetadata(data.count, totalPages);
	}

	campaignStore.setLoading(query.isLoading as boolean);

	const error = query.error as Error | undefined;
	if (error) {
		campaignStore.setError(getFriendlyErrorMessage(error));
	} else {
		campaignStore.setError(null);
	}
}

/**
 * Helper pour synchroniser le store des évaluations avec les données de la query.
 * À utiliser DANS un $effect dans un composant .svelte.
 *
 * Exemple :
 * ```svelte
 * $effect(() => {
 *   syncReviewsStore($reviewsQuery);
 * });
 * ```
 */
export function syncReviewsStore(query: any) {
	const data = query.data as { results: PerformanceReview[]; count: number } | undefined;
	if (data) {
		const perPage = reviewsStore.perPage;
		const totalPages = Math.ceil(data.count / perPage) || 1;
		reviewsStore.setMetadata(data.count, totalPages);
	}

	reviewsStore.setLoading(query.isLoading as boolean);

	const error = query.error as Error | undefined;
	if (error) {
		reviewsStore.setError(getFriendlyErrorMessage(error));
	} else {
		reviewsStore.setError(null);
	}
}

