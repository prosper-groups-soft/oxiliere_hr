import {
	createQuery,
	createMutation,
	useQueryClient
} from '@tanstack/svelte-query';
import { onboardingService } from '../services/onboarding.service';
import type { OnboardingSubmitData } from '../types/types';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';


// QUERY KEYS
export const onboardingQueryKeys = {
	all: ['onboarding'] as const,
	positions: () => [...onboardingQueryKeys.all, 'positions'] as const,
	seniorityLevels: (positionId: string) =>
		[...onboardingQueryKeys.all, 'seniority-levels', positionId] as const
};


/**
 * Query pour récupérer toutes les positions disponibles
 * Utilisé dans le step Contract
 */
export function usePositionsQuery() {
	return createQuery({
		queryKey: onboardingQueryKeys.positions(),
		queryFn: () => onboardingService.getPositions(),
		staleTime: 1000 * 60 * 5, // 5 minutes
		gcTime: 1000 * 60 * 10
	});
}


/**
 * Query pour récupérer les niveaux de séniorité d'une position
 * Utilisé quand une position est sélectionnée
 */
export function useSeniorityLevelsQuery(positionId: string | null) {
	return createQuery({
		queryKey: onboardingQueryKeys.seniorityLevels(positionId || ''),
		queryFn: () => {
			if (!positionId) return [];
			return onboardingService.getPositionSeniorityLevels(positionId);
		},
		enabled: !!positionId,
		staleTime: 1000 * 60 * 5,
		gcTime: 1000 * 60 * 10
	});
}


/**
 * Mutation pour soumettre l'onboarding complet
 * À utiliser dans le composant de finalisation
 */
export function useOnboardingMutation() {
	const queryClient = useQueryClient();

	return createMutation({
		mutationFn: (data: OnboardingSubmitData) =>
			onboardingService.submitFullOnboarding(data),
		onSuccess: async (result) => {
			if (result.success && result.employee) {
				// Invalider le cache des employés
				await queryClient.invalidateQueries({
					queryKey: ['employees']
				});

				notification.toast.success(
					`Employé ${result.employee.matricule} onboardé avec succès`
				);
			}
		},
		onError: (error) => {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(`Échec de l'onboarding: ${message}`);
		}
	});
}
