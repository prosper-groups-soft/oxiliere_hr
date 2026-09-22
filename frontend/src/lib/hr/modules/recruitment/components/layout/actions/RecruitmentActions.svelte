<script lang="ts">
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import SortMenu from "@/hr/actions/components/SortMenu.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import { recruitmentStore } from "@/hr/modules/recruitment/stores/recruitment.svelte";
  import { CAMPAIGN_STATUS_OPTIONS } from "@/hr/modules/recruitment/constants/recruitment";
  let { onAdd, filterState = recruitmentStore } = $props<{ onAdd: () => void; filterState?: any }>();
  const fs = $derived(filterState ?? recruitmentStore);
  const filterDefs = [{ key: "status", label: "Statut", icon: "user-check", mode: "multi" as const, options: CAMPAIGN_STATUS_OPTIONS }];
  const sortDefs = { options: [{ value: "title", label: "Titre" },{ value: "jobName", label: "Poste" },{ value: "type", label: "Type" },{ value: "status", label: "Statut" }] };
  const adaptedState = $derived({
    filters: { status: fs.campaignFilters?.status ?? fs.filters?.status ?? [] },
    activeFiltersCount: fs.activeFiltersCount, sortBy: fs.sortBy, sortOrder: fs.sortOrder,
    toggleFilter: (k:string,v:string)=>fs.toggleCampaignFilter?.(k,v) ?? fs.toggleFilter?.(k,v),
    resetFilters: ()=>fs.resetCampaignFilters?.() ?? fs.resetFilters?.(),
    setSort: (by:string,order:string)=>{ fs.sortBy=by; fs.sortOrder=order; if(fs.currentPage!==undefined) fs.currentPage=1; }
  });
</script>
<ActionBar>
  <SortMenu {sortDefs} filterState={adaptedState} />
  <FilterMenu {filterDefs} filterState={adaptedState} />
  <div class="w-px h-5 bg-slate-200 mx-1"></div>
  <Button onclick={onAdd} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={15} /> Nouvelle campagne</Button>
</ActionBar>
