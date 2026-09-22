<script lang="ts">
  import { fade, fly } from "svelte/transition";
  import { cubicOut } from "svelte/easing";
  import MobilityHeader from "@/hr/modules/jobs/components/mobility/layout/MobilityHeader.svelte";
  import TransitionsActions from "@/hr/modules/jobs/components/mobility/layout/actions/TransitionsActions.svelte";
  import VacanciesActions from "@/hr/modules/jobs/components/mobility/layout/actions/VacanciesActions.svelte";
  import TransitionList from "@/hr/modules/jobs/components/mobility/transitions/TransitionList.svelte";
  import VacancyList from "@/hr/modules/jobs/components/mobility/vacancies/VacancyList.svelte";
  import TransitionSheet from "@/hr/modules/jobs/components/mobility/transitions/sheets/TransitionSheet.svelte";
  import VacancySheet from "@/hr/modules/jobs/components/mobility/vacancies/sheets/VacancySheet.svelte";
  import { ui } from "@/hr/stores/ui.svelte";
  import type { Transition, Vacancy } from "@/hr/modules/jobs/types/types";
  import { useDeleteTransitionMutation } from "@/hr/modules/jobs/queries/transitionQueries";
  import { useDeleteVacancyMutation } from "@/hr/modules/jobs/queries/vacancyQueries";
  import { createFilterState } from "@/hr/async/filters/filterState.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import AsyncView from "@/hr/async/components/AsyncView.svelte";
  import { transitionsService } from "@/hr/modules/jobs/services/transitionsService";
  import { vacanciesService } from "@/hr/modules/jobs/services/vacanciesService";

  let activeTab = $state<'transitions' | 'vacancies'>('transitions');
  let showTransitionSheet = $state(false);
  let showVacancySheet = $state(false);
  let selectedTransition = $state<Transition | null>(null);
  let selectedVacancy = $state<Vacancy | null>(null);

  const transUi = createFilterState<{ type: string[] }>({ type: [] });
  const vacUi = createFilterState<{ priority: string[], status: string[] }>({ priority: [], status: [] });

  const transitionsRes = useAsyncResource(
    () => ({ queryKey: ['transitions', transUi.page, transUi.perPage, transUi.search, transUi.filters.type[0] ?? null], queryFn: () => transitionsService.listTransitions({ page: transUi.page, perPage: transUi.perPage, search: transUi.search, type: transUi.filters.type[0] ?? null } as any) }),
    { mapData: (d: any) => ({ items: d.results ?? [], total: d.count ?? 0, totalPages: Math.ceil((d.count ?? 0) / transUi.perPage) }) }
  );
  const vacanciesRes = useAsyncResource(
    () => ({ queryKey: ['vacancies', vacUi.page, vacUi.perPage, vacUi.search, vacUi.filters.priority, vacUi.filters.status], queryFn: () => vacanciesService.listVacancies({ page: vacUi.page, perPage: vacUi.perPage, search: vacUi.search, priority: vacUi.filters.priority, status: vacUi.filters.status } as any) }),
    { mapData: (d: any) => ({ items: d.results ?? [], total: d.count ?? 0, totalPages: Math.ceil((d.count ?? 0) / vacUi.perPage) }) }
  );

  const deleteTransMutation = useDeleteTransitionMutation();
  const deleteVacMutation = useDeleteVacancyMutation();

  function handleSearchChange(v: string) { if (activeTab === 'transitions') transUi.setSearch(v); else vacUi.setSearch(v); }
  $effect(() => { ui.addActions('mobility-main', ActionsSnippet); return () => ui.removeActions('mobility-main'); });
  function openTransitionSheet(t?: Transition) { selectedTransition = t ?? null; showTransitionSheet = true; }
  function openVacancySheet(v?: Vacancy) { selectedVacancy = v ?? null; showVacancySheet = true; }
</script>

<svelte:head><title>Oxiliere HR - Mobilité</title></svelte:head>

{#snippet ActionsSnippet()}
  <div class="flex items-center gap-2">
    {#if activeTab === 'transitions'}<TransitionsActions onAdd={() => openTransitionSheet()} />{:else}<VacanciesActions onAdd={() => openVacancySheet()} />{/if}
  </div>
{/snippet}

<div class="flex h-full flex-col overflow-hidden min-h-0">
  <MobilityHeader bind:activeTab searchQuery={activeTab === 'transitions' ? transUi.search : vacUi.search} onSearchQueryChange={handleSearchChange} />
  <main class="flex-1 grid grid-cols-1 overflow-hidden min-h-0">
    {#key activeTab}
      <div class="col-start-1 row-start-1 flex flex-col min-h-0 overflow-y-auto custom-scrollbar" in:fly={{ y: 8, duration: 350, delay: 80, easing: cubicOut }} out:fade={{ duration: 180 }}>
        {#if activeTab === 'transitions'}
          <AsyncView state={transitionsRes} loadingText="Chargement des mouvements" emptyWhen={(d)=>d.total===0} isFiltered={!!transUi.search || transUi.filters.type.length>0} searchQuery={transUi.search} onResetFilters={()=>transUi.resetFilters()} onCreate={()=>openTransitionSheet()}>
            {#snippet children(data)}<TransitionList transitions={data.items} onEdit={openTransitionSheet} onDelete={(t)=>$deleteTransMutation.mutate(t.id)} />{/snippet}
          </AsyncView>
        {:else}
          <AsyncView state={vacanciesRes} loadingText="Chargement des besoins" emptyWhen={(d)=>d.total===0} isFiltered={!!vacUi.search || vacUi.activeFiltersCount>0} searchQuery={vacUi.search} onResetFilters={()=>vacUi.resetFilters()} onCreate={()=>openVacancySheet()}>
            {#snippet children(data)}<VacancyList vacancies={data.items} onEdit={openVacancySheet} onDelete={(v)=>$deleteVacMutation.mutate(v.id)} />{/snippet}
          </AsyncView>
        {/if}
      </div>
    {/key}
  </main>
</div>

<TransitionSheet bind:open={showTransitionSheet} transition={selectedTransition} />
<VacancySheet bind:open={showVacancySheet} vacancy={selectedVacancy} />
