<script lang="ts">
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { vacanciesStore } from "../../../../stores/vacanciesStore.svelte";
  import { VACANCY_PRIORITY_OPTIONS, VACANCY_STATUS_OPTIONS } from "../../../../constants/vacancy.constants";
  let { onAdd, filterState = vacanciesStore } = $props<{ onAdd: () => void; filterState?: any }>();
  const fs = $derived(filterState ?? vacanciesStore);
  const filterDefs = [
    { key: "priority", label: "Priorité", icon: "triangle-alert", mode: "single" as const, options: VACANCY_PRIORITY_OPTIONS.map(o=>({value:o.value,label:o.label})) },
    { key: "status", label: "Statut", icon: "tag", mode: "single" as const, options: VACANCY_STATUS_OPTIONS.map(o=>({value:o.value,label:o.label})) }
  ];
  const adaptedState = $derived({
    filters: { priority: fs.filters.priority?[fs.filters.priority]:[], status: fs.filters.status?[fs.filters.status]:[] },
    activeFiltersCount: fs.activeFiltersCount,
    toggleFilter: (k:string,v:string)=> k==="priority" ? (fs.filters.priority===v?fs.clearPriority():fs.setPriority(v as any)) : (fs.filters.status===v?fs.clearStatus():fs.setStatus(v as any)),
    resetFilters: ()=>fs.resetFilters()
  });
</script>
<ActionBar>
  <FilterMenu {filterDefs} filterState={adaptedState} />
  <div class="w-px h-5 bg-slate-200 mx-1"></div>
  <Button onclick={onAdd} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={15} /> Nouveau besoin</Button>
</ActionBar>
