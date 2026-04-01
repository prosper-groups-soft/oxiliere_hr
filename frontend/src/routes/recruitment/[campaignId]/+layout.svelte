<script lang="ts">
  import { page } from '$app/state';
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import CampaignHeader from '@/features/recruitment/components/nav/CampaignHeader.svelte';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';

  let { children } = $props();

  const campaignId = $derived(page.params.campaignId);
  const campaign = $derived(campaignId ? recruitmentStore.getCampaignById(campaignId) : undefined);
  const isCandidateDetail = $derived(!!page.params.candidateId);

  // Set active campaign in store when entering this layout
  $effect(() => {
    if (campaignId) {
      recruitmentStore.setActiveCampaign(campaignId);
    }
  });
</script>


{#if campaign}
  {#if !isCandidateDetail}
    <CampaignHeader {campaign} />
  {/if}
  
  <div class="flex-1 overflow-y-auto custom-scrollbar">
    {@render children?.()}
  </div>
{:else}
  <Empty title="Campagne introuvable" />
{/if}


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

