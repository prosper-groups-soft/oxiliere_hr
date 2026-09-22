<script lang="ts">
  import FilterMenu from '@/hr/actions/components/FilterMenu.svelte';
  import SortMenu from '@/hr/actions/components/SortMenu.svelte';
  import ActionBar from '@/hr/actions/components/ActionBar.svelte';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { RUN_LIST_STATUS_LABELS } from '@/hr/modules/payroll/types/types';
  import { orgService } from '@/hr/modules/jobs/services/org.service';
  import { goToActiveOrNewPayroll } from '@/hr/modules/payroll/utils/goToActiveOrNewPayroll';
  import type { FilterDef } from '@/hr/actions/types';

  let { filterState }: { filterState: any } = $props();

  let orgUnits = $state<string[]>([]);
  $effect(() => { let c=false; orgService.listOrgUnits(1,200).then(r=>{ if(!c) orgUnits=(r.results||[]).map((u:any)=>u.name).sort((a:string,b:string)=>a.localeCompare(b)); }).catch(()=>{}); return ()=>{c=true;}; });

  const filterDefs: FilterDef[] = $derived([
    { key:'status', label:'Statut', icon:'circle', mode:'single', options: Object.entries(RUN_LIST_STATUS_LABELS).map(([value,label])=>({value,label})) },
    { key:'period', label:'Période', icon:'calendar', mode:'date', options: [] },
    { key:'orgUnit', label:'Unité', icon:'building-2', mode:'single', options: orgUnits.map(u=>({value:u,label:u})) },
  ]);

  const sortDefs = { options: [{value:'period',label:'Période'},{value:'status',label:'Statut'},{value:'employeeCount',label:'Employés'},{value:'grossTotal',label:'Masse salariale'}] };
</script>

<ActionBar>
  <SortMenu {sortDefs} {filterState} />
  <FilterMenu {filterDefs} {filterState} />
  <Button onclick={()=>goToActiveOrNewPayroll()} variant="default" size="sm" class="h-7 px-3 text-[0.84rem] text-white shadow-fine rounded-lg"><AppIcon name="plus" size={15} /> Nouvelle paie</Button>
</ActionBar>
