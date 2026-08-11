<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Badge } from "@/components/ui/badge";
  import * as Avatar from "@/components/ui/avatar";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { useUpdateOrgUnitMutation } from "../../../queries/orgQueries";
  import { z } from 'zod';
  import ValidationError from "@/components/ui/validation-error";
  import { useAllEmployees, useAssignEmployeeToOrgUnitMutation, useUnassignEmployeeFromOrgUnitMutation } from "@/features/employees/queries/employeeQueries";
  import ConfirmAction from "@/components/shared/actions/ConfirmAction.svelte";
  import { formatEmployeeName } from "@/utilities/common/employee.utils";
  import { getFriendlyErrorMessage } from "@/constants/errors";
  import type { OrgUnit } from "../../../types/org.types";

  
  let {
    open = $bindable(false),
    orgUnit,
    members = []
  } = $props<{
    open: boolean,
    orgUnit: OrgUnit | null,
    members?: any[] // Passé depuis OrgDrawer
  }>();

  // --- Form state ---
  let isAdding = $state(false);
  let selectedEmployeeId = $state<string | null>(null);
  let activeTab = $state<'members' | 'leadership'>('members');
  let formManagerId = $state<string | null>(null);
  let formAffointId = $state<string | null>(null);
  let confirmingEmployeeId = $state<string | number | null>(null);

  // Schéma Zod pour validation du leadership
  const leadershipSchema = z.object({
    managerId: z.string().nullable().refine((val) => val !== null && val !== '', {
      message: 'Un responsable (manager) est requis'
    })
  });

  // État des erreurs de validation
  let validationErrors = $state<Record<string, string>>({});

  function clearValidationError(field: string) {
    if (validationErrors[field]) {
      const { [field]: _, ...rest } = validationErrors;
      validationErrors = rest;
    }
  }

  const updateOrgUnitMutation = useUpdateOrgUnitMutation();
  const assignEmployeeMutation = useAssignEmployeeToOrgUnitMutation();
  const unassignEmployeeMutation = useUnassignEmployeeFromOrgUnitMutation();
  const allEmployeesQuery = useAllEmployees();
  
  // Liste des employés depuis la query
  const allEmployees = $derived($allEmployeesQuery.data ?? []);
  
  // Utiliser les membres passés en prop, sinon tableau vide
  const assignedEmployees = $derived(members ?? []);

  // Track previous open state to detect opening vs updates
  let wasOpen = $state(false);

  // Reset state when sheet opens (not when orgUnit updates)
  $effect(() => {
    if (open && orgUnit) {
      // Réinitialiser seulement à l'ouverture initiale, pas quand orgUnit change
      if (!wasOpen) {
        isAdding = false;
        selectedEmployeeId = null;
        activeTab = 'members';
        wasOpen = true;
      }
      // Toujours mettre à jour les IDs (pour réactivité après mutation)
      formManagerId = orgUnit.managerId?.toString() ?? null;
      // Normaliser: string vide ou undefined/null → null pour cohérence du Select
      const rawAffointId = orgUnit.affointId?.toString();
      formAffointId = rawAffointId && rawAffointId !== '' ? rawAffointId : null;
    } else if (!open) {
      wasOpen = false;
    }
  });

  // Helper pour trouver un employé par ID
  function getEmployeeById(id: string | null) {
    if (!id) return undefined;
    return allEmployees.find((e: { id: string | number }) => String(e.id) === id);
  }

  // Employee not assigned to the current org unit (tous sauf les affectés)
  const memberIds = $derived.by(() => 
    new Set(assignedEmployees.map((m: { id: string | number }) => String(m.id)))
  );
  const unassignedEmployees = $derived(
    allEmployees.filter((e: { id: string | number }) => !memberIds.has(String(e.id)))
  );

  async function handleAssign() {
    if (!selectedEmployeeId || !orgUnit) return;

    const employee = getEmployeeById(selectedEmployeeId);
    if (!employee) return;

    // Vérifier si l'employé est déjà affecté
    if (assignedEmployees.some((e: { id: string | number }) => String(e.id) === selectedEmployeeId)) {
      notification.toast.error(`${employee.name} est déjà affecté à cette unité.`);
      return;
    }

    // Vérifier la limite d'effectif autorisé
    if (orgUnit.authorizedHeadcount !== null && orgUnit.authorizedHeadcount !== undefined && assignedEmployees.length >= orgUnit.authorizedHeadcount) {
      notification.toast.error(`L'effectif autorisé (${orgUnit.authorizedHeadcount}) est déjà atteint.`);
      return;
    }

    try {
      await $assignEmployeeMutation.mutateAsync({
        employeeId: selectedEmployeeId,
        orgUnitId: orgUnit.id
      });
      selectedEmployeeId = null;
      isAdding = false;
    } catch (error) {
      // Erreur déjà gérée par la mutation
    }
  }

  async function handleUnassignRequest(employeeId: string | number) {
    confirmingEmployeeId = employeeId;
  }

  async function handleUnassignConfirm() {
    if (!confirmingEmployeeId) return;
    try {
      await $unassignEmployeeMutation.mutateAsync(String(confirmingEmployeeId));
      confirmingEmployeeId = null;
    } catch (error) {
      notification.toast.error(getFriendlyErrorMessage(error));
      console.error('[EmployeeAssignment] Unassign mutation error:', error);
      confirmingEmployeeId = null;
    }
  }

  function handleUnassignCancel() {
    confirmingEmployeeId = null;
  }
  // --- Helpers for Select ---
  const selectEmployeeId = $derived(selectedEmployeeId ?? '');
  const employeeLabel = $derived(
    selectedEmployeeId
      ? getEmployeeById(selectedEmployeeId)?.name ?? '— Sélectionner un employé'
      : '— Sélectionner un employé'
  );

  function handleEmployeeChange(value: string) {
    selectedEmployeeId = value || null;
  }
</script>


{#snippet EmployeeRow(emp: any)}
  {@const empPalette = getAvatarPalette(emp.name)}
  <div class="group flex items-center justify-between py-2.5 border-b border-slate-100 last:border-0 animate-in slide-in-from-left-3 fade-in duration-200">
    <div class="flex items-center gap-3 min-w-0">
      <Avatar.Root class="h-8 w-8 border border-slate-200 rounded-full shrink-0">
        <Avatar.Image src={emp.avatarUrl} alt={emp.name} />
        <Avatar.Fallback class={cn("text-[0.75rem] font-medium", empPalette.bg, empPalette.text)}>
          {getInitials(...emp.name.split(' '))}
        </Avatar.Fallback>
      </Avatar.Root>
      <div class="min-w-0">
        <span class="text-[0.875rem] font-medium text-slate-900 block truncate">{emp.name}</span>
        <span class="text-[0.82rem] text-slate-500 block truncate">{emp.jobTitle}</span>
      </div>
    </div>

    <ConfirmAction
      isConfirming={confirmingEmployeeId === emp.id}
      onRequest={() => handleUnassignRequest(emp.id)}
      onConfirm={handleUnassignConfirm}
      onCancel={handleUnassignCancel}
      labels={{ action: 'Détacher', confirm: 'Détacher', cancel: 'Annuler' }}
      icons={{ action: 'x', confirm: 'check', cancel: 'x' }}
      variant="danger"
    />
  </div>
{/snippet}


{#snippet AddEmployeeRow()}
  <div class="flex items-center gap-3 py-2.5 border-b border-slate-100 animate-in slide-in-from-top-2 fade-in duration-200">
    <div class="flex-1 min-w-0">
      <Select type="single" value={selectEmployeeId} onValueChange={handleEmployeeChange}>
        <SelectTrigger class="h-9 w-full shadow-fine bg-white border-slate-200 cursor-pointer text-[0.875rem]">
          <span class="truncate text-[0.875rem]">{employeeLabel}</span>
        </SelectTrigger>
        <SelectContent class="z-9999">
          {#each unassignedEmployees as emp}
            <SelectItem value={String(emp.id)}>
              <div class="flex flex-col">
                <span class="font-medium text-[0.88rem]">{emp.name}</span>
                <span class="text-[0.85rem] text-slate-500">{emp.jobTitle}</span>
              </div>
            </SelectItem>
          {:else}
            <div class="p-4 text-center text-slate-500 text-[0.875rem]">
              Tous les employés sont déjà affectés.
            </div>
          {/each}
        </SelectContent>
      </Select>
    </div>
    <div class="flex items-center gap-2">
      <Button
        variant="ghost"
        onclick={() => { isAdding = false; selectedEmployeeId = null; }}
        class="h-8 w-8 hover:bg-slate-100 rounded text-slate-400 hover:text-slate-600"
        title="Annuler"
      >
        <AppIcon name="x" size={16} />
      </Button>
      <Button
        onclick={handleAssign}
        disabled={!selectedEmployeeId || $assignEmployeeMutation.isPending || (orgUnit?.authorizedHeadcount ? assignedEmployees.length >= orgUnit.authorizedHeadcount : false)}
        title={orgUnit?.authorizedHeadcount && assignedEmployees.length >= orgUnit.authorizedHeadcount ? `Effectif autorisé atteint (${orgUnit.authorizedHeadcount}/${orgUnit.authorizedHeadcount})` : ''}
        class="h-8 px-3 bg-primary text-white text-[0.8rem]"
      >
        {#if $assignEmployeeMutation.isPending}
          <AnimateSpin class="border-white size-3 mr-1.5" text="" />
        {:else}
          <AppIcon name="check" size={16} class="mr-1" />
        {/if}
        Affecter
      </Button>
    </div>
  </div>
{/snippet}


{#snippet AssignedListView()}
  <div class="flex flex-col h-full px-6 py-6 gap-3">
    <!-- Header -->
    <div class="flex items-center justify-between shrink-0">
      {#if !isAdding}
        <Button onclick={() => isAdding = true} size="sm" class="h-7 text-[0.875rem]">
          <AppIcon name="plus" size={17} />
          Nouveau
        </Button>
      {:else}
        <span class="text-[0.875rem] text-slate-500 font-medium">Affecter un employé</span>
      {/if}
      <span class="text-[0.875rem] text-slate-500">{assignedEmployees.length} collaborateur{assignedEmployees.length > 1 ? 's' : ''}</span>
    </div>

    <!-- Content area -->
    <div class="flex-1 flex flex-col min-h-0 overflow-y-auto custom-scrollbar">
      {#if $allEmployeesQuery.isLoading}
        <div class="flex-1 flex items-center justify-center">
          <div class="text-center">
            <AnimateSpin class="border-primary size-5 mx-auto mb-3" text="Chargement des employées" />
          </div>
        </div>
      {:else if isAdding}
        {@render AddEmployeeRow()}
        {#if assignedEmployees.length > 0}
          <div class="mt-3 border-t border-slate-100 pt-3">
            {#each assignedEmployees as emp, index (emp.id)}
              <div style="animation-delay: {index * 50}ms" class="animate-in slide-in-from-left-2 fade-in fill-mode-backwards duration-300">
                {@render EmployeeRow(emp)}
              </div>
            {/each}
          </div>
        {/if}
      {:else if assignedEmployees.length > 0}
        {#each assignedEmployees as emp, index (emp.id)}
          <div style="animation-delay: {index * 50}ms" class="animate-in slide-in-from-left-2 fade-in fill-mode-backwards duration-300">
            {@render EmployeeRow(emp)}
          </div>
        {/each}
      {:else}
        <div class="flex-1 flex flex-col items-center justify-center text-center animate-in zoom-in-95 fade-in duration-300">
          <div class="w-12 h-12 rounded-full bg-slate-100 flex items-center justify-center mb-3">
            <AppIcon name="users" size={20} class="text-slate-400" />
          </div>
          <p class="text-[0.875rem] text-slate-600 font-medium">Aucun collaborateur</p>
          <p class="text-[0.85rem] text-slate-400 mt-1">Affectez des employés à cette unité</p>
        </div>
      {/if}
    </div>
  </div>
{/snippet}


{#snippet FooterActions()}
  {#if activeTab === 'leadership'}
    <Sheet.Close class="flex-1">
      <Button variant="outline" class="w-full h-9 text-slate-900 border-slate-200 shadow-fine">
        <AppIcon name="x" size={17} class="text-slate-300" />
        Fermer
      </Button>
    </Sheet.Close>
    <Button
      onclick={async () => {
        if (!orgUnit) return;
        
        // Validation Zod
        validationErrors = {};
        const result = leadershipSchema.safeParse({ managerId: formManagerId });
        if (!result.success) {
          result.error.issues.forEach((err: z.core.$ZodIssue) => {
            validationErrors = { ...validationErrors, [String(err.path[0])]: err.message };
          });
          return;
        }
        
        try {
          await $updateOrgUnitMutation.mutateAsync({
            id: orgUnit.id,
            data: {
              managerId: formManagerId,
              affointId: formAffointId ?? ''  // "" pour supprimer l'adjoint
            }
          });
          validationErrors = {}; // Effacer les erreurs après succès
        } catch (error) {
          // Erreur déjà gérée par la mutation
        }
      }}
      disabled={$updateOrgUnitMutation.isPending || !formManagerId}
      class="flex-1 bg-primary text-white shadow-fine h-9"
    >
      {#if $updateOrgUnitMutation.isPending}
        <AnimateSpin class="border-white size-3" text="" />
      {:else}
        <AppIcon name="check" size={17} class="mr-2" />
      {/if}
      Enregistrer
    </Button>
  {:else}
    <Sheet.Close class="w-full">
      <Button variant="outline" class="w-full h-9 text-slate-900 border-slate-200 shadow-fine">
        <AppIcon name="x" size={17} class="text-slate-300" />
        Fermer
      </Button>
    </Sheet.Close>
  {/if}
{/snippet}


{#snippet LeadershipView()}
  <div class="px-6 py-6 space-y-6">
    <!-- Manager Section -->
    <div class="space-y-3">
      <div class="flex items-center gap-2">
        <AppIcon name="user-cog" size={18} class="text-primary" />
        <h3 class="font-medium text-slate-800 text-[0.875rem]">Responsable (Manager)</h3>
      </div>
      
      <Select type="single" value={formManagerId ?? ''} onValueChange={(v) => { 
        formManagerId = v || null; 
        // Valider immédiatement pour feedback instantané
        const result = leadershipSchema.safeParse({ managerId: v || null });
        if (!result.success) {
          validationErrors = { managerId: result.error.issues[0]?.message || 'Erreur' };
        } else {
          clearValidationError('managerId');
        }
      }}>
        <SelectTrigger class="h-10 w-full shadow-fine bg-white border-slate-200 cursor-pointer">
          <span class="truncate text-sm">
            {formManagerId ? formatEmployeeName(getEmployeeById(formManagerId)) : '— Aucun manager'}
          </span>
        </SelectTrigger>
        <SelectContent class="z-9999">
          <SelectItem value="">— Aucun</SelectItem>
          {#each allEmployees as emp (emp.id)}
            <SelectItem value={String(emp.id)}>
              <div class="flex flex-col">
                <span class="font-medium text-[0.88rem]">{emp.name}</span>
                <span class="text-[0.85rem] text-slate-500">{emp.jobTitle}</span>
              </div>
            </SelectItem>
          {/each}
        </SelectContent>
      </Select>
      <ValidationError errors={validationErrors} field="managerId" />
      
      {#if formManagerId}
        {@const manager = getEmployeeById(formManagerId)}
        {@const managerPalette = manager ? getAvatarPalette(manager.name) : null}
        {#if manager}
          <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
            <Avatar.Root class="h-10 w-10 border border-slate-200 rounded-full shrink-0">
              <Avatar.Image src={manager.avatarUrl} alt={manager.name} />
              <Avatar.Fallback class={cn("text-[0.85rem] font-medium", managerPalette?.bg, managerPalette?.text)}>
                {getInitials(...manager.name.split(' '))}
              </Avatar.Fallback>
            </Avatar.Root>
            <div class="flex-1 min-w-0">
              <span class="text-[0.9rem] font-bold text-slate-900 block truncate">{manager.name}</span>
              <span class="text-[0.82rem] text-slate-500 block truncate">{manager.jobTitle}</span>
            </div>
          </div>
        {/if}
      {/if}
    </div>

    <!-- Adjoint Section -->
    <div class="space-y-3 pt-4 border-t border-slate-100">
      <div class="flex items-center gap-2">
        <AppIcon name="user-check" size={18} class="text-primary" />
        <h3 class="font-medium text-slate-800 text-[0.875rem]">Adjoint</h3>
      </div>
      <Select type="single" value={formAffointId ?? ""} onValueChange={(v) => formAffointId = v || null}>
        <SelectTrigger class="h-10 w-full shadow-fine bg-white border-slate-200 cursor-pointer">
          <span class="truncate text-sm">
            {formAffointId ? formatEmployeeName(getEmployeeById(formAffointId)) : '— Aucun adjoint'}
          </span>
        </SelectTrigger>
        <SelectContent class="z-9999">
          <SelectItem value="">— Aucun</SelectItem>
          {#each allEmployees as emp (emp.id)}
            <SelectItem value={String(emp.id)}>
              <div class="flex flex-col">
                <span class="font-medium text-[0.88rem]">{emp.name}</span>
                <span class="text-[0.85rem] text-slate-500">{emp.jobTitle}</span>
              </div>
            </SelectItem>
          {/each}
        </SelectContent>
      </Select>
      
      {#if formAffointId}
        {@const affoint = getEmployeeById(formAffointId)}
        {@const affointPalette = affoint ? getAvatarPalette(affoint.name) : null}
        {#if affoint}
          <div class="flex items-center gap-3 p-3 bg-slate-50 rounded-lg border border-slate-100">
            <Avatar.Root class="h-10 w-10 border border-slate-200 rounded-full shrink-0">
              <Avatar.Image src={affoint.avatarUrl} alt={affoint.name} />
              <Avatar.Fallback class={cn("text-[0.85rem] font-medium", affointPalette?.bg, affointPalette?.text)}>
                {getInitials(...affoint.name.split(' '))}
              </Avatar.Fallback>
            </Avatar.Root>
            <div class="flex-1 min-w-0">
              <span class="text-[0.9rem] font-bold text-slate-900 block truncate">{affoint.name}</span>
              <span class="text-[0.82rem] text-slate-500 block truncate">{affoint.jobTitle}</span>
            </div>
          </div>
        {/if}
      {/if}
    </div>
  </div>
{/snippet}


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl flex flex-col h-full overflow-hidden p-0 bg-white shadow-2xl">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex flex-col items-start justify-start">
        <Sheet.Title class="text-[1rem] font-bold text-slate-900">
          Gérer les affectations
        </Sheet.Title>
        <Badge variant="outline" class="bg-white text-slate-600 py-0 border-slate-200 rounded-full font-medium text-[0.85rem]">
          {orgUnit?.name}
        </Badge>
      </div>
    </Sheet.Header>

    <!-- Tabs -->
    <div class="px-6 pt-0 pb-3 flex justify-center border-b border-slate-100">
      <div class="relative inline-grid grid-cols-2 bg-slate-100 rounded-lg p-1 w-56 overflow-hidden">
        <!-- Sliding indicator -->
        <div class="absolute top-0.5 bottom-0.5 left-0.5 right-0.5 grid grid-cols-2 pointer-events-none">
          <div
            class={cn(
              "bg-white rounded-md shadow-sm border border-slate-200 transition-transform duration-300 ease-[cubic-bezier(0.22,1,0.36,1)]",
              activeTab === 'leadership' && "translate-x-full"
            )}
          ></div>
        </div>

        <!-- Membres Tab -->
        <button
          onclick={() => activeTab = 'members'}
          class={cn(
            "relative z-10 flex items-center justify-center gap-0.5 px-3 py-1.5 text-[0.82rem] font-medium transition-colors cursor-pointer",
            activeTab === 'members' ? "text-primary" : "text-slate-600 hover:text-slate-800"
          )}
        >
          <AppIcon
            name="users"
            size={17}
            strokeWidth={activeTab === 'members' ? 2 : 1.5}
            class={activeTab === 'members' ? "text-primary" : "text-slate-500"}
          />
          <span class="text-[0.82rem]">Membres</span>
          <span class="text-[0.82rem]">({assignedEmployees.length})</span>
        </button>

        <!-- Direction Tab -->
        <button
          onclick={() => activeTab = 'leadership'}
          class={cn(
            "relative z-10 flex items-center justify-center gap-2 px-3 py-1.5 text-[0.82rem] font-medium transition-colors cursor-pointer",
            activeTab === 'leadership' ? "text-primary" : "text-slate-600 hover:text-slate-800"
          )}
        >
          <AppIcon
            name="shield"
            size={17}
            strokeWidth={activeTab === 'leadership' ? 2 : 1.5}
            class={activeTab === 'leadership' ? "text-primary" : "text-slate-500"}
          />
          Direction
        </button>
      </div>
    </div>

    <div class="flex-1 overflow-hidden">
      {#if activeTab === 'members'}
        <div class="h-full animate-in fade-in slide-in-from-left-2 duration-200">
          {@render AssignedListView()}
        </div>
      {:else}
        <div class="h-full overflow-y-auto custom-scrollbar animate-in fade-in slide-in-from-right-2 duration-200">
          {@render LeadershipView()}
        </div>
      {/if}
    </div>

    <Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      {@render FooterActions()}
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




