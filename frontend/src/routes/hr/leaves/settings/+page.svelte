<script lang="ts">
  import { 
    useLeavePoliciesQuery, 
    useCircumstanceRulesQuery,
    useSeniorityRulesQuery,
    useSaveLeaveSettingsMutation,
    useInitializeDefaultsMutation
  } from "@/hr/leaves/queries/leaveSettingsQueries";
  import { leaveSettingsStore } from "@/hr/leaves/stores/leaveSettingsStore.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import LeaveConfigPanel from "@/hr/leaves/components/settings/LeaveConfigPanel.svelte";
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
  
  const cdPolicy = $derived.by(() => {
    const policies = $policiesQuery.data ?? [];
    return policies.find(p => p.country_code === DEFAULT_COUNTRY_CODE) || policies[0];
  });

  const policyId = $derived(cdPolicy?.id ?? null);
  let circumstanceRulesQuery = $state(useCircumstanceRulesQuery(null));
  let seniorityRulesQuery = $state(useSeniorityRulesQuery(null));
  let lastPolicyId = $state<string | null>(null);
  
    $effect(() => {
    const pid = policyId;
    if (pid && pid !== lastPolicyId) {
      circumstanceRulesQuery = useCircumstanceRulesQuery(pid);
      seniorityRulesQuery = useSeniorityRulesQuery(pid);
      lastPolicyId = pid;
    }
  });

  const saveMutation = useSaveLeaveSettingsMutation();
  const resetMutation = useInitializeDefaultsMutation();
  
  const isLoading = $derived(
    $policiesQuery.isLoading || 
    $circumstanceRulesQuery.isLoading || 
    $seniorityRulesQuery.isLoading
  );
  
  const error = $derived(
    $policiesQuery.error || 
    $circumstanceRulesQuery.error || 
    $seniorityRulesQuery.error
  );
  
  let loadedPolicyId = $state<string | null>(null);
  let dataGeneration = $state(0);
  
  $effect(() => {
    const policy = cdPolicy;
    const circumstances = $circumstanceRulesQuery.data;
    const seniority = $seniorityRulesQuery.data;
    const currentGen = dataGeneration;
    
    const shouldLoad = policy && 
      Array.isArray(circumstances) && 
      Array.isArray(seniority) && 
      (policy.id !== loadedPolicyId || currentGen > 0);
    if (shouldLoad) {
      leaveSettingsStore.loadFromData(policy, circumstances, seniority);
      loadedPolicyId = policy.id ?? null;
      if (currentGen > 0) dataGeneration = 0;
    }
  });
  
  function handleRetry() { $policiesQuery.refetch(); }
  
  function handleMutationSuccess() { dataGeneration += 1; }
</script>


<svelte:head>
  <title>Configuration des congés | Oxiliere HR</title>
</svelte:head>


{#if isLoading}
  <div class="flex justify-center items-center h-full py-16" transition:fade={{ duration: 200 }}>
    <AnimateSpin text="Chargement des paramètres de congé" />
  </div>
{:else if error}
  <div class="flex justify-center items-center h-full py-16" transition:fade={{ duration: 200 }}>
    <Empty 
      icon="alert-circle" 
      title="Erreur de Connexion" 
      description={getFriendlyErrorMessage(error.message) || ERROR_MESSAGES.NETWORK.UNKNOWN} 
      iconClass="text-red-400" 
      iconContainerClass="bg-red-50/30"
      iconSize={28}
      iconStrokeWidth={1.3}
    >
      <Button onclick={handleRetry} variant="outline" class="h-7 mt-2 rounded-lg"><AppIcon name="refresh-cw" />Réessayer</Button>
    </Empty>
  </div>
{:else}
  <div class="h-full overflow-y-auto" transition:slide={{ duration: 300, easing: cubicOut }}>
    <LeaveConfigPanel 
      saveMutation={saveMutation}
      resetMutation={resetMutation}
      onSuccess={handleMutationSuccess}
    />
  </div>
{/if}
