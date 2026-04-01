<script lang="ts">
  import { fade, fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import SeniorityMatrix from "@/features/jobs/components/careers/seniority/SeniorityMatrix.svelte";
  import PositionsList from "@/features/jobs/components/careers/positions/PositionsList.svelte";
  import CareersHeader from "@/features/jobs/components/careers/layout/CareersHeader.svelte";
  import PositionsActions from "@/features/jobs/components/careers/layout/actions/PositionsActions.svelte";
  import SeniorityActions from "@/features/jobs/components/careers/layout/actions/SeniorityActions.svelte";
  import PositionSheet from "@/features/jobs/components/careers/positions/sheets/PositionSheet.svelte";
  import SenioritySheet from "@/features/jobs/components/careers/seniority/sheets/SenioritySheet.svelte";
  import { positionsStore } from "@/features/jobs/stores/positionsStore.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { jobsStore } from "@/features/jobs/stores/jobs.svelte";
  import type { 
    JobPosition, 
    SeniorityLevelDefinition 
  } from "@/features/jobs/types/types";

  // UI state
  let activeTab = $state<'positions' | 'seniority'>('positions');
  let showPositionSheet = $state(false);
  let showSenioritySheet = $state(false);
  let editingPosition = $state<JobPosition | null>(null);
  let editingSeniority = $state<SeniorityLevelDefinition | null>(null);
  let isResettingSeniority = $state(false);

  // Persistence
  $effect(() => {
    const stored = localStorage.getItem('oxiliere_careers_active_tab');
    if (stored === 'positions' || stored === 'seniority') {
      activeTab = stored;
    }
  });

  $effect(() => {
    localStorage.setItem('oxiliere_careers_active_tab', activeTab);
  });

  /**
   * GLOBAL ACTION REGISTRATION
   */
  $effect(() => {
    if (activeTab === 'positions') {
      ui.addActions('career-positions', PositionsActionsSnippet);
      ui.removeActions('career-seniority');
    } else {
      ui.addActions('career-seniority', SeniorityActionsSnippet);
      ui.removeActions('career-positions');
    }
    return () => {
      ui.removeActions('career-positions');
      ui.removeActions('career-seniority');
    };
  });

  function openPositionAdd() {
    editingPosition = null;
    showPositionSheet = true;
  }

  function openPositionEdit(pos: JobPosition) {
    editingPosition = pos;
    showPositionSheet = true;
  }

  function openSeniorityAdd() {
    editingSeniority = null;
    showSenioritySheet = true;
  }

  function openSeniorityEdit(lvl: SeniorityLevelDefinition) {
    editingSeniority = lvl;
    showSenioritySheet = true;
  }

  function handleResetSeniority() {
    isResettingSeniority = true;
    jobsStore.restoreDefaultSeniorityLevels();
    notification.toast.success("Niveaux réinitialisés par défaut");
    setTimeout(() => isResettingSeniority = false, 1000);
  }

  function openSeniorityDelete(lvl: SeniorityLevelDefinition) {
    notification.confirm({
      title: 'Supprimer le niveau ?',
      message: `Voulez-vous vraiment supprimer le niveau "${lvl.name}" ? Cette action est irréversible.`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => {
        jobsStore.deleteSeniorityLevel(lvl.id);
        notification.toast.success(`Le niveau "${lvl.name}" a été supprimé.`);
      }
    });
  }

  function openPositionDelete(pos: JobPosition) {
    notification.confirm({
      title: 'Supprimer le poste ?',
      message: `Voulez-vous vraiment supprimer le poste "${pos.title}" ?`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: () => {
        jobsStore.deletePosition(pos.id);
        notification.toast.success(`Le poste "${pos.title}" a été supprimé.`);
      }
    });
  }
</script>


<svelte:head>
  <title>Oxiliere HR - Carrières</title>
</svelte:head>


<!-- WRAPPERS FOR ui.addActions -->
{#snippet PositionsActionsSnippet()}
  <PositionsActions onAdd={openPositionAdd} />
{/snippet}


{#snippet SeniorityActionsSnippet()}
  <SeniorityActions 
    isResetting={isResettingSeniority} 
    onAdd={openSeniorityAdd} 
    onReset={handleResetSeniority} 
  />
{/snippet}


<div class="flex h-full flex-col overflow-hidden min-h-0">
  <CareersHeader 
    bind:activeTab
    bind:searchQuery={positionsStore.searchQuery} 
  />

  <main class="flex-1 grid grid-cols-1 overflow-hidden min-h-0">
    {#key activeTab}
      <div class="col-start-1 row-start-1 flex flex-col min-h-0" in:fly={{ y: 8, duration: 350, delay: 80, easing: cubicOut }} out:fade={{ duration: 180 }}>
        {#if activeTab === 'positions'}
          <PositionsList 
            onEdit={openPositionEdit}
            onDelete={openPositionDelete}
            onNew={openPositionAdd}
          />
        {:else}
          <SeniorityMatrix 
            onEdit={openSeniorityEdit} 
            onDelete={openSeniorityDelete}
            onNew={openSeniorityAdd} 
          />
        {/if}
      </div>
    {/key}
  </main>
</div>


<PositionSheet 
  bind:open={showPositionSheet} 
  bind:position={editingPosition} 
/>
<SenioritySheet 
  bind:open={showSenioritySheet} 
  bind:level={editingSeniority} 
/>

