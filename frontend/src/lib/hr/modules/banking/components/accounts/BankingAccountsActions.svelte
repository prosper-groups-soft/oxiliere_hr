<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { bankingStore } from "../../stores/banking.svelte";
  import { VERIFICATION_STATUS_LABELS } from "../../constants";
  import { CURRENCIES } from "@/hr/constants/finance";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import SortMenu from "@/hr/actions/components/SortMenu.svelte";
  import type { FilterDef } from "@/hr/actions/types";

  let { filterState = bankingStore, onAdd } = $props<{ filterState?: any; onAdd?: () => void }>();

  const filterDefs = $derived<FilterDef[]>([
    { key: 'status', label: 'Statut', icon: 'user-check', mode: 'multi', options: Object.entries(VERIFICATION_STATUS_LABELS).map(([v,l]) => ({ value: v, label: l })) },
    { key: 'currency', label: 'Devise', icon: 'coins', mode: 'multi', options: Object.values(CURRENCIES).map(c => ({ value: c, label: c })) },
    { key: 'institutionId', label: 'Institution', icon: 'building-2', mode: 'multi', options: (filterState.institutions ?? bankingStore.institutions).map((i: any) => ({ value: i.id, label: i.name })) },
  ]);
  const sortDefs = { options: [{ value: 'created_at', label: 'Date de création' }, { value: 'account_name', label: 'Nom du compte' }] };
  const fs = $derived({
    get filters() { return filterState.filters; },
    get activeFiltersCount() { return filterState.activeFiltersCount; },
    toggleFilter: (k: string, v: string) => filterState.toggleFilter(k, v),
    resetFilters: () => filterState.resetFilters(),
    get sortBy() { return filterState.sortBy; },
    get sortOrder() { return filterState.sortOrder; },
    setSort: (v: string, o: string) => { filterState.setSort(v); if(o) filterState.sortOrder = o; },
    toggleSortOrder: () => filterState.toggleSortOrder?.()
  });
</script>

<ActionBar>
  <SortMenu sortDefs={sortDefs} filterState={fs} />
  <FilterMenu filterDefs={filterDefs} filterState={fs} />
  {#if fs.activeFiltersCount > 0}
    <button onclick={() => fs.resetFilters()} class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer">
      <span class="text-[0.8rem]">{fs.activeFiltersCount} filtre{fs.activeFiltersCount > 1 ? 's' : ''}</span><AppIcon name="x" size={13} />
    </button>
  {/if}
  {#if onAdd}<button onclick={onAdd} class="h-7 px-3 bg-primary text-white rounded-lg text-[0.84rem] flex items-center gap-1"><AppIcon name="plus" size={14}/> Ajouter</button>{/if}
</ActionBar>
