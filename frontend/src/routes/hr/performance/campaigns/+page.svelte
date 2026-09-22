<script lang="ts">
  import { fade } from 'svelte/transition';
  import DataPagination from '@/hr/components/layout/elements/DataPagination.svelte';
  import SearchBar from '@/hr/components/shared/elements/SearchBar.svelte';
  import FilterChips from '@/hr/components/shared/elements/FilterChips.svelte';
  import { useActivateCampaignMutation, useCloseCampaignMutation } from '@/hr/modules/performance/queries/performanceQueries';
  import { CAMPAIGN_STATUS_LABELS, CAMPAIGN_TYPE_LABELS } from '@/hr/modules/performance/constants';
  import type { Campaign } from '@/hr/modules/performance/types/types';
  import CampaignSheet from '@/hr/modules/performance/components/campaigns/sheets/CampaignSheet.svelte';
  import CampaignList from '@/hr/modules/performance/components/campaigns/views/CampaignList.svelte';
  import CampaignsActions from '@/hr/modules/performance/components/campaigns/actions/CampaignsActions.svelte';
  import { ui } from '@/hr/stores/ui.svelte';
  import { createFilterState } from "@/hr/async/filters/filterState.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import AsyncView from "@/hr/async/components/AsyncView.svelte";
  import { performanceService } from "@/hr/modules/performance/services/performance.service";

  const uiState = createFilterState<{ status: string[], campaign_type: string[] }>({ status: [], campaign_type: [] });

  const campaignsRes = useAsyncResource(
    () => ({
      queryKey: ['performance', 'campaigns', uiState.page, uiState.perPage, uiState.search, uiState.filters.status[0] ?? '', uiState.filters.campaign_type[0] ?? ''],
      queryFn: () => performanceService.listCampaigns({ page: uiState.page, perPage: uiState.perPage, search: uiState.search, status: uiState.filters.status[0], campaign_type: uiState.filters.campaign_type[0] } as any)
    }),
    { mapData: (d: any) => ({ items: d.results ?? [], total: d.count ?? 0, totalPages: Math.ceil((d.count ?? 0) / uiState.perPage) }) }
  );

  $effect(() => { ui.addActions('campaigns', CampaignsActionsSnippet); return () => ui.removeActions('campaigns'); });

  function getFilterDisplayLabel(key: string, value: string): string {
    if (key === 'status') return CAMPAIGN_STATUS_LABELS[value as keyof typeof CAMPAIGN_STATUS_LABELS] || value;
    if (key === 'campaign_type') return CAMPAIGN_TYPE_LABELS[value as keyof typeof CAMPAIGN_TYPE_LABELS] || value;
    if (key === 'search') return `Recherche: "${value}"`;
    return value;
  }

  let sheetOpen = $state(false);
  let editingCampaign = $state<Campaign | null>(null);
  function openCreateSheet() { editingCampaign = null; sheetOpen = true; }
  function openEditSheet(c: Campaign) { editingCampaign = c; sheetOpen = true; }
  function handleSheetClose() { sheetOpen = false; editingCampaign = null; }
  const activateMutation = useActivateCampaignMutation();
  const closeMutation = useCloseCampaignMutation();
  const activateState = $derived($activateMutation);
  const closeState = $derived($closeMutation);
  async function handleActivate(id: string) { $activateMutation.mutate(id); }
  async function handleClose(id: string) { $closeMutation.mutate(id); }

  const filtersWithSearch = $derived.by(() => {
    const f: Record<string,string[]> = {};
    if (uiState.filters.status.length) f.status = uiState.filters.status;
    if (uiState.filters.campaign_type.length) f.campaign_type = uiState.filters.campaign_type;
    if (uiState.search) f.search = [uiState.search];
    return f;
  });
</script>

<svelte:head><title>Oxiliere RH - Campagnes</title></svelte:head>

<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}
  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips filters={filtersWithSearch} activeFiltersCount={uiState.activeFiltersCount + (uiState.search ? 1 : 0)} getDisplayLabel={getFilterDisplayLabel} onRemove={(k,v)=>k==='search'?uiState.setSearch(''):uiState.toggleFilter(k as any, v)} onReset={()=>uiState.resetFilters()} class="py-1 pb-1.5 px-6 border-b border-slate-50" />
    <AsyncView state={campaignsRes} loadingText="Chargement des campagnes" emptyWhen={(d)=>d.total===0} isFiltered={uiState.activeFiltersCount>0 || !!uiState.search} searchQuery={uiState.search} onResetFilters={()=>uiState.resetFilters()} onCreate={openCreateSheet} createLabel="Nouvelle campagne">
      {#snippet children(data)}
        <div class="flex-1 overflow-y-auto min-h-0" transition:fade={{ duration: 200 }}>
          <CampaignList campaigns={data.items} onEdit={openEditSheet} onActivate={handleActivate} onClose={handleClose} isActivating={activateState.isPending} isClosing={closeState.isPending} />
        </div>
      {/snippet}
    </AsyncView>
    {#if campaignsRes.data && campaignsRes.data.total>0}
      <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
        <DataPagination currentCount={campaignsRes.data.items.length} totalCount={campaignsRes.data.total} currentPage={uiState.page} totalPages={campaignsRes.data.totalPages} perPage={uiState.perPage} onPageChange={(p)=>uiState.setPage(p)} onPerPageChange={(s)=>uiState.setPerPage(s)} onNext={()=>uiState.nextPage()} onPrev={()=>uiState.prevPage()} unitLabel="campagnes" />
      </div>
    {/if}
  </div>
</div>

{#snippet Header()}
  <div class="flex items-center px-5 py-1.5 border-b border-slate-50">
    <SearchBar bind:value={uiState.search} placeholder="Rechercher une campagne..." class="w-125" inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]" iconSize={22} onClear={() => uiState.setSearch('')} />
  </div>
{/snippet}
{#snippet CampaignsActionsSnippet()}<CampaignsActions onCreate={openCreateSheet} />{/snippet}

<CampaignSheet bind:open={sheetOpen} campaign={editingCampaign} onclose={handleSheetClose} />
