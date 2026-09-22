<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import CurrencyToggle from "@/hr/components/ui/currency-toggle";
  import FilterMenu from "@/hr/actions/components/FilterMenu.svelte";
  import SortMenu from "@/hr/actions/components/SortMenu.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import { jobsStore } from "@/hr/modules/jobs/stores/jobs.svelte";
  import { positionsStore } from "@/hr/modules/jobs/stores/positionsStore.svelte.ts";
  import { payrollConfigStore } from "@/hr/modules/payroll/stores/configuration/payrollConfigStore.svelte";
  import { getOrgUnitIcon } from "@/hr/modules/jobs/constants/orgUnit.constants";

  let { onAdd, filterState = positionsStore } = $props<{ onAdd: () => void; filterState?: any }>();

  const filterDefs = $derived([
    { key: 'orgUnit', label: 'Unité', icon: 'building-2', mode: 'multi' as const, options: jobsStore.orgUnits.map((u:any)=>({value:u.id,label:u.name})) },
    { key: 'seniority', label: 'Séniorité', icon: 'layers', mode: 'multi' as const, options: jobsStore.seniorityLevels.map((l:any)=>({value:l.level,label:l.name})) },
  ]);
  const sortDefs = { options: [{value:'name',label:'Titre (A-Z)'},{value:'orgUnit',label:'Unité'},{value:'seniority',label:'Séniorité'}] };
</script>

<ActionBar>
  <SortMenu {sortDefs} {filterState} />
  <FilterMenu {filterDefs} {filterState} />
  <div class="w-px h-5 bg-slate-200 mx-1"></div>
  <CurrencyToggle currency={(payrollConfigStore.configuration?.currency ?? 'CDF')==='CDF'?'CDF':'USD'} onChange={(c)=>payrollConfigStore.saveConfiguration({currency:c})} size="sm" />
  <Button onclick={onAdd} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={15} />Nouveau poste</Button>
</ActionBar>
