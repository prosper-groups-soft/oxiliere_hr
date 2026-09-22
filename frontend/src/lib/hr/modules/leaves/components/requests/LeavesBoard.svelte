<script lang="ts">
  import { fly } from 'svelte/transition';
  import { flip } from 'svelte/animate';
  import { cubicOut } from 'svelte/easing';
  import { get } from 'svelte/store';
  import { leavesStore } from '../../stores/leaves.svelte';
  import { useLeaveRequestsQuery, useApproveLeaveRequestMutation, useRejectLeaveRequestMutation } from '../../queries/leaveQueries';
  import { LEAVE_TYPE_LABELS, LEAVE_STATUS_LABELS } from '../../constants/leaves';
  import type { LeaveType, LeaveStatus } from '../../types/types';
  import type { LeaveRequest } from '../../types/types';
  import LeaveRequestRow from './views/LeaveRequestRow.svelte';
  import DataPagination from '@/hr/components/layout/elements/DataPagination.svelte';
  import LeaveRequestSheet from './sheets/LeaveRequestSheet.svelte';
  import SearchBar from '@/hr/components/shared/elements/SearchBar.svelte';
  import FilterChips from '@/hr/components/shared/elements/FilterChips.svelte';
  import Empty from '@/hr/components/shared/containers/empty/Empty.svelte';
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import LeavesActions from './actions/LeavesActions.svelte';
  import { ui } from '@/hr/stores/ui.svelte';
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
  import LoadingBar from '@/hr/components/layout/elements/LoadingBar.svelte';
  import { notification } from '@/hr/stores/notification.svelte';
  import { leaveRequestsEndpoint } from '../../api/leaveRequests.endpoints';
  import LeaveAttachmentPreview from './views/LeaveAttachmentPreview.svelte';
  import { getMediaUrl } from '@/hr/utilities/common/media';


  // Reactive query avec les getters — le backend gère la pagination, les filtres et le tri
  const leaveQuery = useLeaveRequestsQuery(
    () => leavesStore.currentPage,
    () => leavesStore.perPage,
    () => leavesStore.filters.search,
    () => ({ type: leavesStore.filters.type, status: leavesStore.filters.status, orgUnit: leavesStore.filters.orgUnit }),
    () => leavesStore.sortBy,
    () => leavesStore.sortOrder as 'asc' | 'desc',
  );

  const approveMutation = useApproveLeaveRequestMutation();
  const rejectMutation = useRejectLeaveRequestMutation();
  // Re-fetch quand les filtres, le tri ou la recherche changent (comme la page employés)
  $effect(() => {
    leavesStore.filters.search;
    leavesStore.filters.type;
    leavesStore.filters.status;
    leavesStore.filters.orgUnit;
    leavesStore.sortBy;
    leavesStore.sortOrder;
    leavesStore.currentPage;
    leavesStore.perPage;
    get(leaveQuery).refetch();
  });

  // Données directement depuis TanStack Query + sync pagination
  const queryData = $derived($leaveQuery.data);
  const requests = $derived(queryData?.results ?? []);
  const totalCount = $derived(queryData?.count ?? 0);
  const pendingCount = $derived(requests.filter(r => r.status === 'pending').length);
  const activeFiltersCount = $derived(leavesStore.activeFiltersCount);

  // Synchroniser le totalCount dans le store
  $effect(() => {
    if (totalCount > 0 || $leaveQuery.isFetched) {
      leavesStore.setTotal(totalCount);
    }
  });
  let showRequestSheet = $state(false);
  let editRequest = $state<any>(null);

  // Attachment preview state (single instance)
  let attachmentRequest = $state<LeaveRequest | null>(null);
  const attachmentPreviewUrl = $derived(getMediaUrl(attachmentRequest?.attachment));

  // Construire un objet filters enrichi qui inclut la recherche textuelle
  // pour que FilterChips puisse l'afficher
  const filtersWithSearch = $derived.by((): Record<string, string[]> => {
    const f: Record<string, string[]> = {
      orgUnit: leavesStore.filters.orgUnit,
      type: leavesStore.filters.type,
      status: leavesStore.filters.status,
    };
    if (leavesStore.filters.search) {
      f.search = [leavesStore.filters.search];
    }
    return f;
  });

  function getFilterDisplayLabel(key: string, value: unknown) {
    if (key === 'search') return `Recherche: “${value}”`;
    if (key === 'type') return LEAVE_TYPE_LABELS[value as LeaveType] ?? String(value);
    if (key === 'status') return LEAVE_STATUS_LABELS[value as LeaveStatus] ?? String(value);
    return String(value);
  }

  function openAddRequest() {
    editRequest = null;
    showRequestSheet = true;
  }

  function handleEditRequest(request: any) {
    editRequest = request;
    showRequestSheet = true;
  }

  function formatShortDate(dateStr: string) {
    return new Date(dateStr + 'T00:00:00').toLocaleDateString('fr-FR', { day: 'numeric', month: 'short' });
  }

  function getTypeLabel(request: LeaveRequest) {
    return LEAVE_TYPE_LABELS[request.type] || 'Congé';
  }

  function handleShowAttachment(request: LeaveRequest) {
    attachmentRequest = request;
  }

  function handleCloseAttachment() {
    attachmentRequest = null;
  }

  /** Approuver une demande — avec modale de confirmation */
  function handleApprove(request: LeaveRequest) {
    const typeLabel = getTypeLabel(request);
    const dateRange = `${formatShortDate(request.startDate)} — ${formatShortDate(request.endDate)}`;

    if (request.type === 'sick') {
      checkOverlapThenApprove(request, typeLabel, dateRange);
    } else {
      showApproveConfirm(request, typeLabel, dateRange, null);
    }
  }

  async function checkOverlapThenApprove(request: LeaveRequest, typeLabel: string, dateRange: string) {
    try {
      const overlap = await leaveRequestsEndpoint.checkOverlap(
        request.employeeId,
        request.startDate,
        request.endDate,
        'SICK,CIRCUMSTANCE,UNPAID'
      );
      showApproveConfirm(request, typeLabel, dateRange, overlap);
    } catch {
      showApproveConfirm(request, typeLabel, dateRange, null);
    }
  }

  function showApproveConfirm(
    request: LeaveRequest,
    typeLabel: string,
    dateRange: string,
    overlap: { hasOverlap: boolean; leaves: Array<{ start_date: string; end_date: string; requested_days: number }> } | null
  ) {
    const hasOverlap = overlap?.hasOverlap && overlap.leaves.length > 0;

    let message = `Approuver la demande de ${typeLabel} de <strong>${request.employeeName}</strong> du ${dateRange} (${Math.round(request.days)} jour${Math.round(request.days) > 1 ? 's' : ''}) ?`;

    if (hasOverlap) {
      message += `<br><br><strong>⚠️ Chevauchement détecté</strong><br>`;
      message += `Cette période chevauche un ou plusieurs congés annuels qui seront <strong>automatiquement convertis</strong> en congé maladie lors de l'approbation :<br>`;
      for (const l of overlap.leaves) {
        message += `• Du ${formatShortDate(l.start_date)} au ${formatShortDate(l.end_date)} (${Math.round(l.requested_days)} jour${Math.round(l.requested_days) > 1 ? 's' : ''})<br>`;
      }
    }

    notification.confirm({
      title: hasOverlap
        ? 'Confirmer l\'approbation avec conversion'
        : 'Confirmer l\'approbation',
      message,
      type: hasOverlap ? 'info' : 'warning',
      yesText: 'Approuver',
      noText: 'Annuler',
      onYes: async () => {
        await $approveMutation.mutateAsync(request.id);
      },
    });
  }

  /** Refuser une demande — avec modale de confirmation */
  function handleReject(request: LeaveRequest) {
    const typeLabel = getTypeLabel(request);
    const dateRange = `${formatShortDate(request.startDate)} — ${formatShortDate(request.endDate)}`;

    notification.confirm({
      title: 'Confirmer le refus',
      message: `Refuser la demande de ${typeLabel} de <strong>${request.employeeName}</strong> du ${dateRange} (${Math.round(request.days)} jour${Math.round(request.days) > 1 ? 's' : ''}) ?`,
      type: 'danger',
      yesText: 'Refuser',
      noText: 'Annuler',
      onYes: async () => {
        await $rejectMutation.mutateAsync({ requestId: request.id });
      },
    });
  }

  // Enregistrer les actions dans le store UI (comme la page employés)
  $effect(() => {
    ui.addActions('leaves', LeavesActionsSnippet);
    return () => {
      ui.removeActions('leaves');
    };
  });
</script>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={filtersWithSearch}
      activeFiltersCount={activeFiltersCount}
      getDisplayLabel={getFilterDisplayLabel}
      onRemove={(key, value) => {
        if (key === 'search') {
          leavesStore.setSearch('');
        } else {
          leavesStore.toggleFilter(key as any, value);
        }
      }}
      onReset={() => leavesStore.resetFilters()}
      class="py-1 pb-1.5 px-6 border-b border-slate-50"
    />

    <!-- Overhead loading bar during refetch -->
    <LoadingBar loading={$leaveQuery.isFetching} />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      {#if $leaveQuery.isPending}
        <div class="flex-1 flex items-center justify-center" in:fly={{ y: 15, duration: 300 }}>
          <AnimateSpin text="Chargement des congés" />
        </div>
      {:else if requests.length === 0}
        <div class="flex-1 flex items-center justify-center" in:fly={{ y: 15, duration: 300 }}>
          <Empty 
            title="Aucune demande" 
            description={activeFiltersCount > 0 || leavesStore.filters.search
              ? `Aucune demande de congé ne correspond à vos critères${leavesStore.filters.search ? ' pour « ' + leavesStore.filters.search + ' »' : ''}.`
              : "Aucune demande de congé n'a encore été soumise."}
            icon="calendar-off"
            iconSize={28}
            iconStrokeWidth={1.3}
            iconClass="text-slate-300"
          >
            {#if activeFiltersCount > 0}
              <Button variant="ghost" onclick={() => leavesStore.resetFilters()} class="h-7 bg-slate-50">
                <AppIcon name="x" size={16} class="text-slate-400" />
                Réinitialiser les filtres
              </Button>
            {:else}
              <Button onclick={openAddRequest} class="h-7">
                <AppIcon name="plus" size={15} />
                Nouvelle demande
              </Button>
            {/if}
          </Empty>
        </div>
      {:else}
        <div class="flex-1 overflow-y-auto custom-scrollbar" in:fly={{ y: 15, duration: 300, delay: 80 }}>
          
          <!-- Column Headers -->
          <div class="sticky top-0 z-10 flex items-center h-8 px-6 bg-white border-b border-slate-100">
            <span class="w-[25%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
            <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Type</span>
            <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Période</span>
            <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Motif</span>
            <span class="w-[10%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</span>
            <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right">Actions</span>
          </div>

          {#each requests as request (request.id)}
            <div animate:flip={{ duration: 350, easing: cubicOut }}>
              <LeaveRequestRow {request} onApprove={handleApprove} onReject={handleReject} onEdit={handleEditRequest} onShowAttachment={handleShowAttachment} />
            </div>
          {/each}
        </div>

        {#if totalCount > 0}
          <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10 shrink-0">
            <DataPagination 
              currentCount={requests.length}
              totalCount={totalCount}
              currentPage={leavesStore.currentPage}
              totalPages={leavesStore.totalPages}
              perPage={leavesStore.perPage}
              onPageChange={(p) => leavesStore.setPage(p)}
              onPerPageChange={(s) => leavesStore.setPerPage(s)}
              onNext={() => leavesStore.nextPage()}
              onPrev={() => leavesStore.prevPage()}
              unitLabel="demandes"
            />
          </div>
        {/if}
      {/if}
    </main>
  </div>
</div>


<!-- WRAPPER FOR ui.addActions -->
{#snippet LeavesActionsSnippet()}
  <LeavesActions requests={requests} onAdd={openAddRequest} />
{/snippet}


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
    <div class="flex items-center justify-between">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={leavesStore.filters.search} 
          placeholder="Rechercher un employé ou un département..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => leavesStore.setSearch("")}
        />
      </div>
      
      <!-- Quick Stats -->
      {@render QuickStats()}
    </div>
  </div>
{/snippet}


{#snippet QuickStats()}
  <div class="flex items-center gap-5 px-4 py-1">
    <div class="flex items-center gap-2">
      <AppIcon name="calendar-days" size={17} class="text-slate-500" />
      <span class="text-sm font-semibold text-slate-800 tabular-nums">{totalCount}</span>
      <span class="text-xs text-slate-400">demandes</span>
    </div>
    <div class="flex items-center gap-2">
      <AppIcon name="clock" size={17} class="text-amber-500" />
      <span class="text-sm font-semibold text-amber-600 tabular-nums">{pendingCount}</span>
      <span class="text-xs text-slate-400">en attente</span>
    </div>
    {#if activeFiltersCount > 0}
      <div class="flex items-center gap-2">
        <AppIcon name="filter" size={17} class="text-blue-500" />
        <span class="text-sm font-semibold text-blue-600 tabular-nums">{activeFiltersCount}</span>
        <span class="text-xs text-slate-400">filtres</span>
      </div>
    {/if}
  </div>
{/snippet}


<!-- Leave Request Sheet -->
<LeaveRequestSheet bind:open={showRequestSheet} bind:request={editRequest} />


{#if attachmentRequest?.attachment}
  <LeaveAttachmentPreview
    fileUrl={attachmentPreviewUrl}
    onClose={handleCloseAttachment}
  />
{/if}




