<script lang="ts">
  import { page } from '$app/state';
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import CampaignHeader from '@/features/recruitment/components/nav/CampaignHeader.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import CandidateProfileSheet from '@/features/recruitment/components/shared/sheets/candidate/CandidateProfileSheet.svelte';
  import { Button } from '@/components/ui/button';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { getFriendlyErrorMessage } from '@/constants/errors';
  import type { RecruitmentCampaign } from '@/features/recruitment/types/types';

  
  let { children } = $props();

  const campaignId = $derived(page.params.campaignId);
  const isCandidateDetail = $derived(!!page.params.candidateId);

  // État LOCAL pour le chargement — pas de conflit avec le store
  let campaignLoading = $state(true);
  let campaignError = $state<string | null>(null);
  let campaignData = $state<RecruitmentCampaign | undefined>(undefined);

  // Charge la campagne avec un état local isolé
  async function loadCampaign() {
    campaignLoading = true;
    campaignError = null;
    campaignData = undefined;
    try {
      recruitmentStore.setActiveCampaign(campaignId ?? null);
      await recruitmentStore.getCampaignDetailsById(campaignId ?? '');
      campaignData = recruitmentStore.currentCampaign;
    } catch (err) {
      campaignError = getFriendlyErrorMessage(err) || 'Erreur lors du chargement de la campagne';
    } finally {
      campaignLoading = false;
    }
  }

  $effect(() => {
    if (campaignId) {
      loadCampaign();
    }
  });
</script>


{#if campaignLoading}
  <div class="h-full flex items-center justify-center">
    <AnimateSpin text="Chargement de la campagne" />
  </div>
{:else if campaignError}
  <div class="h-full flex items-center justify-center">
    <Empty 
      icon="alert-circle" 
      title="Erreur de Connexion" 
      description={campaignError} 
      iconClass="text-red-400" 
      iconContainerClass="bg-red-50/30"
      iconSize={28}
      iconStrokeWidth={1.3}
    >
      <Button 
        onclick={loadCampaign} 
        variant="outline"
        class="h-7 mt-2 rounded-lg transition-colors"
      >          
        <AppIcon name="refresh-cw" />
        Réessayer
      </Button> 
    </Empty>
  </div>
{:else if campaignData}
  {#if !isCandidateDetail}
    <CampaignHeader campaign={campaignData} />
  {/if}
  
  <div class="flex-1 overflow-y-auto custom-scrollbar">
    {@render children?.()}
  </div>
{:else}
  <Empty title="Campagne introuvable" />
{/if}


<CandidateProfileSheet
  bind:open={recruitmentStore.profileSheetOpen}
  bind:candidateId={recruitmentStore.profileSheetCandidateId}
/>


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 6px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
</style>

