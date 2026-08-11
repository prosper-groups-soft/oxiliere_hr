<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { Transition, TransitionType } from "../../../../types/types";
  import { SENIORITY_LABELS } from "../../../../types/types";
  import { cn } from "@/utilities/common/css";
  import { fade, slide } from "svelte/transition";
  import { useCreateTransitionMutation, useUpdateTransitionMutation } from "../../../../queries/transitionQueries";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { useAllEmployees } from "@/features/employees/queries/employeeQueries";
  import { usePositionsQuery } from "../../../../queries/jobQueries";
  import { z } from 'zod';
  import { transitionSchema } from "../../../../schemas/transition.schema";
  import ValidationError from "@/components/ui/validation-error";
  import { TRANSITION_TYPE_CONFIG, TRANSITION_TYPE_ICONS } from "../../../../constants/transition.constants";

  
  let {
    open = $bindable(false),
    transition = $bindable(null)
  } = $props<{
    open: boolean,
    transition?: Transition | null
  }>();

  // --- Form state ---
  let formEmployeeId = $state<string | undefined>(undefined); // Select uses string | undefined
  let formType = $state<TransitionType>('TRANSFER');
  let formFromPositionId = $state('');
  let formFromSeniorityLevel = $state('');
  let formToPositionId = $state('');
  let formToSeniorityLevel = $state('');
  let formDate = $state('');
  let formReason = $state('');
  let expandedAffectation = $state(true);
  let isLoadingFromTransition = $state(false); // Flag to prevent auto-reset during initial load

  // Auto-expand/collapse based on formType
  $effect(() => {
    expandedAffectation = formType !== 'OFFBOARD';
  });

  // Auto-select seniority level when position changes
  $effect(() => {
    // Don't auto-reset during initial load from transition
    if (isLoadingFromTransition) return;

    if (formToPositionId && selectedToPos && selectedToPos.seniority_levels && selectedToPos.seniority_levels.length > 0) {
      // For promotions, auto-select the matching seniority level ONLY when fromPositionId changes
      // Don't override the existing formToSeniorityLevel if it's already set (from transition load)
      if (formType === 'PROMOTION' && formFromPositionId === formToPositionId) {
        // Only auto-select if formToSeniorityLevel is not already set to a valid value
        // This prevents overriding the value loaded from transition
        if (!formToSeniorityLevel && formFromSeniorityLevel) {
          const fromLevel = selectedToPos.seniority_levels.find(sl =>
            sl.seniority_level.id === formFromSeniorityLevel
          );
          if (fromLevel) {
            formToSeniorityLevel = fromLevel.seniority_level.id;
          }
        }
      } else {
        // For other cases (not promotion or different positions), reset to empty
        formToSeniorityLevel = '';
      }
    } else if (!formToPositionId) {
      // Clear when no position selected
      formToSeniorityLevel = '';
    }
  });

  $effect(() => {
    if (open) {
      if (transition) {
        isLoadingFromTransition = true;
        formEmployeeId = transition.employee_id;
        formType = transition.transition_type as TransitionType;
        formFromPositionId = transition.from_position?.id || '';
        formToPositionId = transition.to_position?.id || '';
        // Access seniority levels directly from transition (backend returns them at root level in snake_case)
        formFromSeniorityLevel = transition.from_seniority_level?.id || '';
        formToSeniorityLevel = transition.to_seniority_level?.id || '';
        formDate = transition.date;
        formReason = transition.reason || '';
        // Allow auto-select effect to run after initial load
        isLoadingFromTransition = false;
      } else {
        isLoadingFromTransition = true;
        formEmployeeId = undefined;
        formType = 'TRANSFER';
        formFromPositionId = '';
        formFromSeniorityLevel = '';
        formToPositionId = '';
        formToSeniorityLevel = '';
        formDate = '';
        formReason = '';
        isLoadingFromTransition = false;
      }
    }
  });

  // Mutations
  const createMutation = useCreateTransitionMutation();
  const updateMutation = useUpdateTransitionMutation();
  
  // Derived states
  const isSaving = $derived($createMutation.isPending || $updateMutation.isPending);
  
  // --- Validation state ---
  let validationErrors = $state<Record<string, string>>({});

  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function validateForm(): boolean {
    validationErrors = {};
    
    const result = transitionSchema.safeParse({
      employee_id: formEmployeeId ?? '',
      transition_type: formType,
      from_position_id: formFromPositionId || null,
      to_position_id: formToPositionId || undefined,
      date: formDate,
      reason: formReason
    });
    
    if (!result.success) {
      result.error.issues.forEach((err: z.core.$ZodIssue) => {
        const field = err.path.join('.');
        validationErrors = { ...validationErrors, [field]: err.message };
      });
      console.log('Validation errors:', validationErrors);
      return false;
    }
    
    return true;
  }
  
  // Reset validation errors when modal opens
  $effect(() => {
    if (open) {
      validationErrors = {};
    }
  });

  async function handleSave() {
    // Validation Zod
    if (!validateForm()) {
      notification.toast.error('Veuillez corriger les erreurs du formulaire');
      return;
    }

    // Build data - from_position_id is auto-detected by backend on create
    const data = {
      employee_id: String(formEmployeeId),
      transition_type: formType,
      to_position_id: formToPositionId || null,
      to_seniority_level_id: formToSeniorityLevel || null,
      date: formDate || new Date().toISOString().split('T')[0],
      reason: formReason || undefined,
      // Only include from_position_id and from_seniority_level_id when editing - backend auto-detects on create
      ...(transition && { 
        from_position_id: formFromPositionId || null,
        from_seniority_level_id: formFromSeniorityLevel || null
      })
    };

    try {
      if (transition) {
        await $updateMutation.mutateAsync({ id: transition.id, data });
      } else {
        await $createMutation.mutateAsync(data);
      }
      open = false;
    } catch (error) {
      // Error already handled by mutation
    }
  }


  // Queries for select options (all data, not just store page)
  const allEmployeesQuery = useAllEmployees();
  const allPositionsQuery = usePositionsQuery();
  
  const selectedEmpl = $derived(formEmployeeId && $allEmployeesQuery.data ? $allEmployeesQuery.data.find(e => String(e.id) === formEmployeeId) : null);
  const selectedToPos = $derived($allPositionsQuery.data?.find(p => p.id === formToPositionId) || null);

  // Auto-set from_position to employee's current position when creating new transition
  $effect(() => {
    if (!transition && selectedEmpl?.positionId) {
      formFromPositionId = selectedEmpl.positionId;
    }
  });
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-lg bg-white p-0 flex flex-col h-full overflow-hidden">
    <!-- Header aligned with PositionSheet -->
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] text-slate-900 truncate font-bold">
            {transition ? 'Modifier le mouvement' : 'Nouveau mouvement'}
          </Sheet.Title>
        </div>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-4 space-y-7" in:fade={{ duration: 200 }}>
        
        <!-- Employé (Select Pattern) -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Employé concerné <span class="text-red-500">*</span></Label>
          <Select type="single" value={formEmployeeId} onValueChange={(v) => { formEmployeeId = v; clearValidationError('employee_id'); }}>
            <SelectTrigger class={cn(
              "h-10 w-full bg-white border-slate-200 shadow-fine rounded-md cursor-pointer",
              validationErrors.employee_id && "border-red-500"
            )}>
              <span class="truncate text-[0.87rem] font-medium">
                {selectedEmpl?.name || 'Sélectionner un employé...'}
              </span>
            </SelectTrigger>
            <SelectContent class="z-9999 max-h-72">
              {#if $allEmployeesQuery.isLoading}
                <AnimateSpin class="size-3" text="Chargement des employés" textPosition="right" />
              {:else if $allEmployeesQuery.data}
                {#each $allEmployeesQuery.data as emp}
                  <SelectItem value={String(emp.id)} class="text-[0.85rem]">
                    {emp.name}
                  </SelectItem>
                {/each}
              {/if}
            </SelectContent>
          </Select>
          <ValidationError errors={validationErrors} field="employee_id" />
        </div>

        <!-- Type de mouvement -->
        <div class="space-y-3">
          <Label class="text-slate-900">Type de mouvement</Label>
          <div class="grid grid-cols-2 gap-3">
            {#each ['TRANSFER', 'PROMOTION', 'HIRE', 'OFFBOARD'] as typeStr}
              {@const type = typeStr as TransitionType}
              {@const typeCfg = TRANSITION_TYPE_CONFIG[type]}
              <button
                type="button"
                onclick={() => formType = type}
                class={cn(
                  "flex flex-col items-start gap-2 p-3.5 rounded-xl border text-left transition-all group cursor-pointer",
                  formType === type
                    ? "bg-primary/5 border-primary text-primary shadow-md"
                    : "bg-white border-slate-200 text-slate-700 hover:border-indigo-300 hover:bg-indigo-50/50 hover:shadow-xs"
                )}
              >
                <div class="flex items-center gap-2">
                  <AppIcon name={TRANSITION_TYPE_ICONS[type]} size={16} class={typeCfg.color} />
                  <span class="text-[0.85rem]">{typeCfg.label}</span>
                </div>
              </button>
            {/each}
          </div>
        </div>

        <!-- Grid for Date and other potential meta -->
        <div class="grid grid-cols-1 gap-4">
          <div class="space-y-2.5">
            <Label for="trans-date" class="text-slate-900">Date d'effet <span class="text-red-500">*</span></Label>
            <Input 
              id="trans-date"
              type="date"
              bind:value={formDate}
              oninput={() => clearValidationError('date')}
              class={cn(
                "h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine",
                validationErrors.date && "border-red-500 focus:ring-red-500"
              )}
            />
            <ValidationError errors={validationErrors} field="date" />
          </div>
        </div>

        <!-- Nouvelle Affectation - Collapsible Section -->
        <div class="rounded-lg p-1.5 bg-white border border-slate-100 mb-5">
          <!-- Header with toggle -->
          <button
            type="button"
            onclick={() => { if (formType !== 'OFFBOARD') expandedAffectation = !expandedAffectation; }}
            class="w-full flex items-center gap-2 px-0 py-2 text-left transition-colors rounded-lg {formType === 'OFFBOARD' ? 'cursor-default opacity-60' : 'cursor-pointer hover:bg-indigo-100/50'}"
            disabled={formType === 'OFFBOARD'}
          >
            <AppIcon 
              name={expandedAffectation ? 'chevron-down' : 'chevron-right'} 
              size={18} 
              class="text-slate-400 shrink-0 transition-transform duration-200"
            />
            <span class="text-[0.9rem] font-medium {formType === 'OFFBOARD' ? 'text-slate-400' : 'text-slate-700'}">
              Nouvelle Affectation
            </span>
          </button>

          {#if expandedAffectation && formType !== 'OFFBOARD'}
            <div class="space-y-5" in:slide={{ duration: 200 }}>
              
              <!-- Nouveau poste -->
              <div class="space-y-2.5">
                <Label class="text-slate-900">Nouveau poste <span class="text-red-500">*</span></Label>
                <Select type="single" value={formToPositionId} onValueChange={(v) => { formToPositionId = v; formToSeniorityLevel = ''; clearValidationError('to_position_id'); }}>
                  <SelectTrigger class={cn(
                    "h-11 w-full bg-white border-slate-200 shadow-fine rounded-lg cursor-pointer hover:border-slate-300 transition-colors",
                    validationErrors.to_position_id && "border-red-500"
                  )}>
                    <div class="flex items-center gap-0.5">
                      {#if selectedToPos}
                        <div class="h-2 w-2 rounded-full bg-emerald-500 shrink-0"></div>
                        <div class="flex gap-1.5 items-start">
                          <span class="text-[0.87rem] font-semibold text-slate-800">{selectedToPos.name}</span>
                          {#if selectedToPos.job_family?.name || selectedToPos.org_unit?.name}
                            <span class="text-[0.85rem] text-slate-400 pl-1.5 border-l border-slate-300">
                              {selectedToPos.job_family?.name}{selectedToPos.job_family?.name && selectedToPos.org_unit?.name ? ' · ' : ''}{selectedToPos.org_unit?.name}
                            </span>
                          {/if}
                        </div>
                      {:else}
                        <span class="text-[0.87rem] font-medium text-slate-400">Choisir un poste...</span>
                      {/if}
                    </div>
                  </SelectTrigger>
                  <SelectContent class="z-9999 max-h-72">
                    {#if $allPositionsQuery.isLoading}
                      <AnimateSpin text="Chargement..." class="size-3" />
                    {:else if $allPositionsQuery.data}
                      {#each $allPositionsQuery.data as pos}
                        <SelectItem value={pos.id} class="text-[0.85rem] py-2.5">
                          <div class="flex flex-col items-start gap-0.5">
                            <span class="font-medium text-[0.87rem]">{pos.name}</span>
                            {#if pos.job_family?.name || pos.org_unit?.name}
                              <span class="text-[0.85rem] text-slate-400">
                                {pos.job_family?.name}{pos.job_family?.name && pos.org_unit?.name ? ' · ' : ''}{pos.org_unit?.name}
                              </span>
                            {/if}
                          </div>
                        </SelectItem>
                      {/each}
                    {/if}
                  </SelectContent>
                </Select>
                <ValidationError errors={validationErrors} field="to_position_id" />
              </div>

              <!-- Niveau de séniorité du nouveau poste -->
              {#if selectedToPos && selectedToPos.seniority_levels && selectedToPos.seniority_levels.length > 0}
                <div class="space-y-2.5">
                  <Label class="text-slate-900">Niveau de séniorité <span class="text-red-500">*</span></Label>
                  <Select 
                    type="single" 
                    value={formToSeniorityLevel} 
                    onValueChange={(v) => { formToSeniorityLevel = v; clearValidationError('to_seniority_level_id'); }}
                  >
                    <SelectTrigger class={cn(
                      "h-10 w-full bg-white border-slate-200 shadow-fine rounded-lg cursor-pointer hover:border-slate-300 transition-colors",
                      validationErrors.to_seniority_level_id && "border-red-500"
                    )}>
                      <span class="text-[0.87rem] font-medium">
                        {#if formToSeniorityLevel}
                          {@const selectedLevel = selectedToPos?.seniority_levels?.find(sl => sl.seniority_level.id === formToSeniorityLevel)}
                          {selectedLevel?.seniority_level.level ? SENIORITY_LABELS[selectedLevel.seniority_level.level] : ''}
                          <span class="text-slate-400 ml-2 text-[0.87rem]">
                            ({selectedLevel?.salary_min} - {selectedLevel?.salary_max} FC)
                          </span>
                        {:else}
                          Choisir un niveau...
                        {/if}
                      </span>
                    </SelectTrigger>
                    <SelectContent class="z-9999">
                      {#each selectedToPos.seniority_levels.sort((a, b) => a.rank - b.rank) as level}
                        <SelectItem value={level.seniority_level.id} class="text-[0.85rem]">
                          <div class="flex flex-col items-start gap-1">
                            <span class="font-medium text-[0.86rem]">{level.seniority_level.name || SENIORITY_LABELS[level.seniority_level.level] || level.seniority_level.level}</span>
                            <span class="text-slate-400 text-[0.86rem]">
                              {level.salary_min} - {level.salary_max} FC
                            </span>
                          </div>
                        </SelectItem>
                      {/each}
                    </SelectContent>
                  </Select>
                  <ValidationError errors={validationErrors} field="to_seniority_level_id" />
                </div>
              {:else if selectedToPos}
                <div class="p-3 rounded-lg bg-amber-50 border border-amber-200">
                  <p class="text-[0.85rem] text-amber-700">
                    Ce poste n'a pas de niveaux de séniorité définis. Veuillez d'abord configurer les niveaux pour ce poste.
                  </p>
                </div>
              {/if}
            </div>
          {/if}
        </div>

        <!-- Raison -->
        <div class="space-y-2.5">
          <Label for="trans-reason" class="text-slate-900">Motif ou Commentaire</Label>
          <textarea
            id="trans-reason"
            bind:value={formReason}
            oninput={() => clearValidationError('reason')}
            class={cn(
              "w-full h-28 rounded-lg border border-slate-200 px-3.5 py-3 text-[0.88rem] leading-relaxed focus:ring-4 focus:ring-primary/30 focus:border-primary focus:outline-none bg-white shadow-fine resize-none transition-all placeholder:text-slate-400",
              validationErrors.reason && "border-red-500 focus:ring-red-500"
            )}
            placeholder="Précisez les raisons du mouvement (ex: Restructuration, Performance...)"
          ></textarea>
          <ValidationError errors={validationErrors} field="reason" />
        </div>
      </div>
    </div>

    <!-- Footer aligned with PositionSheet -->
    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            <AppIcon name="x" size={18} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button 
          onclick={handleSave} 
          disabled={isSaving}
          class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine text-[0.88rem] hover:opacity-90 transition-all disabled:opacity-70"
        >
          {#if isSaving}
            <AnimateSpin text="" class="size-3 border-white" />
          {:else}
            <AppIcon name="check" size={18} />
          {/if}
          Enregistrer
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




