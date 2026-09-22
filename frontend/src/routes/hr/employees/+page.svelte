<script lang="ts">
  import { fade } from "svelte/transition";
  import DataPagination from "@/hr/components/layout/elements/DataPagination.svelte";
  import EmployeeList from "@/hr/modules/employees/components/mgmt/list/EmployeeList.svelte";
  import SearchBar from "@/hr/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/hr/components/shared/elements/FilterChips.svelte";
  import EmployeesActions from "@/hr/modules/employees/components/mgmt/layout/actions/EmployeesActions.svelte";
  import { useOrgUnitsQuery } from "@/hr/modules/jobs/queries/orgQueries";
  import { CONTRACT_TYPES } from "@/hr/modules/employees/constants/contract";
  import { EMPLOYEE_STATUS_CONFIG } from "@/hr/modules/employees/constants/employeeStatus";
  import { ui } from "@/hr/stores/ui.svelte";
  import { goto } from '$app/navigation';
  import { hr } from '@/hr/constants/navigation/navigation';
  import { createFilterState } from "@/hr/async/filters/filterState.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import AsyncView from "@/hr/async/components/AsyncView.svelte";
  import { employeesService } from "@/hr/modules/employees/services/employees.service";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";

  const uiState = createFilterState<{ orgUnit: string[], status: string[], location: string[], contractType: string[] }>({
    orgUnit: [], status: [], location: [], contractType: []
  });

  const employees = useAsyncResource(
    () => ({
      queryKey: ['employees', uiState.page, uiState.perPage, uiState.search, uiState.filters, uiState.sortBy, uiState.sortOrder],
      queryFn: () => employeesService.listEmployees({
        page: uiState.page, perPage: uiState.perPage, search: uiState.search,
        filters: uiState.filters, sortBy: uiState.sortBy, sortOrder: uiState.sortOrder
      })
    }),
    { mapData: (d: any) => ({ items: d.results, total: d.count, totalPages: Math.ceil(d.count / uiState.perPage) }) }
  );

  const orgUnitsQuery = useOrgUnitsQuery();
  const orgUnits = $derived($orgUnitsQuery.data?.results || []);

  const filtersWithSearch = $derived.by(() => {
    const f = { ...uiState.filters } as Record<string, string[]>;
    if (uiState.search) f.search = [uiState.search];
    return f;
  });

  function getFilterDisplayLabel(key: string, value: string): string {
    if (key === 'orgUnit') return orgUnits.find(u => u.id === value)?.name ? `Unité: ${orgUnits.find(u => u.id === value)!.name}` : `Unité: ${value}`;
    if (key === 'status') return EMPLOYEE_STATUS_CONFIG[value]?.label ?? value;
    if (key === 'contractType') return CONTRACT_TYPES.find(c => c.value === value)?.label ? `Contrat: ${CONTRACT_TYPES.find(c => c.value === value)!.label}` : value;
    if (key === 'location') return `Localité: ${value}`;
    if (key === 'search') return `Recherche: “${value}”`;
    return value;
  }

  function openEmployeeAdd() { goto(hr('/employees/onboarding')); }
  function toggleViewMode() { uiState.toggleViewMode(); }

  $effect(() => {
    ui.addActions('employees', EmployeesActionsSnippet);
    return () => ui.removeActions('employees');
  });
</script>

<svelte:head><title>Oxiliere HR - Employés</title></svelte:head>

<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}
  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips
      filters={filtersWithSearch}
      activeFiltersCount={uiState.activeFiltersCount + (uiState.search ? 1 : 0)}
      getDisplayLabel={getFilterDisplayLabel}
      onRemove={(key, value) => key === 'search' ? uiState.setSearch('') : uiState.toggleFilter(key as any, value)}
      onReset={() => uiState.resetFilters()}
      class="py-1 pb-1.5 px-6 border-b border-slate-50"
    />
    <AsyncView state={employees} loadingText="Chargement des employés" emptyWhen={(d) => d.total === 0}>
      {#snippet children(data)}
        <div class="flex-1 overflow-y-auto min-h-0" transition:fade={{ duration: 200 }}>
          <EmployeeList employees={data.items} viewMode={uiState.viewMode} activeFiltersCount={uiState.activeFiltersCount} searchQuery={uiState.search} onResetFilters={() => uiState.resetFilters()} onAdd={openEmployeeAdd} />
        </div>
      {/snippet}
    </AsyncView>
    {#if employees.data && employees.data.total > 0}
      <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
        <DataPagination currentCount={employees.data.items.length} totalCount={employees.data.total} currentPage={uiState.page} totalPages={employees.data.totalPages} perPage={uiState.perPage} onPageChange={(p) => uiState.setPage(p)} onPerPageChange={(s) => uiState.setPerPage(s)} onNext={() => uiState.nextPage()} onPrev={() => uiState.prevPage()} unitLabel="profils" />
      </div>
    {/if}
  </div>
</div>

{#snippet EmployeesActionsSnippet()}
  <EmployeesActions onAdd={openEmployeeAdd} onToggleViewMode={toggleViewMode} />
{/snippet}

{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
    <div class="flex items-center justify-between">
      <div class="flex-1 ml-0.5">
        <SearchBar bind:value={uiState.search} placeholder="Rechercher un profil..." class="w-125" inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]" iconSize={22} onClear={() => uiState.setSearch("")} />
      </div>
      {@render QuickStats()}
    </div>
  </div>
{/snippet}

{#snippet QuickStats()}
  <div class="flex items-center gap-5 px-4 py-1">
    <div class="flex items-center gap-2"><AppIcon name="users" size={17} class="text-slate-500" /><span class="text-sm font-semibold text-slate-800 tabular-nums">{employees.data?.total ?? 0}</span><span class="text-sm text-slate-400">total</span></div>
    <div class="flex items-center gap-2"><AppIcon name="user-check" size={17} class="text-green-500" /><span class="text-sm font-semibold text-green-600 tabular-nums">{employees.data?.items.filter((e: any) => e.status === 'active').length ?? 0}</span><span class="text-sm text-slate-400">actifs</span></div>
    {#if uiState.activeFiltersCount > 0}<div class="flex items-center gap-2"><AppIcon name="filter" size={17} class="text-blue-500" /><span class="text-sm font-semibold text-blue-600 tabular-nums">{uiState.activeFiltersCount}</span><span class="text-sm text-slate-400">filtres</span></div>{/if}
  </div>
{/snippet}
