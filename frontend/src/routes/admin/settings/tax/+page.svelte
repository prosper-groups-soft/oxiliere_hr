<script lang="ts">
  import { 
    useTaxConfigurationQuery,
    useTaxBracketsQuery,
    useContributionsQuery,
    useLegalAllowancesQuery,
    useOvertimeRulesQuery,
    useSaveTaxSettingsMutation,
    useInitializeTaxDefaultsMutation
  } from "@/features/admin/settings/queries/taxQueries";
  import { taxSettingsStore } from "@/features/admin/settings/stores/taxSettingsStore.svelte";
  import TaxConfigPanel from "@/features/admin/settings/components/tax/TaxConfigPanel.svelte";
  import { Button } from "@/components/ui/button";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { fade, slide } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { 
    ERROR_MESSAGES, 
    getFriendlyErrorMessage 
  } from "@/constants/errors";
  
  // Queries
  const configQuery = useTaxConfigurationQuery();
  const bracketsQuery = useTaxBracketsQuery();
  const contributionsQuery = useContributionsQuery();
  const legalAllowancesQuery = useLegalAllowancesQuery();
  const overtimeRulesQuery = useOvertimeRulesQuery();
  
  // Mutations
  const saveMutation = useSaveTaxSettingsMutation();
  const resetMutation = useInitializeTaxDefaultsMutation();
  
  // Combined loading state
  const isLoading = $derived(
    $configQuery.isLoading || 
    $bracketsQuery.isLoading || 
    $contributionsQuery.isLoading ||
    $legalAllowancesQuery.isLoading ||
    $overtimeRulesQuery.isLoading
  );
  
  // Combined error state
  const error = $derived(
    $configQuery.error || 
    $bracketsQuery.error || 
    $contributionsQuery.error ||
    $legalAllowancesQuery.error ||
    $overtimeRulesQuery.error
  );
  
  // Track which data has been loaded
  let loadedDataKey = $state<string | null>(null);
  let dataGeneration = $state(0);
  let hasLoadedInitially = $state(false);
  
  $effect(() => {
    const config = $configQuery.data;
    const brackets = $bracketsQuery.data;
    const contributions = $contributionsQuery.data;
    const legalAllowances = $legalAllowancesQuery.data;
    const overtimeRules = $overtimeRulesQuery.data;
    const currentGen = dataGeneration;
    
    // Create a key from the data to detect changes
    const dataKey = `${config?.id ?? 'no-config'}-${brackets?.length ?? 0}-${contributions?.length ?? 0}-${legalAllowances?.length ?? 0}-${overtimeRules?.length ?? 0}`;
    
    // Load when: we have config AND all data arrays are loaded (not undefined)
    const hasConfig = !!config;
    const hasAllData = Array.isArray(brackets) && Array.isArray(contributions) && Array.isArray(legalAllowances) && Array.isArray(overtimeRules);
    const isFirstLoad = !hasLoadedInitially;
    const isMutationRefresh = currentGen > 0;
    const isNewData = dataKey !== loadedDataKey || isMutationRefresh;
    const shouldLoad = hasConfig && hasAllData && isNewData && (isFirstLoad || isMutationRefresh);
    
    
    if (shouldLoad) {
      taxSettingsStore.loadFromData(
        config,
        brackets || [],
        contributions || []
      );
      taxSettingsStore.loadLegalAllowances(legalAllowances || []);
      taxSettingsStore.loadOvertimeRules(overtimeRules || []);
      loadedDataKey = dataKey;
      hasLoadedInitially = true;
      if (isMutationRefresh) {
        dataGeneration = 0;
      }
    }
  });
  
  function handleRetry() {
    $configQuery.refetch();
    $bracketsQuery.refetch();
    $contributionsQuery.refetch();
    $legalAllowancesQuery.refetch();
    $overtimeRulesQuery.refetch();
  }

  // Handle successful save/reset by forcing a re-sync
  function handleMutationSuccess() {
    dataGeneration += 1;
  }
</script>


<svelte:head>
  <title>Paramètres - Fiscalité IPR | Oxiliere HR</title>
</svelte:head>


<!-- Loading State -->
{#if isLoading}
  <div class="flex justify-center items-center h-full" transition:fade={{ duration: 200 }}>
    <AnimateSpin text="Chargement des paramètres de la fiscalité" />
  </div>

<!-- Error State -->
{:else if error}
  <div class="flex justify-center items-center h-full" transition:fade={{ duration: 200 }}>
    <Empty 
      icon="alert-circle" 
      title="Erreur de Connexion" 
      description={getFriendlyErrorMessage(error.message) || ERROR_MESSAGES.NETWORK.UNKNOWN} 
      iconClass="text-red-400"
      iconContainerClass="bg-red-50/30"
      iconSize={28}
      iconStrokeWidth={1.3}
    >
      <Button 
        onclick={handleRetry} 
        variant="outline"
        class="h-7 mt-2 rounded-lg transition-colors"
      >
        <AppIcon name="refresh-cw" />
        Réessayer
      </Button>
    </Empty>
  </div>

<!-- Content -->
{:else}
  <div transition:slide={{ duration: 300, easing: cubicOut }}>
    <TaxConfigPanel 
      saveMutation={saveMutation}
      resetMutation={resetMutation}
      onSuccess={handleMutationSuccess}
    />
  </div>
{/if}

