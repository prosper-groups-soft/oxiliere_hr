<script lang="ts">
  import { fade, fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import SeniorityList from "@/hr/jobs/components/careers/seniority/SeniorityList.svelte";
  import PositionsList from "@/hr/jobs/components/careers/positions/PositionsList.svelte";
  import ProfessionalCategoryGrid from "@/hr/jobs/components/careers/grid/ProfessionalCategoryGrid.svelte";
  import CareersHeader from "@/hr/jobs/components/careers/layout/CareersHeader.svelte";
  import PositionsActions from "@/hr/jobs/components/careers/layout/actions/PositionsActions.svelte";
  import SeniorityActions from "@/hr/jobs/components/careers/layout/actions/SeniorityActions.svelte";
  import PositionSheet from "@/hr/jobs/components/careers/positions/sheets/PositionSheet.svelte";
  import SenioritySheet from "@/hr/jobs/components/careers/seniority/sheets/SenioritySheet.svelte";
  import { positionsStore } from "@/hr/jobs/stores/positionsStore.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { jobsStore } from "@/hr/jobs/stores/jobs.svelte";
  import { 
    useSeniorityLevelsQuery, 
    syncSeniorityLevels,
    useCreateSeniorityLevelMutation,
    useUpdateSeniorityLevelMutation,
    useDeleteSeniorityLevelMutation,
    useResetSeniorityLevelsMutation,
    usePositionsQuery,
    useCreatePositionMutation,
    useUpdatePositionMutation,
    useDeletePositionMutation,
    useJobFamiliesQuery,
    useCreateJobFamilyMutation,
    useUpdateJobFamilyMutation,
    useDeleteJobFamilyMutation,
    useProfessionalCategoriesQuery
  } from "@/hr/jobs/queries/jobQueries";
  import { useOrgUnitsQuery } from "@/hr/jobs/queries/orgQueries";
  import type { 
    JobPosition, 
    SeniorityLevelDefinition 
  } from "@/hr/jobs/types/types";

  
  // UI state
  let activeTab = $state<'positions' | 'seniority' | 'grid'>('positions');
  let showPositionSheet = $state(false);
  let showSenioritySheet = $state(false);
  let editingPosition = $state<JobPosition | null>(null);
  let editingSeniority = $state<SeniorityLevelDefinition | null>(null);
  
  // Search queries
  let senioritySearchQuery = $state('');
  
  // Search query courante selon l'onglet
  let currentSearchQuery = $derived(
    activeTab === 'positions' ? positionsStore.searchQuery : senioritySearchQuery
  );
  
  // Mettre à jour la bonne source quand la recherche change
  function handleSearchChange(value: string) {
    if (activeTab === 'positions') {
      positionsStore.searchQuery = value;
    } else {
      senioritySearchQuery = value;
    }
  }

  // Réinitialiser la recherche selon l'onglet actif
  function handleClearSearch() {
    if (activeTab === 'positions') {
      positionsStore.searchQuery = '';
    } else {
      senioritySearchQuery = '';
    }
  }

  // --- TanStack Query: Seniority Levels ---
  const seniorityQuery = useSeniorityLevelsQuery();
  const createSeniorityMutation = useCreateSeniorityLevelMutation();
  const updateSeniorityMutation = useUpdateSeniorityLevelMutation();
  const deleteSeniorityMutation = useDeleteSeniorityLevelMutation();
  const resetSeniorityMutation = useResetSeniorityLevelsMutation();

  // --- TanStack Query: Professional categories grid ---
  const professionalCategoriesQuery = useProfessionalCategoriesQuery();

  // --- TanStack Query: Positions ---
  const positionsQuery = usePositionsQuery();
  const createPositionMutation = useCreatePositionMutation();
  const updatePositionMutation = useUpdatePositionMutation();
  const deletePositionMutation = useDeletePositionMutation();

  // --- TanStack Query: JobFamilies ---
  const jobFamiliesQuery = useJobFamiliesQuery();
  const createJobFamilyMutation = useCreateJobFamilyMutation();
  const updateJobFamilyMutation = useUpdateJobFamilyMutation();
  const deleteJobFamilyMutation = useDeleteJobFamilyMutation();

  // --- TanStack Query: OrgUnits ---
  const orgUnitsQuery = useOrgUnitsQuery(() => 1, () => 500); // Non-paginated, load all

  // Sync backend data to store
  $effect(() => {
    syncSeniorityLevels($seniorityQuery);
  });

  // Sync positions to store
  $effect(() => {
    const data = $positionsQuery.data;
    if (data?.length) {
      jobsStore.positions = data;
    }
  });

  // Sync orgUnits to store
  $effect(() => {
    const data = $orgUnitsQuery.data;
    if (data?.results?.length) {
      jobsStore.setOrgUnits(data.results);
    }
  });

  // Sync jobFamilies to store
  $effect(() => {
    const data = $jobFamiliesQuery.data;
    if (data?.length) {
      jobsStore.setJobFamilies(data);
    }
  });

  // Persistence
  $effect(() => {
    const stored = localStorage.getItem('oxiliere_careers_active_tab');
    if (stored === 'positions' || stored === 'seniority' || stored === 'grid') {
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
    } else if (activeTab === 'seniority') {
      ui.addActions('career-seniority', SeniorityActionsSnippet);
      ui.removeActions('career-positions');
    } else {
      ui.removeActions('career-positions');
      ui.removeActions('career-seniority');
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

  function openSeniorityDelete(lvl: SeniorityLevelDefinition) {
    notification.confirm({
      title: 'Supprimer le niveau ?',
      message: `Voulez-vous vraiment supprimer le niveau "${lvl.name}" ? Cette action est irréversible.`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: async () => {
        await $deleteSeniorityMutation.mutateAsync(lvl.id);
      }
    });
  }

  function handleReset() {
    notification.confirm({
      title: 'Réinitialiser les niveaux ?',
      message: 'Voulez-vous vraiment réinitialiser tous les niveaux de séniorité aux valeurs par défaut ? Cette action supprimera toutes vos configurations personnalisées.',
      type: 'warning',
      yesText: 'Réinitialiser',
      onYes: async () => {
        await $resetSeniorityMutation.mutateAsync();
      }
    });
  }

  function openPositionDelete(pos: JobPosition) {
    notification.confirm({
      title: 'Supprimer le poste ?',
      message: `Voulez-vous vraiment supprimer le poste "${pos.name}" ?`,
      type: 'danger',
      yesText: 'Supprimer',
      onYes: async () => {
        await $deletePositionMutation.mutateAsync(pos.id);
      }
    });
  }

  function handlePositionSave(data: any, positionId?: string) {
    if (positionId) {
      // Update existing position
      return $updatePositionMutation.mutateAsync({ 
        id: positionId, 
        data: {
          name: data.title,
          family_name: data.familyName,
          org_unit_id: data.orgUnitId || null,
          description: data.description,
          seniority_levels: data.seniority_levels,
          requirements: data.requirements,
          skills: data.skills
        }
      });
    } else {
      // Create new position - need family_name
      return $createPositionMutation.mutateAsync({
        name: data.title,
        family_name: data.familyName,
        org_unit_id: data.orgUnitId || null,
        description: data.description,
        seniority_levels: data.seniority_levels,
        requirements: data.requirements,
        skills: data.skills
      });
    }
  }

  // --- JobFamily Handlers ---
  function handleCreateJobFamily(name: string, description?: string) {
    return $createJobFamilyMutation.mutateAsync({ name, description });
  }

  function handleUpdateJobFamily(id: string, name: string, description?: string) {
    return $updateJobFamilyMutation.mutateAsync({ id, data: { name, description } });
  }

  function handleDeleteJobFamily(id: string, name: string) {
    $deleteJobFamilyMutation.mutateAsync(id);
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
    onAdd={openSeniorityAdd}
    onReset={handleReset}
    isResetting={$resetSeniorityMutation.isPending}
  />
{/snippet}


<div class="flex h-full flex-col overflow-hidden min-h-0">
  <CareersHeader
    bind:activeTab
    searchQuery={currentSearchQuery}
    onSearchQueryChange={handleSearchChange}
    onClear={handleClearSearch}
  />

  <main class="flex-1 grid grid-cols-1 overflow-hidden min-h-0">
    {#key activeTab}
      <div class="col-start-1 row-start-1 flex flex-col min-h-0" in:fly={{ y: 8, duration: 350, delay: 80, easing: cubicOut }} out:fade={{ duration: 180 }}>
        {#if activeTab === 'positions'}
          <PositionsList 
            onEdit={openPositionEdit}
            onDelete={openPositionDelete}
            onNew={openPositionAdd}
            onRetry={() => $positionsQuery.refetch()}
            isLoading={$positionsQuery.isLoading}
            isError={$positionsQuery.isError}
            error={$positionsQuery.error}
            searchQuery={positionsStore.searchQuery}
          />
        {:else if activeTab === 'seniority'}
          <SeniorityList
            onEdit={openSeniorityEdit}
            onDelete={openSeniorityDelete}
            onNew={openSeniorityAdd}
            onClearSearch={() => senioritySearchQuery = ''}
            onRetry={() => $seniorityQuery.refetch()}
            isLoading={$seniorityQuery.isLoading}
            isError={$seniorityQuery.isError}
            error={$seniorityQuery.error}
            searchQuery={senioritySearchQuery}
          />
        {:else}
          <ProfessionalCategoryGrid
            categories={$professionalCategoriesQuery.data ?? []}
            isLoading={$professionalCategoriesQuery.isLoading}
          />
        {/if}
      </div>
    {/key}
  </main>
</div>


<PositionSheet 
  bind:open={showPositionSheet} 
  bind:position={editingPosition}
  onSave={handlePositionSave}
  onCreateJobFamily={handleCreateJobFamily}
  onUpdateJobFamily={handleUpdateJobFamily}
  onDeleteJobFamily={handleDeleteJobFamily}
/>

<SenioritySheet 
  bind:open={showSenioritySheet} 
  bind:level={editingSeniority} 
  onSave={async (data, levelId) => {
    if (levelId) {
      await $updateSeniorityMutation.mutateAsync({ 
        id: levelId, 
        data, 
        originalLevel: editingSeniority || undefined 
      });
    } else {
      await $createSeniorityMutation.mutateAsync(data);
    }
  }}
/>

