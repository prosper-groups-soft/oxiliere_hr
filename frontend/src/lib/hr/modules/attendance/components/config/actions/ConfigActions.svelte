<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import { useOrgUnitsQuery } from "@/hr/modules/jobs/queries/orgQueries";
  import { RECURRENCE_LABELS } from "../../../constants/attendance.constants";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import SortMenu from "@/hr/actions/components/SortMenu.svelte";
  import type { FilterDef } from "@/hr/actions/types";

  let { filterState = attendanceStore, onAdd } = $props<{ filterState?: any; onAdd?: () => void }>();

  const orgUnitsQuery = useOrgUnitsQuery();
  const orgUnits = $derived($orgUnitsQuery.data?.results || []);

  const filterDefs = $derived<FilterDef[]>([
    { key: 'orgUnit', label: 'Unités', icon: 'building-2', mode: 'multi', options: orgUnits.map((u: any) => ({ value: u.id, label: u.name })) },
    { key: 'recurrence', label: 'Récurrence', icon: 'refresh-cw', mode: 'multi', options: [
      { value: "NONE", label: RECURRENCE_LABELS.NONE },
      { value: "WEEKLY", label: RECURRENCE_LABELS.WEEKLY },
      { value: "BIWEEKLY", label: RECURRENCE_LABELS.BIWEEKLY },
      { value: "MONTHLY", label: RECURRENCE_LABELS.MONTHLY },
      { value: "QUARTERLY", label: RECURRENCE_LABELS.QUARTERLY },
    ]},
  ]);

  const sortDefs = { options: [
    { value: "name", label: "Nom (A-Z)" },
    { value: "name_desc", label: "Nom (Z-A)" },
    { value: "policy", label: "Modèle de travail" },
  ]};

  const fs = $derived({
    get filters() { return filterState.filters; },
    get activeFiltersCount() { return filterState.activeFiltersCount; },
    toggleFilter: (k: string, v: string) => filterState.toggleFilter(k, v),
    resetFilters: () => filterState.resetFilters(),
    get sortBy() { return filterState.sortBy; },
    get sortOrder() { return filterState.sortOrder; },
    setSort: (value: string, order: string) => {
      const isDesc = value.endsWith('_desc');
      const base = isDesc ? value.replace('_desc','') : value;
      filterState.setSort(base);
      filterState.sortOrder = isDesc ? 'desc' : (order as any) ?? 'asc';
      if (value === 'name_desc') filterState.sortOrder = 'desc';
    }
  });
</script>

<ActionBar>
  <SortMenu sortDefs={sortDefs} filterState={fs} />
  <FilterMenu filterDefs={filterDefs} filterState={fs} />
  {#if fs.activeFiltersCount > 0}
    <button onclick={() => fs.resetFilters()} class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer">
      <span class="text-[0.8rem]">{fs.activeFiltersCount} filtre{fs.activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}
  {#if onAdd}
    <button onclick={onAdd} class="h-7 px-3 text-[0.84rem] bg-primary text-white rounded-lg flex items-center gap-1.5"><AppIcon name="plus" size={15} /> Ajouter</button>
  {/if}
</ActionBar>
