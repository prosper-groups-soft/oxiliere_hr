<script lang="ts">
  import PipelineBoard from '@/features/recruitment/components/pipeline/PipelineBoard.svelte';
  import { useCandidatesQuery, syncRecruitmentCandidates } from '@/features/recruitment/queries/recruitmentQueries';
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';
  import { recruitmentService } from '@/features/recruitment/services/recruitmentService';
  import { ui } from '@/stores/ui.svelte';
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";

  
  let { params } = $props();
  const offerId = $derived(params.campaignId);
  
  // Charger les candidats (avec leurs applications)
  const candidatesQuery = useCandidatesQuery(() => offerId, () => 1, () => 100);

  // Synchroniser le store avec les données de la query
  $effect(() => {
    syncRecruitmentCandidates($candidatesQuery);
  });

  // Charger la campagne (pour avoir les positions)
  $effect(() => {
    if (offerId) {
      recruitmentStore.activeCampaignId = offerId;
      // Charger les détails de la campagne pour avoir evaluationTemplate et positions
      recruitmentService.getJobOfferById(offerId).then(campaign => {
        recruitmentStore.currentCampaign = campaign;
      }).catch((err) => {
        console.error('Error loading campaign:', err);
      });
    }
  });

  // Campaign positions for the position filter dropdown
  const campaignPositions = $derived(recruitmentStore.currentCampaign?.positions || []);
  const activePositionIds = $derived(recruitmentStore.pipelinePositionIds);

  // Enregistrer l'action de filtre dans la barre de titre
  $effect(() => {
    ui.addActions('pipeline-position-filter', PositionFilterSnippet);
    return () => {
      ui.removeActions('pipeline-position-filter');
    };
  });
</script>


<div class="h-full flex flex-col overflow-hidden py-2">
  <PipelineBoard />
</div>


{#snippet PositionFilterSnippet()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger>
      <Button
        variant="ghost"
        size="sm"
        class="h-7 px-2.5 text-[0.84rem] text-slate-600 hover:text-slate-900 hover:bg-slate-100"
      >
        <AppIcon name="briefcase" size={15} class="mr-1.5" />
        Postes
        {#if activePositionIds.length > 0}
          <span class="ml-1.5 flex h-4 w-4 items-center justify-center rounded-full bg-primary text-[0.65rem] font-medium text-white">
            {activePositionIds.length}
          </span>
        {/if}
      </Button>
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="start" class="w-56 p-1 z-100">
      <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
        Filtrer par poste
      </DropdownMenu.Label>

      {#each campaignPositions as pos}
        {@const active = activePositionIds.includes(pos.id)}
        <DropdownMenu.Item
          onclick={() => recruitmentStore.togglePipelinePositionFilter(pos.id)}
          class={[
            "text-[0.86rem] py-1.5 cursor-pointer flex items-center justify-between",
            active && "bg-slate-50 font-medium"
          ]}
        >
          <span class="flex items-center gap-2 text-[0.86rem]">
            <AppIcon name="briefcase" size={16} class="text-slate-500" />
            {pos.name}
          </span>
          {#if active}
            <AppIcon name="check" size={14} class="text-slate-600" />
          {/if}
        </DropdownMenu.Item>
      {:else}
        <p class="text-[0.84rem] text-slate-400 px-3 py-3 text-center">
          Aucun poste défini
        </p>
      {/each}

      {#if activePositionIds.length > 0}
        <DropdownMenu.Separator />
        <DropdownMenu.Item
          onclick={() => { recruitmentStore.resetPipelinePositionFilter(); }}
          class="text-[0.86rem] text-red-600 hover:bg-red-50/30! hover:text-red-700! cursor-pointer"
        >
          <AppIcon name="x" size={16} class="text-inherit" />
          Réinitialiser
        </DropdownMenu.Item>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}

