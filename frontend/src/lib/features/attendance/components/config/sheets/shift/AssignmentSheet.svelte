<script lang="ts">
  import { attendanceStore } from "../../../../stores/attendance.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import type { Employee } from "@/features/employees/types/types";
  import * as Select from "@/components/ui/select";
  import * as Sheet from "@/components/ui/sheet";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import { notification } from "@/stores/notification.svelte";
  
  let { 
    open = $bindable(false),
    employee = $bindable<Employee | null>(null)
  }: {
    open: boolean;
    employee: Employee | null;
  } = $props();

  let selectedEmployees = $state<Employee[]>([]);
  let selectedBasePolicy = $state<string>("");
  let selectedOverridePolicy = $state<string>("");
  let assignmentStartDate = $state<string>(new Date().toISOString().split('T')[0]);
  let overrideStartDate = $state<string>(new Date().toISOString().split('T')[0]);
  let overrideEndDate = $state<string>("");

  // Récupérer les affectations existantes
  $effect(() => {
    if (employee && open) {
      const baseAssignment = attendanceStore.policyAssignments.find(pa => pa.employeeId === employee.id && !pa.isOverride);
      const overrideAssignment = attendanceStore.policyAssignments.find(pa => pa.employeeId === employee.id && pa.isOverride);
      
      selectedBasePolicy = baseAssignment?.policyId || "";
      selectedOverridePolicy = overrideAssignment?.policyId || "";
      assignmentStartDate = baseAssignment?.startDate || new Date().toISOString().split('T')[0];
      overrideStartDate = overrideAssignment?.startDate || new Date().toISOString().split('T')[0];
      overrideEndDate = overrideAssignment?.endDate || "";
    }
  });

  function saveAssignment() {
    if (!employee) return;

    // Assign the base model
    if (selectedBasePolicy) {
      attendanceStore.assignPolicy(employee.id, selectedBasePolicy, assignmentStartDate);
    }

    // Assign the model for shift, if selected
    if (selectedOverridePolicy) {
      attendanceStore.assignOverridePolicy(
        employee.id, 
        selectedOverridePolicy, 
        overrideStartDate, 
        overrideEndDate || undefined
      );
    }

    notification.toast.success(`Le modèle${selectedOverridePolicy ? ' et le shift' : ''} ont été affectés à ${employee.name}`);

    open = false;
  }

  function closeSheet() {
    open = false;
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="font-bold text-[1rem]">Affecter un modèle</Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 space-y-6 custom-scrollbar">
      {#if employee}
        <div class="flex flex-col gap-y-4">
          <div class="text-sm text-slate-600 bg-blue-50 p-3 rounded">
            <span class="font-medium text-sm">Employé:</span> {employee.name}
          </div>
          <div class="space-y-1.5">
            <Label for="policyName">Modèle de base</Label>
            <Select.Root type="single" bind:value={selectedBasePolicy}>
              <Select.Trigger class="w-full h-10 bg-white border border-slate-200 rounded-lg cursor-pointer">
                <span class="text-[0.85rem]">
                  {selectedBasePolicy ? attendanceStore.policies.find(p => p.id === selectedBasePolicy)?.name : "Sélectionner un modèle de base"}
                </span>
              </Select.Trigger>
              <Select.Content class="max-h-60 z-100">
                {#each attendanceStore.policies as policy}
                  <Select.Item value={policy.id!} class="flex flex-col items-start">
                    <div class="font-medium text-[0.875rem]">{policy.name}</div>
                    <div class="text-slate-500 text-[0.82rem]">{policy.description}</div>
                  </Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
          </div>
          
          <div class="space-y-1.5">
            <Label for="startDate">Date de début</Label>
            <Input 
              id="startDate"
              type="date" 
              bind:value={assignmentStartDate}
              class="h-10 bg-white shadow-fine"
            />
          </div>
          
          <div class="space-y-1.5">
            <Label for="overridePolicy">Modèle de shift (optionnel)</Label>
            <Select.Root type="single" bind:value={selectedOverridePolicy}>
              <Select.Trigger class="w-full h-10 bg-white border border-slate-200 rounded-lg cursor-pointer">
                <span class="text-[0.85rem]">
                  {selectedOverridePolicy ? attendanceStore.policies.find(p => p.id === selectedOverridePolicy)?.name : "Sélectionner un modèle de shift"}
                </span>
              </Select.Trigger>
              <Select.Content class="max-h-60 z-100">
                {#each attendanceStore.policies.filter(p => p.id !== selectedBasePolicy) as policy}
                  <Select.Item value={policy.id!} class="flex flex-col items-start">
                    <div class="font-medium text-[0.875rem]">{policy.name}</div>
                    <div class="text-slate-500 text-[0.82rem]">{policy.description}</div>
                  </Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
            
            {#if selectedOverridePolicy}
              <div class="space-y-2 mt-3">
                <div class="grid grid-cols-2 gap-3">
                  <div class="space-y-1">
                    <Label for="overrideStart">Date de début</Label>
                    <Input 
                      id="overrideStart"
                      type="date" 
                      bind:value={overrideStartDate}
                      class="h-9 bg-white border border-slate-200 rounded text-sm"
                    />
                  </div>
                  <div class="space-y-1">
                    <Label for="overrideEnd">Date de fin (optionnel)</Label>
                    <Input 
                      id="overrideEnd"
                      type="date" 
                      bind:value={overrideEndDate}
                      class="h-9 bg-white border border-slate-200 rounded text-sm"
                    />
                  </div>
                </div>
                <p class="text-amber-600 text-[0.8rem]">
                  Ce modèle remplacera temporairement le modèle de base pour la période spécifiée.
                </p>
              </div>
            {/if}
          </div>
        </div>
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 bg-slate-50/50">
      <Button 
        onclick={() => saveAssignment()}
        class="flex-1 h-10 bg-primary text-white font-medium"
        disabled={!selectedBasePolicy}
      >
        <AppIcon name="check" size={18} />
        {selectedBasePolicy ? 'Enregistrer' : 'Assigner'}
      </Button>
      <Sheet.Close onclick={() => closeSheet()} class="flex-1">
        <Button variant="outline" class="w-full h-10">
          Annuler
        </Button>
      </Sheet.Close>
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
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
</style>

