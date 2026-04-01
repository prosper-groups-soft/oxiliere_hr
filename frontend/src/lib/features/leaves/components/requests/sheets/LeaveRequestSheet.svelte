<script lang="ts">
  import { leavesStore } from '../../../stores/leaves.svelte';
  import { LEAVE_TYPE_LABELS, LEAVE_TYPE_COLORS } from '../../../types/types';
  import type { LeaveType } from '../../../types/types';
  import { Button } from '@/components/ui/button';
  import * as Sheet from '@/components/ui/sheet';
  import * as Select from '@/components/ui/select';
  import { Label } from '@/components/ui/label';
  import { Input } from '@/components/ui/input';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { cn } from '@/utilities/common/css';
  import { employeeStore } from '@/features/employees/stores/employees.svelte';

  interface Props {
    open: boolean;
  }

  let { open = $bindable(false) }: Props = $props();

  // Form state
  let selectedType = $state<string>('annual');
  let startDate = $state('');
  let endDate = $state('');
  let reason = $state('');
  let selectedEmployeeStr = $state(employeeStore.employees[0]?.id.toString() || '1');

  const selectedEmployeeId = $derived(parseInt(selectedEmployeeStr));

  // Calculate days between dates
  const calculatedDays = $derived.by(() => {
    if (!startDate || !endDate) return 0;
    
    const start = new Date(startDate);
    const end = new Date(endDate);
    const diffTime = Math.abs(end.getTime() - start.getTime());
    const diffDays = Math.ceil(diffTime / (1000 * 60 * 60 * 24)) + 1;
    
    return diffDays;
  });

  // Check if form is valid
  const isFormValid = $derived.by(() => {
    return selectedType && startDate && endDate && reason && calculatedDays > 0;
  });

  // Get employee balance for selected type
  const currentBalance = $derived.by(() => {
    const balance = leavesStore.getBalancesForEmployee(selectedEmployeeId)
      .find(b => b.type === selectedType);
    return balance || { allocated: 0, taken: 0, remaining: 0 };
  });

  function handleSubmit() {
    if (!isFormValid) return;

    const employee = employeeStore.employees.find(e => e.id === selectedEmployeeId);
    if (!employee) return;

    leavesStore.addRequest({
      employeeId: selectedEmployeeId,
      employeeName: employee.name,
      department: employee.department,
      type: selectedType as LeaveType,
      startDate,
      endDate,
      days: calculatedDays,
      reason,
    });

    // Reset form and close
    resetForm();
    open = false;
  }

  function resetForm() {
    selectedType = 'annual';
    startDate = '';
    endDate = '';
    reason = '';
    selectedEmployeeStr = employeeStore.employees[0]?.id.toString() || '1';
  }

  // Set default dates to today
  $effect(() => {
    if (open && !startDate) {
      const today = new Date().toISOString().split('T')[0];
      startDate = today;
      endDate = today;
    }
  });

  const selectedEmployeeObj = $derived(employeeStore.employees.find(e => e.id === selectedEmployeeId));
  const selectedTypeObj = $derived(selectedType as LeaveType);
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="font-bold text-[1rem] flex items-center gap-2">
        Nouvelle demande de congé
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 space-y-6 custom-scrollbar">
      <p class="text-[0.85rem] text-slate-500 mb-2">Remplissez les informations ci-dessous pour créer une demande de congé.</p>

      <!-- Employee Selection -->
      <div class="space-y-1.5">
        <Label>Employé</Label>
        <Select.Root type="single" bind:value={selectedEmployeeStr}>
          <Select.Trigger class="w-full h-10 bg-white border border-slate-200 rounded-lg cursor-pointer">
            <span class="text-[0.85rem]">
              {selectedEmployeeObj?.name || 'Sélectionner un employé'}
            </span>
          </Select.Trigger>
          <Select.Content class="max-h-60 z-100">
            {#each employeeStore.employees as employee}
              <Select.Item value={employee.id.toString()} class="py-2.5 cursor-pointer">
                <div class="flex items-center gap-3">
                  <div class="w-6 h-6 rounded-full bg-slate-100 flex items-center justify-center">
                    <span class="text-[0.6rem] font-medium text-slate-600">
                      {employee.name.split(' ').map((n: string) => n[0]).join('').toUpperCase()}
                    </span>
                  </div>
                  <div class="flex flex-col">
                    <span class="text-[0.8rem] font-medium">{employee.name}</span>
                    <span class="text-[0.7rem] text-slate-500">{employee.department}</span>
                  </div>
                </div>
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

      <!-- Leave Type -->
      <div class="space-y-1.5">
        <Label>Type de congé</Label>
        <Select.Root type="single" bind:value={selectedType}>
          <Select.Trigger class="w-full h-10 bg-white border border-slate-200 rounded-lg cursor-pointer">
            <div class="flex items-center gap-2 text-[0.85rem]">
              <div class={cn("w-2 h-2 rounded-full", LEAVE_TYPE_COLORS[selectedTypeObj].dot)}></div>
              <span class="text-[0.85rem]">{LEAVE_TYPE_LABELS[selectedTypeObj]}</span>
            </div>
          </Select.Trigger>
          <Select.Content class="z-100">
            {#each Object.entries(LEAVE_TYPE_LABELS) as [value, label]}
              <Select.Item {value} class="py-2.5 cursor-pointer">
                <div class="flex items-center gap-2 text-[0.85rem]">
                  <div class={cn("w-2 h-2 rounded-full", LEAVE_TYPE_COLORS[value as LeaveType].dot)}></div>
                  <span class="text-[0.85rem]">{label}</span>
                </div>
              </Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

      <!-- Date Range -->
      <div class="grid grid-cols-2 gap-4">
        <div class="space-y-1.5">
          <Label for="startDate">Date de début</Label>
          <Input 
            id="startDate"
            type="date" 
            bind:value={startDate}
            min={new Date().toISOString().split('T')[0]}
            class="h-10 bg-white shadow-fine"
          />
        </div>
        <div class="space-y-1.5">
          <Label for="endDate">Date de fin</Label>
          <Input 
            id="endDate"
            type="date" 
            bind:value={endDate}
            min={startDate}
            class="h-10 bg-white shadow-fine"
          />
        </div>
      </div>

      <!-- Days Calculation -->
      {#if calculatedDays > 0}
        <div class="p-3 bg-blue-50 rounded-lg border border-blue-100">
          <div class="flex items-center justify-between">
            <span class="text-[0.85rem] font-medium text-blue-900">Durée totale</span>
            <span class="text-[1rem] font-bold text-blue-600">{calculatedDays} jour{calculatedDays > 1 ? 's' : ''}</span>
          </div>
          <div class="mt-1 text-[0.75rem] text-blue-700">
            Solde disponible : {currentBalance.remaining} / {currentBalance.allocated} jours
          </div>
        </div>
      {/if}

      <!-- Reason -->
      <div class="space-y-1.5">
        <Label for="reason">Motif</Label>
        <textarea 
          id="reason"
          bind:value={reason}
          placeholder="Précisez le motif de votre demande..."
          rows="4"
          class="flex w-full rounded-md border border-input bg-background px-3 py-2 text-[0.85rem] ring-offset-background placeholder:text-muted-foreground focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 disabled:cursor-not-allowed disabled:opacity-50 resize-none shadow-fine"
        ></textarea>
      </div>
    </div>

    <!-- Footer -->
    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 bg-slate-50/50">
      <Button 
        onclick={handleSubmit}
        disabled={!isFormValid}
        class="flex-1 h-10 bg-primary text-white font-medium shadow-fine"
      >
        <AppIcon name="check" size={18} />
        Soumettre la demande
      </Button>
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-10 shadow-fine">
          Annuler
        </Button>
      </Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #e2e8f0; border-radius: 10px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
</style>

