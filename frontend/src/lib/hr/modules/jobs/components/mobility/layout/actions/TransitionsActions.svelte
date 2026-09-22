<script lang="ts">
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { transitionsStore } from "../../../../stores/transitionsStore.svelte";
  import { TRANSITION_TYPE_OPTIONS } from "../../../../constants/transition.constants";
  let { onAdd, filterState = transitionsStore } = $props<{ onAdd: () => void; filterState?: any }>();
  const fs = $derived(filterState ?? transitionsStore);
  const filterDefs = [{ key: "transitionType", label: "Type", icon: "arrow-left-right", mode: "multi" as const, options: TRANSITION_TYPE_OPTIONS.map(o=>({value:o.value,label:o.label})) }];
  const adaptedState = $derived({
    filters: { transitionType: fs.filters?.transitionType ?? [] }, activeFiltersCount: fs.activeFiltersCount,
    toggleFilter: (k:string,v:string)=>fs.setTransitionType ? (fs.filters.transitionType[0]===v ? fs.clearTransitionType() : fs.setTransitionType(v as any)) : fs.toggleFilter(k,v),
    resetFilters: ()=>fs.resetFilters()
  });
</script>
<ActionBar>
  <FilterMenu {filterDefs} filterState={adaptedState} />
  <div class="w-px h-5 bg-slate-200 mx-1"></div>
  <Button onclick={onAdd} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={15} /> Nouveau mouvement</Button>
</ActionBar>
