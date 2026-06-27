import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { vacancyService } from '../services/vacancy.service';
import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { jobsStore } from '../stores/jobs.svelte';
import type { Vacancy, VacancyPriority, VacancyStatus } from '../types/types';
import type { PaginatedResponse } from '@/types/pagination';


// QUERY KEYS - Cache invalidation strategy
export const vacancyQueryKeys = {
	all: ['vacancies'] as const,
	list: (page?: number, perPage?: number, search?: string, priority?: VacancyPriority | null, status?: VacancyStatus | null) =>
		[...vacancyQueryKeys.all, 'list', page ?? 1, perPage ?? 8, search ?? '', priority ?? '', status ?? ''] as const,
	detail: (id: string) => [...vacancyQueryKeys.all, 'detail', id] as const
};


/**
 * Query for fetching paginated vacancies with search and filters
 */
export function useVacanciesQuery(
	page: () => number,
	perPage: () => number = () => 8,
	search: () => string = () => '',
	priority: () => VacancyPriority | null = () => null,
	status: () => VacancyStatus | null = () => null
) {
	return createQuery({
		get queryKey() {
			return vacancyQueryKeys.list(page(), perPage(), search(), priority(), status());
		},
		queryFn: () => vacancyService.listVacancies({
			page: page(),
			per_page: perPage(),
			search: search(),
			priority: priority() || undefined,
			status: status() || undefined
		}),
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 10,   // 10 minutes
		refetchOnWindowFocus: true,
		refetchOnReconnect: true
	});
}


/**
 * Query for fetching all vacancies without pagination (for select dropdowns)
 */
export function useAllVacancies() {
	return createQuery({
		queryKey: ['vacancies', 'all'],
		queryFn: () => vacancyService.listVacancies({ page: 1, per_page: 200 }),
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 10,   // 10 minutes
		refetchOnWindowFocus: false,
		refetchOnReconnect: true,
	});
}


/**
 * Hook pour synchroniser les vacancies avec le jobsStore
 * À utiliser dans un $effect
 */
export function syncVacancies(query: any) {
	const data = query.data as PaginatedResponse<Vacancy> | undefined;
	if (data) {
		jobsStore.setVacancies(data.results);
	}
}


/**
 * Mutation pour créer une vacancy
 */
export function useCreateVacancyMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: async (data: {
			position_id: string;
			priority: VacancyPriority;
			status: VacancyStatus;
			opened_date?: string;
			target_date?: string | null;
			reason?: string;
		}) => {
			return await vacancyService.createVacancy(data);
		},
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: vacancyQueryKeys.all });
		},
		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		}
	});
}


/**
 * Mutation pour mettre à jour une vacancy
 */
export function useUpdateVacancyMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: async ({
			id,
			data
		}: {
			id: string;
			data: Partial<{
				position_id: string;
				priority: VacancyPriority;
				status: VacancyStatus;
				opened_date: string;
				target_date: string | null;
				reason: string;
				filled_date: string | null;
			}>;
		}) => {
			return await vacancyService.updateVacancy(id, data);
		},
		onSuccess: async (_, variables) => {
			await queryClient.invalidateQueries({
				queryKey: vacancyQueryKeys.detail(variables.id)
			});
			await queryClient.invalidateQueries({ queryKey: vacancyQueryKeys.all });
		},
		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		}
	});
}


/**
 * Mutation pour supprimer une vacancy
 */
export function useDeleteVacancyMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: async (id: string) => {
			await vacancyService.deleteVacancy(id);
			return id;
		},
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: vacancyQueryKeys.all });
		},
		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		}
	});
}


/**
 * Mutation pour clôturer une vacancy (marquer comme pourvue)
 */
export function useCloseVacancyMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: async ({ id, transition_id }: { id: string; transition_id?: string }) => {
			return await vacancyService.closeVacancy(id, transition_id);
		},
		onSuccess: async () => {
			await queryClient.invalidateQueries({ queryKey: vacancyQueryKeys.all });
		},
		onError: (error) => {
			notification.toast.error(getFriendlyErrorMessage(error));
		}
	});
}

