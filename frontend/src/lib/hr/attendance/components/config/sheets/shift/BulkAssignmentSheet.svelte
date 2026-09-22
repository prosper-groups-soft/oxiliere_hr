<script lang="ts">
  import { useCreateAssignmentMutation, usePoliciesQuery } from "../../../../queries/attendanceQueries";
  import { useAllEmployees } from "@/hr/employees/queries/employeeQueries";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as Select from "@/components/ui/select";
  import * as Sheet from "@/components/ui/sheet";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import { notification } from "@/stores/notification.svelte";
  import { Switch } from "@/components/ui/switch";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { cn } from "@/utilities/common/css";
  import { getOrgUnitIcon } from "@/hr/jobs/constants/orgUnit.constants";
  import { formatDate } from "date-fns";
  import { fade } from "svelte/transition";
  import type { Employee } from "@/hr/employees/types/types";
  import { useAssignmentsQuery } from "../../../../queries/attendanceQueries";
  import type { RecurrenceMode } from "../../../../constants/attendance.constants";
  import { RECURRENCE_MODE_LABELS } from "../../../../constants/attendance.constants";

  
  let {
    open = $bindable(false)
  } = $props<{
    open: boolean;
  }>();

  let selectedEmployees = $state<Employee[]>([]);
  let selectedBasePolicy = $state<string>("");
  let selectedOverridePolicy = $state<string>("");
  let assignmentStartDate = $state<string>(new Date().toISOString().split('T')[0]);
  let assignmentEndDate = $state<string>("");
  let hasNoEndDate = $state<boolean>(true);
  let overrideStartDate = $state<string>(new Date().toISOString().split('T')[0]);
  let overrideEndDate = $state<string>("");

  // Recurrence state (applies to override/shift only)
  let recurrenceMode = $state<RecurrenceMode>('none');
  let recurrenceCount = $state<number>(4);


  // Compute override end date from start + recurrence
  const overrideEndDateComputed = $derived.by(() => {
    if (recurrenceMode === 'none') return '';
    const start = new Date(overrideStartDate);
    let months = 0, days = 0;
    switch (recurrenceMode) {
      case 'weekly':    days = 7 * recurrenceCount; break;
      case 'biweekly':  days = 14 * recurrenceCount; break;
      case 'monthly':   months = recurrenceCount; break;
      case 'quarterly': months = 3 * recurrenceCount; break;
    }
    const end = new Date(start);
    if (months) end.setMonth(end.getMonth() + months);
    if (days) end.setDate(end.getDate() + days);
    return end.toISOString().split('T')[0];
  });

  // Effective end date: computed by recurrence if set, otherwise manual input
  const effectiveOverrideEndDate = $derived(
    recurrenceMode !== 'none' ? overrideEndDateComputed : overrideEndDate
  );

  // Fetch employees via TanStack Query (not via store)
  const employeesQuery = useAllEmployees();
  const employees = $derived($employeesQuery.data ?? []);

  // Fetch policies via TanStack Query (not via store)
  const policiesQuery = usePoliciesQuery();
  const policies = $derived($policiesQuery.data ?? []);

  // Available override policies: exclude the selected base policy
  const availableOverridePolicies = $derived(
    policies.filter(p => p.id !== selectedBasePolicy)
  );

  // Fetch existing assignments to mark already-assigned employees
  const assignmentsQuery = useAssignmentsQuery(() => 1, () => 200);
  const assignedEmployeeIds = $derived(
    new Set($assignmentsQuery.data?.results?.map(a => a.employee_id) ?? [])
  );

  // Mutation via TanStack Query
  const assignmentMutation = useCreateAssignmentMutation();

  let isSaving = $state(false);
  let totalToProcess = $state(0);
  let processedCount = $state(0);
  let errorList = $state<string[]>([]);

  // Reset on open
  $effect(() => {
    if (open) {
      selectedEmployees = [];
      selectedBasePolicy = "";
      selectedOverridePolicy = "";
      assignmentStartDate = new Date().toISOString().split('T')[0];
      assignmentEndDate = "";
      hasNoEndDate = true;
      overrideStartDate = new Date().toISOString().split('T')[0];
      overrideEndDate = "";
      recurrenceMode = 'none';
      recurrenceCount = 4;
      isSaving = false;
      totalToProcess = 0;
      processedCount = 0;
      errorList = [];
    }
  });

  // Reset recurrence when override policy is cleared
  $effect(() => {
    if (!selectedOverridePolicy) {
      recurrenceMode = 'none';
    }
  });

  const unassignedEmployees = $derived(
    employees.filter(e => !assignedEmployeeIds.has(String(e.id)))
  );

  function selectAllEmployees() {
    selectedEmployees = [...unassignedEmployees];
  }

  function clearSelection() {
    selectedEmployees = [];
  }

  function toggleEmployeeSelection(employee: Employee) {
    const employeeId = employee.id;
    const existing = selectedEmployees.find(e => e.id === employeeId);
    if (existing) {
      selectedEmployees = selectedEmployees.filter(e => e.id !== employeeId);
    } else {
      selectedEmployees = [...selectedEmployees, employee];
    }
  }

  function isEmployeeSelected(employee: Employee) {
    return selectedEmployees.some(e => e.id === employee.id);
  }

  async function saveBulkAssignment() {
    if (selectedEmployees.length === 0 || !selectedBasePolicy) {
      notification.toast.error("Veuillez sélectionner au moins un employé et un modèle de base");
      return;
    }

    isSaving = true;
    totalToProcess = selectedEmployees.length;
    processedCount = 0;
    errorList = [];
    const errors: string[] = [];

    for (const emp of selectedEmployees) {
      try {
        // Single API call: base policy + optional override in one record
        await $assignmentMutation.mutateAsync({
          employee_id: String(emp.id),
          policy_id: selectedBasePolicy,
          start_date: assignmentStartDate,
          end_date: hasNoEndDate ? null : assignmentEndDate,
          recurrence: 'NONE',
          override_policy_id: selectedOverridePolicy || null,
          override_valid_from: selectedOverridePolicy ? overrideStartDate : null,
          override_valid_until: effectiveOverrideEndDate || null,
          override_recurrence: selectedOverridePolicy ? recurrenceMode.toUpperCase() : 'NONE',
          override_recurrence_count: selectedOverridePolicy && recurrenceMode !== 'none' ? recurrenceCount : null,
        });
        processedCount++;
      } catch (err) {
        const msg = err instanceof Error ? err.message : "Erreur inconnue";
        errors.push(`${emp.name}: ${msg}`);
        errorList = [...errors];
        processedCount++;
      }
    }

    isSaving = false;

    // Report results
    if (errors.length === 0) {
      const names = selectedEmployees.map(e => e.name).join(", ");
      notification.toast.success(
        `Modèle${selectedOverridePolicy ? ' et remplacement' : ''} affecté(s) à ${selectedEmployees.length} employé(s) : ${names}`
      );
      document.dispatchEvent(new CustomEvent('assignments-changed'));
      open = false;
    } else if (errors.length < selectedEmployees.length) {
      notification.toast.warning(
        `${selectedEmployees.length - errors.length} affectation(s) réussie(s), ${errors.length} échec(s).`
      );
      document.dispatchEvent(new CustomEvent('assignments-changed'));
      open = false;
    } else {
      notification.toast.error("Échec de toutes les affectations. Consultez les détails.");
    }
  }

  function closeSheet() {
    if (!isSaving) open = false;
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="font-bold text-[1rem]">Affecter en masse</Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-4 space-y-6 custom-scrollbar">
      <!-- Section de sélection des employés -->
      <div class="space-y-3">
        <div class="flex items-center justify-between">
          <Label class="text-[0.875rem] font-medium">Sélection des employés</Label>
          <Button size="sm" onclick={selectedEmployees.length === unassignedEmployees.length ? clearSelection : selectAllEmployees} class={selectedEmployees.length === unassignedEmployees.length ? "bg-red-50! text-red-600! border-red-100! hover:bg-red-100 hover:border-red-200! text-[0.85rem] shadow-fine" : "text-[0.85rem] shadow-fine"} variant="outline">
            <AppIcon name={selectedEmployees.length === unassignedEmployees.length ? "trash" : "check"} size={17} class={selectedEmployees.length === unassignedEmployees.length ? "text-red-500" : "text-slate-500"} />
            {selectedEmployees.length === unassignedEmployees.length ? "Effacer" : "Tout sélectionner"}
          </Button>
        </div>

        {#if $employeesQuery.isLoading}
          <div class="flex items-center justify-center py-12" in:fade={{ duration: 200 }}>
            <AnimateSpin text="Chargement des employés" />
          </div>
        {:else if employees.length === 0}
          <div class="flex flex-col items-center justify-center gap-3 py-12 text-slate-400 text-sm" in:fade={{ duration: 200 }}>
            <AppIcon name="users" size={24} class="text-slate-300" />
            Aucun employé disponible.
            <Button size="sm" variant="outline" onclick={() => $employeesQuery.refetch()} class="text-[0.8rem]">
              <AppIcon name="refresh" size={14} class="text-slate-400 shrink-0" />
              Recharger
            </Button>
          </div>
        {:else}
          <div class="border border-slate-200 rounded-lg bg-white max-h-80 overflow-y-auto custom-scrollbar" in:fade={{ duration: 200 }}>
            {#each employees as emp}
              <div class="flex items-center space-x-3 p-3 hover:bg-slate-50 border-b border-slate-100 last:border-b-0 cursor-pointer" onclick={() => { if (!assignedEmployeeIds.has(String(emp.id))) toggleEmployeeSelection(emp); }} role="none">
                <Switch 
                  checked={isEmployeeSelected(emp)}
                  disabled={assignedEmployeeIds.has(String(emp.id))}
                  class={cn("pointer-events-none", assignedEmployeeIds.has(String(emp.id)) && "opacity-40")}
                />
                <div class="flex items-center gap-2.5 flex-1 min-w-0">
                  <Avatar class="h-10 w-10 shrink-0 border border-slate-200 rounded-full overflow-hidden">
                    <AvatarImage src={getMediaUrl(emp.profile_photo || emp.avatarUrl)} alt={emp.name} class="object-cover" />
                    <AvatarFallback class={cn("text-[0.7rem] font-bold", getAvatarPalette(emp.name).bg, getAvatarPalette(emp.name).text)}>
                      {getInitials(emp.last_name ?? '', emp.middle_name ?? '', emp.first_name ?? '')}
                    </AvatarFallback>
                  </Avatar>
                  <div class="flex-1 min-w-0">
                    <div class="font-medium text-[0.875rem] truncate">{emp.name}</div>
                    {#if assignedEmployeeIds.has(String(emp.id))}
                      <div class="flex items-center gap-1 mt-0.5">
                        <span class="text-[0.75rem] text-amber-700 bg-amber-50 border border-amber-200 px-1.5 py-0.5 rounded-full font-medium leading-tight">
                          Déjà affecté
                        </span>
                      </div>
                    {/if}
                    <div class="flex items-center gap-1.5 text-slate-500 text-[0.82rem] min-w-0">
                      <span class="truncate text-[0.875rem]">
                        {emp.jobTitle || 'Poste non défini'}
                      </span>
                      {#if emp.orgUnit}
                        <span class="shrink-0 text-slate-300">•</span>
                        <span class="flex items-center gap-1 min-w-0">
                          <AppIcon name={getOrgUnitIcon(emp.orgUnitType ?? '')} size={15} class="text-slate-400 shrink-0" />
                          <span class="truncate text-[0.875rem]">{emp.orgUnit}</span>
                        </span>
                      {/if}
                    </div>
                  </div>
                </div>
              </div>
            {/each}
          </div>
        {/if}

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
                {selectedBasePolicy ? policies.find(p => p.id === selectedBasePolicy)?.name : "Sélectionner un modèle de base"}
              </span>
            </Select.Trigger>
            <Select.Content class="max-h-60 w-lg z-100">
              {#each policies as policy}
                <Select.Item value={policy.id!} class="flex flex-col items-start w-full overflow-hidden">
                  <div class="font-medium text-[0.875rem]">{policy.name}</div>
                  <div class="text-slate-500 text-[0.84rem] truncate overflow-hidden w-full">
                    {policy.description}
                  </div>
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
          <div class="flex items-center justify-between">
            <Label for="bulkEndDate">Date de fin</Label>
            <div class="flex items-center gap-1.5">
              <input
                type="checkbox"
                id="bulkNoEndDate"
                bind:checked={hasNoEndDate}
                class="size-3.5 rounded border-slate-300 text-primary cursor-pointer"
              />
              <Label for="bulkNoEndDate" class="text-[0.8rem] text-slate-500 cursor-pointer select-none">Illimité</Label>
            </div>
          </div>
          <Input 
            id="bulkEndDate"
            type="date" 
            bind:value={assignmentEndDate}
            disabled={hasNoEndDate}
            class={cn("h-10 bg-white shadow-fine", hasNoEndDate && "opacity-40")}
          />
        </div>

        <div class="space-y-1.5">
          <Label for="bulkOverridePolicy">Modèle de remplacement (optionnel)</Label>

          {#if availableOverridePolicies.length === 0}
            <div class="flex items-center gap-2 py-3 px-4 border border-dashed border-slate-200 rounded-lg bg-slate-50 text-slate-400 text-[0.85rem]">
              <AppIcon name="info" size={16} class="text-slate-300 shrink-0" />
              Aucun modèle de remplacement disponible
            </div>
          {:else}
            <Select.Root type="single" bind:value={selectedOverridePolicy}>
              <Select.Trigger class="w-full h-10 bg-white border border-slate-200 rounded-lg cursor-pointer">
                <span class="text-[0.85rem]">
                  {selectedOverridePolicy ? policies.find(p => p.id === selectedOverridePolicy)?.name : "Sélectionner un modèle de remplacement"}
                </span>
              </Select.Trigger>
              <Select.Content class="max-h-60 w-lg z-100">
                {#each availableOverridePolicies as policy}
                  <Select.Item value={policy.id!} class="flex flex-col items-start w-full overflow-hidden">
                    <div class="font-medium text-[0.875rem]">{policy.name}</div>
                    <div class="text-slate-500 text-[0.84rem] truncate overflow-hidden w-full">
                      {policy.description}
                    </div>
                  </Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
          {/if}

          {#if selectedOverridePolicy}
            <!-- Recurrence pill selector -->
            <div class="space-y-1.5 mt-3">
              <Label>Récurrence</Label>
              <div class="flex items-center gap-2">
                {#each ['none', 'weekly', 'biweekly', 'monthly', 'quarterly'] as mode}
                  <button
                    onclick={() => recurrenceMode = mode as RecurrenceMode}
                    class={cn(
                      "px-3 py-1.5 text-[0.84rem] rounded-full border transition-all cursor-pointer",
                      recurrenceMode === mode
                        ? "bg-blue-600 text-white border-blue-600 shadow-sm"
                        : "bg-white text-slate-600 border-slate-200 hover:border-slate-300"
                    )}
                  >
                    {RECURRENCE_MODE_LABELS[mode as RecurrenceMode]}
                  </button>
                {/each}
              </div>
            </div>

            {#if recurrenceMode === 'none'}
              <!-- Manual date pickers when no recurrence -->
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
            {:else}
              <!-- Recurrence count and computed end date -->
              <div class="flex items-center gap-3 mt-3">
                <div class="flex items-center gap-1.5">
                  <Label class="text-[0.8rem] text-slate-500">Répéter</Label>
                  <input
                    type="number"
                    min="1"
                    max="52"
                    bind:value={recurrenceCount}
                    class="w-16 h-8 text-center text-sm border border-slate-200 rounded-md bg-white"
                  />
                  <span class="text-[0.8rem] text-slate-500">
                    {recurrenceMode === 'weekly' || recurrenceMode === 'biweekly' ? 'fois' : 'mois'}
                  </span>
                </div>
                {#if overrideEndDateComputed}
                  <span class="text-[0.8rem] text-blue-600 font-medium ml-auto">
                    → jusqu'au {formatDate(new Date(overrideEndDateComputed), 'dd/MM/yyyy')}
                  </span>
                {/if}
              </div>
            {/if}
          {/if}
        </div>
        </div>
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-4 border-t flex flex-row gap-3 bg-slate-50/50">
      <Sheet.Close onclick={closeSheet} class="flex-1">
        <Button variant="outline" class="w-full h-9.5">
          <AppIcon name="x" size={17} class="text-slate-300" />
          Annuler
        </Button>
      </Sheet.Close>
      <Button 
        onclick={saveBulkAssignment}
        class="flex-1 h-9.5 bg-primary text-white font-medium"
        disabled={selectedEmployees.length === 0 || !selectedBasePolicy || isSaving}
      >
        {#if isSaving}
          <AnimateSpin text="" class="border-white size-3" />
        {:else}
          <AppIcon name="check" size={17} />
        {/if}
        Affecter à {selectedEmployees.length} employé(s)
      </Button>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>



