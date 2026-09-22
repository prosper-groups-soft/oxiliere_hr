import { 
  createQuery, 
  createMutation, 
  useQueryClient 
} from '@tanstack/svelte-query';
import { orgService } from '../services/org.service';
import { jobsStore } from '../stores/jobs.svelte';
import type { 
  OrgUnitCreate, 
  OrgUnitUpdate, 
  OrgTreeNode,
  OrgUnit 
} from '../types/org.types';
import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';


// QUERY KEYS
export const orgQueryKeys = {
  all: ['org'] as const,
  tree: () => [...orgQueryKeys.all, 'tree'] as const,
  list: (page?: number, limit?: number, search?: string) =>
    [...orgQueryKeys.all, 'list', page ?? 1, limit ?? 200, search ?? ''] as const,
  detail: (id: string) => [...orgQueryKeys.all, 'detail', id] as const,
  positions: (orgUnitId: string) => [...orgQueryKeys.all, 'positions', orgUnitId] as const,
};


/**
 * Hook pour synchroniser le jobsStore avec l'arbre organisationnel
 * À utiliser dans un $effect dans le composant
 */
export function syncOrgStore(query: any) {
  const data = query.data as { tree: OrgTreeNode[]; orgUnits: OrgUnit[] } | undefined;
  if (data?.orgUnits) {
    jobsStore.setOrgUnits(data.orgUnits);
  }
}


/**
 * Query pour récupérer l'arbre organisationnel complet
 */
export function useOrgTreeQuery() {
  return createQuery({
    queryKey: orgQueryKeys.tree(),
    queryFn: () => orgService.getOrgTree(),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
  });
}


/**
 * Query pour lister toutes les unités (paginé)
 */
export function useOrgUnitsQuery(
  page: () => number = () => 1,
  limit: () => number = () => 200,
  search: () => string = () => ''
) {
  return createQuery({
    get queryKey() {
      return orgQueryKeys.list(page(), limit(), search());
    },
    queryFn: () => orgService.listOrgUnits(page(), limit(), search()),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
  });
}


/**
 * Mutation pour créer une unité
 */
export function useCreateOrgUnitMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: OrgUnitCreate) => orgService.createOrgUnit(data),
    onSuccess: async () => {
      // Invalider les queries pour forcer un rafraîchissement
      await queryClient.invalidateQueries({ queryKey: orgQueryKeys.all });
      notification.toast.success('Unité créée avec succès');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation pour mettre à jour une unité
 */
export function useUpdateOrgUnitMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ id, data }: { id: string; data: OrgUnitUpdate }) =>
      orgService.updateOrgUnit(id, data),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: orgQueryKeys.all });
      notification.toast.success('Unité mise à jour');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation pour transférer la direction
 */
export function useTransferLeadershipMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ unitId, newManagerId }: { unitId: string; newManagerId: string }) =>
      orgService.transferLeadership(unitId, newManagerId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: orgQueryKeys.all });
      notification.toast.success('Direction transférée');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation pour supprimer une unité
 */
export function useDeleteOrgUnitMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (id: string) => orgService.deleteOrgUnit(id),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: orgQueryKeys.all });
      notification.toast.success('Unité supprimée');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Query pour récupérer toutes les positions d'une unité organisationnelle
 * Utilise une grande pagination pour charger toutes les positions
 */
export function usePositionsByOrgUnitQuery(orgUnitId: () => string | null) {
  return createQuery({
    get queryKey() {
      const id = orgUnitId();
      return id ? orgQueryKeys.positions(id) : orgQueryKeys.all;
    },
    queryFn: () => {
      const id = orgUnitId();
      if (!id) throw new Error('OrgUnit ID is required');
      // Charger avec une grande limite pour récupérer toutes les positions
      return orgService.getPositionsByOrgUnit(id, 200);
    },
    enabled: () => !!orgUnitId(),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
  });
}


/**
 * Hook pour rafraîchir l'arbre
 */
export function useRefreshOrgTree() {
  const queryClient = useQueryClient();

  return async () => {
    await queryClient.invalidateQueries({ queryKey: orgQueryKeys.all });
    await queryClient.refetchQueries({ queryKey: orgQueryKeys.all, type: 'active' });
  };
}

