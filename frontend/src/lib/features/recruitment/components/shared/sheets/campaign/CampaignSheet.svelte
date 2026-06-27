<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Textarea } from "@/components/ui/textarea";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import { Switch } from "@/components/ui/switch";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { notification } from "@/stores/notification.svelte";
  import type { RecruitmentCampaign, EvaluationCriterion } from "@/features/recruitment/types/types";
  import { fade } from "svelte/transition";
  import { cn } from "@/utilities/common/css";
  import { preventNonNumeric } from "@/utilities/common/number";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { CAMPAIGN_STATUS_OPTIONS } from "@/features/recruitment/constants/recruitment";
  import { z } from 'zod';
  import { campaignSchema } from "@/features/recruitment/schemas/campaign.schema";
  import ValidationError from "@/components/ui/validation-error";
  import { getFriendlyErrorMessage } from '@/constants/errors';
  import { usePositionsQuery } from "@/features/jobs/queries/jobQueries";
  import { useWorkSitesQuery } from "@/features/admin/settings/queries/workSitesQueries";
  import { useCreateJobOfferMutation, useUpdateJobOfferMutation } from "@/features/recruitment/queries/recruitmentQueries";
  import { useQueryClient } from '@tanstack/svelte-query';
  import { useAllEmployees } from "@/features/employees/queries/employeeQueries";
  import { useAllVacancies } from "@/features/jobs/queries/vacancyQueries";

  
  let {
    open = $bindable(false),
    campaign = $bindable(null)
  } = $props<{
    open: boolean,
    campaign?: RecruitmentCampaign | null
  }>();

  // Form state
  let formTitle = $state('');
  let formJobSlots = $state<Record<string, number>>({}); // positionId -> number of slots
  let formJobNames = $state<string[]>([]);
  let formLocation = $state('');
  let formStatus = $state<'DRAFT' | 'OPEN' | 'PAUSED' | 'CLOSED'>('DRAFT');
  let formDescription = $state('');
  let formEndDate = $state('');
  let formPublishedAt = $state('');
  let formIsPublished = $state(false);
  let formIsActive = $state(true);
  let formEvaluationTemplate = $state<Record<string, EvaluationCriterion[]>>({});
  let expandedEvalPosition = $state<string | null>(null);

  let formMaxApplications = $state<number | undefined>(undefined);
  let formRecruiterId = $state<string>('');
  let formVacancyIds = $state<string[]>([]);
  let isSaving = $state(false);
  let newJobId = $state('');

  // Backend data queries using existing hooks
  const positionsQuery = usePositionsQuery();
  const workSitesQuery = useWorkSitesQuery(() => 1, () => 200);
  const employeesQuery = useAllEmployees();
  const vacanciesQuery = useAllVacancies();

  const positions = $derived($positionsQuery.data || []);
  const workSites = $derived($workSitesQuery.data?.results || []);
  const employees = $derived($employeesQuery.data || []);
  const vacancies = $derived($vacanciesQuery.data?.results || []);
  const isLoadingPositions = $derived($positionsQuery.isLoading);
  const isLoadingWorkSites = $derived($workSitesQuery.isLoading);
  const isLoadingEmployees = $derived($employeesQuery.isLoading);

  // Mutation for creating/updating job offers
  const createJobOfferMutation = useCreateJobOfferMutation();
  const updateJobOfferMutation = useUpdateJobOfferMutation();
  const queryClient = useQueryClient();

  // Selected position data
  const selectedPosition = $derived(formJobNames.length > 0 ? positions.find(p => p.name === formJobNames[0]) : null);

  // Calculate total target hires by summing all position slots
  const calculatedTargetHires = $derived(
    Object.values(formJobSlots).reduce((sum, slots) => sum + slots, 0)
  );

  // Get job IDs from formJobSlots keys
  const formJobIds = $derived(Object.keys(formJobSlots));

  // --- Validation state ---
  let validationErrors = $state<Record<string, string>>({});

  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function syncEvalTemplates() {
  // Add templates for new positions, remove for removed ones
  const currentIds = Object.keys(formJobSlots);
  const newTemplate: Record<string, EvaluationCriterion[]> = {};
  currentIds.forEach(posId => {
    newTemplate[posId] = formEvaluationTemplate[posId] || [];
    ensureEvalTemplate(posId);
  });
}

function updateJobNames() {
    formJobNames = formJobIds
      .map(id => positions.find(p => p.id === id)?.name || '')
      .filter(name => name !== '');
  }

  function handleVacancyToggle(vacancyId: string, vacancyPositionId: string) {
    const index = formVacancyIds.indexOf(vacancyId);
    if (index === -1) {
      // Add vacancy and its position with 1 slot by default
      formVacancyIds = [...formVacancyIds, vacancyId];
      if (!formJobSlots[vacancyPositionId]) {
        formJobSlots = { ...formJobSlots, [vacancyPositionId]: 1 };
        updateJobNames();
      }
    } else {
      // Remove vacancy and its position if not used by other vacancies
      formVacancyIds = formVacancyIds.filter(id => id !== vacancyId);
      const otherVacanciesWithSamePosition = vacancies.filter(
        v => formVacancyIds.includes(v.id) && v.position?.id === vacancyPositionId
      );
      if (otherVacanciesWithSamePosition.length === 0) {
        const newSlots = { ...formJobSlots };
        delete newSlots[vacancyPositionId];
        formJobSlots = newSlots;
        updateJobNames();
      }
    }
  }

  // --- Evaluation template helpers ---
function toggleEvalPosition(posId: string) {
  expandedEvalPosition = expandedEvalPosition === posId ? null : posId;
}

function ensureEvalTemplate(posId: string) {
  if (!formEvaluationTemplate[posId]) {
    const position = positions.find(p => p.id === posId);
    if (!position) return;
    const criteria: EvaluationCriterion[] = [];
    // Add requirements
    (position.requirements || []).forEach((req: string) => {
      criteria.push({ source: 'requirement', name: req, weight: 0 });
    });
    // Add skills
    (position.skills || []).forEach((sk: { name: string; level: number }) => {
      criteria.push({ source: 'skill', name: sk.name, weight: 0 });
    });
    formEvaluationTemplate = { ...formEvaluationTemplate, [posId]: criteria };
  }
}

function toggleCriterion(posId: string, criterionIndex: number) {
  const criteria = [...(formEvaluationTemplate[posId] || [])];
  const item = criteria[criterionIndex];
  if (item.weight > 0) {
    // Uncheck: set weight to 0
    criteria[criterionIndex] = { ...item, weight: 0 };
  } else {
    // Check: give default weight
    criteria[criterionIndex] = { ...item, weight: 1 };
  }
  formEvaluationTemplate = { ...formEvaluationTemplate, [posId]: criteria };
}

function updateCriterionWeight(posId: string, criterionIndex: number, weight: number) {
  const criteria = [...(formEvaluationTemplate[posId] || [])];
  criteria[criterionIndex] = { ...criteria[criterionIndex], weight: Math.max(0, Math.min(100, weight)) };
  formEvaluationTemplate = { ...formEvaluationTemplate, [posId]: criteria };
}

function autoBalance(posId: string) {
  const criteria = (formEvaluationTemplate[posId] || []).filter(c => c.weight > 0);
  if (criteria.length === 0) return;
  const perItem = Math.floor(100 / criteria.length);
  const remainder = 100 - perItem * criteria.length;
  const allCriteria = (formEvaluationTemplate[posId] || []).map(c => {
    if (c.weight > 0) {
      const idx = criteria.indexOf(c);
      return { ...c, weight: perItem + (idx === 0 ? remainder : 0) };
    }
    return c;
  });
  formEvaluationTemplate = { ...formEvaluationTemplate, [posId]: allCriteria };
}

function activeEvalCount(posId: string): number {
  return (formEvaluationTemplate[posId] || []).filter(c => c.weight > 0).length;
}

function activeEvalTotal(posId: string): number {
  return (formEvaluationTemplate[posId] || []).reduce((sum, c) => sum + c.weight, 0);
}

function addPosition() {
    if (newJobId && !formJobSlots[newJobId]) {
      formJobSlots = { ...formJobSlots, [newJobId]: 1 };
      updateJobNames();
      syncEvalTemplates();
      newJobId = '';
    }
  }

  function removePosition(jobId: string) {
    const newSlots = { ...formJobSlots };
    delete newSlots[jobId];
    formJobSlots = newSlots;
    updateJobNames();
    syncEvalTemplates();
  }

  function updatePositionSlots(jobId: string, slots: number) {
    if (slots > 0) {
      formJobSlots = { ...formJobSlots, [jobId]: slots };
    }
  }

  function validateForm(): boolean {
    validationErrors = {};

    const result = campaignSchema.safeParse({
      title: formTitle,
      jobIds: formJobIds.filter(id => id !== ''),
      jobNames: formJobNames.filter(j => j !== ''),
      location: formLocation,
      status: formStatus,
      targetHires: calculatedTargetHires,
      description: formDescription,
      requirements: selectedPosition?.requirements || [],
      closeDate: formEndDate,
      vacancyIds: formVacancyIds,
      maxApplications: (formMaxApplications === null || formMaxApplications === undefined) ? undefined : formMaxApplications,
      recruiterId: formRecruiterId || undefined
    });

    if (!result.success) {
      result.error.issues.forEach((err: z.core.$ZodIssue) => {
        const field = err.path.join('.');
        validationErrors = { ...validationErrors, [field]: err.message };
      });
      console.error('Validation errors:', validationErrors);
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

  $effect(() => {
    if (open) {
      if (campaign) {
        formTitle = campaign.title || '';
        // Convert jobIds to formJobSlots with 1 slot each by default, or use position_slots if available
        if (campaign.positionSlots && Object.keys(campaign.positionSlots).length > 0) {
          formJobSlots = campaign.positionSlots;
        } else {
          formJobSlots = (campaign.jobIds || []).reduce((acc: Record<string, number>, id: string) => ({ ...acc, [id]: 1 }), {});
        }
        formJobNames = campaign.jobNames || [];
        formLocation = campaign.location || '';
        formStatus = campaign.status || 'DRAFT';
        formDescription = campaign.description || '';
        formEndDate = campaign.closeDate ? campaign.closeDate.split('T')[0] : '';
        formPublishedAt = campaign.openDate ? campaign.openDate.split('T')[0] : '';
        formIsPublished = campaign.isPublished || false;
        formIsActive = campaign.isActive !== undefined ? campaign.isActive : true;
        formMaxApplications = campaign.maxApplications || undefined;
        formRecruiterId = campaign.hiringManagerId || '';
        formVacancyIds = campaign.vacancyIds || [];
        formEvaluationTemplate = campaign.evaluationTemplate || {};
      } else {
        formTitle = '';
        formJobSlots = {};
        formJobNames = [];
        formLocation = '';
        formStatus = 'DRAFT';
        formDescription = '';
        formEndDate = '';
        formPublishedAt = '';
        formIsPublished = false;
        formIsActive = true;
        formMaxApplications = undefined;
        formRecruiterId = '';
        formVacancyIds = [];
      }
    }
  });

  async function handleSave() {
    // Validation Zod
    if (!validateForm()) {
      notification.toast.error('Veuillez corriger les erreurs du formulaire');
      return;
    }

    try {
      isSaving = true;

      if (campaign) {
        // Update existing campaign
        try {
          await $updateJobOfferMutation.mutateAsync({
            offerId: campaign.id,
            data: {
              title: formTitle,
              target_position_ids: formJobIds.filter(id => id !== ''),
              position_slots: formJobSlots,
              vacancy_ids: formVacancyIds,
              location: formLocation,
              status: formStatus,
              description: formDescription,
              requirements: selectedPosition?.requirements?.join(', ') || '',
              slots: calculatedTargetHires,
              end_date: formEndDate || undefined,
              published_at: formPublishedAt || undefined,
              is_published: formIsPublished,
              is_active: formIsActive,
              max_applications: formMaxApplications,
              recruiter_id: formRecruiterId || undefined,
              evaluation_template: formEvaluationTemplate
            }
          });
        } catch (error) {
          console.error(error);
          notification.toast.error(getFriendlyErrorMessage(error));
          throw error;
        }
      } else {
        // Create new campaign using mutation
        const jobOfferData = {
          title: formTitle,
          target_position_ids: formJobIds.filter(id => id !== ''),
          position_slots: formJobSlots,
          vacancy_ids: formVacancyIds,
          location: formLocation,
          status: formStatus,
          description: formDescription,
          requirements: selectedPosition?.requirements?.join(', ') || '',
          slots: calculatedTargetHires, // Total slots for backward compatibility
          end_date: formEndDate || undefined,
          published_at: formPublishedAt || undefined,
          is_published: formIsPublished,
          is_active: formIsActive,
          max_applications: formMaxApplications,
          recruiter_id: formRecruiterId || undefined,
          evaluation_template: formEvaluationTemplate
        };
        await $createJobOfferMutation.mutateAsync(jobOfferData);
        notification.toast.success('Campagne créée avec succès');
      }

      // Invalidate queries to refresh data
      await queryClient.invalidateQueries({ queryKey: ['recruitment'] });

      open = false;
    } catch (error) {
      console.error(error);
      notification.toast.error(getFriendlyErrorMessage(error));
    } finally {
      isSaving = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl bg-white p-0 flex flex-col h-full overflow-hidden">
    <!-- Header aligned with TransitionSheet -->
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <div class="space-y-0.5 min-w-0">
        <Sheet.Title class="text-[1rem] text-slate-900 truncate font-bold">
          {campaign ? 'Modifier la campagne' : 'Nouvelle campagne'}
        </Sheet.Title>
      </div>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-4 space-y-7" in:fade={{ duration: 200 }}>

        <!-- Titre de la campagne -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Titre de la campagne <span class="text-red-500">*</span></Label>
          <Input
            bind:value={formTitle}
            oninput={() => clearValidationError('title')}
            placeholder="ex: Recrutement Tech Q3"
            class={cn(
              "h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine",
              validationErrors.title && "border-red-500 focus:ring-red-500"
            )}
          />
          <ValidationError errors={validationErrors} field="title" />
        </div>

        <!-- Nom du poste et Localisation -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2.5">
            <Label class="text-slate-900">Postes <span class="text-red-500">*</span></Label>
            <div class="flex gap-2">
              <Select type="single" value={newJobId} onValueChange={(v) => newJobId = v}>
                <SelectTrigger class="h-9 flex-1 bg-white border-slate-200 shadow-fine rounded-lg cursor-pointer hover:border-slate-300 transition-colors">
                  <span class="truncate text-[0.87rem] font-medium">
                    {#if isLoadingPositions}
                      <AnimateSpin text="Chargement..." textPosition="right" class="size-3"/>
                    {:else if newJobId}
                      {positions.find(p => p.id === newJobId)?.name || 'Poste inconnu'}
                    {:else}
                      Sélectionner un poste
                    {/if}
                  </span>
                </SelectTrigger>
                <SelectContent class="z-9999">
                  {#each positions as position}
                    <SelectItem value={position.id} class="text-[0.85rem]">{position.name}</SelectItem>
                  {/each}
                </SelectContent>
              </Select>
              <Button variant="secondary" onclick={addPosition} class="h-9 w-9 p-0 shrink-0">
                <AppIcon name="plus" size={17} />
              </Button>
            </div>
            <ValidationError errors={validationErrors} field="jobNames" />
          </div>
          <div class="space-y-2.5">
            <Label class="text-slate-900">Localisation</Label>
            <Select type="single" value={formLocation} onValueChange={(v) => formLocation = v}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-lg cursor-pointer hover:border-slate-300 transition-colors">
                <span class="truncate text-[0.87rem] font-medium">
                  {#if isLoadingWorkSites}
                    <AnimateSpin text="Chargement..." textPosition="right" class="size-3"/>
                  {:else if formLocation}
                    {formLocation}
                  {:else}
                    Sélectionner une localisation
                  {/if}
                </span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                {#each workSites as site}
                  <SelectItem value={site.name} class="text-[0.85rem]">{site.name}</SelectItem>
                {/each}
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- Postes sélectionnés -->
        <div class="flex flex-wrap gap-2 space-y-1.5">
          {#each formJobIds as jobId}
            {@const position = positions.find(p => p.id === jobId)}
            {@const slots = formJobSlots[jobId] || 1}
            {#if position}
              <div class="flex items-center gap-2 px-3 py-1 rounded-xl bg-slate-50 border border-slate-100 text-[0.87rem] font-medium text-slate-700 animate-in fade-in scale-in-95 duration-200 group">
                <AppIcon name="briefcase" size={16} class="text-primary" strokeWidth={1.7} />
                {position.name}
                <div class="flex items-center gap-1 ml-2">
                  <input
                    type="number"
                    value={slots}
                    oninput={(e) => updatePositionSlots(jobId, parseInt((e.target as HTMLInputElement).value) || 1)}
                    onkeydown={preventNonNumeric}
                    min="1"
                    class="w-12 h-6 text-center text-sm bg-white border border-slate-200 rounded focus:ring-1 focus:ring-primary focus:outline-none"
                  />
                  <span class="text-[0.84rem] text-slate-500">poste{slots > 1 ? 's' : ''}</span>
                </div>
                <button 
                  type="button"
                  onclick={(e) => { e.preventDefault(); e.stopPropagation(); removePosition(jobId); }}
                  class="text-slate-400 hover:text-red-500 transition-colors cursor-pointer"
                >
                  <AppIcon name="x" size={16} />
                </button>
              </div>
            {/if}
          {:else}
            <p class="text-[0.87rem] text-slate-400 flex justify-center items-center gap-1.5 px-2 w-full">
              <AppIcon name="circle-x" size={17} class="text-slate-300" />
              Aucun poste sélectionné.
            </p>
          {/each}
        </div>

        <!-- Grille d'évaluation par poste -->
        {#if formJobIds.length > 0}
          <div class="space-y-3">
            <Label class="text-slate-900">Critères d'évaluation</Label>
            <p class="text-[0.83rem] text-slate-500 -mt-1.5">
              Sélectionnez les compétences à évaluer pour chaque poste et définissez leurs pondérations.
            </p>
            {#each formJobIds as jobId}
              {@const position = positions.find(p => p.id === jobId)}
              {#if position}
                {@const count = activeEvalCount(jobId)}
                <div class="border border-slate-200 rounded-lg overflow-hidden transition-all">
                  <!-- En-tête cliquable -->
                  <button
                    type="button"
                    onclick={() => { ensureEvalTemplate(jobId); toggleEvalPosition(jobId); }}
                    class="w-full flex items-center justify-between px-3.5 py-2.5 bg-slate-50 hover:bg-slate-100 transition-colors cursor-pointer border-none text-left"
                  >
                    <div class="flex items-center gap-2.5">
                      <AppIcon name="briefcase" size={15} class="text-primary" strokeWidth={1.7} />
                      <span class="text-[0.85rem] font-semibold text-slate-800">{position.name}</span>
                      {#if count > 0}
                        <span class="text-[0.77rem] px-1.5 py-0.5 rounded-full bg-indigo-50 text-indigo-600 font-medium">{count} critère{count > 1 ? 's' : ''} · {activeEvalTotal(jobId)}%</span>
                      {:else}
                        <span class="text-[0.77rem] px-1.5 py-0.5 rounded-full bg-amber-50 text-amber-600 font-medium">Aucun critère</span>
                      {/if}
                    </div>
                    <AppIcon name={expandedEvalPosition === jobId ? 'chevron-up' : 'chevron-down'} size={16} class="text-slate-400 transition-transform" />
                  </button>

                  <!-- Contenu dépliable -->
                  {#if expandedEvalPosition === jobId}
                    {@const criteria = formEvaluationTemplate[jobId] || []}
                    <div class="p-3.5 space-y-2 bg-white border-t border-slate-100 animate-in fade-in slide-in-from-top-2 duration-150">
                      {#if criteria.length === 0}
                        <p class="text-[0.83rem] text-slate-400 text-center py-2">Aucune compétence définie pour ce poste.</p>
                      {:else}
                        <div class="flex items-center gap-2 mb-2">
                          <button type="button" onclick={() => autoBalance(jobId)}
                            class="text-[0.84rem] px-2 py-1 rounded-md bg-indigo-50 text-indigo-600 hover:bg-indigo-100 transition-colors cursor-pointer border-none font-medium"
                          >
                            Équilibrer les poids
                          </button>
                          <span class="text-[0.82rem] text-slate-400">Total: {activeEvalTotal(jobId)}%</span>
                          {#if activeEvalTotal(jobId) !== 100 && activeEvalTotal(jobId) > 0}
                            <span class="text-[0.82rem] text-amber-500">(doit faire 100%)</span>
                          {/if}
                        </div>
                        {#each criteria as criterion, i}
                          {@const isActive = criterion.weight > 0}
                          <div class="flex items-center gap-2.5 py-1.5 px-2 rounded-md hover:bg-slate-50 transition-colors {isActive ? '' : 'opacity-50'}">
                            <input
                              type="checkbox"
                              checked={isActive}
                              onchange={() => toggleCriterion(jobId, i)}
                              class="w-3.5 h-3.5 rounded border-slate-300 text-indigo-600 focus:ring-indigo-500 cursor-pointer"
                            />
                            <div class="flex-1 min-w-0">
                              <div class="flex items-center gap-1.5">
                                <span class="text-[0.85rem] text-slate-700 truncate">{criterion.name}</span>
                                <span class="text-[0.85rem] px-1 py-0 rounded font-medium {criterion.source === 'requirement' ? 'bg-blue-50 text-blue-600' : 'bg-emerald-50 text-emerald-600'}">
                                  {criterion.source === 'requirement' ? 'req' : 'skill'}
                                </span>
                              </div>
                            </div>
                            {#if isActive}
                              <div class="flex items-center gap-1 shrink-0">
                                <input
                                  type="number"
                                  value={criterion.weight}
                                  oninput={(e) => updateCriterionWeight(jobId, i, parseInt((e.target as HTMLInputElement).value) || 0)}
                                  onkeydown={preventNonNumeric}
                                  min="0"
                                  max="100"
                                  class="w-12 h-7 text-center text-[0.84rem] bg-white border border-slate-200 rounded focus:ring-1 focus:ring-indigo-500 focus:outline-none"
                                />
                                <span class="text-[0.84rem] text-slate-500">%</span>
                              </div>
                            {/if}
                          </div>
                        {/each}
                      {/if}
                    </div>
                  {/if}
                </div>
              {/if}
            {/each}
          </div>
        {/if}

        <!-- Nombre de postes et Max applications -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2.5">
            <Label class="text-slate-900">Max candidatures (optionnel)</Label>
            <Input
              type="number"
              bind:value={formMaxApplications}
              onkeydown={preventNonNumeric}
              placeholder="Illimité"
              min="1"
              class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine"
            />
          </div>
          <div class="space-y-2.5">
            <Label class="text-slate-900">Nombre de postes</Label>
            <p class="text-sm font-medium text-slate-500">Total: {calculatedTargetHires} poste{calculatedTargetHires > 1 ? 's' : ''} ({formJobIds.length} type{formJobIds.length > 1 ? 's' : ''} de poste{formJobIds.length > 1 ? 's' : ''})</p>
          </div>
        </div>

        <!-- Vacancies (Besoins) -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Besoins (Vacancies)</Label>
          <div class="space-y-2">
            {#each vacancies as vacancy}
              <div class="flex items-center gap-2 p-2 border border-slate-200 rounded-lg hover:border-slate-300 transition-colors">
                <Switch
                  checked={formVacancyIds.includes(vacancy.id)}
                  onCheckedChange={() => handleVacancyToggle(vacancy.id, vacancy.position?.id || '')}
                  class="cursor-pointer"
                />
                <div class="flex-1">
                  <div class="text-sm font-medium">{vacancy.position?.name || 'Poste inconnu'}</div>
                  <div class="text-xs text-slate-500">{vacancy.reason || ''}</div>
                </div>
                <div class="text-xs text-slate-400">{vacancy.priority}</div>
              </div>
            {/each}
          </div>
        </div>

        <!-- Statut et Recruteur -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2.5">
            <Label class="text-slate-900">Statut</Label>
            <Select type="single" value={formStatus} onValueChange={(v) => formStatus = v as any}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-lg cursor-pointer hover:border-slate-300 transition-colors">
                <span class="truncate text-[0.87rem] font-medium">{CAMPAIGN_STATUS_OPTIONS.find(opt => opt.value === formStatus)?.label || formStatus}</span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                {#each CAMPAIGN_STATUS_OPTIONS as option}
                  <SelectItem value={option.value} class="text-[0.85rem]">{option.label}</SelectItem>
                {/each}
              </SelectContent>
            </Select>
            <ValidationError errors={validationErrors} field="status" />
          </div>
          <div class="space-y-2.5">
            <Label class="text-slate-900">Recruteur</Label>
            <Select type="single" value={formRecruiterId} onValueChange={(v) => formRecruiterId = v}>
              <SelectTrigger class="h-10 w-full bg-white border-slate-200 shadow-fine rounded-lg cursor-pointer hover:border-slate-300 transition-colors">
                <span class="truncate text-[0.87rem] font-medium">
                  {#if isLoadingEmployees}
                    <AnimateSpin text="Chargement..." textPosition="right" class="size-3"/>
                  {:else if formRecruiterId}
                    {employees.find(e => String(e.id) === formRecruiterId)?.name || 'Recruteur inconnu'}
                  {:else}
                    Sélectionner un recruteur
                  {/if}
                </span>
              </SelectTrigger>
              <SelectContent class="z-9999">
                {#each employees as employee}
                  <SelectItem value={String(employee.id)} class="text-[0.85rem]">{employee.name}</SelectItem>
                {/each}
              </SelectContent>
            </Select>
          </div>
        </div>

        <!-- Options de publication -->
        <div class="space-y-3">
          <Label class="text-slate-900">Options de publication</Label>
          <div class="flex items-center gap-4">
            <label class="flex items-center gap-2 cursor-pointer">
              <Switch bind:checked={formIsPublished} class="cursor-pointer" />
              <span class="text-[0.87rem] text-slate-700">Publier immédiatement</span>
            </label>
            <label class="flex items-center gap-2 cursor-pointer">
              <Switch bind:checked={formIsActive} class="cursor-pointer" />
              <span class="text-[0.87rem] text-slate-700">Campagne active</span>
            </label>
          </div>
        </div>

        <!-- Date de publication et Date de fin -->
        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2.5">
            <Label class="text-slate-900">Date de publication</Label>
            <Input
              type="date"
              bind:value={formPublishedAt}
              class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine"
            />
          </div>
          <div class="space-y-2.5">
            <Label for="campaign-end-date" class="text-slate-900">Date de fin</Label>
            <Input
              id="campaign-end-date"
              type="date"
              bind:value={formEndDate}
              class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine"
            />
          </div>
        </div>
        
        <!-- Description du besoin -->
        <div class="space-y-2.5">
          <Label for="campaign-desc" class="text-slate-900">Description du besoin</Label>
          <Textarea
            id="campaign-desc"
            bind:value={formDescription}
            placeholder="Détails sur le poste, l'équipe, etc..."
            class="w-full h-28 rounded-lg border border-slate-200 px-3.5 py-3 text-[0.88rem] leading-relaxed focus:ring-4 focus:ring-primary/30 focus:border-primary focus:outline-none bg-white shadow-fine resize-none transition-all placeholder:text-slate-400"
          />
        </div>

      </div>
    </div>

    <!-- Footer aligned with TransitionSheet -->
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
          {campaign ? 'Enregistrer' : 'Enregistrer'}
        </Button>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>


<style>
  .custom-scrollbar::-webkit-scrollbar { width: 4px; }
  .custom-scrollbar::-webkit-scrollbar-track { background: transparent; }
  .custom-scrollbar::-webkit-scrollbar-thumb { background: #cbd5e1; border-radius: 10px; }
 </style>

