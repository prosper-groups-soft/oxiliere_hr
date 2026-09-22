<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import CampaignCard from "@/hr/recruitment/components/lists/views/campaign/CampaignCard.svelte";
  import { recruitmentStore } from "@/hr/recruitment/stores/recruitment.svelte";
  import { useJobOffersQuery, syncRecruitmentStore } from "@/hr/recruitment/queries/recruitmentQueries";
  import { onMount } from 'svelte';
  import { fade } from 'svelte/transition';
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import CampaignSheet from "@/hr/recruitment/components/shared/sheets/campaign/CampaignSheet.svelte";
  import { notification } from "@/stores/notification.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { ERROR_MESSAGES, getFriendlyErrorMessage } from "@/constants/errors";
  import RecruitmentActions from "@/hr/recruitment/components/layout/actions/RecruitmentActions.svelte";
  import { ui } from "@/stores/ui.svelte";
  import { CAMPAIGN_STATUS_LABELS, CAMPAIGN_TYPE_LABELS } from "@/hr/recruitment/constants/recruitment";
  import type { RecruitmentCampaign } from "@/hr/recruitment/types/types";


  // Charger les données depuis le backend avec pagination côté serveur
  const jobOffersQuery = useJobOffersQuery(
    () => recruitmentStore.currentPage,
    () => recruitmentStore.perPage,
    () => undefined,
    () => true,
    () => recruitmentStore.searchQuery,
    () => recruitmentStore.campaignFilters.status[0] || '',
    () => recruitmentStore.campaignFilters.jobNames,
    () => recruitmentStore.sortBy,
    () => recruitmentStore.sortOrder
  );

  // Synchroniser le store avec les données de la query
  $effect(() => {
    syncRecruitmentStore($jobOffersQuery);
  });

  // Déclencher un refetch quand la pagination, la recherche, les filtres ou le tri changent
  $effect(() => {
    // Lire les valeurs pour que Svelte les traque
    recruitmentStore.currentPage;
    recruitmentStore.perPage;
    recruitmentStore.searchQuery;
    recruitmentStore.campaignFilters.status;
    recruitmentStore.campaignFilters.jobNames;
    recruitmentStore.sortBy;
    recruitmentStore.sortOrder;

    $jobOffersQuery.refetch();
  });

  // Construire un objet filtres incluant la recherche pour FilterChips
  const displayFilters = $derived({
    ...recruitmentStore.campaignFilters,
    ...(recruitmentStore.searchQuery ? { search: [recruitmentStore.searchQuery] } : {})
  });

  const campaigns = $derived(recruitmentStore.campaigns);

  let isSheetOpen = $state(false);
  let selectedCampaign = $state<RecruitmentCampaign | null>(null);

  function openNewCampaign() {
    selectedCampaign = null;
    isSheetOpen = true;
  }

  function handleEdit(campaign: RecruitmentCampaign) {
    selectedCampaign = campaign;
    isSheetOpen = true;
  }

  function handleDelete(campaign: RecruitmentCampaign) {
    notification.confirm({
      title: 'Supprimer la campagne ?',
      message: 'Cette action est irréversible. Cela supprimera également tous les candidats associés à cette campagne.',
      type: 'danger',
      yesText: 'Supprimer',
      noText: 'Annuler',
      onYes: async () => {
        recruitmentStore.campaigns = recruitmentStore.campaigns.filter(c => c.id !== campaign.id);
        notification.toast.success('Campagne supprimée');
      }
    });
  }

  onMount(() => {
    recruitmentStore.setActiveCampaign(null);
  });

  // Fonction pour afficher les labels lisibles des filtres
  function getFilterDisplayLabel(key: string, value: string): string {
    switch (key) {
      case 'search':
        return `Recherche : ${value}`;

      case 'status':
        return CAMPAIGN_STATUS_LABELS[value] || value;

      case 'type':
        return CAMPAIGN_TYPE_LABELS[value] || value;

      case 'jobName':
        return `Poste: ${value}`;

      default:
        return value;
    }
  }

  // Enregistrer les actions dans le store UI
  $effect(() => {
    ui.addActions('recruitment', RecruitmentActionsSnippet);
    return () => {
      ui.removeActions('recruitment');
    };
  });
</script>


<svelte:head>
  <title>Oxiliere HR - Campagnes de Recrutement</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={displayFilters}
      activeFiltersCount={recruitmentStore.activeFiltersCount}
      onRemove={(key, value) => {
        if (key === 'search') {
          recruitmentStore.searchQuery = '';
        } else {
          recruitmentStore.toggleCampaignFilter(key as any, value);
        }
      }}
      onReset={() => recruitmentStore.resetCampaignFilters()}
      getDisplayLabel={getFilterDisplayLabel}
      class="border-b border-slate-100  pt-0 pb-1.5 px-4.5"
    />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      <!-- Loading state (only if no error yet) -->
      {#if $jobOffersQuery.isLoading && !$jobOffersQuery.error && recruitmentStore.serverTotalCount === 0}
        <div class="flex justify-center items-center h-full">
          <AnimateSpin text="Chargement des campagnes" />
        </div>

      <!-- Error state -->
      {:else if $jobOffersQuery.error && recruitmentStore.serverTotalCount === 0}
        <div class="flex justify-center items-center h-full">
          <Empty
            icon="alert-circle"
            title="Erreur de Connexion"
            description={getFriendlyErrorMessage($jobOffersQuery.error) || ERROR_MESSAGES.NETWORK.UNKNOWN}
            iconClass="text-red-400"
            iconContainerClass="bg-red-50/30"
            iconSize={28}
            iconStrokeWidth={1.3}
          >
            <Button
              onclick={() => $jobOffersQuery.refetch()}
              variant="outline"
              class="h-7 mt-2 rounded-lg transition-colors"
            >
              <AppIcon name="refresh-cw" />
              Réessayer
            </Button>
          </Empty>
        </div>

      <!-- Content state -->
      {:else}
        <!-- État: Données vides -->
        {#if !$jobOffersQuery.isLoading && !$jobOffersQuery.error && campaigns.length === 0}
          <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
            <Empty
              title="Aucune campagne"
              description={recruitmentStore.activeFiltersCount > 0 || recruitmentStore.searchQuery
                ? "Aucun résultat ne correspond à vos critères de recherche."
                : "Aucune campagne de recrutement n'a été créée."}
              icon={recruitmentStore.activeFiltersCount > 0 || recruitmentStore.searchQuery ? "search-x" : "briefcase"}
              iconSize={28}
              iconStrokeWidth={1.3}
              iconClass="text-slate-300"
            >
              {#if recruitmentStore.activeFiltersCount > 0 || recruitmentStore.searchQuery}
                <Button variant="ghost" onclick={() => { recruitmentStore.resetCampaignFilters(); recruitmentStore.searchQuery = ""; }} class="h-7 bg-slate-50">
                  <AppIcon name="x" size={16} class="text-slate-400" />
                  Réinitialiser les filtres
                </Button>
              {:else}
                <Button variant="default" onclick={openNewCampaign} class="h-7">
                  <AppIcon name="plus" size={17} class="text-white" />
                  Créer une campagne
                </Button>
              {/if}
            </Empty>
          </div>

        <!-- État: Données disponibles -->
        {:else}
          <div class="flex-1 overflow-y-auto min-h-0">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-4">
              {#each campaigns as campaign}
                <CampaignCard
                  {campaign}
                  onEdit={handleEdit}
                  onDelete={handleDelete}
                />
              {/each}
            </div>
          </div>
        {/if}
      {/if}

      {#if recruitmentStore.serverTotalCount > 0}
        <div class="px-3 bg-slate-50/80 border-t border-[#e9eaea]">
          <DataPagination 
            currentCount={campaigns.length}
            totalCount={recruitmentStore.serverTotalCount}
            currentPage={recruitmentStore.currentPage}
            totalPages={recruitmentStore.serverTotalPages}
            perPage={recruitmentStore.perPage}
            onPageChange={(p) => recruitmentStore.currentPage = p}
            onPerPageChange={(s) => { recruitmentStore.perPage = s; recruitmentStore.currentPage = 1; }}
            onNext={() => { if (recruitmentStore.currentPage < recruitmentStore.serverTotalPages) recruitmentStore.currentPage++; }}
            onPrev={() => { if (recruitmentStore.currentPage > 1) recruitmentStore.currentPage--; }}
            unitLabel="campagnes"
          />
        </div>
      {/if}
    </main>
  </div>
</div>


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2 pt-2 border-b border-slate-100 px-4 mr-4">
    <div class="flex items-center gap-3">
      <div class="flex-1 ml-0.5">
        <SearchBar
          bind:value={recruitmentStore.searchQuery}
          placeholder="Rechercher une campagne..."
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => recruitmentStore.searchQuery = ""}
        />
      </div>
    </div>
  </div>
{/snippet}


<CampaignSheet bind:open={isSheetOpen} campaign={selectedCampaign} />


<!-- WRAPPER FOR ui.addActions -->
{#snippet RecruitmentActionsSnippet()}
  <RecruitmentActions
    onAdd={openNewCampaign}
  />
{/snippet}

