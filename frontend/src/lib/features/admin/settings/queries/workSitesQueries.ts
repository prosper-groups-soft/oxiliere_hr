import { 
  createQuery, 
  createMutation, 
  useQueryClient 
} from '@tanstack/svelte-query';
import { workSitesService } from '../services/workSites.service';
import { notification } from '@/stores/notification.svelte';
import { workSitesStore } from '../stores/workSitesStore.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';


// QUERY KEYS - Cache invalidation strategy
export const workSitesQueryKeys = {
  all: ['work-sites'] as const,
  list: (page?: number, limit?: number) => 
    [...workSitesQueryKeys.all, 'list', page ?? 1, limit ?? 10] as const,
  detail: (id: string) => [...workSitesQueryKeys.all, 'detail', id] as const,
};


/**
 * Query for fetching all work sites with pagination
 * Auto-refetch on window focus, auto-cached for 5 minutes
 * Uses store pagination reactively
 */
export function useWorkSitesQuery(page: () => number, limit: () => number = () => 10) {
  return createQuery({
    get queryKey() { return workSitesQueryKeys.list(page(), limit()); },
    queryFn: () => workSitesService.listWorkSites(page(), limit()),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10,   // 10 minutes (garbage collection)
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * Mutation for creating a work site
 * Auto-invalidates list queries on success
 */
export function useCreateWorkSiteMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (data: Parameters<typeof workSitesService.createWorkSite>[0]) => 
      workSitesService.createWorkSite(data),
    
    onSuccess: async (newSite) => {
      // Update store's work sites list
      workSitesStore.addWorkSite(newSite);
      workSitesStore.closeAddForm();
      
      // Invalidate and refetch list
      await queryClient.invalidateQueries({ 
        queryKey: workSitesQueryKeys.all 
      });
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for updating a work site
 */
export function useUpdateWorkSiteMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      siteId, 
      data 
    }: { 
      siteId: string; 
      data: Parameters<typeof workSitesService.updateWorkSite>[1];
    }) => workSitesService.updateWorkSite(siteId, data),
    
    onSuccess: async (_, { siteId }) => {
      // Invalidate both list and detail
      await queryClient.invalidateQueries({ 
        queryKey: workSitesQueryKeys.all 
      });
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for deleting a work site
 */
export function useDeleteWorkSiteMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (siteId: string) => workSitesService.deleteWorkSite(siteId),
    
    onSuccess: async (_, siteId) => {
      // Remove from store
      workSitesStore.removeWorkSite(siteId);
      
      // Check if we deleted the last item on the last page
      const currentPage = workSitesStore.currentPage;
      const currentSites = workSitesStore.workSites;
      const totalPages = workSitesStore.totalPages;
      
      // If current page is now empty and we're not on page 1, go to previous page
      // before invalidating the query (to avoid fetching a non-existent page)
      if (currentSites.length === 0 && currentPage > 1 && currentPage >= totalPages) {
        workSitesStore.prevPage();
        // Don't invalidate here - the page change will trigger a refetch via the refreshCallback
        return;
      }
      
      // Otherwise, invalidate and refetch current page
      await queryClient.invalidateQueries({ 
        queryKey: workSitesQueryKeys.all 
      });
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Hook to refresh work sites list
 */
export function useRefreshWorkSites() {
  const queryClient = useQueryClient();
  
  return async () => {
    await queryClient.invalidateQueries({
      queryKey: workSitesQueryKeys.all
    });
    await queryClient.refetchQueries({
      queryKey: workSitesQueryKeys.all,
      type: 'active'
    });
  };
}

