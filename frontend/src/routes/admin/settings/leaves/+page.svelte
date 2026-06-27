<script lang="ts">
  import { 
    useLeavePoliciesQuery, 
    useCircumstanceRulesQuery,
    useSeniorityRulesQuery,
    useSaveLeaveSettingsMutation,
    useInitializeDefaultsMutation
  } from "@/features/admin/settings/queries/leaveQueries";
  import { leaveSettingsStore } from "@/features/admin/settings/stores/leaveSettingsStore.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import LeaveConfigPanel from "@/features/admin/settings/components/leaves/LeaveConfigPanel.svelte";
  import { Button } from "@/components/ui/button";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { fade, slide } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { 
    ERROR_MESSAGES, 
    getFriendlyErrorMessage 
  } from "@/constants/errors";
  import { DEFAULT_COUNTRY_CODE } from "@/constants";
  

  const policiesQuery = useLeavePoliciesQuery();
  
  // Derived policy ID from query data using $derived.by
  // Uses DEFAULT_COUNTRY_CODE to find the primary policy
  const cdPolicy = $derived.by(() => {
    const policies = $policiesQuery.data ?? [];
    return policies.find(p => p.country_code === DEFAULT_COUNTRY_CODE) || policies[0];
  });
  
  const policyId = $derived(cdPolicy?.id ?? null);
  
  // Reactive query stores - recreated when policyId changes
  let circumstanceRulesQuery = $state(useCircumstanceRulesQuery(null));
  let seniorityRulesQuery = $state(useSeniorityRulesQuery(null));
  let lastPolicyId = $state<string | null>(null);
  
  // Recreate queries when policyId becomes available or changes
  $effect(() => {
    const pid = policyId;
    if (pid && pid !== lastPolicyId) {
      circumstanceRulesQuery = useCircumstanceRulesQuery(pid);
      seniorityRulesQuery = useSeniorityRulesQuery(pid);
      lastPolicyId = pid;
    }
  });
  
  // Mutations for saving and resetting
  const saveMutation = useSaveLeaveSettingsMutation();
  const resetMutation = useInitializeDefaultsMutation();
  
  // Combined loading state
  const isLoading = $derived(
    $policiesQuery.isLoading || 
    $circumstanceRulesQuery.isLoading || 
    $seniorityRulesQuery.isLoading
  );
  
  // Combined error state
  const error = $derived(
    $policiesQuery.error || 
    $circumstanceRulesQuery.error || 
    $seniorityRulesQuery.error
  );
  
  // Track which policy data has been loaded for
  let loadedPolicyId = $state<string | null>(null);
  // Track data generation to reload when data changes
  let dataGeneration = $state(0);
  
  $effect(() => {
    const policy = cdPolicy;
    const circumstances = $circumstanceRulesQuery.data;
    const seniority = $seniorityRulesQuery.data;
    const currentGen = dataGeneration;
    
    // Load data when: new policy, or data changed, or force reload requested
    const shouldLoad = policy && 
      Array.isArray(circumstances) && 
      Array.isArray(seniority) && 
      (policy.id !== loadedPolicyId || currentGen > 0);
    
    if (shouldLoad) {
      leaveSettingsStore.loadFromData(policy, circumstances, seniority);
      loadedPolicyId = policy.id ?? null;
      // Reset generation counter after loading
      if (currentGen > 0) {
        dataGeneration = 0;
      }
    }
  });
  
  function handleRetry() {
    $policiesQuery.refetch();
  }

  // Handle successful save/reset by forcing a re-sync of the store from query data
  function handleMutationSuccess() {
    // Increment generation to trigger store reload
    dataGeneration += 1;
  }
</script>


<svelte:head>
  <title>Paramètres - Congés | Oxiliere HR</title>
</svelte:head>


<!-- Loading State -->
{#if isLoading}
  <div class="flex justify-center items-center h-full" transition:fade={{ duration: 200 }}>
    <AnimateSpin text="Chargement des paramètres de congé" />
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
    <LeaveConfigPanel 
      saveMutation={saveMutation}
      resetMutation={resetMutation}
      onSuccess={handleMutationSuccess}
    />
  </div>
{/if}

