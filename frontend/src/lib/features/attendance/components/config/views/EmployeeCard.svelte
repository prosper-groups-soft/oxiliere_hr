<script lang="ts">
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import type { 
    WorkPolicy, 
    PolicyAssignment 
  } from "../../../types/types";
  import type { Employee } from "@/features/employees/types/types";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { notification } from "@/stores/notification.svelte";
  import { formatDate } from "date-fns";

  interface EmployeeWithAssignment extends Employee {
    baseAssignment?: PolicyAssignment;
    overrideAssignment?: PolicyAssignment;
    basePolicy?: WorkPolicy;
    overridePolicy?: WorkPolicy;
  }

  let { 
    employee,
    onRemove,
    onEdit,
    onViewDetail
  } = $props<{
    employee: EmployeeWithAssignment;
    onRemove?: (employee: EmployeeWithAssignment) => void;
    onEdit?: (employee: EmployeeWithAssignment) => void;
    onViewDetail?: (employee: EmployeeWithAssignment) => void;
  }>();

  function removeAssignment(employee: EmployeeWithAssignment) {
    if (!employee.baseAssignment && !employee.overrideAssignment) return;

    notification.confirm({
      title: "Suppression de l'affectation",
      message: `Êtes-vous sûr de vouloir supprimer l'affectation du modèle pour ${employee.name} ?`,
      onYes: () => {
        // Remove both base and override if they exist
        [employee.baseAssignment, employee.overrideAssignment].forEach(assignment => {
            if (assignment) {
                const index = attendanceStore.policyAssignments.findIndex(pa => pa.id === assignment.id);
                if (index !== -1) {
                    attendanceStore.policyAssignments.splice(index, 1);
                }
            }
        });
        attendanceStore.policyAssignments = [...attendanceStore.policyAssignments];
      }
    });
  }

</script>


<div class="flex flex-col rounded-xl border border-slate-200 bg-white overflow-hidden transition-all hover:border-slate-300 shadow-fine h-[300px]">
  <div class="px-5 py-3.5 bg-slate-50/50 border-b border-slate-100 shrink-0">
      <div class="flex items-start justify-between gap-4">
        <div class="flex items-center gap-3 flex-1 min-w-0">
          <div class="flex flex-col min-w-0">
            <span class="text-[0.95rem] font-bold text-slate-900 leading-tight truncate">{employee.name}</span>
            <span class="mt-0.5 text-[0.85rem] text-slate-500 line-clamp-1">{employee.department}</span>
            <span class="mt-0.5 text-[0.8rem] text-slate-400">{employee.email}</span>
          </div>
        </div>
        {@render EmployeeMenu({employee})}
      </div>
  </div>

  <div class="p-4 flex flex-col gap-3 flex-1 justify-center bg-white">
    {#if employee.basePolicy}
      <div class="flex items-center justify-between p-2.5 rounded-lg bg-blue-50 border border-blue-100 shrink-0">
        <div class="flex items-center gap-2">
          <AppIcon name="briefcase" size={16} class="text-blue-600" />
          <div>
            <div class="text-[0.85rem] font-medium text-blue-900 leading-tight">{employee.basePolicy.name}</div>
            <div class="text-xs text-blue-600">Modèle de base</div>
          </div>
        </div>
        <div class="text-[0.7rem] text-blue-500 font-medium whitespace-nowrap">
          {employee.baseAssignment?.startDate ? formatDate(new Date(employee.baseAssignment.startDate), 'dd/MM/yyyy') : '...'}
        </div>
      </div>
    {:else}
      <div class="flex items-center justify-center p-3 rounded-lg border border-dashed border-slate-200 bg-slate-50 shrink-0">
        <div class="text-center">
          <AppIcon name="briefcase" size={18} strokeWidth={1} class="text-primary mx-auto mb-1" />
          <p class="text-slate-500 text-[0.75rem]">Aucun modèle</p>
        </div>
      </div>
    {/if}

    {#if employee.overridePolicy}
      <div class="flex items-center justify-between p-2.5 rounded-lg bg-amber-50 border border-amber-100 shrink-0">
        <div class="flex items-center gap-2">
          <AppIcon name="zap" size={15} class="text-amber-600" />
          <div>
            <div class="text-[0.85rem] font-medium text-amber-900 leading-tight">{employee.overridePolicy.name}</div>
            <div class="text-xs text-amber-600">Shift temporaire</div>
          </div>
        </div>
        <div class="text-[0.7rem] text-amber-600 font-medium whitespace-nowrap">
          {#if employee.overrideAssignment?.endDate}
            Jusqu'au {formatDate(new Date(employee.overrideAssignment.endDate), 'dd/MM/yyyy')}
          {:else}
            Indéfini
          {/if}
        </div>
      </div>
    {/if}
  </div>
</div>


{#snippet EmployeeMenu({employee}: {employee: EmployeeWithAssignment})}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger asChild>
      <Button variant="ghost" size="icon" class="h-8 w-8">
        <AppIcon name="more-horizontal" size={16} />
      </Button>
    </DropdownMenu.Trigger>
    <DropdownMenu.Content align="end" sideOffset={5} class="min-w-44 p-1 rounded-lg border border-slate-200 bg-white shadow-md z-50">
      <DropdownMenu.Item onclick={() => onViewDetail?.(employee)} class="flex items-center gap-2.5 px-3 py-2 rounded-md text-[0.875rem] text-slate-700 hover:bg-slate-50 cursor-pointer outline-none transition-colors">
        <AppIcon name="eye" size={16} class="text-slate-400" /> 
        Consulter
      </DropdownMenu.Item>

      <DropdownMenu.Item onclick={() => onEdit?.(employee)} class="flex items-center gap-2.5 px-3 py-2 rounded-md text-[0.875rem] text-slate-700 hover:bg-slate-50 cursor-pointer outline-none transition-colors">
        <AppIcon name="edit-3" size={16} class="text-slate-400" /> 
        Modifier
      </DropdownMenu.Item>
      <DropdownMenu.Item onclick={() => removeAssignment(employee)} class="text-red-600 hover:bg-red-50! hover:text-red-600! cursor-pointer">
        <AppIcon name="trash" size={16} class="text-red-600" />
        Supprimer
      </DropdownMenu.Item>
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

