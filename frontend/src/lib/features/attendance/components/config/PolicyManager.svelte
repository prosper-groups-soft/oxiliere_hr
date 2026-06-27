<script lang="ts">
  import { attendanceStore } from "../../stores/attendance.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import type { WorkPolicy } from "../../types/types";
  import PolicySheet from "./sheets/policy/PolicySheet.svelte";
  import PolicyCard from "./views/PolicyCard.svelte";
  import PolicyDetailsSheet from "./sheets/policy/PolicyDetailsSheet.svelte";
  import { Button } from "@/components/ui/button";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from "@/components/shared/containers/empty/EmptyButton.svelte";
  import { fade, fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { getFriendlyErrorMessage } from '@/constants/errors';
  import { notification } from '@/stores/notification.svelte';
  import { DEFAULT_POLICY_TEMPLATE } from "../../constants/attendance.helpers";
  import { useQueryClient } from "@tanstack/svelte-query";
  import { policyQueryKeys } from "../../queries/attendanceQueries";


  type Policy = WorkPolicy;

  let {
  } = $props();

  let showForm = $state(false);
  let editingPolicy = $state<Policy | null>(null);
  let showDetails = $state(false);
  let detailsPolicy = $state<Policy | null>(null);
  let deletingId = $state<string | null>(null);
  let isLoading = $state(true);
  let isError = $state(false);
  let error = $state<Error | null>(null);

  const queryClient = useQueryClient();

  // Chargement initial des policies
  $effect(() => {
    loadPolicies();
  });

  async function loadPolicies() {
    isLoading = true;
    isError = false;
    error = null;
    try {
      await attendanceStore.loadPolicies();
      if (attendanceStore.policiesError) {
        throw new Error(attendanceStore.policiesError);
      }
    } catch (e: any) {
      isError = true;
      error = e;
    } finally {
      isLoading = false;
    }
  }

  async function handleRetry() {
    await loadPolicies();
  }

  // Les policies sont filtrées et triées côté serveur via la TanStack Query
  const filteredPolicies = $derived.by(() =>
    attendanceStore.getFilteredPolicies(
      attendanceStore.policySearch,
      attendanceStore.policySortBy,
      attendanceStore.policySortOrder
    )
  );

  function openNewForm() {
    editingPolicy = JSON.parse(JSON.stringify(DEFAULT_POLICY_TEMPLATE));
    showForm = true;
  }

  function editPolicy(policy: Policy) {
    editingPolicy = JSON.parse(JSON.stringify(policy));
    showForm = true;
  }

  function deletePolicy(policy: Policy) {
    if (deletingId) return;
    notification.confirm({
      title: 'Supprimer le modèle',
      message: `Êtes-vous sûr de vouloir supprimer « ${policy.name} » ? Cette action est irréversible.`,
      type: 'danger',
      yesText: 'Supprimer',
      noText: 'Annuler',
      onYes: async () => {
        deletingId = policy.id!;
        try {
          await attendanceStore.deletePolicy(policy.id!);
          queryClient.invalidateQueries({ queryKey: policyQueryKeys.all });
        } finally {
          deletingId = null;
        }
      },
    });
  }

  function viewDetails(policy: Policy) {
    detailsPolicy = policy;
    showDetails = true;
  }
</script>


<div class="flex h-full flex-col bg-white overflow-hidden">
  <!-- Header avec Search + Ajouter -->
  {@render Header()}

  <!-- Content area with clean keyed transitions -->
  <div class="flex-1 overflow-hidden">
    {#key `${isLoading}-${isError}-${filteredPolicies.length === 0}`}
      <div class="h-full" transition:fade={{ duration: 200 }}>
        {#if isLoading}
          <div class="h-full flex items-center justify-center">
            <AnimateSpin text="Chargement des modèles de travail" />
          </div>

        {:else if isError}
          <div class="h-full flex items-center justify-center p-8">
            <Empty
              title="Erreur de chargement"
              description={getFriendlyErrorMessage(error)}
              icon="alert-circle"
              iconClass="text-red-400"
              iconSize={28}
              iconStrokeWidth={1.3}
              iconContainerClass="bg-red-50/30"
            >
              <Button onclick={handleRetry} variant="outline" class="h-7 rounded-lg">
                <AppIcon name="refresh-cw" />
                Réessayer
              </Button>
            </Empty>
          </div>

        {:else if filteredPolicies.length === 0}
          <div class="h-full flex items-center justify-center">
            <Empty 
              title="Aucun modèle de travail trouvé" 
              description={attendanceStore.policySearch
                ? "Aucun résultat ne correspond à votre recherche."
                : "Commencez par créer votre premier modèle de travail pour organiser les horaires de vos employés."}
              icon={attendanceStore.policySearch ? "search-x" : "briefcase"}
              iconSize={28}
              iconStrokeWidth={1.3}
              iconClass={attendanceStore.policySearch ? "text-slate-300" : "text-slate-500"}
            >
              {#if attendanceStore.policySearch}
                <Button variant="ghost" onclick={() => attendanceStore.policySearch = ''} class="h-7 bg-slate-50">
                  <AppIcon name="x" size={16} class="text-slate-400" />
                  Réinitialiser la recherche
                </Button>
              {:else}
                <EmptyButton 
                  labelElement="un modèle" 
                  onNew={openNewForm} 
                />
              {/if}
            </Empty>
          </div>

        {:else}
          <div class="custom-scrollbar h-full overflow-auto p-6 pt-3">
            <div 
              class="grid grid-cols-1 gap-6 md:grid-cols-2 lg:grid-cols-3"
              in:fly={{ y: 20, duration: 400, delay: 100 }}
            >
              {#each filteredPolicies as policy (policy.id)}
                <div animate:flip={{ duration: 400 }}>
                  <PolicyCard 
                    {policy} 
                    onEdit={editPolicy}
                    onDelete={deletePolicy}
                    onViewDetails={viewDetails}
                  />
                </div>
              {/each}
            </div>
          </div>
        {/if}
      </div>
    {/key}
  </div>
</div>


<PolicySheet bind:open={showForm} bind:policy={editingPolicy} />
<PolicyDetailsSheet bind:open={showDetails} policy={detailsPolicy} />


{#snippet Header()}
  <div class="flex flex-col px-4 pr-8.5 border-b border-slate-100">
    <div class="flex items-center gap-3 py-2">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={attendanceStore.policySearch} 
          placeholder="Rechercher un modèle..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => attendanceStore.policySearch = ""}
        />
      </div>

      <Button
        onclick={openNewForm}
        size="sm"
        variant="default"
        class="h-7.5 px-3 rounded-lg text-[0.84rem] shadow-fine transition-all"
      >
        <AppIcon name="plus" size={17} />
        Ajouter modèle
      </Button>
    </div>

    <!-- FilterChips pour la recherche active -->
    <FilterChips 
      filters={{ search: attendanceStore.policySearch ? [attendanceStore.policySearch] : [] }}
      activeFiltersCount={attendanceStore.policySearch ? 1 : 0}
      getDisplayLabel={(key, value) => `Recherche: ${value}`}
      onRemove={(key, value) => { attendanceStore.policySearch = ''; }}
      onReset={() => { attendanceStore.policySearch = ''; }}
      class="pb-2"
      badgeClass="bg-amber-50 text-amber-600 border-amber-100/50 hover:bg-amber-100"
    />
  </div>
{/snippet}

