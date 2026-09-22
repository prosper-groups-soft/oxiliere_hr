/**
 * payrollHooks.ts — Hooks TanStack Query pour les éléments de paie du contrat (S10).
 *
 * Suit le pattern du codebase (createQuery / createMutation + useQueryClient)
 * utilisé par leaves/performance/recruitment.
 */
import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { fetchContractPayElements, createContractPayElement, patchContractPayElement, deleteContractPayElement } from './payroll';
import type { ContractPayElementInput, ContractPayElementItem, ContractPayElementSummary, PayrollAdjustmentConfig } from '../types/types';
import { payrollQueryOptions } from './payroll';


/** Query des éléments de paie d'un contrat (S10) */
export function useContractPayElementsQuery(contractId: () => string) {
  return createQuery({
    get queryKey() {
      return payrollQueryOptions.contractPayElements(contractId()).queryKey;
    },
    queryFn: () => fetchContractPayElements(contractId()),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
    enabled: !!contractId(),
  });
}

/** Query du catalogue des ajustements (payroll adjustments types) */
export function usePayrollAdjustmentsQuery() {
  return createQuery<PayrollAdjustmentConfig[]>({
    get queryKey() {
      return payrollQueryOptions.adjustments().queryKey;
    },
    queryFn: () => payrollQueryOptions.adjustments().queryFn(),
    staleTime: 1000 * 60 * 15,
    gcTime: 1000 * 60 * 30,
  });
}

/** Mutation : ajouter un élément de paie à un contrat (S10) */
export function useCreateContractPayElementMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      contractId,
      data,
    }: {
      contractId: string;
      data: ContractPayElementInput;
    }) => createContractPayElement(contractId, data),
    onSuccess: async (_data, variables) => {
      await queryClient.invalidateQueries({
        queryKey: payrollQueryOptions.contractPayElements(variables.contractId).queryKey,
      });
      notification.toast.success('Élément de paie ajouté au contrat');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}

/** Mutation : mettre à jour un élément de paie (toggle actif, montant, période) (S10) */
export function usePatchContractPayElementMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      contractId,
      elementId,
      data,
    }: {
      contractId: string;
      elementId: string;
      data: Partial<ContractPayElementItem>;
    }) => patchContractPayElement(contractId, elementId, data),
    onSuccess: async (_data, variables) => {
      await queryClient.invalidateQueries({
        queryKey: payrollQueryOptions.contractPayElements(variables.contractId).queryKey,
      });
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}

/** Mutation : retirer un élément de paie d'un contrat (S10) */
export function useDeleteContractPayElementMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ contractId, elementId }: { contractId: string; elementId: string }) =>
      deleteContractPayElement(contractId, elementId),
    onSuccess: async (_data, variables) => {
      await queryClient.invalidateQueries({
        queryKey: payrollQueryOptions.contractPayElements(variables.contractId).queryKey,
      });
      notification.toast.success('Élément retiré du contrat');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


export type { ContractPayElementSummary };

