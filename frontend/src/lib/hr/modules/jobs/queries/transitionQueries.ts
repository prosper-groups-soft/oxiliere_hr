import {
  createQuery,
  createMutation,
  useQueryClient
} from '@tanstack/svelte-query';
import { transitionService } from '../services/transition.service';
import { jobsStore } from '../stores/jobs.svelte';
import type {
  Transition,
  TransitionType
} from '../types/types';
import type { PaginatedResponse } from '@/hr/types/pagination';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';


// QUERY KEYS
export const transitionQueryKeys = {
  all: ['transitions'] as const,
  list: () => [...transitionQueryKeys.all, 'list'] as const,
  employee: (employeeId: string) => [...transitionQueryKeys.all, 'employee', employeeId] as const,
  detail: (id: string) => [...transitionQueryKeys.all, 'detail', id] as const,
};


/**
 * Hook pour récupérer toutes les transitions (avec pagination, filtre type et recherche)
 */
export function useTransitionsQuery(
  page: () => number = () => 1,
  pageSize: () => number = () => 10,
  employeeId?: () => string | null,
  transitionType?: () => TransitionType | null,
  search?: () => string | null
) {
  return createQuery({
    get queryKey() {
      const empId = employeeId?.();
      const type = transitionType?.();
      const s = search?.();
      const p = page();
      const ps = pageSize();
      return empId
        ? [...transitionQueryKeys.employee(empId), p, ps, type, s]
        : [...transitionQueryKeys.list(), p, ps, type, s];
    },
    queryFn: () => {
      const empId = employeeId?.() || undefined;
      const type = transitionType?.() || undefined;
      const s = search?.() || undefined;
      return transitionService.listTransitions(empId, type, page(), pageSize(), s);
    },
    staleTime: 1000 * 60 * 5,   // 5 minutes
    gcTime: 1000 * 60 * 10,     // 10 minutes
  });
}


/**
 * Hook pour récupérer les transitions d'un employé spécifique
 */
export function useEmployeeTransitionsQuery(employeeId: () => string) {
  return createQuery({
    get queryKey() {
      return transitionQueryKeys.employee(employeeId());
    },
    queryFn: () => transitionService.getEmployeeTransitions(employeeId()),
    enabled: () => !!employeeId(),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
  });
}


/**
 * Hook pour récupérer une transition par ID
 */
export function useTransitionQuery(id: () => string | null) {
  return createQuery({
    get queryKey() {
      const tid = id();
      return tid ? transitionQueryKeys.detail(tid) : transitionQueryKeys.list();
    },
    queryFn: () => {
      const tid = id();
      if (!tid) throw new Error('Transition ID is required');
      return transitionService.getTransition(tid);
    },
    enabled: () => !!id(),
    staleTime: 1000 * 60 * 5,
  });
}


/**
 * Hook pour synchroniser les transitions avec le jobsStore
 * À utiliser dans un $effect
 * Supporte PaginatedResponse ou Transition[]
 */
export function syncTransitions(query: any) {
  const data = query.data as PaginatedResponse<Transition> | Transition[] | undefined;
  if (data) {
    const transitions = Array.isArray(data) ? data : data.results;
    jobsStore.setTransitions(transitions);
  }
}


/**
 * Mutation pour créer une transition
 */
export function useCreateTransitionMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: async (data: {
      employee_id: string;
      transition_type: TransitionType;
      from_position_id?: string | null;
      from_seniority_level_id?: string | null;
      to_position_id?: string | null;
      to_seniority_level_id?: string | null;
      date?: string;
      reason?: string;
    }) => {
      return await transitionService.createTransition(data);
    },
    onSuccess: async (newTransition) => {
      // Invalider les queries pour forcer un rafraîchissement
      await queryClient.invalidateQueries({ queryKey: transitionQueryKeys.all });

      // Mettre à jour le store
      jobsStore.addTransition(newTransition);
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    }
  });
}


/**
 * Mutation pour mettre à jour une transition
 */
export function useUpdateTransitionMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: async ({
      id,
      data
    }: {
      id: string;
      data: Partial<{
        transition_type: TransitionType;
        from_position_id: string | null;
        from_seniority_level_id: string | null;
        to_position_id: string | null;
        to_seniority_level_id: string | null;
        date: string;
        reason: string;
      }>
    }) => {
      return await transitionService.updateTransition(id, data);
    },
    onSuccess: async (updatedTransition, variables) => {
      // Invalider les queries
      await queryClient.invalidateQueries({
        queryKey: transitionQueryKeys.detail(variables.id)
      });
      await queryClient.invalidateQueries({
        queryKey: transitionQueryKeys.all
      });

      // Mettre à jour le store
      jobsStore.updateTransition(variables.id, updatedTransition);
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    }
  });
}


/**
 * Mutation pour supprimer une transition
 */
export function useDeleteTransitionMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: async (id: string) => {
      await transitionService.deleteTransition(id);
      return id;
    },
    onSuccess: async (deletedId) => {
      // Invalider les queries
      await queryClient.invalidateQueries({ queryKey: transitionQueryKeys.all });
      
      // Mettre à jour le store
      jobsStore.deleteTransition(deletedId);
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    }
  });
}

