import { 
  createQuery, 
  createMutation, 
  useQueryClient 
} from '@tanstack/svelte-query';
import { taxSettingsService } from '../services/tax.service';
import { notification } from '@/stores/notification.svelte';
import { taxSettingsStore } from '../stores/taxSettingsStore.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';


// QUERY KEYS - Cache invalidation strategy
export const taxQueryKeys = {
  all: ['tax-settings'] as const,
  config: () => [...taxQueryKeys.all, 'config'] as const,
  brackets: () => [...taxQueryKeys.all, 'brackets'] as const,
  contributions: () => [...taxQueryKeys.all, 'contributions'] as const,
  legalAllowances: () => [...taxQueryKeys.all, 'legal-allowances'] as const,
  overtimeRules: () => [...taxQueryKeys.all, 'overtime-rules'] as const,
};


/**
 * Query for fetching global payroll configuration
 */
export function useTaxConfigurationQuery() {
  return createQuery({
    queryKey: taxQueryKeys.config(),
    queryFn: () => taxSettingsService.getConfiguration(),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
  });
}


/**
 * Query for fetching tax brackets (IPR)
 */
export function useTaxBracketsQuery() {
  return createQuery({
    queryKey: taxQueryKeys.brackets(),
    queryFn: () => taxSettingsService.listTaxBrackets(),
    staleTime: 1000 * 60 * 5,
  });
}


/**
 * Query for fetching social contribution rates (CNSS)
 */
export function useContributionsQuery() {
  return createQuery({
    queryKey: taxQueryKeys.contributions(),
    queryFn: () => taxSettingsService.listContributions(),
    staleTime: 1000 * 60 * 5,
  });
}


/**
 * Query for fetching legal allowances (FAMILY, HOUSING, etc.)
 */
export function useLegalAllowancesQuery() {
  return createQuery({
    queryKey: taxQueryKeys.legalAllowances(),
    queryFn: () => taxSettingsService.listLegalAllowances(),
    staleTime: 1000 * 60 * 5,
  });
}


/**
 * Query for fetching overtime rules (heures supplémentaires)
 */
export function useOvertimeRulesQuery() {
  return createQuery({
    queryKey: taxQueryKeys.overtimeRules(),
    queryFn: () => taxSettingsService.listOvertimeRules(),
    staleTime: 1000 * 60 * 5,
  });
}


/**
 * Mutation for updating a tax bracket
 */
export function useUpdateTaxBracketMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({
      bracketId,
      data,
      silent
    }: {
      bracketId: string;
      data: Parameters<typeof taxSettingsService.updateTaxBracket>[1];
      silent?: boolean;
    }) => taxSettingsService.updateTaxBracket(bracketId, data, silent),
    
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: taxQueryKeys.brackets() 
      });
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for updating CNSS/social contribution rates
 */
export function useUpdateContributionMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({
      rateId,
      data,
      silent
    }: {
      rateId: string;
      data: Parameters<typeof taxSettingsService.updateContribution>[1];
      silent?: boolean;
    }) => taxSettingsService.updateContribution(rateId, data, silent),
    
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: taxQueryKeys.contributions() 
      });
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for updating global payroll configuration
 */
export function useUpdateTaxConfigurationMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: ({
      data,
      silent
    }: {
      data: Parameters<typeof taxSettingsService.updateConfiguration>[0];
      silent?: boolean;
    }) => taxSettingsService.updateConfiguration(data, silent),
    
    onSuccess: () => {
      queryClient.invalidateQueries({ 
        queryKey: taxQueryKeys.config() 
      });
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for initializing/resetting to defaults
 */
export function useInitializeTaxDefaultsMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: () => taxSettingsService.initializeDefaults(),
    
    onSuccess: async () => {
      await queryClient.invalidateQueries({ 
        queryKey: taxQueryKeys.all 
      });
      await queryClient.refetchQueries({
        queryKey: taxQueryKeys.all,
        type: 'active'
      });
      
      notification.toast.success('Configuration fiscale réinitialisée aux valeurs par défaut');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation to create a new tax bracket
 */
export function useCreateTaxBracketMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (data: import('../schemas/tax.schemas').TaxBracketCreate) => 
      taxSettingsService.createTaxBracket(data),
    
    onSuccess: async () => {
      await queryClient.invalidateQueries({ 
        queryKey: taxQueryKeys.brackets()
      });
      notification.toast.success('Barème IPR créé');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}

/**
 * Mutation to create a new social contribution rate
 */
export function useCreateSocialContributionMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: (data: import('../schemas/tax.schemas').SocialContributionCreate) => 
      taxSettingsService.createContribution(data),
    
    onSuccess: async () => {
      await queryClient.invalidateQueries({ 
        queryKey: taxQueryKeys.contributions()
      });
      notification.toast.success('Taux de cotisation créé');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}

/**
 * Orchestrating mutation that saves all pending tax settings changes
 */
export function useSaveTaxSettingsMutation() {
  const queryClient = useQueryClient();
  
  return createMutation({
    mutationFn: async () => {
      const changes = taxSettingsStore.getPendingChanges();
      
      if (!changes) {
        throw new Error('Aucune modification à sauvegarder ou erreurs de validation');
      }
      
      // Check if there are actual changes to save
      const hasConfigChanges = Object.keys(changes.configUpdates).length > 0;
      const hasBracketChanges = changes.bracketUpdates.length > 0;
      const hasContributionChanges = changes.contributionUpdates.length > 0;
      const hasLegalAllowanceChanges = changes.legalAllowanceUpdates.length > 0;
      const hasOvertimeRuleChanges = changes.overtimeRuleUpdates.length > 0;
      
      if (!hasConfigChanges && !hasBracketChanges && !hasContributionChanges && !hasLegalAllowanceChanges && !hasOvertimeRuleChanges) {
        return { success: true, message: 'Aucune modification détectée' };
      }
      
      // Update global configuration
      if (hasConfigChanges) {
        await taxSettingsService.updateConfiguration(changes.configUpdates, true);
      }
      
      // Update tax brackets
      for (const bracket of changes.bracketUpdates) {
        await taxSettingsService.updateTaxBracket(bracket.id, bracket.data, true);
      }
      
      // Update contribution rates (CNSS)
      for (const contribution of changes.contributionUpdates) {
        await taxSettingsService.updateContribution(contribution.id, contribution.data, true);
      }
      
      // Update legal allowances
      for (const allowance of changes.legalAllowanceUpdates) {
        await taxSettingsService.updateLegalAllowance(allowance.id, allowance.data, true);
      }
      
      // Update overtime rules
      for (const rule of changes.overtimeRuleUpdates) {
        await taxSettingsService.updateOvertimeRule(rule.id, rule.data);
      }
      
      return { success: true };
    },
    
    onSuccess: async (result) => {
      // Only commit and refetch if there were actual changes saved
      if (result.message === 'Aucune modification détectée') {
        notification.toast.info('Aucune modification à enregistrer');
        return;
      }
      
      taxSettingsStore.commitChanges();
      
      await queryClient.invalidateQueries({ 
        queryKey: taxQueryKeys.all 
      });
      await queryClient.refetchQueries({
        queryKey: taxQueryKeys.all,
        type: 'active'
      });
      
      notification.toast.success('Configuration fiscale enregistrée');
    },
    
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}

