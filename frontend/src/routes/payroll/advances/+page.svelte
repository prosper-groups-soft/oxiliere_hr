<script lang="ts">
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { Badge } from "@/components/ui/badge";
  import { scale } from "svelte/transition";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import { notification } from "@/stores/notification.svelte";
  import AdvanceRequestSheet from "@/features/payroll/components/advances/sheets/AdvanceRequestSheet.svelte";
  import AdvanceCard from "@/features/payroll/components/advances/views/AdvanceCard.svelte";
  import { dndzone, TRIGGERS, type DndEvent } from "svelte-dnd-action";
  import { flip } from "svelte/animate";
  import type { Advance, AdvanceStatus } from "@/features/payroll/types/types";

  // Filter state
  let searchTerm = $state('');
  let showOnlyHighRisk = $state(false);
  
  // Archived pagination
  const ARCHIVED_LIMIT = 10;
  let archivedLimit = $state(ARCHIVED_LIMIT);
  
  // Sheet state
  let showNewRequestForm = $state(false);

  // Filtered advances
  const filteredAdvances = $derived.by(() => {
    return payrollStore.advances.filter(advance => {
      const matchesSearch = advance.employeeName.toLowerCase().includes(searchTerm.toLowerCase()) ||
        advance.reason.toLowerCase().includes(searchTerm.toLowerCase());
      const matchesRisk = !showOnlyHighRisk || advance.riskLevel === 'high';
      return matchesSearch && matchesRisk;
    });
  });

  // Group by status (derived for initial state)
  const pendingAdvances = $derived(filteredAdvances.filter(a => a.status === 'pending'));
  const approvedAdvances = $derived(filteredAdvances.filter(a => a.status === 'approved'));
  const otherAdvances = $derived(filteredAdvances.filter(a => ['rejected', 'completed'].includes(a.status)));

  // Local state for DnD (synced with derived values)
  let pendingItems = $state<Advance[]>([]);
  let approvedItems = $state<Advance[]>([]);
  let otherItems = $state<Advance[]>([]);

  // Sync local state with derived values
  $effect(() => {
    pendingItems = [...pendingAdvances];
  });
  $effect(() => {
    approvedItems = [...approvedAdvances];
  });
  $effect(() => {
    otherItems = [...otherAdvances];
  });

  const flipDurationMs = 200;

  // Stats
  const totalPendingAmount = $derived(
    payrollStore.advances
      .filter(a => a.status === 'pending')
      .reduce((sum, a) => sum + a.amount, 0)
  );

  const activeFiltersCount = $derived(
    (showOnlyHighRisk ? 1 : 0) + (searchTerm ? 1 : 0)
  );

  function resetFilters() {
    searchTerm = '';
    showOnlyHighRisk = false;
    archivedLimit = ARCHIVED_LIMIT;
  }

  function getActiveFilters() {
    const filters: Record<string, string[]> = {};
    if (showOnlyHighRisk) {
      filters.risk = ['high'];
    }
    return filters;
  }

  function handleRemoveFilter(key: string) {
    if (key === 'risk') {
      showOnlyHighRisk = false;
    }
  }

  function handleDndConsider(columnId: 'pending' | 'approved' | 'archived', e: CustomEvent<DndEvent<Advance>>) {
    const { items: newItems } = e.detail;
    if (columnId === 'pending') pendingItems = newItems;
    else if (columnId === 'approved') approvedItems = newItems;
    else otherItems = newItems;
  }

  function handleDndFinalize(
    columnId: 'pending' | 'approved' | 'archived',
    targetStatus: AdvanceStatus,
    e: CustomEvent<DndEvent<Advance>>
  ) {
    const { items: newItems, info } = e.detail;
    
    // Update local state
    if (columnId === 'pending') pendingItems = newItems;
    else if (columnId === 'approved') approvedItems = newItems;
    else otherItems = newItems;
    
    // Only process actual drops (not reorders within same column)
    if (info.trigger === TRIGGERS.DROPPED_INTO_ZONE) {
      handleAdvanceDrop(info.id, targetStatus);
    }
  }

  async function handleAdvanceDrop(advanceId: string, newStatus: AdvanceStatus) {
    const advance = payrollStore.advances.find(a => a.id === advanceId);
    if (!advance || advance.status === newStatus) return;

    const statusLabels: Record<AdvanceStatus, string> = {
      pending: 'En attente',
      approved: 'En remboursement',
      rejected: 'Rejetée',
      completed: 'Terminée'
    };

    try {
      if (newStatus === 'approved') {
        await payrollStore.approveAdvance(advanceId);
      } else if (newStatus === 'rejected') {
        await payrollStore.rejectAdvance(advanceId);
      } else {
        // For other status changes, update directly
        // await payrollStore.updateAdvanceStatus(advanceId, newStatus);
      }
      notification.toast.success(`Avance déplacée vers ${statusLabels[newStatus]}`);
    } catch (error) {
      notification.toast.error('Erreur lors du déplacement');
      // Reset local state on error
      pendingItems = [...pendingAdvances];
      approvedItems = [...approvedAdvances];
      otherItems = [...otherAdvances];
    }
  }

  function handleApprove(id: string) {
    notification.confirm({
      title: 'Approuver la demande',
      message: 'Voulez-vous approuver cette demande d\'avance ?',
      type: 'info',
      yesText: 'Approuver',
      noText: 'Annuler',
      onYes: () => {
        payrollStore.approveAdvance(id);
        notification.toast.success('Demande approuvée');
      }
    });
  }

  function handleReject(id: string) {
    notification.confirm({
      title: 'Rejeter la demande',
      message: 'Voulez-vous rejeter cette demande d\'avance ?',
      type: 'danger',
      yesText: 'Rejeter',
      noText: 'Annuler',
      onYes: () => {
        payrollStore.rejectAdvance(id);
        notification.toast.info('Demande rejetée');
      }
    });
  }
</script>


<svelte:head>
  <title>Oxiliere HR - Avances sur salaire</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={getActiveFilters()}
      activeFiltersCount={activeFiltersCount}
      getDisplayLabel={(key) => {
        if (key === 'risk') return 'Risque élevé';
        return key;
      }}
      onRemove={handleRemoveFilter}
      onReset={resetFilters}
      class="py-1.5"
    />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      <div class="flex-1 overflow-y-auto min-h-0 {filteredAdvances.length === 0 ? 'px-4 py-4 pr-8.5' : 'px-4 py-4'}">
        {#if filteredAdvances.length === 0}
          <Empty 
            title="Aucune avance trouvée"
            description="Aucune demande d'avance ne correspond à vos critères de recherche."
            icon="banknote"
            iconSize={28}
            iconStrokeWidth={1.3}
          />
        {:else}
          <!-- Kanban Board -->
          <div class="grid grid-cols-3 gap-4 h-full min-h-0">
            {@render KanbanColumn(
              'En attente',
              'clock',
              'amber',
              pendingItems,
              true,
              undefined,
              'pending'
            )}
            {@render KanbanColumn(
              'En remboursement',
              'banknote',
              'emerald',
              approvedItems,
              false,
              undefined,
              'approved'
            )}
            {@render KanbanColumn(
              'Archivées',
              'archive',
              'slate',
              otherItems,
              false,
              archivedLimit,
              'archived'
            )}
          </div>
        {/if}
      </div>
    </main>
  </div>
</div>


{#snippet KanbanColumn(
  title: string,
  icon: string,
  color: 'amber' | 'emerald' | 'slate',
  items: Advance[],
  showActions: boolean,
  limit?: number,
  columnId?: 'pending' | 'approved' | 'archived'
)}
  {@const bgColor = color === 'amber' ? 'bg-amber-50' : color === 'emerald' ? 'bg-emerald-50' : 'bg-slate-100'}
  {@const borderColor = color === 'amber' ? 'border-amber-100' : color === 'emerald' ? 'border-emerald-100' : 'border-slate-200'}
  {@const textColor = color === 'amber' ? 'text-amber-700' : color === 'emerald' ? 'text-emerald-700' : 'text-slate-600'}
  {@const badgeColor = color === 'amber' ? 'text-amber-600 bg-amber-100' : color === 'emerald' ? 'text-emerald-600 bg-emerald-100' : 'text-slate-500 bg-slate-200'}
  {@const iconColor = color === 'amber' ? 'text-amber-600' : color === 'emerald' ? 'text-emerald-600' : 'text-slate-500'}
  {@const emptyIconColor = color === 'amber' ? 'text-amber-400' : color === 'emerald' ? 'text-emerald-400' : 'text-slate-400'}
  {@const emptyText = title === 'En attente' ? 'Aucune demande en attente' : title === 'En remboursement' ? 'Aucun remboursement en cours' : 'Aucune avance archivée'}
  {@const isArchived = color === 'slate'}
  {@const hasLimit = limit !== undefined && items.length > limit}
  {@const displayItems = hasLimit ? items.slice(0, limit) : items}
  {@const remainingCount = hasLimit ? items.length - limit : 0}
  {@const targetStatus = columnId === 'pending' ? 'pending' : columnId === 'approved' ? 'approved' : 'completed'}

  <div class="flex flex-col min-h-0">
    <div class="flex items-center gap-2 px-3 py-2 {bgColor} border {borderColor} rounded-t-lg">
      <AppIcon name={icon} size={18} class={iconColor} />
      <span class="text-sm font-semibold {textColor}">{title}</span>
      <span class="ml-auto text-xs font-medium {badgeColor} px-2 py-0.5 rounded-full">
        {items.length}
      </span>
    </div>
    <div
      class="flex-1 overflow-y-auto {isArchived ? 'bg-slate-50/50' : 'bg-slate-50'} border border-t-0 {borderColor} rounded-b-lg p-3 space-y-3 min-h-0 outline-none"
      use:dndzone={{ items: displayItems, flipDurationMs, type: 'advance', dropTargetStyle: { outline: 'none' } }}
      onconsider={(e) => handleDndConsider(columnId!, e)}
      onfinalize={(e) => handleDndFinalize(columnId!, targetStatus, e)}
    >
      {#if items.length === 0}
        <div class="flex flex-col justify-center items-center h-full">
          <AppIcon name={icon} size={25} strokeWidth={1} class={emptyIconColor} />
          <div class="text-center pt-1 text-slate-400 text-sm">
            {emptyText}
          </div>
        </div>
      {:else}
        {#each displayItems as advance (advance.id)}
          <div animate:flip={{ duration: flipDurationMs }}>
            <AdvanceCard {advance} {showActions} onApprove={handleApprove} onReject={handleReject} />
          </div>
        {/each}
        {#if hasLimit}
          <button
            onclick={() => archivedLimit += ARCHIVED_LIMIT}
            class="w-full py-2 px-3 text-xs text-slate-500 hover:text-slate-700 hover:bg-slate-100 rounded-lg transition-colors flex items-center justify-center gap-1"
          >
            <AppIcon name="chevron-down" size={14} />
            Voir {remainingCount} de plus
          </button>
        {/if}
      {/if}
    </div>
  </div>
{/snippet}


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8.5">
    <div class="flex items-center gap-3">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={searchTerm} 
          placeholder="Rechercher une avance..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => searchTerm = ''}
        />
      </div>
      
      <div class="flex items-center gap-2">
        <!-- Stats Summary -->
        <div class="flex items-center gap-3 px-3 py-1.5 bg-slate-50 rounded-lg border border-slate-200">
          <div class="flex items-center gap-1.5">
            <AppIcon name="clock" size={14} class="text-amber-500" />
            <span class="text-[0.8rem] text-slate-600">{payrollStore.pendingAdvances}</span>
          </div>
          <div class="w-px h-4 bg-slate-200"></div>
          <div class="flex items-center gap-1.5">
            <AppIcon name="alert-circle" size={14} class="text-rose-500" />
            <span class="text-[0.8rem] text-slate-600">{payrollStore.highRiskAdvances}</span>
          </div>
          <div class="w-px h-4 bg-slate-200"></div>
          <div class="flex items-center gap-1.5">
            <AppIcon name="banknote" size={14} class="text-emerald-500" />
            <span class="text-[0.8rem] text-slate-600">
              {totalPendingAmount.toLocaleString('fr-FR', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 })}
            </span>
          </div>
        </div>

        {@render FilterMenu()}
        
        <Button 
          onclick={() => showNewRequestForm = true}
          class="h-7.5 px-3 bg-primary text-white text-[0.84rem] rounded-lg shadow-fine transition-all cursor-pointer"
        >
          <AppIcon name="plus" size={17} />
          Nouvelle demande
        </Button>
      </div>
    </div>
  </div>
{/snippet}


{#snippet FilterMenu()}
  <DropdownMenu.Root>
    <DropdownMenu.Trigger 
      class="inline-flex items-center justify-center bg-white hover:bg-slate-50 text-slate-600 border border-slate-200 rounded-lg shadow-fine h-7.5 px-3 gap-2 cursor-pointer transition-all"
    >
      <AppIcon name="filter" size={16} class={activeFiltersCount > 0 ? "text-blue-500" : "text-slate-400"} />
      <span class="text-[0.84rem] text-slate-700">Filtrer</span>
      {#if activeFiltersCount > 0}
        <div transition:scale={{ duration: 200, start: 0.8 }}>
          <Badge class="h-4.5 min-w-4.5 p-0 flex items-center justify-center bg-blue-500 text-white font-medium rounded-full text-[0.65rem] border-none">
            {activeFiltersCount}
          </Badge>
        </div>
      {/if}
    </DropdownMenu.Trigger>

    <DropdownMenu.Content align="end" class="p-0 rounded-md shadow-fine border-slate-100 bg-white overflow-hidden">
      <div class="p-2 max-h-80 overflow-y-auto">
        <!-- Risk Filter -->
        <DropdownMenu.Label class="text-[0.75rem]! font-bold text-slate-400 uppercase tracking-widest px-2 py-2">
          Risque
        </DropdownMenu.Label>
        <DropdownMenu.CheckboxItem 
          checked={showOnlyHighRisk}
          onCheckedChange={(checked) => { showOnlyHighRisk = checked; }}
          class="rounded-lg py-1.5 px-2 text-[0.85rem]! cursor-pointer pl-7"
        >
          Risque élevé uniquement
        </DropdownMenu.CheckboxItem>
      </div>

      {#if activeFiltersCount > 0}
        <div class="p-2 bg-slate-50/50 border-t border-slate-100">
          <Button variant="ghost" onclick={resetFilters} class="w-full h-8 text-[0.84rem] bg-white text-red-500 hover:text-red-600 hover:bg-red-50! font-medium">
            Réinitialiser tout
          </Button>
        </div>
      {/if}
    </DropdownMenu.Content>
  </DropdownMenu.Root>
{/snippet}


<AdvanceRequestSheet bind:open={showNewRequestForm} />

