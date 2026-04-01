<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Badge } from "@/components/ui/badge";
  import { Label } from "@/components/ui/label";
  import {
    Select,
    SelectContent,
    SelectItem,
    SelectTrigger
  } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Department } from "../../../types/types";

  let {
    open = $bindable(false),
    department
  } = $props<{
    open: boolean,
    department: Department | null
  }>();

  // --- Form state ---
  let isAdding = $state(false);
  let selectedEmployeeId = $state<string | null>(null);

  // Reset state when sheet opens/closes or department changes
  $effect(() => {
    if (open || department) {
      isAdding = false;
      selectedEmployeeId = null;
    }
  });

  // Employee not assigned to the current department
  const unassignedEmployees = $derived(
    department 
      ? employeeStore.employees.filter(e => 
          e.department !== department.name && 
          e.departmentId !== department.id
        )
      : []
  );

  // Employee already assigned to the department
  const assignedEmployees = $derived(
    department
      ? employeeStore.employees.filter(e => 
          e.department === department.name || 
          e.departmentId === department.id
        )
      : []
  );

  function handleAssign() {
    if (!selectedEmployeeId || !department) return;

    const empIdNum = Number(selectedEmployeeId);
    const employee = employeeStore.getById(empIdNum);
    if (!employee) return;

    // Update the employee with the new department
    employeeStore.updateEmployee(empIdNum, {
      departmentId: department.id,
      department: department.name
    });

    notification.toast.success(`${employee.name} a été affecté(e) à ${department.name}`);

    selectedEmployeeId = null;
    isAdding = false;
  }

  function handleUnassign(employeeId: number) {
    if (!department) return;

    const employee = employeeStore.getById(employeeId);
    if (!employee) return;

    notification.confirm({
      title: 'Détacher l\'employé',
      message: `Êtes-vous sûr(e) ? ${employee.name} sera détaché(e) du département.`,
      type: 'info',
      onYes: () => {
        employeeStore.updateEmployee(employeeId, {
          departmentId: undefined,
          department: ''
        });
        notification.toast.success(`${employee.name} a été détaché(e)`);
      }
    });
  }
  // --- Helpers for Select ---
  const selectEmployeeId = $derived(selectedEmployeeId ?? '');
  const employeeLabel = $derived(
    selectedEmployeeId
      ? employeeStore.getById(Number(selectedEmployeeId))?.name ?? '— Sélectionner un employé'
      : '— Sélectionner un employé'
  );

  function handleEmployeeChange(value: string) {
    selectedEmployeeId = value || null;
  }
</script>


{#snippet formHeader(title: string)}
  <header class="flex flex-col gap-9 mb-6">
     <Button variant="default" onclick={() => isAdding = false} class="h-7.5 text-[0.84rem] rounded-lg transition-colors self-start">
       <AppIcon name="arrow-left" size={19} />
       Retour
     </Button>
     <h3 class="font-bold text-slate-800 text-[0.95rem]">{title}</h3>
  </header>
{/snippet}


{#snippet employeeRow(emp: any)}
  <div class="group relative flex items-center justify-between p-4 hover:bg-slate-50 transition-colors border-b border-slate-100 last:border-0">
    <div class="flex items-center gap-3 min-w-0">
      <div class="w-9 h-9 rounded-full bg-slate-100 border border-slate-200 flex items-center justify-center shrink-0 overflow-hidden">
        {#if emp.avatarUrl}
          <img src={emp.avatarUrl} alt={emp.name} class="w-full h-full object-cover" />
        {:else}
          <AppIcon name="user" size={16} class="text-slate-500" />
        {/if}
      </div>
      <div class="min-w-0">
        <span class="text-[0.86rem] font-bold text-slate-900 block truncate">{emp.name}</span>
        <span class="text-[0.79rem] text-slate-500 block truncate">{emp.jobTitle}</span>
      </div>
    </div>

    <Button 
      variant="ghost"
      onclick={() => handleUnassign(emp.id)}
      class="p-1! h-8 w-8 hover:bg-red-50 hover:shadow-fine rounded border-none text-slate-400 hover:text-red-600 transition-all opacity-0 group-hover:opacity-100"
      title="Détacher"
    >
      <AppIcon name="x" size={18} />
    </Button>
  </div>
{/snippet}


{#snippet assignedListView()}
  <div class="px-6 mb-3 flex items-center justify-between">
    <Button onclick={() => isAdding = true} size="sm" class="bg-primary text-white text-[0.84rem] h-7.5">
      <AppIcon name="plus" size={19} />Nouveau
    </Button>
    <Badge variant="secondary" class="bg-indigo-50 text-indigo-700 font-bold text-[0.7rem] px-2 py-0.5 border border-indigo-100">
      {assignedEmployees.length} Collaborateur{assignedEmployees.length > 1 ? 's' : ''}
    </Badge>
  </div>

  <div class="divide-y divide-slate-100 border-none">
    {#each assignedEmployees as emp}
      {@render employeeRow(emp)}
    {:else}
      <div class="py-12 flex items-center justify-center">
        <Empty 
          title="Aucun collaborateur" 
          description="Aucun employé n'est actuellement affecté à cette unité." 
          icon="users"
          iconSize={24}
          iconStrokeWidth={1.5}
          titleSize="0.9rem"
          iconClass="text-primary"
        />
      </div>
    {/each}
  </div>
{/snippet}


{#snippet assignFormView()}
  <div class="p-6 pt-0 animate-in fade-in slide-in-from-right-4 duration-300">
    {@render formHeader('Affecter un employé')}

    <div class="space-y-6">
      <div class="space-y-2">
        <Label>Employé</Label>
        <Select type="single" value={selectEmployeeId} onValueChange={handleEmployeeChange}>
          <SelectTrigger class="h-10 w-full shadow-fine bg-white border-slate-200 cursor-pointer">
            <span class="truncate text-sm">{employeeLabel}</span>
          </SelectTrigger>
          <SelectContent class="z-9999 max-h-[300px]">
            {#each unassignedEmployees as emp}
              <SelectItem value={String(emp.id)}>
                <div class="flex flex-col">
                  <span class="font-medium text-[0.83rem]">{emp.name}</span>
                  <span class="text-[0.77rem] text-slate-500">{emp.jobTitle}</span>
                </div>
              </SelectItem>
            {:else}
              <div class="p-4 text-center text-sm text-slate-500">
                Tous les employés sont déjà affectés.
              </div>
            {/each}
          </SelectContent>
        </Select>
      </div>

      <div class="bg-slate-50 border border-slate-200 rounded-lg p-4 flex gap-3">
        <div class="h-8 w-8 rounded-full bg-white border border-slate-200 flex items-center justify-center shrink-0">
          <AppIcon name="info" size={16} class="text-primary" />
        </div>
        <div>
          <h4 class="text-[0.8rem] font-bold text-slate-900">Note sur l'affectation</h4>
          <p class="text-[0.75rem] text-slate-600 leading-relaxed mt-0.5">
            L'employé sera rattaché à <span class="font-bold text-primary text-[0.75rem]">{department?.name}</span>. 
            Ses informations de département seront mises à jour immédiatement.
          </p>
        </div>
      </div>
    </div>
  </div>
{/snippet}


{#snippet footerActions()}
  {#if isAdding}
    <Button 
      onclick={handleAssign}
      disabled={!selectedEmployeeId}
      class="flex-1 bg-primary text-white shadow-fine transition-transform h-9"
    >
      <AppIcon name="check" size={16} />
      Affecter
    </Button>
    <Button variant="outline" onclick={() => isAdding = false} class="flex-1 h-9 shadow-fine">
      Annuler
    </Button>
  {:else}
    <Sheet.Close class="w-full">
      <Button variant="outline" class="w-full h-9 text-slate-900 border-slate-200 shadow-fine">
        Fermer
      </Button>
    </Sheet.Close>
  {/if}
{/snippet}


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0 bg-white shadow-2xl">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <div class="flex flex-col items-start justify-start">
        <Sheet.Title class="text-[1rem] font-bold text-slate-900">
          Gérer les affectations
        </Sheet.Title>
        <Badge variant="outline" class="bg-white text-slate-600 border-slate-200 font-medium lowercase">
          {department?.name}
        </Badge>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar h-full py-6">
      {#if isAdding}
        {@render assignFormView()}
      {:else}
        {@render assignedListView()}
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      {@render footerActions()}
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 4px;
  }
  
  .custom-scrollbar::-webkit-scrollbar-thumb { 
    background: #e2e8f0; 
    border-radius: 10px; 
  }
</style>

