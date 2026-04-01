<script lang="ts">
	import AppIcon from '../../../../../components/layout/elements/AppIcon.svelte';
  import * as Sheet from "@/components/ui/sheet";
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { Button } from "@/components/ui/button";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import * as Select from "@/components/ui/select";

  let { open = $bindable(false) } = $props<{ open: boolean }>();

  let selectedEmployeeId = $state<string>('');
  let date = $state(new Date().toISOString().split('T')[0]);
  let checkIn = $state('08:00');
  let checkOut = $state('17:00');
  let status = $state<string>('PRESENT');

  const selectedEmployee = $derived(
    selectedEmployeeId ? employeeStore.employees.find(e => e.id.toString() === selectedEmployeeId) : null
  );

  function handleSave() {
    if (!selectedEmployeeId || !selectedEmployee) return;

    attendanceStore.addRecord({
      employeeId: selectedEmployee.id,
      employeeName: selectedEmployee.name,
      avatarUrl: selectedEmployee.avatarUrl,
      department: selectedEmployee.department,
      date,
      checkIn,
      checkOut,
      status: status as any
    });

    open = false;
    reset();
  }

  function reset() {
    selectedEmployeeId = '';
    date = new Date().toISOString().split('T')[0];
    checkIn = '08:00';
    checkOut = '17:00';
    status = 'PRESENT';
  }

  const statuses = [
    { value: 'PRESENT', label: 'Présent', color: 'bg-emerald-500' },
    { value: 'LATE', label: 'Retard', color: 'bg-amber-500' },
    { value: 'ABSENT', label: 'Absent', color: 'bg-rose-500' },
  ];
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-md flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-4 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] text-bold">Pointage Manuel</Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-6 space-y-6">
      <!-- Employee Selection -->
      <div class="space-y-1.5">
        <Label for="employee-trigger" class="text-[0.875rem] text-slate-900 font-medium tracking-tight">Employé</Label>
        <Select.Root type="single" value={selectedEmployeeId} onValueChange={(v) => { if (v) selectedEmployeeId = v; }}>
          <Select.Trigger id="employee-trigger" class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-[0.875rem] cursor-pointer">
            <div class="flex items-center gap-2">
              {#if selectedEmployee}
                <Avatar class="h-5 w-5 rounded-full border border-slate-200">
                  <AvatarImage src={selectedEmployee.avatarUrl} />
                  <AvatarFallback class={cn("text-[0.5rem] font-bold", getAvatarPalette(selectedEmployee.name).bg, getAvatarPalette(selectedEmployee.name).text)}>
                    {getInitials(...selectedEmployee.name.split(' '))}
                  </AvatarFallback>
                </Avatar>
                <span class="text-[0.875rem]">{selectedEmployee.name}</span>
              {:else}
                <span class="text-slate-500 text-[0.875rem]">Sélectionner un employé...</span>
              {/if}
            </div>
          </Select.Trigger> 
          <Select.Content class="z-100">
            {#each employeeStore.employees as emp}
              <Select.SelectItem value={emp.id.toString()} label={emp.name}>
                <div class="flex items-center gap-2">
                  <Avatar class="h-5 w-5 rounded-full border border-slate-200">
                    <AvatarImage src={emp.avatarUrl} />
                    <AvatarFallback class={cn("text-[0.5rem] font-bold", getAvatarPalette(emp.name).bg, getAvatarPalette(emp.name).text)}>
                      {getInitials(...emp.name.split(' '))}
                    </AvatarFallback>
                  </Avatar>
                  <span class="text-[0.875rem]">{emp.name}</span>
                </div>
              </Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

      <!-- Date -->
      <div class="space-y-1.5">
        <Label for="punchDate" class="text-[0.875rem] text-slate-900 font-medium tracking-tight">Date</Label>
        <Input 
          id="punchDate"
          type="date"
          bind:value={date}
          class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine text-[0.875rem] cursor-pointer"
        />
      </div>

      <!-- Status -->
      <div class="space-y-1.5">
        <Label class="text-[0.875rem] text-slate-900 font-medium tracking-tight">Statut</Label>
        <div class="grid grid-cols-3 gap-2">
          {#each statuses as s}
            <button 
              onclick={() => status = s.value}
              class={cn(
                "rounded-xl border transition-all py-0.5 flex items-center justify-center gap-1 cursor-pointer",
                status === s.value 
                  ? "bg-slate-200 border-primary shadow-fine ring-1 ring-primary/20"
                  : "bg-slate-50/50 border hover:border-slate-200"
              )}
            >
              <div class={cn("h-2.5 w-2.5 rounded-full", s.color)}></div>
              <span class={cn("text-[0.8rem]", status === s.value ? "text-slate-900" : "text-slate-600")}>{s.label}</span>
            </button>
          {/each}
        </div>
      </div>

      <div class="grid grid-cols-2 gap-4">
        <!-- Check In -->
        <div class="space-y-1.5">
          <Label for="checkInTime" class="text-[0.875rem] text-slate-900 font-medium tracking-tight">Arrivée</Label>
          <Input 
            id="checkInTime"
            type="time" 
            bind:value={checkIn}
            class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine text-[0.875rem] cursor-pointer"
          />
        </div>

        <!-- Check Out -->
        <div class="space-y-1.5">
          <Label for="checkOutTime" class="text-[0.875rem] text-slate-900 font-medium tracking-tight">Départ</Label>
          <Input 
            id="checkOutTime"
            type="time" 
            bind:value={checkOut}
            class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine text-[0.875rem] cursor-pointer"
          />
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer">
          Annuler
        </Button>
        <Button 
          onclick={handleSave}
          class="flex-1 h-9 rounded-md bg-primary text-white text-sm font-medium shadow-sm hover:shadow-md transition-all disabled:opacity-50 cursor-pointer"
        >
          <AppIcon name="check" size={18} />
          Enregistrer
        </Button>
      </Sheet.Close>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>

