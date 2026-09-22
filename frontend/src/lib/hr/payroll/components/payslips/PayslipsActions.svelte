<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import * as DropdownMenu from '@/components/ui/dropdown-menu';
  import { payslipsStore } from '@/hr/payroll/stores/payslips/payslipsStore.svelte';
  import { payrollRunStore } from '@/hr/payroll/stores/runs/payrollRunStore.svelte';
  import { orgService } from '@/hr/jobs/services/org.service';
  import PayslipExportDialog from './PayslipExportDialog.svelte';

  let orgUnits = $state<string[]>([]);
  let isLoadingOrgUnits = $state(true);
  $effect(() => {
    let c = false;
    orgService.listOrgUnits(1,200).then(r=>{ if(!c) orgUnits = (r.results||[]).map((u:any)=>u.name).sort((a:string,b:string)=>a.localeCompare(b)); }).catch(()=>{}).finally(()=>{ if(!c) isLoadingOrgUnits=false; });
    return ()=>{c=true;};
  });

  let exportOpen = $state(false);

  // runs for filtre par exécution
  let runOptions = $derived(payrollRunStore.runList.map(r=>({ id:r.id, label:r.periodLabel })));
</script>


<div class="flex items-center gap-2">
  <DropdownMenu.Root>
    <DropdownMenu.Trigger><Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"><AppIcon name="arrow-down-up" size={15} class="mr-1.5" />Tri</Button></DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="w-44 p-1 z-100">
      <DropdownMenu.Label class="text-[0.82rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">Trier par</DropdownMenu.Label>
      {#each [['employeeName','Employé'],['gross','Brut'],['net','Net'],['period','Période'],['createdAt','Date']] as [k,label]}
        <DropdownMenu.Item onclick={()=>payslipsStore.setOrdering(payslipsStore.ordering===k ? `-${k}` : k as string)} class={["text-[0.86rem] py-1.5 cursor-pointer", payslipsStore.ordering.replace('-','')===k && "bg-slate-50 font-medium"]}>{label} {#if payslipsStore.ordering.replace('-','')===k}<AppIcon name={payslipsStore.ordering.startsWith('-')?'arrow-down':'arrow-up'} size={14} class="ml-auto" />{/if}</DropdownMenu.Item>
      {/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <DropdownMenu.Root>
    <DropdownMenu.Trigger><Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"><AppIcon name="building-2" size={15} class="mr-1.5" />Unité {#if payslipsStore.orgUnit}<span class="ml-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[0.82rem] font-medium text-white">1</span>{/if}</Button></DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.82rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">Unité</DropdownMenu.Label>
      {#if isLoadingOrgUnits}<div class="px-2 py-1.5 text-[0.82rem] text-slate-400">Chargement…</div>{:else if orgUnits.length===0}<div class="px-2 py-1.5 text-[0.82rem] text-slate-400">Aucune unité</div>{:else}
        {#each orgUnits as u}<DropdownMenu.Item onclick={()=>payslipsStore.setOrgUnit(payslipsStore.orgUnit===u?'':u)} class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", payslipsStore.orgUnit===u && "bg-slate-50 font-medium"]}><span>{u}</span> {#if payslipsStore.orgUnit===u}<AppIcon name="check" size={14} />{/if}</DropdownMenu.Item>{/each}
      {/if}
      {#if payslipsStore.orgUnit}<DropdownMenu.Separator /><DropdownMenu.Item onclick={()=>payslipsStore.setOrgUnit('')} class="text-[0.86rem] text-red-600 cursor-pointer"><AppIcon name="x" size={14} />Réinitialiser</DropdownMenu.Item>{/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <DropdownMenu.Root>
    <DropdownMenu.Trigger><Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"><AppIcon name="layers" size={15} class="mr-1.5" />Exécution {#if payslipsStore.runId}<span class="ml-1.5 flex h-5 w-5 items-center justify-center rounded-full bg-primary text-[0.82rem] font-medium text-white">1</span>{/if}</Button></DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.82rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">Filtrer par exécution</DropdownMenu.Label>
      <DropdownMenu.Item onclick={()=>payslipsStore.setRunId('')} class={["text-[0.86rem] py-1.5 cursor-pointer", !payslipsStore.runId && "bg-slate-50 font-medium"]}>Toutes les exécutions</DropdownMenu.Item>
      {#each runOptions as r}<DropdownMenu.Item onclick={()=>payslipsStore.setRunId(r.id)} class={["text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between", payslipsStore.runId===r.id && "bg-slate-50 font-medium"]}><span>{r.label}</span> {#if payslipsStore.runId===r.id}<AppIcon name="check" size={14} />{/if}</DropdownMenu.Item>{/each}
    </DropdownMenu.Content>
  </DropdownMenu.Root>

  <Button variant="outline" size="sm" class="h-7 px-3 text-[0.84rem]" onclick={()=> exportOpen = true}><AppIcon name="download" size={15} class="mr-1.5" />Exporter ZIP</Button>
</div>

<PayslipExportDialog bind:open={exportOpen} />

