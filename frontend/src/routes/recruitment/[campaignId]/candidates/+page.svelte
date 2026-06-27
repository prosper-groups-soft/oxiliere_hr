<script lang="ts">
  import { page } from '$app/state';
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import CandidatesList from '@/features/recruitment/components/lists/CandidatesList.svelte';
  import { STAGE_CONFIG } from '@/features/recruitment/constants/recruitment';
  import { useCandidatesQuery, syncRecruitmentCandidates } from '@/features/recruitment/queries/recruitmentQueries';
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Button } from "@/components/ui/button";
  import { 
    CANDIDATE_STAGE_OPTIONS, CANDIDATE_STAGE_LABELS, CANDIDATE_PRIORITY_OPTIONS,
    CANDIDATE_PRIORITY_LABELS, CANDIDATE_SOURCE_OPTIONS, CANDIDATE_SOURCE_LABELS,
    CANDIDATE_GENDER_OPTIONS, CANDIDATE_GENDER_LABELS
  } from '@/features/recruitment/constants/recruitment';
  

  const campaignId = $derived(page.params.campaignId);
  const offerId = $derived(campaignId ? campaignId : undefined);

  // Pagination — dans le store
  const candidatesPage = $derived(recruitmentStore.candidateCurrentPage);

  // Récupère les candidats de la campagne via la query TanStack avec pagination et filtres
  const candidatesQuery = useCandidatesQuery(
    () => offerId,
    () => recruitmentStore.candidateCurrentPage,
    () => recruitmentStore.candidatePerPage,
    () => recruitmentStore.filters.search,
    () => recruitmentStore.filters.stage || [],
    () => recruitmentStore.filters.source || [],
    () => recruitmentStore.filters.priority || [],
    () => recruitmentStore.filters.positionId || [],
    () => recruitmentStore.filters.gender || []
  );

  // Candidats déjà groupés par le backend
  const candidates = $derived($candidatesQuery.data?.results || []);
  const totalCount = $derived($candidatesQuery.data?.count || 0);

  const totalPages = $derived(
    totalCount > 0
      ? Math.ceil(totalCount / recruitmentStore.candidatePerPage)
      : 1
  );

  // Synchronise les données de la query dans le store
  // $candidatesQuery est nécessaire pour souscrire réactivement au store TanStack
  $effect(() => {
    syncRecruitmentCandidates($candidatesQuery);
  });

  // Re-fetch quand les filtres ou la pagination changent
  $effect(() => {
    // Surveiller les changements de filtres et pagination
    recruitmentStore.filters;
    recruitmentStore.candidateCurrentPage;
    recruitmentStore.candidatePerPage;

    // Forcer le re-fetch
    $candidatesQuery.refetch();
  });

  // Callbacks de pagination
  function onPageChange(page: number) {
    recruitmentStore.candidateCurrentPage = page;
  }

  function onNext() {
    if (recruitmentStore.candidateCurrentPage < totalPages) {
      recruitmentStore.candidateCurrentPage++;
    }
  }

  function onPrev() {
    if (recruitmentStore.candidateCurrentPage > 1) {
      recruitmentStore.candidateCurrentPage--;
    }
  }

  function onPerPageChange(size: number) {
    recruitmentStore.candidatePerPage = size;
    recruitmentStore.candidateCurrentPage = 1; // Reset à la page 1 quand on change le nombre par page
  }

  const activeStages = $derived(recruitmentStore.filters.stage || []);
  const activePriorities = $derived(recruitmentStore.filters.priority || []);
  const activeSources = $derived(recruitmentStore.filters.source || []);
  const activePositionIds = $derived(recruitmentStore.filters.positionId || []);
  const activeGenders = $derived(recruitmentStore.filters.gender || []);

  // Campaign positions for the position filter dropdown
  const campaignPositions = $derived(recruitmentStore.currentCampaign?.positions || []);

  function onRetry() {
    $candidatesQuery.refetch();
  }
</script>


<div class="h-full flex flex-col overflow-hidden bg-white">
  <!-- Filter Toolbar -->
  <div class="px-6 py-1.5 border-b border-slate-100 bg-white shadow-none flex items-center justify-between">
    <div class="flex items-center justify-between w-full">
      <!-- Search -->
      <SearchBar 
        bind:value={recruitmentStore.filters.search} 
        placeholder="Rechercher un candidat..."
        onClear={() => recruitmentStore.filters.search = ''}
        class="w-125"
        inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
        iconSize={22}
      />

      <div class="flex items-center gap-2">
        {@render PositionFilter()}
        {@render StageFilter()}
        {@render PriorityFilter()}
        {@render GenderFilter()}
        {@render SourceFilter()}

        {#if recruitmentStore.activeCandidateFiltersCount > 0}
          <button
            onclick={() => recruitmentStore.resetFilters()}
            class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer"
          >
            <span class="text-[0.8rem]">{recruitmentStore.activeCandidateFiltersCount} filtre{recruitmentStore.activeCandidateFiltersCount > 1 ? 's' : ''}</span>
            <AppIcon name="x" size={13} />
          </button>
        {/if}
      </div>
    </div>
  </div>

  <!-- Active Removal Chips (Dynamic Context) -->
  <FilterChips 
    filters={recruitmentStore.filters}
    activeFiltersCount={recruitmentStore.activeCandidateFiltersCount} 
    onRemove={(key, value) => recruitmentStore.toggleFilter(key as any, value)}
    onReset={() => recruitmentStore.resetFilters()}
    getDisplayLabel={(key, value) => {
      if (key === 'stage') return CANDIDATE_STAGE_LABELS[value] || value;
      if (key === 'priority') return CANDIDATE_PRIORITY_LABELS[value] || value;
      if (key === 'source') return CANDIDATE_SOURCE_LABELS[value] || value;
      if (key === 'gender') return CANDIDATE_GENDER_LABELS[value] || value;
      if (key === 'positionId') return campaignPositions.find(p => p.id === value)?.name || value;
      return value;
    }}
    class="py-1 pt-0 px-6 border-b border-slate-100"
  />

  <div class="flex-1">
      <CandidatesList
        {candidates}
        stageConfig={STAGE_CONFIG}
        isLoading={$candidatesQuery.isLoading}
        isError={$candidatesQuery.isError}
        error={$candidatesQuery.error}
        activeFiltersCount={recruitmentStore.activeCandidateFiltersCount}
        {onRetry}
      />
    </div>

    <!-- Pagination (cachée si aucun résultat) -->
    {#if totalCount > 0}
      <div class="px-6 py-0.5 border-t border-slate-100 bg-white shrink-0">
        <DataPagination
          currentCount={candidates.length}
          totalCount={totalCount}
          currentPage={candidatesPage}
          totalPages={totalPages}
          perPage={recruitmentStore.candidatePerPage}
          {onPageChange}
          {onPerPageChange}
          {onNext}
          {onPrev}
          unitLabel="candidats"
        />
      </div>
    {/if}
</div>


{#snippet PositionFilter()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="briefcase" size={15} class="mr-1.5" />
        Postes
        {#if activePositionIds.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {activePositionIds.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="start" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Filtrer par poste
      </DropdownMenu.Label>

      {#each campaignPositions as pos}
        {@const active = activePositionIds.includes(pos.id)}
        <DropdownMenu.Item
          onclick={() => recruitmentStore.toggleFilter('positionId', pos.id)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name="briefcase" size={16} class="text-slate-500" />
            {pos.name}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {:else}
        <p class="text-[0.84rem] text-slate-400 px-3 py-3 text-center">
          Aucun poste défini
        </p>
      {/each}

      {#if activePositionIds.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => { recruitmentStore.filters.positionId = []; }}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

{#snippet StageFilter()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="list-filter" size={15} class="mr-1.5" />
        Étapes
        {#if activeStages.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {activeStages.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="start" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Filtrer par étape
      </DropdownMenu.Label>

      {#each CANDIDATE_STAGE_OPTIONS as stage}
        {@const active = activeStages.includes(stage.value)}
        <DropdownMenu.Item
          onclick={() => recruitmentStore.toggleFilter('stage', stage.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={stage.icon} size={16} class="text-slate-500" />
            {stage.label}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if activeStages.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => { recruitmentStore.filters.stage = []; }}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet PriorityFilter()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="flag" size={15} class="mr-1.5" />
        Priorité
        {#if activePriorities.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {activePriorities.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="start" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Filtrer par priorité
      </DropdownMenu.Label>

      {#each CANDIDATE_PRIORITY_OPTIONS as prio}
        {@const active = activePriorities.includes(prio.value)}
        <DropdownMenu.Item
          onclick={() => recruitmentStore.toggleFilter('priority', prio.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{prio.label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if activePriorities.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => { recruitmentStore.filters.priority = []; }}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet SourceFilter()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="share-2" size={15} class="mr-1.5" />
        Source
        {#if activeSources.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {activeSources.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="start" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Filtrer par source
      </DropdownMenu.Label>

      {#each CANDIDATE_SOURCE_OPTIONS as src}
        {@const active = activeSources.includes(src.value)}
        <DropdownMenu.Item
          onclick={() => recruitmentStore.toggleFilter('source', src.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="text-[0.86rem]">{src.label}</span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if activeSources.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => { recruitmentStore.filters.source = []; }}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


{#snippet GenderFilter()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="users" size={15} class="mr-1.5" />
        Sexe
        {#if activeGenders.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {activeGenders.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="start" class="w-48 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Filtrer par sexe
      </DropdownMenu.Label>

      {#each CANDIDATE_GENDER_OPTIONS as opt}
        {@const active = activeGenders.includes(opt.value)}
        <DropdownMenu.Item
          onclick={() => recruitmentStore.toggleFilter('gender', opt.value)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name={opt.icon} size={16} class="text-slate-500" />
            {opt.label}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {/each}

      {#if activeGenders.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => { recruitmentStore.filters.gender = []; }}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

