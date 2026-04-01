<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { payrollStore } from "../../../stores/payroll.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { Textarea } from "@/components/ui/textarea";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";

  let { open = $bindable(false) }: { open: boolean } = $props();

  let selectedEmployee = $state(1);
  let requestAmount = $state('');
  let requestReason = $state('');

  const MOCK_EMPLOYEES = [
    { id: 1, name: 'Jean-Paul Mabuso', department: 'IT' },
    { id: 2, name: 'Merveille Kabamba', department: 'RH' },
    { id: 3, name: 'Christian Luvambo', department: 'Finance' },
    { id: 4, name: 'Grace Mbuyi', department: 'Commercial' },
    { id: 5, name: 'Patrick Kalala', department: 'Production' },
    { id: 6, name: 'Sophie Tshibola', department: 'Administration' }
  ];

  const selectedEmployeeData = $derived(MOCK_EMPLOYEES.find(e => e.id === selectedEmployee));

  function resetForm() {
    selectedEmployee = 1;
    requestAmount = '';
    requestReason = '';
  }

  function handleSubmit() {
    const amount = parseFloat(requestAmount);
    if (!amount || amount <= 0) {
      notification.toast.error('Veuillez entrer un montant valide');
      return;
    }
    if (!requestReason.trim()) {
      notification.toast.error('Veuillez indiquer le motif de la demande');
      return;
    }

    payrollStore.requestAdvance(selectedEmployee, amount, requestReason);
    notification.toast.success('Demande soumise avec succès');
    open = false;
    resetForm();
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md p-0 overflow-hidden flex flex-col bg-white h-full">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] font-bold text-slate-900 text-left">
        Nouvelle demande d'avance
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
      <!-- Employee Selection -->
      <div class="space-y-3">
        <Label for="employee" class="text-[0.875rem] font-medium text-slate-700">
          Employé <span class="text-rose-500">*</span>
        </Label>
        <Select.Root
          type="single"
          value={selectedEmployee.toString()}
          onValueChange={(v) => selectedEmployee = parseInt(v)}
        >
          <Select.Trigger id="employee" class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-[0.875rem]">
            {selectedEmployeeData?.name || "Sélectionner un employé..."}
          </Select.Trigger>
          <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
            {#each MOCK_EMPLOYEES as emp}
              <Select.Item value={emp.id.toString()} label={emp.name}>
                <div class="flex items-center gap-2">
                  <span class="text-[0.875rem]">{emp.name}</span>
                  <span class="text-xs text-slate-400">({emp.department})</span>
                </div>
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

      <!-- Amount -->
      <div class="space-y-3">
        <Label for="amount" class="text-[0.875rem] font-medium text-slate-700">
          Montant (USD) <span class="text-rose-500">*</span>
        </Label>
        <div class="relative">
          <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm">$</span>
          <Input
            id="amount"
            type="number"
            bind:value={requestAmount}
            placeholder="Ex: 500"
            class="h-10 border-slate-200 bg-white shadow-fine text-[0.875rem] pl-8"
          />
        </div>
      </div>

      <!-- Reason -->
      <div class="space-y-3">
        <Label class="text-[0.875rem] font-medium text-slate-700">
          Motif <span class="text-rose-500">*</span>
        </Label>
        <Textarea 
          bind:value={requestReason} 
          placeholder="Raison de la demande..." 
          class="min-h-32 shadow-fine text-[0.85rem]"
        />
      </div>
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-9.5 rounded-md text-sm font-medium shadow-fine cursor-pointer">
          Annuler
        </Button>
      </Sheet.Close>
      <Button
        onclick={handleSubmit}
        class="flex-1 h-9.5 rounded-md bg-primary text-white text-sm font-medium shadow-fine transition-all cursor-pointer"
      >
        <AppIcon name="check" size={18} />
        Soumettre
      </Button>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
</style>

