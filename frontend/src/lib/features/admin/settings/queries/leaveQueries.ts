import { 
  createQuery, 
  createMutation, 
  useQueryClient 
} from '@tanstack/svelte-query';
import { leaveSettingsService } from '../services/leave.service';
import { notification } from '@/stores/notification.svelte';
import { leaveSettingsStore } from '../stores/leaveSettingsStore.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';


// QUERY KEYS - Cache invalidation strategy
export const leaveQueryKeys = {
  all: ['leave-settings'] as const,
  policies: () => [...leaveQueryKeys.all, 'policies'] as const,
  policy: (id: string) => [...leaveQueryKeys.policies(), id] as const,
  circumstanceRules: (policyId: string) => 
    [...leaveQueryKeys.all, 'circumstance-rules', policyId] as const,
  seniorityRules: (policyId: string) => 
    [...leaveQueryKeys.all, 'seniority-rules', policyId] as const,
};


/**
 * Query for fetching all leave policies
 * Auto-refetch on window focus, auto-cached for 5 minutes
 */
export function useLeavePoliciesQuery() {
  return createQuery({
    get queryKey() { return leaveQueryKeys.policies(); },
    queryFn: () => leaveSettingsService.listPolicies(),
    staleTime: 1000 * 60 * 5, // 5 minutes
    gcTime: 1000 * 60 * 10,   // 10 minutes (garbage collection)
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * Query for fetching circumstance rules for a policy
 */
export function useCircumstanceRulesQuery(policyId: string | null) {
  return createQuery({
    get queryKey() { return leaveQueryKeys.circumstanceRules(policyId ?? ''); },
    queryFn: () => leaveSettingsService.listCircumstanceRules(policyId!),
    enabled: !!policyId,
    staleTime: 1000 * 60 * 5,
  });
}


/**
 * Query for fetching seniority rules for a policy
 */
export function useSeniorityRulesQuery(policyId: string | null) {
  return createQuery({
    get queryKey() { return leaveQueryKeys.seniorityRules(policyId ?? ''); },
    queryFn: () => leaveSettingsService.listSeniorityRules(policyId!),
    enabled: !!policyId,
    staleTime: 1000 * 60 * 5,
  });
}


/**
 * Mutation for updating leave policy
 * Auto-invalidates related queries on success
 */
export function useUpdatePolicyMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({ 
      policyId, 
      updates, 
      silent 
    }: { 
      policyId: string; 
      updates: Parameters<typeof leaveSettingsService.updatePolicy>[1];
      silent?: boolean;
    }) => leaveSettingsService.updatePolicy(policyId, updates, silent),
    
    onSuccess: (_, { policyId }) => {
      // Invalidate and refetch
      queryClient.invalidateQueries({ 
        queryKey: leaveQueryKeys.policy(policyId) 
      });
      
      notification.toast.success('Politique de congés mise à jour');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for updating circumstance rule
 */
export function useUpdateCircumstanceRuleMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({
      ruleId,
      data,
      silent
    }: {
      ruleId: string;
      data: Parameters<typeof leaveSettingsService.updateCircumstanceRule>[1];
      silent?: boolean;
    }) => leaveSettingsService.updateCircumstanceRule(ruleId, data, silent),
    
    onSuccess: (_, { ruleId }) => {
      // Optimistic update possible here
      queryClient.invalidateQueries({ 
        queryKey: leaveQueryKeys.all 
      });
    },
  });
}


/**
 * Mutation for updating seniority rule
 */
export function useUpdateSeniorityRuleMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({
      ruleId,
      data,
      silent
    }: {
      ruleId: string;
      data: Parameters<typeof leaveSettingsService.updateSeniorityRule>[1];
      silent?: boolean;
    }) => leaveSettingsService.updateSeniorityRule(ruleId, data, silent),
    
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: leaveQueryKeys.all 
      });
    },
  });
}


/**
 * Mutation for creating seniority rule
 */
export function useCreateSeniorityRuleMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({
      policyId,
      data
    }: {
      policyId: string;
      data: Parameters<typeof leaveSettingsService.createSeniorityRule>[1];
    }) => leaveSettingsService.createSeniorityRule(policyId, data),
    
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: leaveQueryKeys.all 
      });
    },
  });
}


/**
 * Mutation for deleting seniority rule
 */
export function useDeleteSeniorityRuleMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (ruleId: string) => leaveSettingsService.deleteSeniorityRule(ruleId),
    
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: leaveQueryKeys.all 
      });
    },
  });
}


/**
 * Mutation for initializing/resetting to defaults
 */
export function useInitializeDefaultsMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: () => leaveSettingsService.initializeDefaults(),
    
    onSuccess: async () => {
      // Invalidate and immediately refetch all leave-related queries
      await queryClient.invalidateQueries({ 
        queryKey: leaveQueryKeys.all 
      });
      await queryClient.refetchQueries({
        queryKey: leaveQueryKeys.all,
        type: 'active'
      });
      
      notification.toast.success('Configuration réinitialisée aux valeurs par défaut');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Orchestrating mutation that saves all pending leave settings changes
 * This combines policy updates, circumstance rules, and seniority rules
 * Uses the store's getPendingChanges() to determine what needs to be saved
 */
export function useSaveLeaveSettingsMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: async () => {
      const changes = leaveSettingsStore.getPendingChanges();
      
      if (!changes) {
        throw new Error('Aucune modification à sauvegarder ou erreurs de validation');
      }
      
      // Execute all mutations in sequence
      // Policy update
      if (changes.policyUpdates) {
        await leaveSettingsService.updatePolicy(
          changes.policyId, 
          changes.policyUpdates, 
          true
        );
      }
      
      // Circumstance rules updates
      for (const rule of changes.circumstanceRules) {
        await leaveSettingsService.updateCircumstanceRule(
          rule.ruleId, 
          rule.data, 
          true
        );
      }
      
      // Seniority rule operation
      // Ensure only one rule exists - delete extras first
      if (changes.seniorityRule) {
        const currentRuleId = changes.seniorityRule.type === 'update' 
          ? changes.seniorityRule.ruleId 
          : null;
        const extraRuleIds = leaveSettingsStore.getExtraSeniorityRuleIds(currentRuleId);
        
        // Delete all extra rules first to ensure single rule constraint
        for (const ruleId of extraRuleIds) {
          await leaveSettingsService.deleteSeniorityRule(ruleId);
        }
        
        if (changes.seniorityRule.type === 'update') {
          await leaveSettingsService.updateSeniorityRule(
            changes.seniorityRule.ruleId,
            changes.seniorityRule.data,
            true
          );
        } else if (changes.seniorityRule.type === 'create') {
          const newRule = await leaveSettingsService.createSeniorityRule(
            changes.seniorityRule.policyId,
            changes.seniorityRule.data
          );
          // Update the store's rule ID for future updates
          leaveSettingsStore.seniorityRuleId = newRule.id || null;
        } else if (changes.seniorityRule.type === 'delete') {
          await leaveSettingsService.deleteSeniorityRule(changes.seniorityRule.ruleId);
        }
      }
      
      return { success: true };
    },
    
    onSuccess: async () => {
      // Commit changes to store tracking
      leaveSettingsStore.commitChanges();
      
      // Invalidate and refetch to ensure fresh data
      await queryClient.invalidateQueries({ 
        queryKey: leaveQueryKeys.all 
      });
      await queryClient.refetchQueries({
        queryKey: leaveQueryKeys.all,
        type: 'active'
      });
      
      notification.toast.success('Configuration enregistrée');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}

