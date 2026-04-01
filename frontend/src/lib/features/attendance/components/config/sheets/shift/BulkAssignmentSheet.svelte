<script lang="ts">
  import { attendanceStore } from "../../../../stores/attendance.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as Select from "@/components/ui/select";
  import * as Sheet from "@/components/ui/sheet";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import { notification } from "@/stores/notification.svelte";
  import * as Checkbox from "@/components/ui/checkbox";
  import type { Employee } from "@/features/employees/types/types";
  
  let { 
    open = $bindable(false)
  } = $props<{
    open: boolean;
  }>();

  let selectedEmployees = $state<Employee[]>([]);

  let selectedBasePolicy = $state<string>("");
  let selectedOverridePolicy = $state<string>("");
  let assignmentStartDate = $state<string>(new Date().toISOString().split('T')[0]);
  let overrideStartDate = $state<string>(new Date().toISOString().split('T')[0]);
  let overrideEndDate = $state<string>("");

  // Réinitialiser les valeurs à l'ouverture
  $effect(() => {
    if (open) {
      selectedBasePolicy = "";
      selectedOverridePolicy = "";
      assignmentStartDate = new Date().toISOString().split('T')[0];
      overrideStartDate = new Date().toISOString().split('T')[0];
      overrideEndDate = "";
    }
  });

  function selectAllEmployees() {
    selectedEmployees = [...employeeStore.employees];
  }

  function clearSelection() {
    selectedEmployees = [];
  }

  function toggleEmployeeSelection(employee: Employee) {
    const employeeId = employee.id;
    const isSelected = selectedEmployees.some(emp => emp.id === employeeId);
    
    if (isSelected) {
      selectedEmployees = selectedEmployees.filter(emp => emp.id !== employeeId);
    } else {
      selectedEmployees = [...selectedEmployees, employee];
    }
  }

  function isEmployeeSelected(employee: Employee) {
    return selectedEmployees.some(emp => emp.id === employee.id);
  }

  function saveBulkAssignment() {
    if (selectedEmployees.length === 0 || !selectedBasePolicy) {
      notification.toast.error("Veuillez sélectionner au moins un employé et un modèle de base");
      return;
    }

    selectedEmployees.forEach((employee: Employee) => {
      attendanceStore.assignPolicy(employee.id, selectedBasePolicy, assignmentStartDate);
      
      if (selectedOverridePolicy) {
        attendanceStore.assignOverridePolicy(
          employee.id, 
          selectedOverridePolicy, 
          overrideStartDate, 
          overrideEndDate || undefined
        );
      }
    });

    const employeeNames = selectedEmployees.map(emp => emp.name).join(', ');
    notification.toast.success(`Le modèle${selectedOverridePolicy ? ' et le shift' : ''} ont été affectés à ${selectedEmployees.length} employé(s): ${employeeNames}`);
    open = false;
    selectedEmployees = [];
  }

  function closeSheet() {
    open = false;
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="font-bold text-[1rem]">Affecter en masse</Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 space-y-6 custom-scrollbar">
      <!-- Section de sélection des employés -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <Label class="text-[0.875rem] font-medium">Sélection des employés</Label>
          <div class="flex gap-2">
            <Button size="sm" variant="outline" onclick={selectAllEmployees} class="text-[0.85rem]">
              Tout sélectionner
            </Button>
            <Button size="sm" variant="outline" onclick={clearSelection} class="bg-red-50 text-red-600 border-red-100 hover:bg-red-100 hover:border-red-200 text-[0.85rem]">
              Effacer
            </Button>
          </div>
        </div>
        
        <div class="border border-slate-200 rounded-lg bg-white max-h-48 overflow-y-auto custom-scrollbar">
          {#each employeeStore.employees as emp}
            <div class="flex items-center space-x-3 p-3 hover:bg-slate-50 border-b border-slate-100 last:border-b-0 cursor-pointer" onclick={() => toggleEmployeeSelection(emp)} role="none">
              <Checkbox.Root 
                checked={isEmployeeSelected(emp)}
                onchange={() => toggleEmployeeSelection(emp)}
                class="h-4 w-4"
              />
              <div class="flex-1">
                <div class="font-medium text-[0.875rem]">{emp.name}</div>
                <div class="text-slate-500 text-[0.82rem]">{emp.department || 'Non spécifié'}</div>
              </div>
            </div>
          {/each}
        </div>
        
        {#if selectedEmployees.length > 0}
          <div class="text-sm text-slate-600 bg-blue-50 p-2 rounded">
            <span class="font-medium text-sm">{selectedEmployees.length}</span> employé(s) sélectionné(s)
          </div>
        {/if}
      </div>

      {#if selectedEmployees.length > 0}
        <div class="space-y-4">
        <div class="space-y-1.5">
          <Label for="bulkBasePolicy">Modèle de base</Label>
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
                  <div class="text-slate-500 text-[0.84rem]">{policy.description}</div>
                </Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>

        <div class="space-y-1.5">
          <Label for="bulkStartDate">Date de début</Label>
          <Input 
            id="bulkStartDate"
            type="date" 
            bind:value={assignmentStartDate}
            class="h-10 bg-white shadow-fine"
          />
        </div>

        <div class="space-y-1.5">
          <Label for="bulkOverridePolicy">Modèle de shift (optionnel)</Label>
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
                  <div class="text-slate-500 text-[0.84rem]">{policy.description}</div>
                </Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
          
          {#if selectedOverridePolicy}
            <div class="space-y-2 mt-3">
              <div class="grid grid-cols-2 gap-3">
                <div class="space-y-1">
                  <Label for="bulkOverrideStart">Date de début</Label>
                  <Input 
                    id="bulkOverrideStart"
                    type="date" 
                    bind:value={overrideStartDate}
                    class="h-9 bg-white border border-slate-200 rounded text-sm"
                  />
                </div>
                <div class="space-y-1">
                  <Label for="bulkOverrideEnd">Date de fin (optionnel)</Label>
                  <Input 
                    id="bulkOverrideEnd"
                    type="date" 
                    bind:value={overrideEndDate}
                    class="h-9 bg-white border border-slate-200 rounded text-sm"
                  />
                </div>
              </div>
              <p class="text-xs text-amber-600">
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
        onclick={saveBulkAssignment}
        class="flex-1 h-10 bg-primary text-white font-medium"
        disabled={selectedEmployees.length === 0 || !selectedBasePolicy}
      >
        <AppIcon name="check" size={18} />
        Affecter à {selectedEmployees.length} employé(s)
      </Button>
      <Sheet.Close onclick={closeSheet} class="flex-1">
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

