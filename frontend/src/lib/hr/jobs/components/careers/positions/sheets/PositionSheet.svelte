<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { jobsStore } from "../../../../stores/jobs.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import type { JobPosition, SeniorityLevel, JobFamily } from "../../../../types/types";
  import { SENIORITY_LABELS } from "../../../../types/types";
  import { fade, slide } from "svelte/transition";
  import { useJobFamiliesQuery } from "../../../../queries/jobQueries";
  import ConfirmAction from "@/components/shared/actions/ConfirmAction.svelte";
  import ValidationError from "@/components/ui/validation-error";
  import { cn } from "@/utilities/common/css";
  import { payrollConfigStore } from "@/hr/payroll/stores/configuration/payrollConfigStore.svelte";
  import { CURRENCIES } from "@/constants/finance";
  import { fromCDF, formatCurrency, setExchangeRate } from "@/utilities/common/currency";
  import { preventNonNumeric } from "@/utilities/common/number";
  import CurrencyToggle from "@/components/ui/currency-toggle";
  import { ORG_UNIT_ICONS } from "../../../../constants/orgUnit.constants";
  

  let { 
    open = $bindable(false),
    position = $bindable(null),
    prefilledOrgUnitId = '',
    onSave,
    onCreateJobFamily,
    onUpdateJobFamily,
    onDeleteJobFamily
  } = $props<{ 
    open: boolean, 
    position?: JobPosition | null,
    prefilledOrgUnitId?: string,
    onSave?: (data: any, positionId?: string) => Promise<any>,
    onCreateJobFamily?: (name: string, description?: string) => Promise<any>,
    onUpdateJobFamily?: (id: string, name: string, description?: string) => Promise<any>,
    onDeleteJobFamily?: (id: string, name: string) => void
  }>();

  // --- Form state ---
  let formTitle = $state('');
  let formFamilyName = $state('');
  let formOrgUnitId = $state('');
  let formSeniorityLevels = $state<{
    seniority_level: SeniorityLevel;
    salary_min: number;
    salary_max: number;
    echelon: number | null;
    rank: number;
    is_active: boolean;
  }[]>([]);

  let formRequirements = $state<string[]>([]);
  let formSkills = $state<{ name: string; level: number }[]>([]);
  let isEditing = $state(false);
  let isSaving = $state(false);

  // --- Validation state ---
  let validationErrors = $state<Record<string, string>>({});

  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function validateForm(): boolean {
    validationErrors = {};
    
    // Basic validation
    if (!formTitle.trim()) {
      validationErrors.title = 'L\'intitulé du poste est requis';
    }
    
    if (!formFamilyName.trim()) {
      validationErrors.familyName = 'La famille de métier est requise';
    }
    
    // Seniority levels validation
    if (formSeniorityLevels.length === 0) {
      validationErrors.seniorityLevels = 'Au moins un niveau de séniorité est requis';
    } else {
      // Check for duplicate seniority levels
      const levelCodes = formSeniorityLevels.map(l => l.seniority_level);
      const uniqueLevels = new Set(levelCodes);
      if (levelCodes.length !== uniqueLevels.size) {
        validationErrors.seniorityLevels = 'Les niveaux de séniorité doivent être uniques';
      }
      
      // Validate salary ranges
      formSeniorityLevels.forEach((level, index) => {
        if (level.salary_min <= 0 || level.salary_max <= 0) {
          validationErrors[`seniority_${index}_salary`] = 'Les salaires doivent être positifs';
        }
        if (level.salary_min > level.salary_max) {
          validationErrors[`seniority_${index}_salary`] = 'Le minimum ne peut pas dépasser le maximum';
        }
      });
    }
    
    return Object.keys(validationErrors).length === 0;
  }

  // --- JobFamily management state ---
  let showFamilyManager = $state(false);
  let newFamilyName = $state('');
  let newFamilyDesc = $state('');
  let editingFamilyId = $state<string | null>(null);
  let editingFamilyName = $state('');
  let editingFamilyDesc = $state('');
  let deletingFamilyId = $state<string | null>(null); // For ConfirmAction
  let deletingSeniorityLevelIndex = $state<number | null>(null); // For ConfirmAction
  let isCreatingFamily = $state(false); // Loading state for create

  // --- Queries ---
  const jobFamiliesQuery = useJobFamiliesQuery();

  // UI state for adding new items
  let newReq = $state('');
  let newSkill = $state('');

  // Reset validation errors when modal opens
  $effect(() => {
    if (open) {
      validationErrors = {};
    }
  });

  // Sync when position is passed for editing
  $effect(() => {
    if (position) {
      isEditing = true;
      formTitle = position.name || '';
      formFamilyName = position.job_family?.name || '';
      formOrgUnitId = position.org_unit?.id || prefilledOrgUnitId || '';
      
      // Convert seniority_levels to form format
      if (position.seniority_levels && position.seniority_levels.length > 0) {
        formSeniorityLevels = position.seniority_levels.map((sl: any) => ({
          seniority_level: sl.seniority_level.level,
          salary_min: sl.salary_min,
          salary_max: sl.salary_max,
          echelon: sl.echelon ?? null,
          rank: sl.rank,
          is_active: sl.is_active
        }));
      } else {
        // Start with empty list for new positions
        formSeniorityLevels = [];
      }
      
      formRequirements = [...(position.requirements || [])];
      formSkills = [...(position.skills || [])];
    } else {
      isEditing = false;
      formTitle = '';
      formFamilyName = '';
      formOrgUnitId = prefilledOrgUnitId || '';
      formSeniorityLevels = [];
      formRequirements = [];
      formSkills = [];
    }
  });

  // --- Seniority Levels Management ---
  let showAddForm = $state(false);
  let newLevelForm = $state({
    seniority_level: 'TRAINEE' as SeniorityLevel,
    salary_min: 0,
    salary_max: 0,
    echelon: null as number | null,
    rank: 1
  });

  function addSeniorityLevel() {
    showAddForm = true;
    // Calculate next rank
    const maxRank = Math.max(...formSeniorityLevels.map(l => l.rank), 0);
    newLevelForm = {
      seniority_level: 'TRAINEE' as SeniorityLevel,
      salary_min: 0,
      salary_max: 0,
      echelon: null,
      rank: maxRank + 1
    };
  }

  function confirmAddLevel() {
    if (newLevelForm.salary_min <= 0 || newLevelForm.salary_max <= 0) {
      validationErrors[`new_level_salary`] = 'Les salaires doivent être positifs';
      return;
    }

    // Check if seniority level already exists
    const existingLevel = formSeniorityLevels.find(level => level.seniority_level === newLevelForm.seniority_level);
    if (existingLevel) {
      validationErrors[`new_level_salary`] = `Le niveau ${newLevelForm.seniority_level} existe déjà`;
      return;
    }
    if (newLevelForm.salary_min > newLevelForm.salary_max) {
      validationErrors[`new_level_salary`] = 'Le minimum ne peut pas dépasser le maximum';
      return;
    }

    formSeniorityLevels = [...formSeniorityLevels, { ...newLevelForm, is_active: true }];
    showAddForm = false;
    validationErrors = { ...validationErrors, new_level_salary: '' };
  }

  function cancelAddLevel() {
    showAddForm = false;
    validationErrors = { ...validationErrors, new_level_salary: '' };
  }
  
  function removeSeniorityLevel(index: number) {
    formSeniorityLevels = formSeniorityLevels.filter((_, i) => i !== index);
    // Re-rank remaining levels
    formSeniorityLevels = formSeniorityLevels.map((level, i) => ({
      ...level,
      rank: i + 1
    }));
  }
  
  function moveSeniorityLevel(index: number, direction: 'up' | 'down') {
    if (
      (direction === 'up' && index === 0) || 
      (direction === 'down' && index === formSeniorityLevels.length - 1)
    ) {
      return;
    }
    
    const newLevels = [...formSeniorityLevels];
    const targetIndex = direction === 'up' ? index - 1 : index + 1;
    
    // Swap levels
    [newLevels[index], newLevels[targetIndex]] = [newLevels[targetIndex], newLevels[index]];
    
    // Update ranks
    newLevels.forEach((level, i) => {
      level.rank = i + 1;
    });
    
    formSeniorityLevels = newLevels;
  }

  function addSkill() {
    const val = newSkill.trim();
    if (val && !formSkills.find(s => s.name.toLowerCase() === val.toLowerCase())) {
      formSkills = [...formSkills, { name: val, level: 3 }];
      newSkill = '';
    }
  }

  function addRequirement() {
    const val = newReq.trim();
    if (val && !formRequirements.includes(val)) {
      formRequirements = [...formRequirements, val];
      newReq = '';
    }
  }

  function removeRequirement(req: string) {
    formRequirements = formRequirements.filter(r => r !== req);
  }

  function removeSkill(name: string) {
    formSkills = formSkills.filter(s => s.name !== name);
  }

  async function handleSave() {
    // Validation
    if (!validateForm()) {
      return;
    }

    const data = {
      title: formTitle.trim(),
      familyName: formFamilyName.trim() || (position?.job_family?.name),
      orgUnitId: formOrgUnitId,
      seniority_levels: formSeniorityLevels.map(level => ({
        seniority_level: level.seniority_level,
        salary_min: level.salary_min,
        salary_max: level.salary_max,
        echelon: level.echelon,
        rank: level.rank,
        is_active: level.is_active
      })),
      requirements: formRequirements,
      skills: formSkills
    };

    isSaving = true;
    try {
      if (onSave) {
        await onSave(data, position?.id);
        open = false;
      }
    } catch (error) {
      // Error handled by mutation
    } finally {
      isSaving = false;
    }
  }

  // --- JobFamily Management Functions ---
  async function handleCreateFamily() {
    if (!newFamilyName.trim() || !onCreateJobFamily || isCreatingFamily) return;
    isCreatingFamily = true;
    try {
      await onCreateJobFamily(newFamilyName.trim(), newFamilyDesc.trim() || undefined);
      newFamilyName = '';
      newFamilyDesc = '';
    } finally {
      isCreatingFamily = false;
    }
  }

  async function handleUpdateFamily(family: JobFamily) {
    if (!editingFamilyName.trim() || !onUpdateJobFamily) return;
    await onUpdateJobFamily(family.id, editingFamilyName.trim(), editingFamilyDesc.trim() || undefined);
    editingFamilyId = null;
    editingFamilyName = '';
    editingFamilyDesc = '';
  }

  function startEditFamily(family: JobFamily) {
    editingFamilyId = family.id;
    editingFamilyName = family.name;
    editingFamilyDesc = family.description || '';
  }

  function cancelEditFamily() {
    editingFamilyId = null;
    editingFamilyName = '';
    editingFamilyDesc = '';
  }

  function selectFamilyForPosition(familyName: string) {
    formFamilyName = familyName;
  }

  const selectedOrgUnit = $derived(jobsStore.getOrgUnitById(formOrgUnitId));
  
  // --- Currency ---
  const currency = $derived(payrollConfigStore.configuration?.currency ?? 'CDF');
  const currencySymbol = $derived(currency === CURRENCIES.USD ? '$' : 'FC');
  const exchangeRate = $derived(payrollConfigStore.configuration?.exchange_rate_usd_cdf ?? payrollConfigStore.exchangeRate ?? 2850);

  // Helper function to get salary display for existing levels
  function getSalaryDisplay(salary: number) {
    return salary > 0 
      ? formatCurrency(fromCDF(salary, currency), currency) 
      : '0';
  }

  // Sync exchange rate globally when it changes
  $effect(() => {
    setExchangeRate(exchangeRate);
  });
  
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-142 bg-white p-0 flex flex-col h-full overflow-hidden">
    
    <!-- Header -->
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="flex items-center gap-3">
        <div class="space-y-0.5 min-w-0">
          <Sheet.Title class="text-[1rem] text-slate-900 truncate font-bold">
            {position ? 'Modifier le poste' : 'Nouveau poste'}
          </Sheet.Title>
        </div>
        <!-- Currency Toggle -->
        <CurrencyToggle
          currency={currency === 'CDF' ? 'CDF' : 'USD'}
          onChange={(c) => payrollConfigStore.saveConfiguration({ currency: c })}
          size="sm"
        />
      </div>
    </Sheet.Header>

    <!-- Form Content -->
    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-6 space-y-7" in:fade={{ duration: 200 }}>
        <!-- Intitulé -->
        <div class="space-y-2.5">
          <Label for="pos-title" class="text-slate-900">
            Intitulé du poste <span class="text-red-500">*</span>
          </Label>
          <Input 
            id="pos-title" 
            bind:value={formTitle} 
            placeholder="ex: Comptable" 
            oninput={() => clearValidationError('title')}
            class={cn(
              "h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine",
              validationErrors.title && "border-red-500 focus:ring-red-500"
            )}
          />
          <ValidationError errors={validationErrors} field="title" />
        </div>

        <!-- Famille de métier -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">
            Famille de métier <span class="text-red-500">*</span>
          </Label>
          <Select
            type="single"
            value={formFamilyName}
            onValueChange={(v) => {
              formFamilyName = v;
              clearValidationError('familyName');
            }}
          >
            <SelectTrigger class={cn(
              "h-9 w-full bg-white border-slate-200 shadow-fine rounded-md cursor-pointer",
              validationErrors.familyName && "border-red-500"
            )}>
              <span class="truncate text-[0.87rem] font-medium">
                {formFamilyName || 'Choisir une famille...'}
              </span>
            </SelectTrigger>
            <SelectContent class="z-9999">
              {#each jobsStore.jobFamilies as family}
                <SelectItem value={family.name} class="text-[0.87rem]">
                  {family.name}
                  {#if family.description}
                    <span class="text-slate-400 text-[0.87rem]">- {family.description}</span>
                  {/if}
                </SelectItem>
              {:else}
                <div class="px-3 py-2 text-[0.85rem] text-slate-400 flex items-center justify-center gap-1.5">
                  <AppIcon name="circle-x" size={17} />
                  Aucune famille disponible. Créez-en une ci-dessous.
                </div>
              {/each}
            </SelectContent>
          </Select>
          <ValidationError errors={validationErrors} field="familyName" />
          <p class="text-[0.85rem] text-slate-500">La famille regroupe les postes similaires (ex: tous les postes "Comptable")</p>
        </div>

        <!-- Gestion des Familles de métiers -->
        <div class="space-y-3 pt-2 border-t border-slate-100">
          <button
            type="button"
            onclick={() => showFamilyManager = !showFamilyManager}
            class="flex items-center gap-2 text-[0.9rem] font-medium text-slate-700 hover:text-primary transition-colors cursor-pointer"
          >
            <AppIcon name={showFamilyManager ? 'chevron-down' : 'chevron-right'} size={18} />
            Gérer les familles de métiers
            {#if jobsStore.jobFamilies.length}
              <span class="text-[0.85rem] text-slate-400">({jobsStore.jobFamilies.length})</span>
            {/if}
          </button>

          {#if showFamilyManager}
            <div class="space-y-3 p-4 rounded-xl bg-slate-50/50 border border-slate-100" in:slide={{ duration: 200 }}>
              <!-- Create new family -->
              <div class="space-y-2" in:fade={{ duration: 200, delay: 50 }}>
                <Label class="text-[0.85rem] font-medium text-slate-600">Nouvelle famille</Label>
                <div class="flex gap-2 flex-col">
                  <Input
                    placeholder="Nom de la famille..."
                    bind:value={newFamilyName}
                    class="h-9 text-[0.85rem] bg-white shadow-fine"
                  />
                  <Input
                    placeholder="Description (optionnel)"
                    bind:value={newFamilyDesc}
                    class="h-9 text-[0.85rem] bg-white shadow-fine"
                  />
                </div>
                <Button
                  type="button"
                  variant="secondary"
                  onclick={handleCreateFamily}
                  disabled={!newFamilyName.trim() || isCreatingFamily}
                  class="h-7.5 px-3 transition-all w-full pt-1"
                >
                  {#if isCreatingFamily}
                    <AnimateSpin class="size-3" text="" />
                  {:else}
                    <AppIcon name="plus" size={16} />
                  {/if}
                  Ajouter une famille
                </Button>
              </div>

              <!-- List existing families -->
              {#if $jobFamiliesQuery.isLoading}
                <div in:fade={{ duration: 200 }}>
                  <AnimateSpin text="Chargement des familles de métiers" />
                </div>
              {:else if jobsStore.jobFamilies.length}
                <div class="space-y-1 max-h-40 overflow-y-auto" in:fade={{ duration: 250, delay: 100 }}>
                  {#each jobsStore.jobFamilies as family, i}
                    <div
                      class="flex items-center gap-2 p-2 rounded-lg bg-white border border-slate-100 group"
                      in:slide={{ duration: 200, delay: i * 30 }}
                    >
                      {#if editingFamilyId === family.id}
                        <Input
                          bind:value={editingFamilyName}
                          class="h-7 text-[0.85rem] flex-1"
                          onkeydown={(e) => e.key === 'Enter' && handleUpdateFamily(family)}
                        />
                        <Input
                          bind:value={editingFamilyDesc}
                          placeholder="Description"
                          class="h-7 text-[0.85rem] flex-1"
                        />
                        <button
                          onclick={() => handleUpdateFamily(family)}
                          onmousedown={(e) => e.preventDefault()}
                          class="p-1 text-emerald-600 hover:bg-emerald-50 rounded cursor-pointer"
                        >
                          <AppIcon name="check" size={17} />
                        </button>
                        <button
                          onclick={cancelEditFamily}
                          onmousedown={(e) => e.preventDefault()}
                          class="p-1 text-slate-400 hover:bg-slate-100 rounded cursor-pointer"
                        >
                          <AppIcon name="x" size={17} />
                        </button>
                      {:else}
                        <button
                          onclick={() => selectFamilyForPosition(family.name)}
                          class="flex-1 text-left text-[0.875rem] font-medium text-slate-700 hover:text-primary transition-colors"
                          class:text-primary={formFamilyName === family.name}
                        >
                          {family.name}
                          {#if family.description}
                            <span class="text-slate-400 font-normal text-[0.87rem]">- {family.description}</span>
                          {/if}
                        </button>
                        <div class="flex gap-1" onmousedown={(e) => e.preventDefault()} role="none">
                          <button
                            onclick={(e) => { e.stopPropagation(); startEditFamily(family); }}
                            class="p-1 text-slate-700 hover:text-indigo-600 hover:bg-blue-50 rounded cursor-pointer"
                          >
                            <AppIcon name="edit" size={16} />
                          </button>
                          <ConfirmAction
                            isConfirming={deletingFamilyId === family.id}
                            onRequest={() => deletingFamilyId = family.id}
                            onConfirm={() => {
                              onDeleteJobFamily?.(family.id, family.name);
                              deletingFamilyId = null;
                            }}
                            onCancel={() => deletingFamilyId = null}
                            labels={{ action: '', confirm: '', cancel: '' }}
                            icons={{ action: 'trash', confirm: 'check', cancel: 'x' }}
                            variant="danger"
                          />
                        </div>
                      {/if}
                    </div>
                  {/each}
                </div>
              {:else}
                <div
                  class="text-[0.85rem] text-slate-400 flex justify-center items-center gap-1.5 py-4"
                  in:fade={{ duration: 200 }}
                >
                  <AppIcon name="circle-x" size={17} />
                  Aucune famille de métiers définie.
                </div>
              {/if}

              <p class="text-[0.85rem] text-slate-400" in:fade={{ duration: 200, delay: 200 }}>
                Cliquez sur une famille pour la sélectionner pour ce poste.
              </p>
            </div>
          {/if}
        </div>

        <!-- Unité organisationnelle -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Unité organisationnelle</Label>
          <Select 
            type="single" 
            value={formOrgUnitId} 
            onValueChange={(v) => {
              formOrgUnitId = v;
              clearValidationError('orgUnitId');
            }}
          >
            <SelectTrigger class={cn(
              "h-10 w-full bg-white border-slate-200 shadow-fine rounded-md cursor-pointer",
              validationErrors.orgUnitId && "border-red-500"
            )}>
              <span class="truncate text-[0.87rem] font-medium">
                {selectedOrgUnit?.name || 'Choisir une unité...'}
              </span>
            </SelectTrigger>
            <SelectContent class="z-9999">
              {#each jobsStore.orgUnits as orgUnit}
                <SelectItem value={orgUnit.id} class="text-[0.87rem]">
                  <AppIcon name={ORG_UNIT_ICONS[orgUnit.type] ?? 'business'} size={18} class="text-slate-500 shrink-0" />
                  {orgUnit.name}
                </SelectItem>
              {/each}
            </SelectContent>
          </Select>
          <ValidationError errors={validationErrors} field="orgUnitId" />
        </div>

        <!-- Niveaux de séniorité -->
        <div class="space-y-4">
          <!-- Header -->
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2">
              <Label class="text-slate-900 font-medium text-[0.95rem]">Niveaux de séniorité</Label>
              <span class="text-red-500">*</span>
              <span class="text-slate-400 text-[0.86rem]">
                ({formSeniorityLevels.length} défini{formSeniorityLevels.length > 1 ? 's' : ''})
              </span>
            </div>

            {#if showAddForm}
              <div class="flex items-center gap-2">
                <Button variant="ghost" onclick={cancelAddLevel} class="h-8 px-3 text-[0.85rem] text-slate-600 hover:bg-slate-100 cursor-pointer">
                  <AppIcon name="x" size={16} class="text-slate-300" /> 
                  Annuler
                </Button>
                <Button variant="default" onclick={() => { confirmAddLevel(); clearValidationError('seniorityLevels');}} class="h-8 px-3 text-[0.85rem] cursor-pointer">
                  <AppIcon name="check" size={16} /> 
                  Ajouter
                </Button>
              </div>
            {:else}
              <Button variant="outline" onclick={addSeniorityLevel} class="h-8 px-3 text-[0.85rem] border-slate-200 cursor-pointer">
                <AppIcon name="plus" size={16} class="mr-1.5" /> 
                Ajouter un niveau
              </Button>
            {/if}
          </div>

          <ValidationError errors={validationErrors} field="seniorityLevels" />

          <!-- Formulaire d'ajout -->
          {#if showAddForm}
            <div class="rounded-xl border border-slate-200 bg-white overflow-hidden" transition:slide={{ duration: 300 }}>
              <div class="p-2 space-y-4">
                <div class="grid grid-cols-2 gap-4">
                  <div class="space-y-2">
                    <Label class="text-[0.85rem] font-medium">Niveau de séniorité</Label>
                    <div class="flex gap-2">
                      <span class="text-[0.85rem] font-medium text-slate-600 bg-slate-100 px-2 py-1 rounded-lg border border-slate-200 shrink-0">
                        Niveau {newLevelForm.rank}
                      </span>
                      <Select type="single" bind:value={newLevelForm.seniority_level}>
                        <SelectTrigger class="h-8! w-full bg-white border-slate-200 cursor-pointer text-[0.85rem]">
                          {SENIORITY_LABELS[newLevelForm.seniority_level as keyof typeof SENIORITY_LABELS]}
                        </SelectTrigger>
                        <SelectContent class="z-9999">
                          {#each Object.entries(SENIORITY_LABELS) as [levelCode, label]}
                            {@const isDisabled = formSeniorityLevels.some(l => l.seniority_level === levelCode)}
                            <SelectItem value={levelCode} disabled={isDisabled}>
                              <span class="flex items-center gap-2 text-[0.876rem] {isDisabled ? 'opacity-50' : ''}">
                                <span class="font-medium text-[0.876rem]">{levelCode}</span> - {label}
                                {#if isDisabled}<span class="text-xs text-red-500 ml-auto">(déjà utilisé)</span>{/if}
                              </span>
                            </SelectItem>
                          {/each}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div class="space-y-2">
                    <Label class="text-[0.85rem] font-medium">Échelon (1-4)</Label>
                    <Select
                      type="single"
                      value={newLevelForm.echelon != null ? String(newLevelForm.echelon) : ''}
                      onValueChange={(v) => (newLevelForm.echelon = v ? Number(v) : null)}
                    >
                      <SelectTrigger class="h-8! w-full bg-white border-slate-200 cursor-pointer text-[0.85rem]">
                        {newLevelForm.echelon != null ? `Éch. ${newLevelForm.echelon}` : '—'}
                      </SelectTrigger>
                      <SelectContent class="z-9999">
                        <SelectItem value="" class="text-[0.85rem] text-slate-400">—</SelectItem>
                        {#each [1, 2, 3, 4] as e}
                          <SelectItem value={String(e)} class="text-[0.85rem]">Éch. {e}</SelectItem>
                        {/each}
                      </SelectContent>
                    </Select>
                  </div>

                  <div class="space-y-2">
                    <Label class="text-[0.85rem] font-medium">Fourchette salariale ({currencySymbol})</Label>
                    <div class="grid grid-cols-2 gap-2">
                      <Input type="number" onkeydown={preventNonNumeric} bind:value={newLevelForm.salary_min} placeholder="Min" class="h-8 text-[0.85rem] {validationErrors.new_level_salary ? 'border-red-500' : ''}" />
                      <Input type="number" onkeydown={preventNonNumeric} bind:value={newLevelForm.salary_max} placeholder="Max" class="h-8 text-[0.85rem] {validationErrors.new_level_salary ? 'border-red-500' : ''}" />
                    </div>
                  </div>
                </div>
                <ValidationError errors={validationErrors} field="new_level_salary" />
              </div>
            </div>
          {/if}

          <!-- Liste ou État vide -->
          {#if formSeniorityLevels.length === 0 && !showAddForm}
            <div class="p-8 rounded-xl border border-slate-200 bg-slate-50/30 text-center">
              <div class="flex flex-col items-center gap-3">
                <div class="p-3 rounded-full bg-slate-100"><AppIcon name="layers" size={24} class="text-slate-400" /></div>
                <p class="text-slate-600 text-[0.95rem] font-medium">Aucun niveau défini</p>
                <Button variant="secondary" onclick={addSeniorityLevel} class="h-8 px-4 text-[0.85rem] cursor-pointer">
                  <AppIcon name="plus" size={16} /> 
                  Ajouter le premier niveau
                </Button>
              </div>
            </div>
          {:else}
            <div class="space-y-2">
              {#each formSeniorityLevels as level, index (level.seniority_level)}
                <div class="group relative flex items-center p-3 rounded-lg border border-slate-200 bg-white hover:bg-indigo-50/30 transition-colors" in:slide={{ duration: 200, delay: index * 50 }}>
                  <div class="absolute -top-3 left-2 bg-slate-100 px-2 py-0.5 rounded-full border text-[0.75rem] font-medium text-slate-600">
                    Niveau {level.rank}
                  </div>
                  
                  <div class="w-[15%] flex gap-1">
                    <button onclick={() => moveSeniorityLevel(index, 'up')} disabled={index === 0} class="p-1.5 hover:bg-indigo-100 rounded disabled:opacity-20 cursor-pointer">
                      <AppIcon name="chevron-up" size={16} />
                    </button>
                    <button onclick={() => moveSeniorityLevel(index, 'down')} disabled={index === formSeniorityLevels.length - 1} class="p-1.5 hover:bg-indigo-100 rounded disabled:opacity-20 cursor-pointer">
                      <AppIcon name="chevron-down" size={16} />
                    </button>
                  </div>

                  <div class="flex-1 flex flex-col px-4">
                    <span class="text-[0.85rem] font-semibold text-slate-800">
                      {SENIORITY_LABELS[level.seniority_level]}
                    </span>
                    <span class="text-[0.77rem] text-slate-400">
                      {level.seniority_level}
                      {#if level.echelon != null}
                        <span class="ml-1.5 text-[0.82rem] font-medium text-indigo-600 bg-indigo-50 px-1.5 py-0.5 rounded">Éch. {level.echelon}</span>
                      {/if}
                    </span>:
                  </div>

                  <div class="flex items-center gap-2 text-[0.85rem] font-medium text-slate-700">
                    {getSalaryDisplay(level.salary_min)} <span class="text-slate-300">-</span> {getSalaryDisplay(level.salary_max)}
                  </div>

                  <div class="w-[13%] flex justify-end">
                    <ConfirmAction
                      isConfirming={deletingSeniorityLevelIndex === index}
                      onRequest={() => deletingSeniorityLevelIndex = index}
                      onConfirm={() => { removeSeniorityLevel(index); deletingSeniorityLevelIndex = null; }}
                      onCancel={() => deletingSeniorityLevelIndex = null}
                      labels={{ action: '', confirm: '', cancel: '' }}
                      icons={{ action: 'trash-2', confirm: 'check', cancel: 'x' }}
                      variant="danger"
                    />
                  </div>
                </div>
              {/each}
            </div>
          {/if}
        </div>

        <!-- Exigences (Requirements) -->
        <div class="space-y-3">
          <Label class="text-slate-900 flex items-center gap-2">
            Exigences spécifiques
          </Label>
          <div class="flex gap-2">
            <Input 
              placeholder="Ajouter une exigence (Diplômes, années d'exp...)" 
              bind:value={newReq}
              onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addRequirement())}
              class="h-9 bg-white border-slate-200 shadow-fine focus:bg-white transition-colors"
            />
            <Button variant="secondary" onclick={addRequirement} class="h-9 w-9 p-0 shrink-0">
              <AppIcon name="plus" size={17} />
            </Button>
          </div>
          <div class="flex flex-wrap gap-2 pt-1">
            {#each formRequirements as req}
              <div class="flex items-center gap-2 px-3 py-1 rounded-xl bg-slate-50 border border-slate-100 text-[0.87rem] font-medium text-slate-700 animate-in fade-in scale-in-95 duration-200 group">
                <AppIcon name="circle-check" size={16} class="text-emerald-500" strokeWidth={1.7} />
                {req}
                <button 
                  type="button"
                  onclick={(e) => { e.preventDefault(); e.stopPropagation(); removeRequirement(req); }}
                  class="text-slate-400 hover:text-red-500 transition-colors cursor-pointer"
                >
                  <AppIcon name="x" size={16} />
                </button>
              </div>
            {:else}
              <p class="text-[0.87rem] text-slate-400 flex justify-center items-center gap-1.5 px-2 w-full">
                <AppIcon name="circle-x" size={17} class="text-slate-300" />
                Aucune exigence spécifique définie.
              </p>
            {/each}
          </div>
          <ValidationError errors={validationErrors} field="requirements" />
        </div>

        <!-- Compétences (Skills) -->
        <div class="space-y-3">
          <Label class="text-slate-900 flex items-center gap-2">
            Compétences clés
            <span class="text-[0.87rem] text-slate-400">(Techniques, Soft Skills...)</span>
          </Label>
          <div class="flex gap-2">
            <Input 
              placeholder="ex: React, SQL, Management..." 
              bind:value={newSkill}
              onkeydown={(e) => e.key === 'Enter' && (e.preventDefault(), addSkill())}
              class="h-9 bg-white border-slate-200 shadow-fine focus:bg-white transition-colors"
            />
            <Button variant="secondary" onclick={addSkill} class="h-9 w-9 p-0 shrink-0">
              <AppIcon name="plus" size={17} />
            </Button>
          </div>
          <div class="flex flex-wrap gap-2 pt-1">
            {#each formSkills as skill}
              <div class="flex items-center gap-2 px-3 py-1 rounded-xl bg-blue-50/50 border border-blue-100/50 text-[0.87rem] font-medium text-blue-700 animate-in fade-in scale-in-95 duration-200">
                <AppIcon name="tag" size={16} />
                {skill.name}
                <button 
                  type="button"
                  onclick={(e) => { e.preventDefault(); e.stopPropagation(); removeSkill(skill.name); }}
                  class="text-blue-400 hover:text-red-500 transition-colors ml-1 cursor-pointer"
                >
                  <AppIcon name="x" size={16} />
                </button>
              </div>
            {:else}
              <p class="text-[0.87rem] text-slate-400 flex justify-center items-center gap-1.5 px-2 w-full">
                <AppIcon name="circle-x" size={16} class="text-slate-300" />
                Aucune compétence clé définie.
              </p>
            {/each}
          </div>
          <ValidationError errors={validationErrors} field="skills" />
        </div>

        
        <!-- Info Box -->
        <div class="p-4 rounded-2xl bg-indigo-50/50 border border-indigo-100/50" in:slide={{ duration: 300 }}>
          <div class="flex gap-3">
            <div class="p-1.5 rounded-lg bg-indigo-100 text-indigo-600 shrink-0 h-fit">
              <AppIcon name="info" size={17} />
            </div>
            <p class="text-[0.87rem] leading-relaxed text-slate-600 font-medium">
              Les exigences définies ici s'ajoutent à celles du niveau de séniorité séléctionné.
            </p>
          </div>
        </div>
      </div>
    </div>

    <!-- Footer -->
    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            <AppIcon name="x" size={17} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>
        <Button 
          onclick={handleSave}
          disabled={isSaving}
          class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine text-[0.88rem] hover:opacity-90 transition-all disabled:opacity-50"
        >
          {#if isSaving}
            <AnimateSpin class="border-white size-3" text="" />
          {:else}
            <AppIcon name="check" size={17} />
          {/if}
          Enregistrer
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




