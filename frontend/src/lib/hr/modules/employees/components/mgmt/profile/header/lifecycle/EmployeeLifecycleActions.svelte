<script lang="ts">
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { buttonVariants } from "@/components/ui/button";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import ActionBar from "@/hr/actions/components/ActionBar.svelte";
  import { cn } from "@/hr/utilities/common/css";
  import EmployeeLifecycleSheet from "./EmployeeLifecycleSheet.svelte";
  import { useSuspendEmployeeMutation, useReactivateEmployeeMutation, useOffboardEmployeeMutation } from "../../../../../queries/employeeQueries";
  import { employeeStore } from "@/hr/modules/employees/stores/employees.svelte";
  import type { EmployeeFullProfile } from '@/hr/modules/employees/types/types';
  let { employee, filterState } = $props<{ employee: EmployeeFullProfile; filterState?:any }>();
  const status = $derived(employee.current_status?.status ?? (employee.is_active ? 'ACTIVE' : 'INACTIVE'));
  let isSheetOpen = $state(false); let currentAction = $state<'SUSPEND'|'REACTIVATE'|'OFFBOARD'|null>(null);
  function handleAction(a:'SUSPEND'|'REACTIVATE'|'OFFBOARD'){ currentAction=a; isSheetOpen=true; }
  const suspendMutation=useSuspendEmployeeMutation(), reactivateMutation=useReactivateEmployeeMutation(), offboardMutation=useOffboardEmployeeMutation();
  async function handleSave(action:'SUSPEND'|'REACTIVATE'|'OFFBOARD',data:any){
    const id=employee.id.toString();
    if(action==='SUSPEND') await $suspendMutation.mutateAsync({employeeId:id,data});
    else if(action==='REACTIVATE') await $reactivateMutation.mutateAsync({employeeId:id,data});
    else await $offboardMutation.mutateAsync({employeeId:id,data});
    await employeeStore.getFullProfileById(id); isSheetOpen=false;
  }
</script>

<ActionBar>
  <DropdownMenu.Root>
    <DropdownMenu.Trigger class={cn(buttonVariants({size:"sm"}),"text-[0.85rem] h-7.5 px-3 rounded-lg!")}><AppIcon name="more-vertical" size={16} />Actions</DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
      <DropdownMenu.Label class="uppercase tracking-wider text-muted-foreground text-[0.75rem]!">Cycle de vie</DropdownMenu.Label>
      <DropdownMenu.Separator class="my-1 bg-slate-50" />
      {#if ['ACTIVE','PROBATION','PENDING','MATERNITY_LEAVE','SICK_LEAVE','SABBATICAL'].includes(status)}<DropdownMenu.Item onclick={()=>handleAction('SUSPEND')} class="cursor-pointer text-[0.85rem]!"><AppIcon name="circle-pause" size={20} />Suspendre le contrat</DropdownMenu.Item>{/if}
      {#if status==='SUSPENDED'}<DropdownMenu.Item onclick={()=>handleAction('REACTIVATE')} class="cursor-pointer text-[0.85rem]!"><AppIcon name="play-circle" size={20} />Réactiver l'employé</DropdownMenu.Item>{/if}
      {#if status==='PENDING'}<DropdownMenu.Item onclick={()=>handleAction('REACTIVATE')} class="cursor-pointer text-[0.85rem]!"><AppIcon name="play-circle" size={20} />Activer l'employé</DropdownMenu.Item>{/if}
      {#if ['TERMINATED','RESIGNED','RETIRED'].includes(status??'')}<DropdownMenu.Item onclick={()=>handleAction('REACTIVATE')} class="cursor-pointer text-[0.85rem]!"><AppIcon name="play-circle" size={20} />Réintégrer l'employé</DropdownMenu.Item>{/if}
      <DropdownMenu.Separator />
      {#if !['TERMINATED','RESIGNED','RETIRED'].includes(status??'')}<DropdownMenu.Item onclick={()=>handleAction('OFFBOARD')} class="cursor-pointer text-red-600 hover:text-red-700! hover:bg-red-100! text-[0.85rem]!"><AppIcon name="user-minus" size={20} class="text-red-600" />Lancer l'offboarding</DropdownMenu.Item>{/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
</ActionBar>

{#if isSheetOpen}<EmployeeLifecycleSheet bind:open={isSheetOpen} action={currentAction} {employee} onSave={handleSave} />{/if}
