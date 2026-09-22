import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { recruitmentService } from '../services/recruitmentService';
import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import type { RecruitmentCampaign, Candidate, Interview } from '../types/types';
import type { JobOfferUpdate } from '../api/recruitment.endpoints';
import { recruitmentStore } from '../stores/recruitment.svelte';


// QUERY KEYS - Cache invalidation strategy
export const recruitmentQueryKeys = {
	all: ['recruitment'] as const,
	jobOffers: (page?: number, limit?: number, orgUnitId?: number, isActive?: boolean, search?: string, status?: string, jobNames?: string[], sortBy?: string, sortOrder?: string) =>
		[...recruitmentQueryKeys.all, 'jobOffers', page ?? 1, limit ?? 50, orgUnitId, isActive, search, status, jobNames, sortBy ?? 'title', sortOrder ?? 'asc'] as const,
	applications: (offerId: string, page?: number, limit?: number, search?: string, status?: string[], source?: string[], priority?: string[], positionId?: string[], gender?: string[]) =>
		[...recruitmentQueryKeys.all, 'applications', offerId, page ?? 1, limit ?? 50, search, status, source, priority, positionId, gender] as const,
	interviews: (offerId?: string, page?: number, limit?: number) =>
		[...recruitmentQueryKeys.all, 'interviews', offerId ?? '', page ?? 1, limit ?? 50] as const,
	detail: (id: string) => [...recruitmentQueryKeys.all, 'detail', id] as const,
	candidates: ['recruitment', 'candidates'] as const,
};

/**
 * Query for fetching job offers with pagination and filters
 * Auto-refetch on window focus, auto-cached for 5 minutes
 */
export function useJobOffersQuery(
	page: () => number = () => 1,
	limit: () => number = () => 50,
	orgUnitId: () => number | undefined = () => undefined,
	isActive: () => boolean = () => true,
	search: () => string = () => '',
	status: () => string = () => '',
	jobNames: () => string[] = () => [],
	sortBy: () => string = () => 'title',
	sortOrder: () => 'asc' | 'desc' = () => 'asc'
) {
	return createQuery({
		get queryKey() {
			return recruitmentQueryKeys.jobOffers(page(), limit(), orgUnitId(), isActive(), search(), status(), jobNames(), sortBy(), sortOrder());
		},
		queryFn: () => recruitmentService.listJobOffers(page(), limit(), orgUnitId(), isActive(), search(), status(), jobNames(), sortBy(), sortOrder()),
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 10, // 10 minutes (garbage collection)
		refetchOnWindowFocus: true,
		refetchOnReconnect: true,
	});
}

/**
 * Query for fetching applications with pagination
 */
export function useApplicationsQuery(
	offerId: () => string,
	page: () => number = () => 1,
	limit: () => number = () => 50
) {
	return createQuery({
		get queryKey() {
			return recruitmentQueryKeys.applications(offerId(), page(), limit());
		},
		queryFn: () => recruitmentService.listApplications(offerId(), page(), limit()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		refetchOnWindowFocus: true,
		refetchOnReconnect: true,
	});
}

/**
 * Query for fetching interviews with pagination
 */
export function useInterviewsQuery(
	offerId: () => string | undefined = () => undefined,
	page: () => number = () => 1,
	limit: () => number = () => 50
) {
	return createQuery({
		get queryKey() {
			return recruitmentQueryKeys.interviews(offerId(), page(), limit());
		},
		queryFn: () => recruitmentService.listInterviews(offerId() ?? '', page(), limit()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		refetchOnWindowFocus: true,
		refetchOnReconnect: true,
		get enabled() {
			return offerId() !== undefined && offerId() !== '';
		},
	});
}

/**
 * Mutation for creating a new job offer
 */
export function useCreateJobOfferMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: (data: any) => recruitmentService.createJobOffer(data),

		onSuccess: async (newJobOffer) => {
			// Invalidate and refetch list
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});

			notification.toast.success('Offre d\'emploi créée avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for updating a job offer
 */
export function useUpdateJobOfferMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ offerId, data }: { offerId: string; data: JobOfferUpdate }) =>
			recruitmentService.updateJobOffer(offerId, data),

		onSuccess: async () => {
			// Invalidate and refetch list
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});

			notification.toast.success('Offre mise à jour avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for publishing a job offer
 */
export function usePublishJobOfferMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: (offerId: string) => recruitmentService.publishJobOffer(offerId),

		onSuccess: async () => {
			// Invalidate and refetch list
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});

			notification.toast.success('Offre publiée avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for closing a job offer
 */
export function useCloseJobOfferMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: (offerId: string) => recruitmentService.closeJobOffer(offerId),

		onSuccess: async () => {
			// Invalidate and refetch list
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});

			notification.toast.success('Offre fermée avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for updating application status
 */
export function useUpdateApplicationStatusMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ applicationId, newStatus }: { applicationId: string; newStatus: string }) =>
			recruitmentService.updateApplicationStatus(applicationId, newStatus),

		onSuccess: async () => {
			// Invalidate and refetch applications (toutes les offres)
			await queryClient.invalidateQueries({
				queryKey: ['recruitment', 'applications']
			});

			notification.toast.success('Statut mis à jour avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for scheduling an interview
 */
export function useScheduleInterviewMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: (data: any) => recruitmentService.scheduleInterview(data),

		onSuccess: async (newInterview) => {
			// Invalidate and refetch interviews
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.interviews()
			});

			// Update store directly so reactive views update immediately
			if (newInterview) {
				recruitmentStore.interviews = [...recruitmentStore.interviews, newInterview];
			}

			notification.toast.success('Entretien planifié avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for submitting interview feedback
 */
export function useSubmitInterviewFeedbackMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ interviewId, data }: { interviewId: string; data: { score: number; feedback?: string; strengths?: string[]; weaknesses?: string[]; wouldHire?: boolean; nextSteps?: string; status: string } }) =>
			recruitmentService.submitInterviewFeedback(interviewId, data),

		onSuccess: async (updatedInterview) => {
			// Update store immediately for reactive views
			if (updatedInterview) {
				recruitmentStore.interviews = recruitmentStore.interviews.map(i =>
					i.id === updatedInterview.id ? updatedInterview : i
				);
			}
			// Invalidate and refetch interviews
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.interviews()
			});
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for updating an interview
 */
export function useUpdateInterviewMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ interviewId, data }: { interviewId: string; data: Partial<Interview> }) =>
			recruitmentService.updateInterview(interviewId, data),

		onSuccess: async (updatedInterview, variables) => {
			// Invalidate and refetch interviews
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.interviews()
			});

			// Update store directly so reactive views update immediately
			// Preserve fields not returned by backend PATCH response (e.g. duration_minutes)
			if (updatedInterview) {
				recruitmentStore.interviews = recruitmentStore.interviews.map(i =>
					i.id === updatedInterview.id
						? {
								...updatedInterview,
								duration: variables.data.duration ?? updatedInterview.duration,
							}
						: i
				);
			}

			notification.toast.success('Entretien mis à jour avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

// ==========================================
// CANDIDATE MUTATIONS (TanStack Query pattern, same as CampaignSheet)
// ==========================================

/**
 * Mutation for creating a new candidate (application)
 */
export function useCreateCandidateMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: (data: any) => recruitmentService.create(data),

		onSuccess: async (newCandidate) => {
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});

			notification.toast.success('Candidat ajouté avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for updating a candidate profile
 */
export function useUpdateCandidateMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ candidateId, data }: { candidateId: string; data: any }) =>
			recruitmentService.update(candidateId, data),

		onSuccess: async () => {
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});

			notification.toast.success('Candidat mis à jour avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for uploading candidate photo
 */
export function useUploadCandidatePhotoMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ candidateId, file }: { candidateId: string; file: File }) =>
			recruitmentService.uploadPhoto(candidateId, file),

		onSuccess: async () => {
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for uploading candidate resume
 */
export function useUploadCandidateResumeMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ candidateId, file }: { candidateId: string; file: File }) =>
			recruitmentService.uploadResume(candidateId, file),

		onSuccess: async () => {
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for updating application evaluation scores
 */
export function useUpdateApplicationEvaluationMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ applicationId, data }: { applicationId: string; data: { scores?: Record<string, number>; evaluationNotes?: string } }) =>
			recruitmentService.updateApplicationEvaluation(applicationId, data),

		onSuccess: async () => {
			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});

			notification.toast.success('Évaluation mise à jour');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Mutation for updating application offer details
 */
export function useUpdateApplicationOfferMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: ({ applicationId, data }: { applicationId: string; data: { salaryMin?: number; salaryMax?: number; salaryCurrency?: string; offerStartDate?: string } }) =>
			recruitmentService.updateApplicationOffer(applicationId, data),

		onSuccess: async (result: any, variables) => {
			// Update store directly so reactive UI refreshes immediately
			const { salary_min, salary_max, salary_currency, offer_start_date } = result || {};
			recruitmentStore.candidates = recruitmentStore.candidates.map(c => {
				const updatedApps = (c.applications || []).map(a => {
					if (a.applicationId === variables.applicationId) {
						return {
							...a,
							salaryMin: salary_min ?? variables.data.salaryMin,
							salaryMax: salary_max ?? variables.data.salaryMax,
							salaryCurrency: salary_currency ?? variables.data.salaryCurrency,
							offerStartDate: offer_start_date ?? variables.data.offerStartDate,
							// Also update stage to OFFER
							currentStage: 'OFFER' as any,
						};
					}
					return a;
				});
				// If any app was updated, also update the candidate's currentStage
				const hasUpdatedApp = updatedApps.some(a => a.applicationId === variables.applicationId);
				return {
					...c,
					applications: updatedApps,
					currentStage: hasUpdatedApp ? 'OFFER' as any : c.currentStage,
				};
			});

			await queryClient.invalidateQueries({
				queryKey: recruitmentQueryKeys.all
			});

			notification.toast.success('Offre enregistrée avec succès');
		},

		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		},
	});
}

/**
 * Helper pour synchroniser le store avec les données de la query
 * À utiliser DANS un $effect dans un composant .svelte
 *
 * Exemple d'utilisation:
 * ```svelte
 * <script>
 *   const query = useJobOffersQuery(() => 1, () => 50);
 *
 *   $effect(() => {
 *     syncRecruitmentStore(query);
 *   });
 * </script>
 * ```
 */
export function syncRecruitmentStore(query: any) {
	const data = query.data as { results: RecruitmentCampaign[]; count: number } | undefined;
	if (data) {
		// Calculer le nombre de pages basé sur le perPage actuel du store
		const perPage = recruitmentStore.perPage;
		const totalPages = Math.ceil(data.count / perPage) || 1;
		recruitmentStore.setJobOffers(data.results, data.count, totalPages);
	}

	recruitmentStore.setLoading(query.isLoading as boolean);

	const error = query.error as Error | undefined;
	if (error) {
		recruitmentStore.setError(getFriendlyErrorMessage(error));
	} else {
		recruitmentStore.setError(null);
	}
}

/**
 * Helper pour synchroniser les interviews du store avec la query
 */
export function syncInterviewsToStore(query: any) {
	const data = query.data as { results: any[]; count: number } | undefined;
	if (data) {
		recruitmentStore.interviews = data.results;
	}
}

/**
 * Helper pour synchroniser les candidats du store avec la query applications
 */
export function syncRecruitmentCandidates(query: any) {
	const data = query.data as { results: Candidate[]; count: number } | undefined;
	if (data) {
		recruitmentStore.candidates = data.results;
	}

	recruitmentStore.setLoading(query.isLoading as boolean);

	const error = query.error as Error | undefined;
	if (error) {
		recruitmentStore.setError(getFriendlyErrorMessage(error));
	} else {
		recruitmentStore.setError(null);
	}
}

/**
 * Query pour récupérer les candidats d'une offre (campagne)
 */
export function useCandidatesQuery(
	offerId: () => string | undefined,
	page: () => number = () => 1,
	limit: () => number = () => 100,
	search: () => string = () => '',
	status: () => string[] = () => [],
	source: () => string[] = () => [],
	priority: () => string[] = () => [],
	positionId: () => string[] = () => [],
	gender: () => string[] = () => []
) {
	return createQuery({
		get queryKey() {
			return recruitmentQueryKeys.applications(offerId()!, page(), limit(), search(), status(), source(), priority(), positionId(), gender());
		},
		queryFn: () => recruitmentService.listCandidatesWithApplications(offerId()!, page(), limit(), search() || undefined, status(), source(), priority(), positionId(), gender()),
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10,
		refetchOnWindowFocus: true,
		refetchOnReconnect: true,
		get enabled() {
			return offerId() !== undefined;
		},
	});
}

/**
 * Hook to refresh job offers list
 */
export function useRefreshJobOffers() {
	const queryClient = useQueryClient();

	return async () => {
		await queryClient.invalidateQueries({
			queryKey: recruitmentQueryKeys.jobOffers()
		});
		await queryClient.refetchQueries({
			queryKey: recruitmentQueryKeys.jobOffers(),
			type: 'active'
		});
	};
}
