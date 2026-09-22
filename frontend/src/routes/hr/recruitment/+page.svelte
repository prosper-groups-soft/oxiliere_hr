<script lang="ts">
  import DataPagination from "@/hr/components/layout/elements/DataPagination.svelte";
  import CampaignCard from "@/hr/modules/recruitment/components/lists/views/campaign/CampaignCard.svelte";
  import SearchBar from "@/hr/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/hr/components/shared/elements/FilterChips.svelte";
  import CampaignSheet from "@/hr/modules/recruitment/components/shared/sheets/campaign/CampaignSheet.svelte";
  import { notification } from "@/hr/stores/notification.svelte";
  import { ui } from "@/hr/stores/ui.svelte";
  import { CAMPAIGN_STATUS_LABELS, CAMPAIGN_TYPE_LABELS } from "@/hr/modules/recruitment/constants/recruitment";
  import type { RecruitmentCampaign } from "@/hr/modules/recruitment/types/types";
  import { createFilterState } from "@/hr/async/filters/filterState.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import AsyncView from "@/hr/async/components/AsyncView.svelte";
  import { recruitmentService } from "@/hr/modules/recruitment/services/recruitmentService";
  import { onMount } from 'svelte';

  const filterState = createFilterState<{ status: string[], jobNames: string[] }>({ status: [], jobNames: [] });

  const campaignsRes = useAsyncResource(
    () => ({
      queryKey: ['recruitment', 'campaigns', filterState.page, filterState.perPage, filterState.search, filterState.filters.status[0] ?? '', filterState.filters.jobNames, filterState.sortBy, filterState.sortOrder],
      queryFn: () => recruitmentService.listJobOffers(filterState.page, filterState.perPage, undefined, true, filterState.search, filterState.filters.status[0] ?? '', filterState.filters.jobNames, filterState.sortBy, filterState.sortOrder)
    }),
    { mapData: (d: any) => ({ items: d.results, total: d.count, totalPages: Math.ceil(d.count / filterState.perPage) }) }
  );

  const displayFilters = $derived({ ...filterState.filters, ...(filterState.search ? { search: [filterState.search] } : {}) });
  let isSheetOpen = $state(false);
  let selectedCampaign = $state<RecruitmentCampaign | null>(null);

  function openNewCampaign() { selectedCampaign = null; isSheetOpen = true; }
  function handleEdit(c: RecruitmentCampaign) { selectedCampaign = c; isSheetOpen = true; }
  function handleDelete(c: RecruitmentCampaign) {
    notification.confirm({
      title: 'Supprimer la campagne ?', message: 'Cette action est irréversible.', type: 'danger', yesText: 'Supprimer', noText: 'Annuler',
      onYes: async () => { notification.toast.success('Campagne supprimée'); campaignsRes.refetch(); }
    });
  }
  onMount(() => {});
  function getFilterDisplayLabel(key: string, value: string) {
    if (key === 'search') return `Recherche : ${value}`;
    if (key === 'status') return CAMPAIGN_STATUS_LABELS[value] || value;
    if (key === 'type') return CAMPAIGN_TYPE_LABELS[value] || value;
    if (key === 'jobName') return `Poste: ${value}`;
    return value;
  }
  $effect(() => { ui.addActions('recruitment', RecruitmentActionsSnippet); return () => ui.removeActions('recruitment'); });
</script>

<svelte:head><title>Oxiliere HR - Campagnes de Recrutement</title></svelte:head>

<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}
  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips filters={displayFilters} activeFiltersCount={filterState.activeFiltersCount + (filterState.search ? 1 : 0)} onRemove={(k,v)=>k==='search'?filterState.setSearch(''):filterState.toggleFilter(k as any, v)} onReset={()=>filterState.resetFilters()} getDisplayLabel={getFilterDisplayLabel} class="border-b border-slate-100 pt-0 pb-1.5 px-4.5" />
    <AsyncView state={campaignsRes} loadingText="Chargement des campagnes" emptyWhen={(d)=>d.total===0}>
      {#snippet children(data)}
        {#if data.items.length===0}
          <div class="flex-1 flex items-center justify-center"><p class="text-slate-400">Aucune campagne</p></div>
        {:else}
          <div class="flex-1 overflow-y-auto min-h-0">
            <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 xl:grid-cols-4 gap-6 p-4">
              {#each data.items as campaign}<CampaignCard {campaign} onEdit={handleEdit} onDelete={handleDelete} />{/each}
            </div>
          </div>
        {/if}
      {/snippet}
    </AsyncView>
    {#if campaignsRes.data && campaignsRes.data.total>0}
      <div class="px-3 bg-slate-50/80 border-t border-[#e9eaea]">
        <DataPagination currentCount={campaignsRes.data.items.length} totalCount={campaignsRes.data.total} currentPage={filterState.page} totalPages={campaignsRes.data.totalPages} perPage={filterState.perPage} onPageChange={(p)=>filterState.setPage(p)} onPerPageChange={(s)=>{filterState.setPerPage(s); filterState.setPage(1);}} onNext={()=>{if(filterState.page < campaignsRes.data!.totalPages) filterState.setPage(filterState.page+1)}} onPrev={()=>{if(filterState.page>1) filterState.setPage(filterState.page-1)}} unitLabel="campagnes" />
      </div>
    {/if}
  </div>
</div>

{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2 pt-2 border-b border-slate-100 px-4 mr-4">
    <div class="flex items-center gap-3"><div class="flex-1 ml-0.5"><SearchBar bind:value={filterState.search} placeholder="Rechercher une campagne..." class="w-125" inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]" iconSize={22} onClear={()=>filterState.setSearch("")} /></div></div>
  </div>
{/snippet}

<CampaignSheet bind:open={isSheetOpen} campaign={selectedCampaign} />
{#snippet RecruitmentActionsSnippet()}<div></div>{/snippet}
