<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import { campaignStore } from "../../../stores/campaigns.svelte.ts";
  import { CAMPAIGN_STATUS_LABELS, CAMPAIGN_TYPE_LABELS } from "../../../constants";
  let { onCreate, filterState = campaignStore } = $props<{ onCreate:()=>void; filterState?:any }>();
  const filterDefs = $derived([
    { key:'status', label:'Statut', icon:'flag', mode:'single' as const, options:[{value:'DRAFT',label:CAMPAIGN_STATUS_LABELS.DRAFT},{value:'ACTIVE',label:CAMPAIGN_STATUS_LABELS.ACTIVE},{value:'CLOSED',label:CAMPAIGN_STATUS_LABELS.CLOSED}] },
    { key:'type', label:'Type', icon:'folder-tree', mode:'single' as const, options:[{value:'ANNUAL',label:CAMPAIGN_TYPE_LABELS.ANNUAL},{value:'SEMESTRIAL',label:CAMPAIGN_TYPE_LABELS.SEMESTRIAL},{value:'TRIMESTRIAL',label:CAMPAIGN_TYPE_LABELS.TRIMESTRIAL},{value:'PROBATION',label:CAMPAIGN_TYPE_LABELS.PROBATION}] },
  ]);
</script>

<ActionBar>
  <FilterMenu {filterDefs} {filterState} />
  <div class="w-px h-5 bg-slate-200 mx-1"></div>
  <Button onclick={onCreate} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={16} />Nouvelle campagne</Button>
</ActionBar>
