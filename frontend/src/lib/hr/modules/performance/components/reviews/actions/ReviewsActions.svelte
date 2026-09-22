<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import { reviewsStore } from "../../../stores/reviews.svelte.ts";
  import { REVIEW_STATUS_LABELS } from "../../../constants";
  import type { Campaign } from "../../../types/types";
  let { onCreate, campaigns=[], filterState=reviewsStore } = $props<{ onCreate:()=>void; campaigns?:Campaign[]; filterState?:any }>();
  const filterDefs = $derived([
    { key:'status', label:'Statut', icon:'flag', mode:'single' as const, options: Object.entries(REVIEW_STATUS_LABELS).map(([v,l])=>({value:v,label:l})) },
    { key:'campaign', label:'Campagne', icon:'layers', mode:'single' as const, options: campaigns.map(c=>({value:c.id,label:c.name})) },
  ]);
</script>

<ActionBar>
  <FilterMenu {filterDefs} {filterState} />
  <div class="w-px h-5 bg-slate-200 mx-1"></div>
  <Button onclick={onCreate} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={17} />Nouvelle évaluation</Button>
</ActionBar>
