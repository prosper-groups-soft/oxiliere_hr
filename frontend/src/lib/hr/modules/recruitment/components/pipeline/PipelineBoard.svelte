<script lang="ts">
  import { fade } from 'svelte/transition';
  import PipelineColumn from "./PipelineColumn.svelte";
  import InterviewSheet from "../shared/sheets/interview/InterviewSheet.svelte";
  import OfferSheet from "../shared/sheets/candidate/OfferSheet.svelte";
  import CandidateSheet from "../shared/sheets/candidate/CandidateSheet.svelte";
  import EvaluationSheet from "../shared/sheets/candidate/EvaluationSheet.svelte";
  import FeedbackSheet from "../shared/sheets/interview/FeedbackSheet.svelte";
  import { recruitmentStore } from "../../stores/recruitment.svelte";
  import { notification } from '@/hr/stores/notification.svelte';
  import type { PipelineApplicationItem, CandidateStage, Interview, Candidate, CandidateApplication } from "../../types/types";


  const pipelineData = $derived(recruitmentStore.pipelineApplications);
  const campaign = $derived(recruitmentStore.currentCampaign);

  // Position filter
  const activePositionIds = $derived(recruitmentStore.pipelinePositionIds);
  const campaignPositions = $derived(campaign?.positions || []);
  const filteredPipelineData = $derived(
    activePositionIds.length > 0
      ? pipelineData.map(col => ({
          ...col,
          applications: col.applications.filter(
            item => activePositionIds.includes(item.application.positionId || '')
          )
        }))
      : pipelineData
  );

  // --- Sheet states ---
  let isInterviewSheetOpen = $state(false);
  let isOfferSheetOpen = $state(false);
  let isEvaluationSheetOpen = $state(false);
  let isFeedbackSheetOpen = $state(false);
  let isCandidateSheetOpen = $state(false);
  let activeItem = $state<PipelineApplicationItem | null>(null);
  let selectedInterview = $state<Interview | null>(null);

  // Snapshots stables des props pour chaque sheet — capturés à l'ouverture, jamais modifiés pendant la vie du sheet
  let _interviewCandidate = $state<Candidate | null>(null);

  // _sheetActionPending kept for sheet UX (not for global loading — now handled by parent AsyncView)
  let _sheetActionPending = $state(false);
  
  $effect(() => {
    const anyOpen = isInterviewSheetOpen || isOfferSheetOpen || isEvaluationSheetOpen
      || isFeedbackSheetOpen || isCandidateSheetOpen || recruitmentStore.profileSheetOpen;
    if (anyOpen) _sheetActionPending = true;
    else _sheetActionPending = false;
  });

  let _interviewInterview = $state<Interview | null>(null);
  let _offerApplication = $state<CandidateApplication | null>(null);
  let _evaluationApplication = $state<CandidateApplication | null>(null);
  let _feedbackInterview = $state<Interview | null>(null);
  let _candidateCandidate = $state<Candidate | null>(null);
  let _candidateCampaignId = $state('');

  // Stocker l'ID de l'application séparément pour éviter la race condition du rollback
  // (rollbackDrag vide activeItem avant que onSuccess puisse l'utiliser)
  let _pendingInterviewAppId = $state<string | null>(null);
  let _pendingOfferAppId = $state<string | null>(null);

  // Capturer les snapshots à l'ouverture de chaque sheet — ne JAMAIS changer ensuite
  $effect(() => {
    if (isInterviewSheetOpen && activeItem) {
      _interviewCandidate = activeItem.candidate;
      _pendingInterviewAppId = activeItem.application.applicationId;
      _interviewInterview = selectedInterview;
    }
  });

  $effect(() => {
    if (isOfferSheetOpen && activeItem) {
      _offerApplication = activeItem.application;
    }
  });

  $effect(() => {
    if (isEvaluationSheetOpen && activeItem) {
      _evaluationApplication = activeItem.application;
    }
  });

  $effect(() => {
    if (isFeedbackSheetOpen && selectedInterview) {
      _feedbackInterview = selectedInterview;
    }
  });

  $effect(() => {
    if (isCandidateSheetOpen && activeItem) {
      _candidateCandidate = activeItem.candidate;
      _candidateCampaignId = activeItem.candidate.campaignId || '';
    }
  });

  // --- Rollback tracking ---
  let _pendingDropAppId = $state<string | null>(null);
  let _pendingDropOriginalStage = $state<CandidateStage | null>(null);

  // Evaluation template by position
  const evaluationTemplate = $derived(
    activeItem?.application?.positionId && campaign?.evaluationTemplate
      ? campaign.evaluationTemplate[activeItem.application.positionId]
      : undefined
  );

  // --- Helpers ---
  function getStageTitle(stage: CandidateStage): string {
    return recruitmentStore.getStageTitle(stage);
  }

  function findItemByAppId(appId: string): PipelineApplicationItem | undefined {
    for (const col of pipelineData) {
      const found = col.applications.find(a => a.application.applicationId === appId);
      if (found) return found;
    }
    return undefined;
  }

  // --- Transition logic ---

  // Ordre forward-only des étapes du pipeline
  const STAGE_ORDER: CandidateStage[] = ['SCREENING', 'SHORTLIST', 'INTERVIEW', 'OFFER', 'ACCEPTED'];

  /** Vérifie que le mouvement est forward-only (pas de rétrogradation) */
  function isForwardOnly(oldStage: CandidateStage, newStage: CandidateStage): boolean {
    // Rejected est toujours atteignable depuis n'importe quel état non-terminal
    if (newStage === 'REJECTED') return true;
    // Autoriser le retour SHORTLIST → SCREENING
    if (oldStage === 'SHORTLIST' && newStage === 'SCREENING') return true;
    const oldIdx = STAGE_ORDER.indexOf(oldStage);
    const newIdx = STAGE_ORDER.indexOf(newStage);
    // Si l'un des deux n'est pas dans l'ordre (ex: REJECTED), on autorise
    if (oldIdx === -1 || newIdx === -1) return true;
    return newIdx >= oldIdx;
  }

  async function handleApplicationDrop(applicationId: string, newStage: CandidateStage) {
    const item = findItemByAppId(applicationId);
    if (!item) return;

    const oldStage = item.application.currentStage;
    if (oldStage === newStage) return;

    // Bloquer la rétrogradation (drag-and-drop vers une étape antérieure)
    if (!isForwardOnly(oldStage, newStage)) {
      notification.toast.error(
        `Impossible de rétrograder "${item.candidate.lastName} ${item.candidate.middleName} ${item.candidate.firstName}" de ${getStageTitle(oldStage)} vers ${getStageTitle(newStage)}. Seuls les déplacements avants sont autorisés.`
      );
      recruitmentStore.refreshPipeline();
      return;
    }

    activeItem = item;
    _pendingDropAppId = applicationId;
    _pendingDropOriginalStage = oldStage;

    switch (newStage) {
      case 'SHORTLIST':
        notification.confirm({
          title: 'Shortlister la candidature ?',
          message: `Passer "${item.candidate.lastName} ${item.candidate.middleName} ${item.candidate.firstName}" — ${item.application.targetPositionName || ''} en shortlist ?`,
          onYes: () => doStageChange(applicationId, newStage),
          onNo: () => rollbackDrag()
        });
        break;

      case 'INTERVIEW':
        selectedInterview = null;
        _pendingInterviewAppId = applicationId;
        isInterviewSheetOpen = true;
        break;

      case 'OFFER':
        _pendingOfferAppId = applicationId;
        isOfferSheetOpen = true;
        break;

      case 'REJECTED':
        notification.confirm({
          title: 'Rejeter la candidature ?',
          message: `Êtes-vous sûr de rejeter "${item.candidate.lastName} ${item.candidate.middleName} ${item.candidate.firstName}" pour le poste "${item.application.targetPositionName || ''}" ? Cette action est irréversible.`,
          type: 'danger',
          onYes: () => doStageChange(applicationId, newStage),
          onNo: () => rollbackDrag()
        });
        break;

      default:
        notification.confirm({
          title: 'Déplacer la candidature ?',
          message: `Déplacer "${item.candidate.lastName} ${item.candidate.middleName} ${item.candidate.firstName}" vers ${getStageTitle(newStage)} ?`,
          onYes: () => doStageChange(applicationId, newStage),
          onNo: () => rollbackDrag()
        });
    }
  }

  /** Rollback visual state when user cancels the drop */
  function rollbackDrag() {
    _pendingDropAppId = null;
    _pendingDropOriginalStage = null;
    activeItem = null;
    // Force refresh by triggering pipelineApplications re-derivation
    recruitmentStore.refreshPipeline();
  }

  async function doStageChange(applicationId: string, stage: CandidateStage, showToast = true) {
    // Mask loading state during confirm-dialog-initiated actions too (no sheet is open).
    _sheetActionPending = true;
    try {
      await recruitmentStore.updateApplicationStage(applicationId, stage);
      if (showToast) {
        notification.toast.success(`Candidature déplacée vers ${getStageTitle(stage)}`);
      }
      clearPendingDrop();
    } catch (e) {
      // Error already handled by store
      rollbackDrag();
    }
  }

  function clearPendingDrop() {
    _pendingDropAppId = null;
    _pendingDropOriginalStage = null;
    _pendingInterviewAppId = null;
    _pendingOfferAppId = null;
    activeItem = null;
  }

  // --- Sheet close detection for rollback ---
  // When a sheet closes without onSuccess being called, rollback the visual state
  let _interviewSheetWasOpen = $state(false);
  let _offerSheetWasOpen = $state(false);

  $effect(() => {
    // Track when interview sheet closes
    if (isInterviewSheetOpen) {
      _interviewSheetWasOpen = true;
    } else if (_interviewSheetWasOpen && _pendingDropAppId) {
      // Sheet closed with pending drop = user cancelled
      rollbackDrag();
    }
  });

  $effect(() => {
    // Track when offer sheet closes
    if (isOfferSheetOpen) {
      _offerSheetWasOpen = true;
    } else if (_offerSheetWasOpen && _pendingDropAppId) {
      // Sheet closed with pending drop = user cancelled
      rollbackDrag();
    }
  });

  // --- Sheet callbacks ---

  function onInterviewScheduled() {
    // Utiliser _pendingInterviewAppId comme fallback car rollbackDrag()
    // peut avoir déjà vidé activeItem avant que ce callback soit appelé
    // ($effect se déclenche quand le sheet pose open=false dans handleSave
    //  avant d'appeler onSuccess).
    const appId = activeItem?.application.applicationId || _pendingInterviewAppId;
    if (appId) {
      doStageChange(appId, 'INTERVIEW', false);
    }
    _pendingDropAppId = null;
    _pendingDropOriginalStage = null;
    _pendingInterviewAppId = null;
    isInterviewSheetOpen = false;
    activeItem = null;
  }

  function onOfferSaved() {
    // Même fix qu'au-dessus: rollbackDrag peut avoir vidé activeItem avant onSuccess
    const appId = activeItem?.application.applicationId || _pendingOfferAppId;
    if (appId) {
      doStageChange(appId, 'OFFER', false);
    }
    _pendingDropAppId = null;
    _pendingDropOriginalStage = null;
    _pendingOfferAppId = null;
    isOfferSheetOpen = false;
    activeItem = null;
  }

  function onFeedbackSaved() {
    isFeedbackSheetOpen = false;
    activeItem = null;
    selectedInterview = null;
  }

  function handleScheduleInterview(item: PipelineApplicationItem) {
    activeItem = item;
    selectedInterview = null;
    isInterviewSheetOpen = true;
  }

  function handleFeedback(item: PipelineApplicationItem) {
    activeItem = item;
    selectedInterview = recruitmentStore.interviews.find(
      i => i.applicationId === item.application.applicationId
    ) ?? null;
    isFeedbackSheetOpen = true;
  }

  function handleEvaluate(item: PipelineApplicationItem) {
    activeItem = item;
    isEvaluationSheetOpen = true;
  }

  function handleEditCandidate(item: PipelineApplicationItem) {
    activeItem = item;
    isCandidateSheetOpen = true;
  }

  function handleViewProfile(item: PipelineApplicationItem) {
    recruitmentStore.profileSheetCandidateId = item.candidate.id;
    recruitmentStore.profileSheetOpen = true;
  }

  // handleRetry now handled by parent AsyncView (refetch)
</script>


<div class="flex-1 flex flex-col min-h-0 h-full overflow-hidden">
  <div class="flex h-full gap-4 p-4 py-2 overflow-x-auto overflow-y-hidden bg-slate-50/10" in:fade={{ duration: 200 }}>
      {#each filteredPipelineData as column (column.stage)}
        <div class="flex-1 min-w-[320px] max-w-100 h-full">
          <PipelineColumn
            stage={column.stage}
            title={column.title}
            applications={column.applications}
            onScheduleInterview={handleScheduleInterview}
            onViewProfile={handleViewProfile}
            onUpdateStage={(item, stage) => handleApplicationDrop(item.application.applicationId, stage as CandidateStage)}
            onDrop={handleApplicationDrop}
            onFeedback={handleFeedback}
            onEvaluate={handleEvaluate}
            onApplicationEdit={handleEditCandidate}
          />
        </div>
      {/each}
    </div>
</div>


<InterviewSheet 
  bind:open={isInterviewSheetOpen} 
  candidate={_interviewCandidate} 
  interview={_interviewInterview} 
  applicationId={_pendingInterviewAppId || ''} 
  onSuccess={onInterviewScheduled}
/>

<OfferSheet 
  bind:open={isOfferSheetOpen} 
  application={_offerApplication} 
  onSuccess={onOfferSaved}
/>

<CandidateSheet 
  bind:open={isCandidateSheetOpen} 
  candidate={_candidateCandidate} 
  campaignId={_candidateCampaignId} 
/>

<EvaluationSheet 
  bind:open={isEvaluationSheetOpen} 
  application={_evaluationApplication} 
  evaluationTemplate={evaluationTemplate} 
/>

<FeedbackSheet 
  bind:open={isFeedbackSheetOpen} 
  interview={_feedbackInterview} 
  onsaved={onFeedbackSaved} 
/>


<style>
  div::-webkit-scrollbar {
    height: 8px;
  }
  div::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
</style>

