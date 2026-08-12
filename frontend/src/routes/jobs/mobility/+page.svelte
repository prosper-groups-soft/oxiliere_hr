<script lang="ts">
  import { fade, fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import { useQueryClient } from '@tanstack/svelte-query';
  import { jobsStore } from "@/features/jobs/stores/jobs.svelte";
  import { transitionsStore } from "@/features/jobs/stores/transitionsStore.svelte";
  import { vacanciesStore } from "@/features/jobs/stores/vacanciesStore.svelte";
  import MobilityHeader from "@/features/jobs/components/mobility/layout/MobilityHeader.svelte";
  import TransitionsActions from "@/features/jobs/components/mobility/layout/actions/TransitionsActions.svelte";
  import VacanciesActions from "@/features/jobs/components/mobility/layout/actions/VacanciesActions.svelte";
  import TransitionList from "@/features/jobs/components/mobility/transitions/TransitionList.svelte";
  import VacancyList from "@/features/jobs/components/mobility/vacancies/VacancyList.svelte";
  import TransitionSheet from "@/features/jobs/components/mobility/transitions/sheets/TransitionSheet.svelte";
  import VacancySheet from "@/features/jobs/components/mobility/vacancies/sheets/VacancySheet.svelte";
  import { ui } from "@/stores/ui.svelte";
  import type { Transition, Vacancy } from "@/features/jobs/types/types";
  import { useTransitionsQuery, useDeleteTransitionMutation, transitionQueryKeys } from "@/features/jobs/queries/transitionQueries";
  import {
    useVacanciesQuery, useDeleteVacancyMutation,
    vacancyQueryKeys, syncVacancies
  } from "@/features/jobs/queries/vacancyQueries";

  
  // State
  let activeTab = $state<'transitions' | 'vacancies'>('transitions');

  let showTransitionSheet = $state(false);
  let showVacancySheet = $state(false);
  let selectedTransition = $state<Transition | null>(null);
  let selectedVacancy = $state<Vacancy | null>(null);

  // Load transitions from backend with pagination, search and filters
  const transitionsQuery = useTransitionsQuery(
    () => transitionsStore.page,
    () => transitionsStore.perPage,
    () => null, // no employee filter
    () => transitionsStore.firstTransitionType, // derived from store
    () => transitionsStore.searchQuery
  );
  const deleteMutation = useDeleteTransitionMutation();

  // Load vacancies from backend with pagination, search and filters
  const vacanciesQuery = useVacanciesQuery(
    () => vacanciesStore.page,
    () => vacanciesStore.perPage,
    () => vacanciesStore.searchQuery,
    () => vacanciesStore.filters.priority,
    () => vacanciesStore.filters.status
  );
  const deleteVacancyMutation = useDeleteVacancyMutation();

  // Sync vacancies with store when data changes
  $effect(() => {
    if ($vacanciesQuery.data?.results) {
      syncVacancies($vacanciesQuery);
    }
  });

  // Sync with store when data changes (sync all results, not just current page)
  $effect(() => {
    if ($transitionsQuery.data?.results) {
      jobsStore.setTransitions($transitionsQuery.data.results);
    }
  });

  // Invalidate query cache when search or filter changes to force fresh data
  const queryClient = useQueryClient();
  $effect(() => {
    // Track reactive dependencies
    const _search = transitionsStore.searchQuery;
    const _type = transitionsStore.firstTransitionType;
    
    // Invalidate transitions queries to force immediate refetch
    queryClient.invalidateQueries({ queryKey: transitionQueryKeys.all });
  });

  // Invalidate vacancies cache when search or filter changes
  $effect(() => {
    // Track reactive dependencies
    const _search = vacanciesStore.searchQuery;
    const _priority = vacanciesStore.filters.priority;
    const _status = vacanciesStore.filters.status;
    
    // Invalidate vacancies queries to force immediate refetch
    queryClient.invalidateQueries({ queryKey: vacancyQueryKeys.all });
  });

  // Derived pagination data from API response
  const transitionsData = $derived($transitionsQuery.data);
  const paginatedTransitions = $derived(transitionsData?.results || []);
  const totalTransitionCount = $derived(transitionsData?.count || 0);
  const totalTransitionPages = $derived(
    Math.max(1, Math.ceil(totalTransitionCount / transitionsStore.perPage))
  );

  function handleDeleteTransition(trans: Transition) {
    $deleteMutation.mutate(trans.id);
  }

  function handleDeleteVacancy(vac: Vacancy) {
    $deleteVacancyMutation.mutate(vac.id);
  }

  function handleSearchChange(value: string) {
    if (activeTab === 'transitions') {
      transitionsStore.setSearchQuery(value);
    } else {
      vacanciesStore.setSearchQuery(value);
    }
  }

  // Derived pagination data for vacancies
  const vacanciesData = $derived($vacanciesQuery.data);
  const paginatedVacancies = $derived(vacanciesData?.results || []);
  const totalVacancyCount = $derived(vacanciesData?.count || 0);
  const totalVacancyPages = $derived(
    Math.max(1, Math.ceil(totalVacancyCount / vacanciesStore.perPage))
  );

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

</script>


<svelte:head>
  <title>Oxiliere HR - Mobilité</title>
</svelte:head>


<!-- Global Actions Snippet -->
{#snippet ActionsSnippet()}
  <div class="flex items-center gap-2">
    {#if activeTab === 'transitions'}
      <TransitionsActions onAdd={() => { showTransitionSheet = true; selectedTransition = null; }} />
    {:else}
      <VacanciesActions onAdd={() => { showVacancySheet = true; selectedVacancy = null; }} />
    {/if}
  </div>
{/snippet}


<div class="flex h-full flex-col overflow-hidden min-h-0">

  <!-- Standard Header -->
  <MobilityHeader
    bind:activeTab
    searchQuery={activeTab === 'transitions' ? transitionsStore.searchQuery : vacanciesStore.searchQuery}
    onSearchQueryChange={handleSearchChange}
  />

  <!-- Main Content Area -->
  <main class="flex-1 grid grid-cols-1 overflow-hidden min-h-0">
    {#key activeTab}
      <div 
        class="col-start-1 row-start-1 flex flex-col min-h-0 overflow-y-auto custom-scrollbar" 
        style="--scrollbar-size: 6px"
        in:fly={{ y: 8, duration: 350, delay: 80, easing: cubicOut }} 
        out:fade={{ duration: 180 }}
      >
        {#if activeTab === 'transitions'}
          <TransitionList
            transitions={paginatedTransitions}
            onEdit={openTransitionSheet}
            onDelete={handleDeleteTransition}
            onNew={() => openTransitionSheet()}
            onRetry={() => $transitionsQuery.refetch()}
            isLoading={$transitionsQuery.isLoading}
            isError={$transitionsQuery.isError}
            error={$transitionsQuery.error}
            totalCount={totalTransitionCount}
            currentPage={transitionsStore.page}
            totalPages={totalTransitionPages}
            perPage={transitionsStore.perPage}
            onPageChange={(page) => transitionsStore.setPage(page)}
            onPerPageChange={(size) => transitionsStore.setPerPage(size)}
            onNext={() => transitionsStore.nextPage()}
            onPrev={() => transitionsStore.prevPage()}
          />
        {:else}
          <VacancyList
            vacancies={paginatedVacancies}
            onEdit={openVacancySheet}
            onDelete={handleDeleteVacancy}
            onNew={() => openVacancySheet()}
            onRetry={() => $vacanciesQuery.refetch()}
            isLoading={$vacanciesQuery.isLoading}
            isError={$vacanciesQuery.isError}
            error={$vacanciesQuery.error}
            totalCount={totalVacancyCount}
            currentPage={vacanciesStore.page}
            totalPages={totalVacancyPages}
            perPage={vacanciesStore.perPage}
            onPageChange={(page: number) => vacanciesStore.setPage(page)}
            onPerPageChange={(size: number) => vacanciesStore.setPerPage(size)}
            onNext={() => vacanciesStore.nextPage()}
            onPrev={() => vacanciesStore.prevPage()}
          />
        {/if}
      </div>
    {/key}
  </main>
</div>


<!-- Sheets -->
<TransitionSheet bind:open={showTransitionSheet} transition={selectedTransition} />
<VacancySheet bind:open={showVacancySheet} vacancy={selectedVacancy} />

