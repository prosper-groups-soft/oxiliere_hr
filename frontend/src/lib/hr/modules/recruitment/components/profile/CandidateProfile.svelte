<script lang="ts">
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import * as Tabs from "@/components/ui/tabs";
  import { Separator } from "@/components/ui/separator";
  import { cn } from "@/hr/utilities/common/css";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import AvatarGallery from "@/hr/components/shared/media/AvatarGallery.svelte";
  import { differenceInDays } from 'date-fns';
  import { crossfade } from 'svelte/transition';
  import { cubicInOut } from 'svelte/easing';
  import { recruitmentStore } from "../../stores/recruitment.svelte";
  import { recruitmentService } from "../../services/recruitmentService";
  import type { Interview, CandidateApplication, RecruitmentCampaign } from "../../types/types";
  import { STAGE_CONFIG, CANDIDATE_PRIORITY_CONFIG, CANDIDATE_SOURCE_CONFIG } from "../../constants/recruitment";
  import InterviewTimeline from "./elements/InterviewTimeline.svelte";
  import CandidateScorecard from "./elements/CandidateScorecard.svelte";
  import ResumeViewer from "./elements/ResumeViewer.svelte";
  import InterviewSheet from "../shared/sheets/interview/InterviewSheet.svelte";
  import OfferSheet from "../shared/sheets/candidate/OfferSheet.svelte";
  import CandidateSheet from "../shared/sheets/candidate/CandidateSheet.svelte";
  import EvaluationSheet from "../shared/sheets/candidate/EvaluationSheet.svelte";
  import FeedbackSheet from "../shared/sheets/interview/FeedbackSheet.svelte";
  import { get_api_base_origin } from "@/hr/utilities/http/urls";

  
  let { candidateId } = $props<{ candidateId: string }>();

  // Get candidate data from store
  const candidate = $derived(
    recruitmentStore.candidates.find(c => c.id === candidateId)
  );

  const fullName = $derived(
    [candidate?.lastName, candidate?.middleName, candidate?.firstName]
      .filter(Boolean)
      .join(' ')
  );

  // Application selection state
  let selectedAppId = $state<string | null>(null);

  const apps = $derived(candidate?.applications ?? []);
  const hasMultipleApps = $derived(apps.length > 1);

  // Auto-select first application
  const selectedApplicationId = $derived(
    selectedAppId ?? apps[0]?.applicationId ?? null
  );

  const selectedApp = $derived<CandidateApplication | undefined>(
    apps.find((a: CandidateApplication) => a.applicationId === selectedApplicationId)
  );

  // Crossfade transition for the active tab indicator
  const [send, receive] = crossfade({
    duration: 300,
    easing: cubicInOut
  });

  // Use selected app fields, fall back to candidate-level fields
  const activeStage = $derived(selectedApp?.currentStage ?? candidate?.currentStage ?? '');
  const activePriority = $derived(selectedApp?.priority ?? candidate?.priority ?? '');
  const activePosition = $derived(selectedApp?.targetPositionName ?? candidate?.targetPositionName ?? candidate?.position);

  const campaign = $derived<RecruitmentCampaign | undefined>(
    recruitmentStore.campaigns.find(c => c.id === candidate?.campaignId)
  );

  const positionEvalCriteria = $derived(
    (selectedApp?.positionId && campaign?.evaluationTemplate) 
      ? campaign.evaluationTemplate[selectedApp.positionId] 
      : undefined
  );

  // Load interviews when component mounts
  let isLoadingInterviews = $state(false);
  let refreshInterviews = $state(0);

  $effect(() => {
    if (candidateId) {
      loadInterviews();
    }
  });

  // Reload interviews when feedback is saved
  $effect(() => {
    if (refreshInterviews > 0 && candidateId) {
      loadInterviews();
    }
  });

  async function loadInterviews() {
    isLoadingInterviews = true;
    try {
      const result = await recruitmentService.listInterviewsByCandidate(candidateId);
      recruitmentStore.interviews = result.results;
    } catch (e) {
      // Silently fail
    } finally {
      isLoadingInterviews = false;
    }
  }

  function onFeedbackSaved() {
    refreshInterviews++;
  }

  // Sheet states
  let isInterviewSheetOpen = $state(false);
  let isOfferSheetOpen = $state(false);
  let isEditSheetOpen = $state(false);
  let isEvaluationSheetOpen = $state(false);
  let isFeedbackSheetOpen = $state(false);
  let selectedInterview = $state<Interview | null>(null);

  // Reload interviews when refreshInterviews changes
  $effect(() => {
    if (refreshInterviews > 0 && candidateId) {
      loadInterviews();
    }
  });

  // Reload interviews when refreshInterviews changes
  const profilePhoto = $derived(getMediaUrl(candidate?.avatarUrl));
  const palette = $derived(candidate ? getAvatarPalette(fullName || '') : { bg: '', text: '' });
  const priCfg = $derived(candidate ? CANDIDATE_PRIORITY_CONFIG[activePriority] ?? CANDIDATE_PRIORITY_CONFIG['MEDIUM'] : null);
  const stCfg = $derived(candidate ? STAGE_CONFIG[activeStage] ?? STAGE_CONFIG.SCREENING : null);
  const srcCfg = $derived(candidate ? CANDIDATE_SOURCE_CONFIG[candidate.source] ?? CANDIDATE_SOURCE_CONFIG['DIRECT'] : null);
  
  const daysInStage = $derived(
    candidate ? differenceInDays(new Date(), new Date(selectedApp?.lastStageChange ?? candidate.lastStageChange)) : 0
  );

  function handleScheduleInterview() {
    selectedInterview = null;
    isInterviewSheetOpen = true;
  }

  function handleCreateOffer() {
    isOfferSheetOpen = true;
  }

  function handleGenerateReport() {
    const params = selectedApplicationId ? `?application_id=${selectedApplicationId}` : '';
    window.open(`${get_api_base_origin()}/api/recruitment/candidates/${candidate?.id}/export/${params}`, '_blank');
  }

  // Reset selected interview when sheets close to avoid stale state
  $effect(() => {
    if (!isInterviewSheetOpen) {
      selectedInterview = null;
    }
  });

  $effect(() => {
    if (!isFeedbackSheetOpen) {
      selectedInterview = null;
    }
  });
</script>


<div class="bg-white border-b border-slate-100 mb-3 sticky top-0 z-11">
  {#if candidate}
    <div class="px-4 pt-3 pb-0">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <div class="shrink-0">
            <AvatarGallery
              name={fullName || ''}
              src={profilePhoto}
              iconSize={16}
              iconStroke={2}
              disableUploadHover={true}
              onUpload={() => {}}
              class="h-14 w-14 rounded-full shadow-fine"
            >
              <Avatar class="h-full w-full border border-slate-200">
                <AvatarImage src={profilePhoto} alt={fullName} class="object-cover" />
                <AvatarFallback class={cn("font-bold text-[0.85rem]", palette?.bg, palette?.text)}>
                  {getInitials(candidate?.lastName, candidate?.middleName, candidate?.firstName)}
                </AvatarFallback>
              </Avatar>
            </AvatarGallery>
          </div>
          <div class="flex flex-col min-w-0 flex-1">
            <span class="font-semibold text-[0.95rem] text-slate-900 leading-tight truncate">
              {fullName}
            </span>
            <span class="text-[0.82rem] text-slate-500 truncate">{candidate?.email}</span>
          </div>
        </div>

        <DropdownMenu.Root>
          <DropdownMenu.Trigger asChild>
            {#snippet child({ props })}
              <button {...props} class="flex items-center gap-1.5 rounded-lg text-[0.84rem] h-7.5 px-3 bg-indigo-600 text-white hover:bg-indigo-700 transition-colors cursor-pointer">
                <AppIcon name="more-vertical" size={18} />
                Actions
              </button>
            {/snippet}
          </DropdownMenu.Trigger>

          <DropdownMenu.Content align="end" class="z-200 p-1 rounded-lg shadow-fine bg-white border-slate-100 w-54">
            <DropdownMenu.Item onclick={handleScheduleInterview} class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600">
              <AppIcon name="calendar" size={16} class="text-slate-500" />
              Programmer entretien
            </DropdownMenu.Item>
            {#if activeStage === 'INTERVIEW' || activeStage === 'SHORTLIST' || activeStage === 'OFFER'}
              <DropdownMenu.Item onclick={handleCreateOffer} class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600">
                <AppIcon name={selectedApp?.salaryMin ? "edit" : "send"} size={16} class="text-slate-500" />
                {selectedApp?.salaryMin ? 'Modifier l\'offre' : 'Créer une offre'}
              </DropdownMenu.Item>
            {/if}
            <DropdownMenu.Item onclick={() => isEditSheetOpen = true} class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600">
              <AppIcon name="edit" size={16} class="text-slate-500" />
              Modifier le candidat
            </DropdownMenu.Item>
            <DropdownMenu.Item onclick={() => isEvaluationSheetOpen = true} class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600">
              <AppIcon name="star" size={16} class="text-slate-500" />
              Évaluer le candidat
            </DropdownMenu.Item>
            <DropdownMenu.Item onclick={handleGenerateReport} class="rounded-md py-1.5 px-2 text-[0.85rem]! cursor-pointer flex items-center gap-2 text-slate-900 hover:text-indigo-600">
              <AppIcon name="download" size={16} class="text-slate-500" />
              Générer rapport
            </DropdownMenu.Item>
          </DropdownMenu.Content>
        </DropdownMenu.Root>
      </div>

      {#if hasMultipleApps}
        <Tabs.Root value={selectedApplicationId ?? ''} onValueChange={(v) => selectedAppId = v} class="w-full mt-2">
          <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-0 border-none">
            {#each apps as app (app.applicationId)}
              <Tabs.Trigger
                value={app.applicationId}
                class={cn(
                  "relative flex items-center gap-1.5 bg-transparent shadow-none transition-all duration-300",
                  "rounded-none border-none px-2 pb-3 outline-none focus-visible:ring-0",
                  "group cursor-pointer text-slate-600",
                  "data-[state=active]:text-indigo-700 data-[state=active]:bg-transparent data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-indigo-700"
                )}
              >
                <AppIcon name="briefcase" size={16} class="group-data-[state=active]:text-indigo-700 text-slate-400 shrink-0" />
                <span class="text-[0.82rem] tracking-tight truncate max-w-[140px]">{app.targetPositionName || 'Poste #' + app.applicationId.slice(0, 6)}</span>
                {#if app.applicationId === selectedApplicationId}
                  <div 
                    in:receive={{ key: 'app-tab-bar' }}
                    out:send={{ key: 'app-tab-bar' }}
                    class="absolute bottom-0 left-0 right-0 h-0.5 rounded-full bg-indigo-600 z-10"
                  ></div>
                {/if}
              </Tabs.Trigger>
            {/each}
          </Tabs.List>
        </Tabs.Root>
      {/if}
    </div>
  {/if}
</div>

{#if candidate}
  <div class="px-4 py-3">
    <div class="space-y-4">
      <!-- Status Bar -->
      <div class="flex flex-wrap items-center gap-3 p-3 bg-slate-50/50 rounded-xl border border-slate-100">
        <div class="flex items-center gap-2">
          <span class="text-[0.83rem] text-slate-500">Statut :</span>
          <Badge variant="outline" class={cn("text-[0.82rem] border", stCfg?.color)}>
            <AppIcon name={stCfg?.icon || "info"} size={15} />
            {stCfg?.label}
          </Badge>
        </div>
        <div class="flex items-center gap-2">
          <span class="text-[0.83rem] text-slate-500">Priorité :</span>
          <Badge variant="outline" class={cn("text-[0.82rem] border", priCfg?.color)}>
            {priCfg?.label}
          </Badge>
        </div>
        <div class="flex items-center gap-1 text-[0.83rem] text-slate-500">
          <AppIcon name={srcCfg?.icon || "info"} size={15} class="text-slate-400" />
          {srcCfg?.label}
        </div>
        <div class="text-[0.83rem] text-slate-500 ml-auto">
          {daysInStage} {daysInStage <= 1 ? 'jour' : 'jours'} dans cette étape
        </div>
      </div>

      <!-- Info Grid -->
      <div class="grid grid-cols-2 gap-3">
        <div class="p-3 bg-slate-50/30 rounded-xl border border-slate-50">
          <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider">Téléphone</p>
          <p class="text-[0.85rem] text-slate-900 mt-0.5">{candidate?.phone || 'Non renseigné'}</p>
        </div>
        <div class="p-3 bg-slate-50/30 rounded-xl border border-slate-50">
          <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider">Localisation</p>
          <p class="text-[0.85rem] text-slate-900 mt-0.5">{candidate?.location || 'Non renseigné'}</p>
        </div>
        <div class="p-3 bg-slate-50/30 rounded-xl border border-slate-50">
          <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider">Poste visé</p>
          <p class="text-[0.85rem] text-slate-900 mt-0.5">{activePosition || 'Non renseigné'}</p>
        </div>
        <div class="p-3 bg-slate-50/30 rounded-xl border border-slate-50">
          <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider">Expérience</p>
          <p class="text-[0.85rem] text-slate-900 mt-0.5">{candidate?.experience || 'Non renseigné'}</p>
        </div>
      </div>

      <!-- Resume / Summary -->
      {#if candidate?.summary}
        <div>
          <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider mb-1.5">Résumé</p>
          <p class="text-[0.85rem] text-slate-700 leading-relaxed">{candidate.summary}</p>
        </div>
      {/if}

      <Separator class="bg-slate-100" />

      <!-- Skills -->
      <div>
        <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider mb-2">Compétences</p>
        <div class="flex flex-wrap gap-1.5">
          {#if candidate?.skills && candidate?.skills.length > 0}
            {#each candidate?.skills as skill}
              <Badge variant="outline" class="text-[0.75rem] border-slate-200 px-2 py-0.5 flex justify-center items-center gap-2">
                <AppIcon name="tag" size={16} class="text-slate-500"/>  
                {skill}
              </Badge>
            {/each}
          {:else}
            <p class="text-[0.82rem] text-slate-400">
              <AppIcon name="tag" size={16} class="text-slate-300 flex justify-center items-center gap-2"/>
              Aucune compétence listée
            </p>
          {/if}
        </div>
      </div>

      <!-- Resume Document -->
      <div>
        <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider mb-2">CV</p>
        <ResumeViewer resumeUrl={candidate?.resumeUrl} />
      </div>

      <Separator class="bg-slate-100" />

      <!-- Scorecard -->
      <div>
        <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider mb-2">Évaluation</p>
        <CandidateScorecard 
          application={selectedApp ?? null} 
          evaluationTemplate={positionEvalCriteria} 
          onEdit={() => isEvaluationSheetOpen = true} 
        />
      </div>

      <Separator class="bg-slate-100" />

      <!-- Offer Details -->
      <div>
        <div class="flex items-center justify-between mb-2">
          <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider">Offre</p>
          {#if selectedApp?.salaryMin || selectedApp?.salaryMax}
            <button 
              onclick={() => isOfferSheetOpen = true}
              class="text-[0.78rem] text-indigo-600 hover:text-indigo-800 font-medium transition-colors cursor-pointer flex items-center gap-1"
            >
              <AppIcon name="edit" size={14} />
              Modifier l'offre
            </button>
          {:else}
            <button 
              onclick={() => isOfferSheetOpen = true}
              class="text-[0.78rem] text-indigo-600 hover:text-indigo-800 font-medium transition-colors cursor-pointer flex items-center gap-1"
            >
              <AppIcon name="plus" size={14} />
              Créer une offre
            </button>
          {/if}
        </div>
        {#if selectedApp?.salaryMin || selectedApp?.salaryMax}
          <div class="grid grid-cols-2 gap-3">
            <div class="p-3 bg-emerald-50/50 rounded-xl border border-emerald-100">
              <p class="text-[0.7rem] font-medium text-emerald-600 uppercase tracking-wider">Salaire proposé</p>
              <p class="text-[0.9rem] text-slate-900 mt-0.5 font-semibold">
                {selectedApp.salaryMin?.toLocaleString()} - {selectedApp.salaryMax?.toLocaleString()} {selectedApp.salaryCurrency || 'USD'}
              </p>
            </div>
            <div class="p-3 bg-emerald-50/50 rounded-xl border border-emerald-100">
              <p class="text-[0.7rem] font-medium text-emerald-600 uppercase tracking-wider">Date de début</p>
              <p class="text-[0.9rem] text-slate-900 mt-0.5 font-semibold">
                {selectedApp.offerStartDate ? new Date(selectedApp.offerStartDate + 'T00:00:00').toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' }) : 'Non définie'}
              </p>
            </div>
          </div>
        {:else}
          <div class="p-4 rounded-xl bg-slate-50 border border-dashed border-slate-200 text-center">
            <p class="text-[0.85rem] text-slate-400">Aucune offre créée pour cette candidature</p>
          </div>
        {/if}
      </div>

      <Separator class="bg-slate-100" />

      <!-- Interviews -->
      <div>
        <p class="text-[0.7rem] font-medium text-slate-500 uppercase tracking-wider mb-2">Entretiens</p>
        <InterviewTimeline 
          interviews={recruitmentStore.interviews}
          applicationId={selectedApplicationId ?? ''}
          loading={isLoadingInterviews}
          onReschedule={(interview: Interview) => {
            selectedInterview = interview;
            isInterviewSheetOpen = true;
          }}
          onAddFeedback={(interview: Interview) => {
            selectedInterview = interview;
            isFeedbackSheetOpen = true;
          }}
        />
      </div>
    </div>
  </div>
{/if}


<InterviewSheet bind:open={isInterviewSheetOpen} candidate={candidate ?? null} interview={selectedInterview} applicationId={selectedApplicationId ?? ''} />
<OfferSheet bind:open={isOfferSheetOpen} application={selectedApp ?? null} />
<CandidateSheet bind:open={isEditSheetOpen} candidate={candidate ?? null} campaignId={candidate?.campaignId || ''} />
<EvaluationSheet 
  bind:open={isEvaluationSheetOpen} 
  application={selectedApp ?? null} 
  evaluationTemplate={positionEvalCriteria} 
/>
<FeedbackSheet bind:open={isFeedbackSheetOpen} interview={selectedInterview} onsaved={onFeedbackSaved} />

