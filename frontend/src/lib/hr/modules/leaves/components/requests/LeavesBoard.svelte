<script lang="ts">
  import { fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { cubicOut } from 'svelte/easing';
  import LeaveRequestRow from './views/LeaveRequestRow.svelte';
  import DataPagination from '@/hr/components/layout/elements/DataPagination.svelte';
  import LeaveRequestSheet from './sheets/LeaveRequestSheet.svelte';
  import SearchBar from '@/hr/components/shared/elements/SearchBar.svelte';
  import FilterChips from '@/hr/components/shared/elements/FilterChips.svelte';
  import { useApproveLeaveRequestMutation, useRejectLeaveRequestMutation } from '../../queries/leaveQueries';
  import { LEAVE_TYPE_LABELS, LEAVE_STATUS_LABELS } from '../../constants/leaves';
  import type { LeaveType, LeaveStatus, LeaveRequest } from '../../types/types';
  import LeavesActions from './actions/LeavesActions.svelte';
  import { ui } from '@/hr/stores/ui.svelte';
  import { notification } from '@/hr/stores/notification.svelte';
  import { leaveRequestsEndpoint } from '../../api/leaveRequests.endpoints';
  import LeaveAttachmentPreview from './views/LeaveAttachmentPreview.svelte';
  import { getMediaUrl } from '@/hr/utilities/common/media';
  import { createFilterState } from "@/hr/async/filters/filterState.svelte";
  import { useAsyncResource } from "@/hr/async/core/useAsyncResource.svelte";
  import AsyncView from "@/hr/async/components/AsyncView.svelte";
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';

  const uiState = createFilterState<{ type: string[], status: string[], orgUnit: string[] }>({ type: [], status: [], orgUnit: [] });

  const leavesRes = useAsyncResource(
    () => ({
      queryKey: ['leaves', uiState.page, uiState.perPage, uiState.search, uiState.filters, uiState.sortBy, uiState.sortOrder],
      queryFn: () => leaveRequestsEndpoint.listRequests({ page: uiState.page, perPage: uiState.perPage, search: uiState.search, filters: uiState.filters, sortBy: uiState.sortBy, sortOrder: uiState.sortOrder } as any)
    }),
    { mapData: (d: any) => ({ items: d.results ?? [], total: d.count ?? 0, totalPages: Math.ceil((d.count ?? 0) / uiState.perPage) }) }
  );

  const approveMutation = useApproveLeaveRequestMutation();
  const rejectMutation = useRejectLeaveRequestMutation();

  let showRequestSheet = $state(false);
  let editRequest = $state<any>(null);
  let attachmentRequest = $state<LeaveRequest | null>(null);
  const attachmentPreviewUrl = $derived(getMediaUrl(attachmentRequest?.attachment));

  const filtersWithSearch = $derived.by((): Record<string, string[]> => {
    const f: Record<string, string[]> = { orgUnit: uiState.filters.orgUnit, type: uiState.filters.type, status: uiState.filters.status };
    if (uiState.search) f.search = [uiState.search];
    return f;
  });

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'search') return `Recherche: “${value}”`;
    if (key === 'type') return LEAVE_TYPE_LABELS[value as LeaveType] ?? String(value);
    if (key === 'status') return LEAVE_STATUS_LABELS[value as LeaveStatus] ?? String(value);
    return String(value);
  }
  
  function openAddRequest() { editRequest = null; showRequestSheet = true; }
  function handleEditRequest(r: any) { editRequest = r; showRequestSheet = true; }
  function formatShortDate(s: string) { return new Date(s + 'T00:00:00').toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' }); }
  function getTypeLabel(r: LeaveRequest) { return LEAVE_TYPE_LABELS[r.type] || 'Congé'; }
  function handleShowAttachment(r: LeaveRequest) { attachmentRequest = r; }
  function handleCloseAttachment() { attachmentRequest = null; }
  
  function handleApprove(request: LeaveRequest) {
    const typeLabel = getTypeLabel(request);
    const dateRange = `${formatShortDate(request.startDate)} — ${formatShortDate(request.endDate)}`;
    if (request.type === 'sick') {
      leaveRequestsEndpoint.checkOverlap(request.employeeId, request.startDate, request.endDate, 'SICK,CIRCUMSTANCE,UNPAID').then(overlap => showApproveConfirm(request, typeLabel, dateRange, overlap)).catch(()=>showApproveConfirm(request, typeLabel, dateRange, null));
    } else showApproveConfirm(request, typeLabel, dateRange, null);
  }

  function showApproveConfirm(request: LeaveRequest, typeLabel: string, dateRange: string, overlap: any) {
    const hasOverlap = overlap?.hasOverlap && overlap.leaves.length > 0;
    let message = `Approuver la demande de ${typeLabel} de <strong>${request.employeeName}</strong> du ${dateRange} (${Math.round(request.days)} jour${Math.round(request.days) > 1 ? 's' : ''}) ?`;
    if (hasOverlap) { message += `<br><br><strong>⚠️ Chevauchement détecté</strong><br>`; for (const l of overlap.leaves) message += `• Du ${formatShortDate(l.start_date)} au ${formatShortDate(l.end_date)}<br>`; }
    notification.confirm({ title: hasOverlap ? 'Confirmer l\'approbation avec conversion' : 'Confirmer l\'approbation', message, type: hasOverlap ? 'info' : 'warning', yesText: 'Approuver', noText: 'Annuler', onYes: async () => { await $approveMutation.mutateAsync(request.id); leavesRes.refetch(); } });
  }

  function handleReject(request: LeaveRequest) {
    const typeLabel = getTypeLabel(request);
    const dateRange = `${formatShortDate(request.startDate)} — ${formatShortDate(request.endDate)}`;
    notification.confirm({ title: 'Confirmer le refus', message: `Refuser la demande de ${typeLabel} de <strong>${request.employeeName}</strong> du ${dateRange} ?`, type: 'danger', yesText: 'Refuser', noText: 'Annuler', onYes: async () => { await $rejectMutation.mutateAsync({ requestId: request.id }); leavesRes.refetch(); } });
  }

  $effect(() => { ui.addActions('leaves', LeavesActionsSnippet); return () => ui.removeActions('leaves'); });
</script>

<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}
  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips filters={filtersWithSearch} activeFiltersCount={uiState.activeFiltersCount + (uiState.search ? 1 : 0)} getDisplayLabel={getFilterDisplayLabel} onRemove={(k,v)=>k==='search'?uiState.setSearch(''):uiState.toggleFilter(k as any, v)} onReset={()=>uiState.resetFilters()} class="py-1 pb-1.5 px-6 border-b border-slate-50" />
    <AsyncView state={leavesRes} loadingText="Chargement des congés" emptyWhen={(d)=>d.total===0} isFiltered={uiState.activeFiltersCount>0 || !!uiState.search} searchQuery={uiState.search} onResetFilters={()=>uiState.resetFilters()} onCreate={openAddRequest} createLabel="Nouvelle demande">
      {#snippet children(data)}
        <div class="flex-1 overflow-y-auto custom-scrollbar" in:fly={{ y: 15, duration: 300, delay: 80 }}>
          <div class="sticky top-0 z-10 flex items-center h-8 px-6 bg-white border-b border-slate-100">
            <span class="w-[25%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
            <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Type</span>
            <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Période</span>
            <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Motif</span>
            <span class="w-[10%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</span>
            <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right">Actions</span>
          </div>
          {#each data.items as request (request.id)}<div animate:flip={{ duration: 350, easing: cubicOut }}><LeaveRequestRow {request} onApprove={handleApprove} onReject={handleReject} onEdit={handleEditRequest} onShowAttachment={handleShowAttachment} /></div>{/each}
        </div>
        {#if data.total>0}
          <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10 shrink-0">
            <DataPagination currentCount={data.items.length} totalCount={data.total} currentPage={uiState.page} totalPages={data.totalPages} perPage={uiState.perPage} onPageChange={(p)=>uiState.setPage(p)} onPerPageChange={(s)=>uiState.setPerPage(s)} onNext={()=>uiState.nextPage()} onPrev={()=>uiState.prevPage()} unitLabel="demandes" />
          </div>
        {/if}
      {/snippet}
    </AsyncView>
  </div>
</div>

{#snippet LeavesActionsSnippet()}<LeavesActions requests={leavesRes.data?.items ?? []} onAdd={openAddRequest} filterState={uiState} />{/snippet}
{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
    <div class="flex items-center justify-between">
      <div class="flex-1 ml-0.5"><SearchBar bind:value={uiState.search} placeholder="Rechercher un employé ou un département..." class="w-125" inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]" iconSize={22} onClear={() => uiState.setSearch("")} /></div>
      <div class="flex items-center gap-5 px-4 py-1">
        <div class="flex items-center gap-2"><AppIcon name="calendar-days" size={17} class="text-slate-500" /><span class="text-sm font-semibold text-slate-800 tabular-nums">{leavesRes.data?.total ?? 0}</span><span class="text-xs text-slate-400">demandes</span></div>
        <div class="flex items-center gap-2"><AppIcon name="clock" size={17} class="text-amber-500" /><span class="text-sm font-semibold text-amber-600 tabular-nums">{leavesRes.data?.items.filter((r:any)=>r.status==='pending').length ?? 0}</span><span class="text-xs text-slate-400">en attente</span></div>
        {#if uiState.activeFiltersCount>0}<div class="flex items-center gap-2"><AppIcon name="filter" size={17} class="text-blue-500" /><span class="text-sm font-semibold text-blue-600 tabular-nums">{uiState.activeFiltersCount}</span><span class="text-xs text-slate-400">filtres</span></div>{/if}
      </div>
    </div>
  </div>
{/snippet}

<LeaveRequestSheet bind:open={showRequestSheet} bind:request={editRequest} />
{#if attachmentRequest?.attachment}<LeaveAttachmentPreview fileUrl={attachmentPreviewUrl} onClose={handleCloseAttachment} />{/if}
