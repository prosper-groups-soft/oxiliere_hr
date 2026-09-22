<script lang="ts">
  import FilterMenu from '@/hr/actions/components/FilterMenu.svelte';
  import SortMenu from '@/hr/actions/components/SortMenu.svelte';
  import ActionBar from '@/hr/actions/components/ActionBar.svelte';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { orgService } from '@/hr/modules/jobs/services/org.service';
  import { payrollRunStore } from '@/hr/modules/payroll/stores/runs/payrollRunStore.svelte';
  import PayslipExportDialog from './PayslipExportDialog.svelte';
  import type { FilterDef } from '@/hr/actions/types';

  let { filterState }: { filterState: any } = $props();

  let orgUnits = $state<string[]>([]);
  $effect(() => { let c=false; orgService.listOrgUnits(1,200).then(r=>{ if(!c) orgUnits=(r.results||[]).map((u:any)=>u.name).sort((a:string,b:string)=>a.localeCompare(b)); }).catch(()=>{}); return ()=>{c=true;}; });
  let exportOpen = $state(false);
  let runOptions = $derived(payrollRunStore.runList.map(r=>({id:r.id,label:r.periodLabel})));

  const filterDefs: FilterDef[] = $derived([
    { key:'orgUnit', label:'Unité', icon:'building-2', mode:'single', options: orgUnits.map(u=>({value:u,label:u})) },
    { key:'runId', label:'Exécution', icon:'layers', mode:'single', options: runOptions.map(r=>({value:r.id,label:r.label})) },
  ]);
  const sortDefs = { options: [{value:'employeeName',label:'Employé'},{value:'gross',label:'Brut'},{value:'net',label:'Net'},{value:'period',label:'Période'},{value:'createdAt',label:'Date'}] };
</script>

<ActionBar>
  <SortMenu {sortDefs} {filterState} />
  <FilterMenu {filterDefs} {filterState} />
  <Button variant="outline" size="sm" class="h-7 px-3 text-[0.84rem]" onclick={()=> exportOpen=true}><AppIcon name="download" size={15} class="mr-1.5" />Exporter ZIP</Button>
</ActionBar>
<PayslipExportDialog bind:open={exportOpen} />
