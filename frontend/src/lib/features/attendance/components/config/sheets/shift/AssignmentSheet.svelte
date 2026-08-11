<script lang="ts">
  import { useCreateAssignmentMutation, useUpdateAssignmentMutation, usePoliciesQuery } from "../../../../queries/attendanceQueries";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import * as Select from "@/components/ui/select";
  import * as Sheet from "@/components/ui/sheet";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import { notification } from "@/stores/notification.svelte";
  import type { RecurrenceMode } from "../../../../constants/attendance.constants";
  import { RECURRENCE_MODE_LABELS } from "../../../../constants/attendance.constants";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { cn } from "@/utilities/common/css";
  import { formatDate } from "date-fns";
  import type { Employee } from "@/features/employees/types/types";
  import type { WorkPolicy, PolicyAssignment } from "../../../../types/types";


  interface EmployeeWithAssignment extends Employee {
    baseAssignment?: PolicyAssignment;
    overrideAssignment?: PolicyAssignment;
    basePolicy?: WorkPolicy;
    overridePolicy?: WorkPolicy;
  }


  let { 
    open = $bindable(false),
    employee = $bindable<EmployeeWithAssignment | null>(null)
  }: {
    open: boolean;
    employee: EmployeeWithAssignment | null;
  } = $props();


  // Derived display values
  let fullName = $derived(employee?.name || '');
  let profilePhoto = $derived(getMediaUrl(employee?.profile_photo || employee?.avatarUrl));
  let palette = $derived(getAvatarPalette(fullName));
  let initials = $derived(getInitials(employee?.last_name ?? '', employee?.middle_name ?? '', employee?.first_name ?? ''));

  // Form state
  let selectedBasePolicy = $state<string>("");
  let selectedOverridePolicy = $state<string>("");
  let assignmentStartDate = $state<string>(new Date().toISOString().split('T')[0]);
  let assignmentEndDate = $state<string>("");
  let hasNoEndDate = $state<boolean>(true);
  let overrideStartDate = $state<string>(new Date().toISOString().split('T')[0]);
  let overrideEndDate = $state<string>("");

  // Recurrence state (applies to override only)
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

  // Fetch policies via TanStack Query
  const policiesQuery = usePoliciesQuery();
  const policies = $derived($policiesQuery.data ?? []);

  // Available override policies: exclude the selected base policy
  const availableOverridePolicies = $derived(
    policies.filter(p => p.id !== selectedBasePolicy)
  );

  // Create vs edit mode
  let isEditing = $derived(!!employee?.baseAssignment?.id);

  // Mutations via TanStack Query
  const createAssignmentMutation = useCreateAssignmentMutation();
  const updateAssignmentMutation = useUpdateAssignmentMutation();

  let isSaving = $state(false);

  // Reset on open and pre-populate from existing assignment
  $effect(() => {
    if (open && employee) {
      const emp = employee as EmployeeWithAssignment;
      selectedBasePolicy = emp.baseAssignment?.policyId || "";
      selectedOverridePolicy = emp.overrideAssignment?.policyId || "";
      assignmentStartDate = emp.baseAssignment?.startDate || new Date().toISOString().split('T')[0];
      if (emp.baseAssignment?.endDate) {
        hasNoEndDate = false;
        assignmentEndDate = emp.baseAssignment.endDate;
      } else {
        hasNoEndDate = true;
        assignmentEndDate = "";
      }
      overrideStartDate = emp.overrideAssignment?.startDate || new Date().toISOString().split('T')[0];
      overrideEndDate = emp.overrideAssignment?.endDate || "";

      // Restore recurrence from override if present
      const rec = emp.overrideAssignment?.recurrence;
      if (rec && rec !== 'NONE') {
        const lower = rec.toLowerCase() as RecurrenceMode;
        if (['none', 'weekly', 'biweekly', 'monthly', 'quarterly'].includes(lower)) {
          recurrenceMode = lower;
        }
        // Use pre-computed recurrence count from backend
        recurrenceCount = emp.overrideAssignment?.recurrenceCount ?? 4;
      } else {
        recurrenceMode = 'none';
        recurrenceCount = 4;
      }
      isSaving = false;
    }
  });

  // Reset recurrence when override policy is cleared
  $effect(() => {
    if (!selectedOverridePolicy) {
      recurrenceMode = 'none';
    }
  });

  async function saveAssignment() {
    if (!employee || !selectedBasePolicy) {
      notification.toast.error("Veuillez sélectionner un modèle de base");
      return;
    }

    isSaving = true;

    try {
      const payload = {
        policy_id: selectedBasePolicy,
        start_date: assignmentStartDate,
        end_date: hasNoEndDate ? null : assignmentEndDate,
        recurrence: 'NONE',
        override_policy_id: selectedOverridePolicy || null,
        override_valid_from: selectedOverridePolicy ? overrideStartDate : null,
        override_valid_until: effectiveOverrideEndDate || null,
        override_recurrence: selectedOverridePolicy ? recurrenceMode.toUpperCase() : 'NONE',
        override_recurrence_count: selectedOverridePolicy && recurrenceMode !== 'none' ? recurrenceCount : null,
      };

      if (isEditing && employee.baseAssignment?.id) {
        await $updateAssignmentMutation.mutateAsync({
          assignmentId: employee.baseAssignment.id,
          data: payload,
        });
        notification.toast.success(
          `Affectation mise à jour pour ${employee.name}`
        );
      } else {
        await $createAssignmentMutation.mutateAsync({
          ...payload,
          employee_id: String(employee.id),
        });
        notification.toast.success(
          `Modèle${selectedOverridePolicy ? ' et remplacement' : ''} affecté à ${employee.name}`
        );
      }

      document.dispatchEvent(new CustomEvent('assignments-changed'));
      open = false;
    } catch (err) {
      const msg = err instanceof Error ? err.message : "Erreur inconnue";
      notification.toast.error(`Échec de l'affectation : ${msg}`);
    } finally {
      isSaving = false;
    }
  }

  function closeSheet() {
    if (!isSaving) open = false;
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="font-bold text-[1rem]">{isEditing ? 'Modifier l\'affectation' : 'Affecter un modèle'}</Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto px-6 py-4 space-y-6 custom-scrollbar">
      {#if employee}
        <!-- Employee header: avatar + name + job title -->
        <div class="flex items-center gap-3 p-3 rounded-lg border border-slate-200 bg-white">
          <div class="relative shrink-0">
            <Avatar class="size-11 border border-slate-200 overflow-hidden rounded-full">
              <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
              <AvatarFallback class={cn("text-[0.8rem] font-bold", palette.bg, palette.text)}>
                {initials}
              </AvatarFallback>
            </Avatar>
          </div>
          <div class="flex-1 min-w-0">
            <div class="font-semibold text-[0.875rem] text-slate-900 leading-tight truncate">{fullName}</div>
            {#if employee?.jobTitle}
              <div class="text-[0.84rem] text-slate-500 truncate leading-tight">{employee.jobTitle}</div>
            {/if}
          </div>
        </div>

        <!-- Base Policy -->
        <div class="space-y-1.5">
          <Label for="policyName">Modèle de base</Label>
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
            <Label for="startDate">Date de début</Label>
            <Input 
              id="startDate"
              type="date" 
              bind:value={assignmentStartDate}
              class="h-10 bg-white shadow-fine"
            />
          </div>

        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <Label for="endDate">Date de fin</Label>
            <div class="flex items-center gap-1.5">
              <input
                type="checkbox"
                id="noEndDate"
                bind:checked={hasNoEndDate}
                class="size-3.5 rounded border-slate-300 text-primary cursor-pointer"
              />
              <Label for="noEndDate" class="text-[0.8rem] text-slate-500 cursor-pointer select-none">Illimité</Label>
            </div>
          </div>
          <Input 
            id="endDate"
            type="date" 
            bind:value={assignmentEndDate}
            disabled={hasNoEndDate}
            class={cn("h-10 bg-white shadow-fine", hasNoEndDate && "opacity-40")}
          />
        </div>

        <!-- Override Policy -->
        <div class="space-y-1.5">
          <Label for="overridePolicy">Modèle de remplacement (optionnel)</Label>

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
                {#if isEditing && employee?.overrideAssignment?.policyId}
                  <Select.Item value="" class="flex items-center gap-2 text-slate-400">
                    <AppIcon name="x" size={15} class="text-red-400" />
                    <span class="text-[0.85rem]">Aucun (enlever le remplacement)</span>
                  </Select.Item>
                {/if}
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
        onclick={saveAssignment}
        class="flex-1 h-9.5 bg-primary text-white font-medium"
        disabled={!selectedBasePolicy || isSaving}
      >
        {#if isSaving}
          <AnimateSpin text="" class="border-white size-3" />
        {:else}
          <AppIcon name="check" size={17} />
        {/if}
        {isEditing ? 'Mettre à jour' : 'Affecter'}
      </Button>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>



