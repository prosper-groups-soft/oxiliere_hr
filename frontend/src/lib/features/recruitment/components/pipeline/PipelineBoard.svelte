<script lang="ts">
  import PipelineColumn from "./PipelineColumn.svelte";
  import type { Candidate, CandidateStage } from "../../types/types";
  import { recruitmentStore } from "../../stores/recruitment.svelte";
  import { notification } from '@/stores/notification.svelte';
  import { goto } from '$app/navigation';

  // Get reactive pipeline data from store (filtered by campaign)
  const pipelineData = $derived(recruitmentStore.pipelineData);
  const activeCampaignId = $derived(recruitmentStore.activeCampaignId);

  function getStageTitle(stage: CandidateStage): string {
    const titles: Record<CandidateStage, string> = {
      SCREENING: 'Tri',
      SHORTLIST: 'Shortlist',
      INTERVIEW: 'Entretien',
      OFFER: 'Offre',
      REJECTED: 'Rejeté'
    };
    return titles[stage];
  }

  // Handle candidate drop when card is dropped in new zone
  async function handleCandidateDrop(candidateId: string, newStage: CandidateStage) {
    // Find candidate for toast notification
    const candidate = recruitmentStore.candidates.find(c => c.id === candidateId);
    
    // If stage hasn't changed, do nothing
    if (candidate && candidate.currentStage !== newStage) {
      try {
        await recruitmentStore.updateCandidateStage(candidateId, newStage);
        notification.toast.success(
          `${candidate.firstName} ${candidate.lastName} déplacé vers ${getStageTitle(newStage)}`
        );
      } catch (error) {
        notification.toast.error('Erreur lors de la mise à jour du statut');
        console.error('DnD error:', error);
      }
    }
  }

  // Action handlers
  function handleCandidateEdit(candidate: Candidate) {
    notification.toast.info('Modification bientôt disponible');
  }

  function handleCandidateDelete(candidate: Candidate) {
    notification.confirm({
      title: 'Supprimer le candidat ?',
      message: `Voulez-vous vraiment supprimer "${candidate.firstName} ${candidate.lastName}" ?`,
      type: 'danger',
      onYes: async () => {
        try {
          await recruitmentStore.deleteCandidate(candidate.id);
          notification.toast.success('Candidat supprimé avec succès');
        } catch (error) {
          notification.toast.error('Erreur lors de la suppression');
        }
      }
    });
  }

  function handleScheduleInterview(candidate: Candidate) {
    notification.toast.info('Programmation d\'entretien bientôt disponible');
  }

  function handleViewProfile(candidate: Candidate) {
    goto(`/recruitment/${activeCampaignId}/candidates/${candidate.id}`);
  }

  async function handleUpdateStage(candidate: Candidate, newStage: string) {
    try {
      await recruitmentStore.updateCandidateStage(candidate.id, newStage as CandidateStage);
      notification.toast.success(
        `${candidate.firstName} ${candidate.lastName} déplacé vers ${getStageTitle(newStage as CandidateStage)}`
      );
    } catch (error) {
      notification.toast.error('Erreur lors de la mise à jour');
    }
  }
</script>


<div class="flex h-full gap-4 p-4 py-2 overflow-x-auto overflow-y-hidden bg-slate-50/10">
  {#each pipelineData as column (column.stage)}
    <div class="flex-1 min-w-[320px] max-w-[400px] h-full">
      <PipelineColumn
        stage={column.stage as CandidateStage}
        title={column.title}
        candidates={column.candidates}
        onCandidateEdit={handleCandidateEdit}
        onCandidateDelete={handleCandidateDelete}
        onScheduleInterview={handleScheduleInterview}
        onViewProfile={handleViewProfile}
        onUpdateStage={handleUpdateStage}
        onDrop={handleCandidateDrop}
      />
    </div>
  {/each}
</div>


<style>
  div::-webkit-scrollbar {
    height: 8px;
  }
  div::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
</style>

