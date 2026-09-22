<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import SortMenu from "@/hr/actions/components/SortMenu.svelte";

  let { filterState = attendanceStore, onAdd } = $props<{ filterState?: any; onAdd?: () => void }>();

  const sortDefs = {
    options: [
      { value: "name", label: "Nom (A-Z)" },
      { value: "name_desc", label: "Nom (Z-A)" },
      { value: "created", label: "Date de création" },
      { value: "activeDays", label: "Jours actifs" },
    ]
  };

  // Adapter: SortMenu expects filterState.sortBy/sortOrder/setSort
  const fs = $derived({
    get sortBy() { return filterState.policySortBy ?? filterState.sortBy; },
    get sortOrder() { return filterState.policySortOrder ?? filterState.sortOrder; },
    setSort: (value: string, order: string) => {
      // map value back to policySortBy/Order when using attendanceStore
      if ('policySortBy' in filterState) {
        const isDesc = value.endsWith('_desc');
        filterState.policySortBy = isDesc ? value.replace('_desc','') : value;
        filterState.policySortOrder = isDesc ? 'desc' : (order as any);
        if (value === 'name' || value === 'name_desc') {
          filterState.policySortBy = 'name';
          filterState.policySortOrder = value === 'name_desc' ? 'desc' : 'asc';
        }
      } else {
        filterState.setSort?.(value, order);
      }
    },
    get activeFiltersCount() { return filterState.activeFiltersCount ?? (filterState.policySearch ? 1 : 0); },
    resetFilters: () => { if ('policySearch' in filterState) filterState.policySearch = ''; else filterState.resetFilters?.(); }
  });
</script>

<ActionBar>
  <SortMenu sortDefs={sortDefs} filterState={fs} />
  {#if (filterState.policySearch ? 1 : 0) > 0 || fs.activeFiltersCount > 0}
    <button onclick={() => fs.resetFilters()} class="flex items-center gap-1 px-2 py-0.5 rounded-full bg-slate-100 text-slate-600 text-[0.75rem] hover:bg-slate-200 transition-colors cursor-pointer">
      <span class="text-[0.8rem]">{fs.activeFiltersCount} filtre{fs.activeFiltersCount > 1 ? 's' : ''}</span>
      <AppIcon name="x" size={13} />
    </button>
  {/if}
  {#if onAdd}
    <button onclick={onAdd} class="h-7 px-3 text-[0.84rem] bg-primary text-white rounded-lg flex items-center gap-1.5"><AppIcon name="plus" size={15} /> Ajouter</button>
  {/if}
</ActionBar>
