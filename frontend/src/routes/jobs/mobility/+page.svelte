<script lang="ts">
  import { fade, fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { jobsStore } from "$lib/features/jobs/stores/jobs.svelte";
  import MobilityHeader from "@/features/jobs/components/mobility/layout/MobilityHeader.svelte";
  import TransitionList from "@/features/jobs/components/mobility/transitions/TransitionList.svelte";
  import VacancyList from "@/features/jobs/components/mobility/vacancies/VacancyList.svelte";
  import TransitionSheet from "@/features/jobs/components/mobility/transitions/sheets/TransitionSheet.svelte";
  import VacancySheet from "@/features/jobs/components/mobility/vacancies/sheets/VacancySheet.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { Transition, Vacancy } from "$lib/features/jobs/types/types";

  // State
  let activeTab = $state<'transitions' | 'vacancies'>('transitions');
  let searchQuery = $state('');
  
  let showTransitionSheet = $state(false);
  let showVacancySheet = $state(false);
  let selectedTransition = $state<Transition | null>(null);
  let selectedVacancy = $state<Vacancy | null>(null);

  /**
   * GLOBAL ACTION REGISTRATION
   */
  $effect(() => {
    ui.addActions('mobility-main', ActionsSnippet);
    return () => ui.removeActions('mobility-main');
  });

  function openTransitionSheet(trans?: Transition) {
    selectedTransition = trans || null;
    showTransitionSheet = true;
  }

  function openVacancySheet(vac?: Vacancy) {
    selectedVacancy = vac || null;
    showVacancySheet = true;
  }

  // Filtered data
  const filteredTransitions = $derived(
    jobsStore.transitions.filter(t => 
      !searchQuery || 
      String(t.employeeId).toLowerCase().includes(searchQuery.toLowerCase()) ||
      t.reason?.toLowerCase().includes(searchQuery.toLowerCase())
    )
  );

  const filteredVacancies = $derived(
    jobsStore.vacancies.filter(v => {
      const pos = jobsStore.positions.find(p => p.id === v.positionId);
      return !searchQuery || pos?.title.toLowerCase().includes(searchQuery.toLowerCase());
    })
  );
</script>

<svelte:head>
  <title>Oxiliere HR - Mobilité</title>
</svelte:head>


<!-- Global Actions Snippet -->
{#snippet ActionsSnippet()}
  <div class="flex items-center gap-2">
    <Button 
      onclick={() => activeTab === 'transitions' ? openTransitionSheet() : openVacancySheet()}
      variant="default" 
      class="h-7 px-3 text-[0.78rem] text-white shadow-fine rounded-lg transition-all"
    >
      <AppIcon name="plus" size={15} />
      {activeTab === 'transitions' ? 'Nouveau mouvement' : 'Nouveau besoin'}
    </Button>
  </div>
{/snippet}


<div class="flex h-full flex-col overflow-hidden min-h-0">
  <!-- Standard Header -->
  <MobilityHeader 
    bind:activeTab 
    bind:searchQuery 
  />

  <!-- Main Content Area -->
  <main class="flex-1 grid grid-cols-1 overflow-hidden min-h-0">
    {#key activeTab}
      <div 
        class="col-start-1 row-start-1 flex flex-col min-h-0 overflow-y-auto custom-scrollbar" 
        in:fly={{ y: 8, duration: 350, delay: 80, easing: cubicOut }} 
        out:fade={{ duration: 180 }}
      >
        {#if activeTab === 'transitions'}
          <TransitionList 
            transitions={filteredTransitions}
            onEdit={openTransitionSheet}
            onNew={() => openTransitionSheet()}
          />
        {:else}
          <VacancyList 
            vacancies={filteredVacancies}
            onEdit={openVacancySheet}
            onNew={() => openVacancySheet()}
          />
        {/if}
      </div>
    {/key}
  </main>
</div>


<!-- Sheets -->
<TransitionSheet bind:open={showTransitionSheet} transition={selectedTransition} />
<VacancySheet bind:open={showVacancySheet} vacancy={selectedVacancy} />


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
</style>

