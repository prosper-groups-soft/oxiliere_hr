import { 
  createQuery, 
  createMutation, 
  useQueryClient 
} from '@tanstack/svelte-query';
import { employeesService } from '../services/employees.service';
import { onboardingEndpoint } from '../api/onboarding.endpoints';
import { notification } from '@/stores/notification.svelte';
import { employeeStore } from '../stores/employees.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { orgQueryKeys } from '@/hr/jobs/queries/orgQueries';
import type { 
  Employee,
  EmployeeCreate, 
  EmployeeUpdate, 
  EmployeeFilters 
} from '../types/types';


// QUERY KEYS - Cache invalidation strategy
export const employeeQueryKeys = {
  all: ['employees'] as const,
  list: (page?: number, limit?: number, search?: string, filters?: EmployeeFilters, sortBy?: string, sortOrder?: string) => 
    [...employeeQueryKeys.all, 'list', page ?? 1, limit ?? 10, search ?? '', filters ?? {}, sortBy ?? 'name', sortOrder ?? 'asc'] as const,
  allForSelect: () => [...employeeQueryKeys.all, 'allForSelect'] as const,
  detail: (id: string) => [...employeeQueryKeys.all, 'detail', id] as const,
  byOrgUnit: (orgUnitId: string) => [...employeeQueryKeys.all, 'byOrgUnit', orgUnitId] as const,
};


/**
 * Query for fetching all employees with pagination, search, filters and sorting
 * Auto-refetch on window focus, auto-cached for 5 minutes
 * Synchronise automatiquement le store avec les données du backend
 */
export function useEmployeesQuery(
  page: () => number, 
  limit: () => number = () => 10,
  search: () => string = () => '',
  filters: () => EmployeeFilters = () => ({ gender: undefined, marital_status: undefined, is_active: undefined }),
  sortBy: () => string = () => 'name',
  sortOrder: () => 'asc' | 'desc' = () => 'asc'
) {
  return createQuery({
    get queryKey() { 
      return employeeQueryKeys.list(page(), limit(), search(), filters(), sortBy(), sortOrder()); 
    },
    queryFn: () => employeesService.listEmployees(page(), limit(), search(), filters(), sortBy(), sortOrder()),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10,   // 10 minutes (garbage collection)
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * Query for fetching all employees without pagination (for select dropdowns)
 * Used in org chart, forms, etc.
 */
export function useAllEmployees(filters?: () => EmployeeFilters) {
  return createQuery({
    queryKey: [...employeeQueryKeys.allForSelect(), filters?.() ?? {}],
    queryFn: () => employeesService.getAllForSelect(filters?.()),
    staleTime: 0, // 0 minutes
    gcTime: 0,   // 10 minutes
    refetchOnWindowFocus: false,
    refetchOnReconnect: true,
  });
}


/**
 * Query for fetching a single employee detail
 */
export function useEmployeeDetailQuery(employeeId: () => string | null) {
  return createQuery({
    get queryKey() { 
      const id = employeeId();
      return id ? employeeQueryKeys.detail(id) : employeeQueryKeys.all; 
    },
    queryFn: () => {
      const id = employeeId();
      if (!id) throw new Error('Employee ID is required');
      return employeesService.getEmployeeDetail(id);
    },
    staleTime: 0, // Toujours frais : le current_contract (is_active) doit refléter la DB à chaque ouverture/sélection
    gcTime: 1000 * 60 * 10,
    enabled: () => !!employeeId(), // Only run when employeeId is provided
  });
}

/**
 * Query for fetching all employees by organizational unit
 * Uses large pagination to get all employees in the unit
 */
export function useEmployeesByOrgUnitQuery(orgUnitId: () => string | null) {
  return createQuery({
    get queryKey() {
      const id = orgUnitId();
      return id ? employeeQueryKeys.byOrgUnit(id) : employeeQueryKeys.all;
    },
    queryFn: () => {
      const id = orgUnitId();
      if (!id) throw new Error('OrgUnit ID is required');
      return employeesService.getEmployeesByOrgUnit(id, 1000);
    },
    enabled: () => !!orgUnitId(),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
  });
}


/**
 * Mutation for creating a new employee (onboarding)
 */
export function useCreateEmployeeMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (data: EmployeeCreate) => employeesService.createEmployee(data),
    
    onSuccess: async (newEmployee) => {
      // Ajouter au store localement
      employeeStore.addEmployee(newEmployee);
      
      // Invalidate and refetch list
      await queryClient.invalidateQueries({ 
        queryKey: employeeQueryKeys.all 
      });
      
      notification.toast.success(`Employé ${newEmployee.name} créé avec succès`);
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for updating employee personal info
 */
export function useUpdateEmployeeMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      employeeId, 
      data 
    }: { 
      employeeId: string; 
      data: EmployeeUpdate;
    }) => employeesService.updatePersonalInfo(employeeId, data),
    
    onSuccess: async (updatedEmployee, { employeeId }) => {
      // Invalidate both list and detail
      await queryClient.invalidateQueries({ 
        queryKey: employeeQueryKeys.all 
      });
      
      const { buildFullName } = await import("@/utilities/common/employee.utils");
      notification.toast.success(`Employé ${buildFullName(updatedEmployee)} mis à jour avec succès`);
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for updating employee contract and career info
 */
export function useUpdateContractMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      employeeId, 
      data 
    }: { 
      employeeId: string; 
      data: any;
    }) => employeesService.updateContractInfo(employeeId, data),
    
    onSuccess: async (_, { employeeId }) => {
      // Invalidate both list and detail
      await queryClient.invalidateQueries({ 
        queryKey: employeeQueryKeys.all 
      });
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for assigning a user account to an employee
 */
export function useAssignUserMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      employeeId, 
      userId 
    }: { 
      employeeId: string; 
      userId: string;
    }) => employeesService.assignUserAccount(employeeId, userId),
    
    onSuccess: async (_, { employeeId }) => {
      // Invalidate employee detail
      await queryClient.invalidateQueries({ 
        queryKey: employeeQueryKeys.detail(employeeId)
      });
      
      notification.toast.success('Compte utilisateur lié avec succès');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for revoking user access from an employee
 */
export function useRevokeUserMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (employeeId: string) => employeesService.revokeUserAccess(employeeId),
    
    onSuccess: async (_, employeeId) => {
      // Invalidate employee detail
      await queryClient.invalidateQueries({ 
        queryKey: employeeQueryKeys.detail(employeeId)
      });
      
      notification.toast.success('Accès utilisateur révoqué');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for assigning an employee to an organizational unit
 */
export function useAssignEmployeeToOrgUnitMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      employeeId,
      orgUnitId,
      positionId
    }: {
      employeeId: string;
      orgUnitId: string;
      positionId?: string;
    }) => employeesService.assignToOrgUnit(employeeId, orgUnitId, positionId),

    onSuccess: async (_data, variables) => {
      // Invalidate and refetch all employee and org queries
      console.log('[AssignMutation] Invalidating queries for orgUnit:', variables.orgUnitId);
      
      // Invalidate specific byOrgUnit query
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.byOrgUnit(variables.orgUnitId),
        refetchType: 'all'
      });
      
      // Invalidate all employee queries
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.all,
        refetchType: 'all'
      });
      await queryClient.invalidateQueries({
        queryKey: orgQueryKeys.all,
        refetchType: 'all'
      });
      
      // Force immediate refetch of active queries
      await queryClient.refetchQueries({
        queryKey: employeeQueryKeys.byOrgUnit(variables.orgUnitId),
        type: 'active'
      });
      await queryClient.refetchQueries({
        queryKey: employeeQueryKeys.all,
        type: 'active'
      });
      console.log('[AssignMutation] Queries refreshed');
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    }
  });
}


/**
 * Mutation for unassigning an employee from their organizational unit
 */
export function useUnassignEmployeeFromOrgUnitMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (employeeId: string) => employeesService.unassignFromOrgUnit(employeeId),

    onSuccess: async () => {
      // Invalidate and refetch all employee and org queries
      console.log('[UnassignMutation] Invalidating queries...');
      
      // Invalidate all employee queries (we don't know the orgUnitId here)
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.all,
        refetchType: 'all'
      });
      await queryClient.invalidateQueries({
        queryKey: orgQueryKeys.all,
        refetchType: 'all'
      });
      
      // Force immediate refetch
      await queryClient.refetchQueries({
        queryKey: employeeQueryKeys.all,
        type: 'active'
      });
      console.log('[UnassignMutation] Queries refreshed');
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    }
  });
}


/**
 * Hook to refresh employees list
 */
export function useRefreshEmployees() {
  const queryClient = useQueryClient();
  
  return async () => {
    await queryClient.invalidateQueries({
      queryKey: employeeQueryKeys.all
    });
    await queryClient.refetchQueries({
      queryKey: employeeQueryKeys.all,
      type: 'active'
    });
  };
}


/**
 * Helper pour synchroniser le store avec les données de la query
 * À utiliser DANS un $effect dans un composant .svelte
 * 
 * Exemple d'utilisation:
 * ```svelte
 * <script>
 *   const query = useEmployeesQuery(() => 1, () => 10);
 *   
 *   $effect(() => {
 *     syncEmployeesStore(query);
 *   });
 * </script>
 * ```
 */
export function syncEmployeesStore(query: any) {
  const data = query.data as { results: Employee[]; count: number } | undefined;
  if (data) {
    // Calculer le nombre de pages basé sur le perPage actuel du store
    const perPage = employeeStore.perPage;
    const totalPages = Math.ceil(data.count / perPage) || 1;
    employeeStore.setEmployees(data.results, data.count, totalPages);
  }
  
  employeeStore.setLoading(query.isLoading as boolean);
  
  const error = query.error as Error | undefined;
  if (error) {
    employeeStore.setError(getFriendlyErrorMessage(error));
  } else {
    employeeStore.setError(null);
  }
}

/**
 * Mutation for suspending employee contract
 */
export function useSuspendEmployeeMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      employeeId, 
      data 
    }: { 
      employeeId: string; 
      data: { reason: string; effective_date?: string };
    }) => employeesService.suspendEmployee(employeeId, data),
    
    onSuccess: async (_, { employeeId }) => {
      // Invalidate both list and detail
      await queryClient.invalidateQueries({ 
        queryKey: employeeQueryKeys.all 
      });
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.detail(employeeId)
      });
    },
  });
}

/**
 * Mutation for reactivating employee
 */
export function useReactivateEmployeeMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      employeeId, 
      data 
    }: { 
      employeeId: string; 
      data: { effective_date?: string; reason?: string; is_active?: boolean; can_connect?: boolean };
    }) => employeesService.reactivateEmployee(employeeId, data),
    
    onSuccess: async (_, { employeeId }) => {
      // Invalidate both list and detail
      await queryClient.invalidateQueries({ 
        queryKey: employeeQueryKeys.all 
      });
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.detail(employeeId)
      });
    },
  });
}

/**
 * Mutation for offboarding employee
 */
export function useOffboardEmployeeMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      employeeId, 
      data 
    }: { 
      employeeId: string; 
      data: { end_date: string; departure_type?: string; reason: string };
    }) => employeesService.offboardEmployee(employeeId, data),
    
    onSuccess: async (_, { employeeId }) => {
      // Invalidate both list and detail
      await queryClient.invalidateQueries({ 
        queryKey: employeeQueryKeys.all 
      });
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.detail(employeeId)
      });
    },
  });
}


/**
 * Mutation for uploading employee profile photo
 */
export function useUploadProfilePhotoMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      employeeId, 
      file 
    }: { 
      employeeId: string; 
      file: File;
    }) => onboardingEndpoint.uploadProfilePhoto(employeeId, file),
    
    onSuccess: async (_, { employeeId }) => {
      notification.toast.success('Photo de profil mise à jour');
      
      await employeeStore.getFullProfileById(employeeId);

      // Invalider toutes les queries de liste pour rafraîchir la page courante
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.list()
      });
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.all
      });
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.allForSelect()
      });
      await queryClient.invalidateQueries({
        queryKey: employeeQueryKeys.detail(employeeId)
      });
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}

