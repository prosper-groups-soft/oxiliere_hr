import { 
  createQuery, 
  createMutation, 
  useQueryClient 
} from '@tanstack/svelte-query';
import { jobService } from '../services/job.service';
import { jobsStore } from '../stores/jobs.svelte';
import type { 
  JobPositionCreate, 
  JobPositionUpdate,
  SeniorityLevelDefinition,
  ProfessionalCategory
} from '../types/types';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';


// QUERY KEYS
export const jobQueryKeys = {
  all: ['jobs'] as const,
  families: () => [...jobQueryKeys.all, 'families'] as const,
  positions: () => [...jobQueryKeys.all, 'positions'] as const,
  seniorityLevels: () => [...jobQueryKeys.all, 'seniority-levels'] as const,
  careerPath: (familyId: string) => [...jobQueryKeys.all, 'career-path', familyId] as const,
  professionalCategories: () => [...jobQueryKeys.all, 'professional-categories'] as const,
};


/**
 * Hook pour synchroniser les niveaux de séniorité depuis le backend
 */
export function useSeniorityLevelsQuery() {
  return createQuery({
    queryKey: jobQueryKeys.seniorityLevels(),
    queryFn: () => {
      return jobService.getSeniorityLevels();
    },
    staleTime: 1000 * 60 * 60 * 24,  // 24h
    gcTime: 1000 * 60 * 60 * 24 * 7, // 7j
  });
}


/**
 * Hook pour synchroniser le jobsStore avec les niveaux de séniorité
 * À utiliser dans un $effect dans le composant
 */
export function syncSeniorityLevels(query: any) {
  const data = query.data as SeniorityLevelDefinition[] | undefined;
  if (data?.length) {
    jobsStore.setSeniorityLevels(data);
  }
}


/**
 * Query pour récupérer toutes les positions
 */
export function usePositionsQuery() {
  return createQuery({
    queryKey: jobQueryKeys.positions(),
    queryFn: () => jobService.getPositions(),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
  });
}


/**
 * Query pour récupérer le parcours de carrière d'une famille
 */
export function useCareerPathQuery(familyId: string) {
  return createQuery({
    queryKey: jobQueryKeys.careerPath(familyId),
    queryFn: () => jobService.getCareerPath(familyId),
    enabled: !!familyId,
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
  });
}


/**
 * Mutation pour créer une position
 */
export function useCreatePositionMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: JobPositionCreate) => jobService.createPosition(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.positions() });
      notification.toast.success('Position créée');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour mettre à jour une position
 */
export function useUpdatePositionMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ id, data }: { id: string; data: JobPositionUpdate }) => 
      jobService.updatePosition(id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.positions() });
      notification.toast.success('Position mise à jour');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour supprimer une position
 */
export function useDeletePositionMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (id: string) => jobService.deletePosition(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.positions() });
      notification.toast.success('Position supprimée');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour créer un niveau de séniorité
 */
export function useCreateSeniorityLevelMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: Omit<SeniorityLevelDefinition, 'id'>) => 
      jobService.createSeniorityLevel(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.seniorityLevels() });
      notification.toast.success('Niveau de séniorité créé');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour mettre à jour un niveau de séniorité
 */
export function useUpdateSeniorityLevelMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ 
      id, 
      data, 
      originalLevel 
    }: { 
      id: string; 
      data: Partial<Omit<SeniorityLevelDefinition, 'id'>>;
      originalLevel?: SeniorityLevelDefinition;
    }) => jobService.updateSeniorityLevel(id, data, originalLevel),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.seniorityLevels() });
      notification.toast.success('Niveau de séniorité mis à jour');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour supprimer un niveau de séniorité
 */
export function useDeleteSeniorityLevelMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (id: string) => jobService.deleteSeniorityLevel(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.seniorityLevels() });
      notification.toast.success('Niveau de séniorité supprimé');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour réinitialiser tous les niveaux de séniorité
 */
export function useResetSeniorityLevelsMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: () => jobService.resetSeniorityLevels(),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.seniorityLevels() });
      notification.toast.success('Niveaux de séniorité réinitialisés aux valeurs par défaut');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Query pour récupérer toutes les familles de métiers
 */
export function useJobFamiliesQuery() {
  return createQuery({
    queryKey: jobQueryKeys.families(),
    queryFn: () => jobService.getJobFamilies(),
    staleTime: 1000 * 60 * 60, // 1h
    gcTime: 1000 * 60 * 60 * 24,
  });
}


/**
 * Mutation pour créer une famille de métiers
 */
export function useCreateJobFamilyMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: { name: string; description?: string }) => 
      jobService.createJobFamily(data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.families() });
      notification.toast.success('Famille de métiers créée');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour mettre à jour une famille de métiers
 */
export function useUpdateJobFamilyMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ id, data }: { id: string; data: Partial<{ name: string; description: string }> }) => 
      jobService.updateJobFamily(id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.families() });
      notification.toast.success('Famille de métiers mise à jour');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour supprimer une famille de métiers
 */
export function useDeleteJobFamilyMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (id: string) => jobService.deleteJobFamily(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: jobQueryKeys.families() });
      notification.toast.success('Famille de métiers supprimée');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Query pour récupérer la grille des catégories professionnelles
 */
export function useProfessionalCategoriesQuery() {
  return createQuery({
    queryKey: jobQueryKeys.professionalCategories(),
    queryFn: () => jobService.getProfessionalCategories(),
    staleTime: 1000 * 60 * 60, // 1h
    gcTime: 1000 * 60 * 60 * 24,
  });
}

