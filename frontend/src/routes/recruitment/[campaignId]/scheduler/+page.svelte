<script lang="ts">
  import InterviewScheduler from '@/features/recruitment/components/scheduler/InterviewScheduler.svelte';
  import { useInterviewsQuery, useCandidatesQuery, syncInterviewsToStore } from '@/features/recruitment/queries/recruitmentQueries';
  import { recruitmentStore } from '@/features/recruitment/stores/recruitment.svelte';

  
  let { params } = $props();
  const offerId = $derived(params.campaignId);

  // Charger les entretiens filtrés par campagne
  const interviewsQuery = useInterviewsQuery(() => offerId);

  // Synchroniser le store avec les données de la query
  $effect(() => {
    syncInterviewsToStore($interviewsQuery);
  });

  // Charger les candidats (avec applications) pour le sélecteur lors de l'ajout
  const candidatesQuery = useCandidatesQuery(() => offerId);

  // Synchroniser les candidats dans le store
  $effect(() => {
    const data = $candidatesQuery.data as { results: any[]; count: number } | undefined;
    if (data) {
      recruitmentStore.candidates = data.results;
    }
  });

  // Charger la campagne si pas encore faite
  $effect(() => {
    if (offerId && !recruitmentStore.currentCampaign) {
      recruitmentStore.activeCampaignId = offerId;
      recruitmentStore.getCampaignDetailsById(offerId);
    }
  });
</script>


<div class="h-full flex flex-col overflow-hidden">
  <InterviewScheduler />
</div>

