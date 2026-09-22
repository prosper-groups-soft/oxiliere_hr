<script lang="ts">
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { buttonVariants } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import type { EmployeeFullProfile } from '@/hr/employees/types/types';
  import { cn } from "@/utilities/common/css";
  import EmployeeLifecycleSheet from "./EmployeeLifecycleSheet.svelte";
  import {
    useSuspendEmployeeMutation,
    useReactivateEmployeeMutation,
    useOffboardEmployeeMutation
  } from '../../../../queries/employeeQueries';
  import { employeeStore } from '@/hr/employees/stores/employees.svelte';

  
  let { employee } = $props<{ employee: EmployeeFullProfile }>();

  // Le statut est dans current_status (EmployeeFullProfile n'a pas de champ `status` direct)
  const status = $derived(employee.current_status?.status ?? (employee.is_active ? 'ACTIVE' : 'INACTIVE'));

  let isSheetOpen = $state(false);
  let currentAction = $state<'SUSPEND' | 'REACTIVATE' | 'OFFBOARD' | null>(null);

  function handleAction(action: 'SUSPEND' | 'REACTIVATE' | 'OFFBOARD') {
    currentAction = action;
    isSheetOpen = true;
  }

  const suspendMutation = useSuspendEmployeeMutation();
  const reactivateMutation = useReactivateEmployeeMutation();
  const offboardMutation = useOffboardEmployeeMutation();

  async function handleSave(action: 'SUSPEND' | 'REACTIVATE' | 'OFFBOARD', data: any) {
    try {
      const employeeId = employee.id.toString();

      if (action === 'SUSPEND') {
        await $suspendMutation.mutateAsync({ employeeId, data });
      } else if (action === 'REACTIVATE') {
        await $reactivateMutation.mutateAsync({ employeeId, data });
      } else if (action === 'OFFBOARD') {
        await $offboardMutation.mutateAsync({ employeeId, data });
      }

      // Rafraîchir le store global pour mettre à jour l'UI (header, statut, etc.)
      await employeeStore.getFullProfileById(employeeId);

      isSheetOpen = false;
    } catch (err) {
      console.error('Error executing lifecycle action', err);
    }
  }
</script>


<DropdownMenu.Root>
  <DropdownMenu.Trigger class={cn(buttonVariants({ size: "sm" }), "text-[0.85rem] h-7.5 px-3 rounded-lg!")}>
    <AppIcon name="more-vertical" size={16} />
    Actions
  </DropdownMenu.Trigger>
  <DropdownMenu.Content align="end" class="p-1 rounded-lg shadow-fine bg-white border-slate-100">
    <DropdownMenu.Label class="uppercase tracking-wider text-muted-foreground text-[0.75rem]!">
      Cycle de vie
    </DropdownMenu.Label>
    <DropdownMenu.Separator class="my-1 bg-slate-50" />
    <DropdownMenu.Group>
      <!-- Si l'employé est ACTIF, PROBATION, PENDING ou en congé spécial -->
      {#if status === 'ACTIVE' || status === 'PROBATION' || status === 'PENDING' || status === 'MATERNITY_LEAVE' || status === 'SICK_LEAVE' || status === 'SABBATICAL'}
        <DropdownMenu.Item onclick={() => handleAction('SUSPEND')} class="cursor-pointer text-[0.85rem]!">
          <AppIcon name="circle-pause" size={20} />
          Suspendre le contrat
        </DropdownMenu.Item>
      {/if}

      <!-- Si l'employé est SUSPENDU -->
      {#if status === 'SUSPENDED'}
        <DropdownMenu.Item onclick={() => handleAction('REACTIVATE')} class="cursor-pointer text-[0.85rem]!">
          <AppIcon name="play-circle" size={20} />
          Réactiver l'employé
        </DropdownMenu.Item>
      {/if}

      <!-- Si l'employé est PENDING, permettre de le passer à ACTIF -->
      {#if status === 'PENDING'}
        <DropdownMenu.Item onclick={() => handleAction('REACTIVATE')} class="cursor-pointer text-[0.85rem]!">
          <AppIcon name="play-circle" size={20} />
          Activer l'employé
        </DropdownMenu.Item>
      {/if}

      <!-- Si l'employé est parti, permettre la réintégration -->
      {#if ['TERMINATED', 'RESIGNED', 'RETIRED'].includes(status ?? '')}
        <DropdownMenu.Item onclick={() => handleAction('REACTIVATE')} class="cursor-pointer text-[0.85rem]!">
          <AppIcon name="play-circle" size={20} />
          Réintégrer l'employé
        </DropdownMenu.Item>
      {/if}

      <DropdownMenu.Separator />
      
      <!-- Cacher l'offboarding s'il est déjà parti -->
      {#if !['TERMINATED', 'RESIGNED', 'RETIRED'].includes(status ?? '')}
        <DropdownMenu.Item 
          onclick={() => handleAction('OFFBOARD')} 
          class="cursor-pointer text-red-600 hover:text-red-700! hover:bg-red-100! dark:focus:bg-red-950/20 text-[0.85rem]!"
        >
          <AppIcon name="user-minus" size={20} class="text-red-600 hover:text-red-700!" />
          Lancer l'offboarding
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Group>
  </DropdownMenu.Content>
</DropdownMenu.Root>


{#if isSheetOpen}
  <EmployeeLifecycleSheet
    bind:open={isSheetOpen}
    action={currentAction}
    {employee}
    onSave={handleSave}
  />
{/if}

