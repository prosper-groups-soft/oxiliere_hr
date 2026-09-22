<script lang="ts">
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { payrollStore } from "@/hr/payroll/stores/payroll.svelte";
  import { advancesStore } from "@/hr/payroll/stores/advances/advancesStore.svelte";
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { ui } from "@/stores/ui.svelte";
  import AdvanceRequestSheet from "@/hr/payroll/components/advances/sheets/AdvanceRequestSheet.svelte";
  import AdvanceDetailSheet from "@/hr/payroll/components/advances/sheets/AdvanceDetailSheet.svelte";
  import AdvanceTable from "@/hr/payroll/components/advances/views/AdvanceTable.svelte";
  import AdvanceActions from "@/hr/payroll/components/advances/actions/AdvanceActions.svelte";
  import AdvanceApproveSheet from "@/hr/payroll/components/advances/sheets/AdvanceApproveSheet.svelte";
  import LoadingBar from "@/components/layout/elements/LoadingBar.svelte";
  import type { Advance } from "@/hr/payroll/types/types";
  import { ADVANCE_RISK_LABELS, ADVANCE_STATUS_LABELS } from "@/hr/payroll/types/types";


  // ── Cycle de vie de la vue 
  let viewState: 'loading' | 'success' | 'error' | 'offline' = $state('loading');

  async function retry() {
    viewState = 'loading';
    try {
      await payrollStore.syncFromApi('advances');
      viewState = 'success';
    } catch {
      viewState = 'error';
    }
  }

  // ── État des filtres (envoyés au backend) 
  const searchTerm = $derived(advancesStore.searchQuery);
  const isRefetching = $derived(advancesStore.loading);
  const riskLevelFilters = $derived(advancesStore.riskLevelFilters);
  const statusFilters = $derived(advancesStore.statusFilters);

  const activeFiltersCount = $derived(
    riskLevelFilters.length + statusFilters.length + (advancesStore.searchQuery ? 1 : 0)
  );

  // ── Avances (filtrées par le backend) 
  const filteredAdvances = $derived(payrollStore.advances);

  // Chargement initial + refetch quand les filtres changent (server-side)
  $effect(() => {
    // Toucher les dépendances réactives du store
    advancesStore.searchQuery;
    advancesStore.statusFilters;
    advancesStore.riskLevelFilters;
    payrollStore.syncFromApi('advances').then(() => {
      viewState = 'success';
    }).catch(() => {
      viewState = 'error';
    });
  });

  // ── Sheets 
  let showNewRequestForm = $state(false);
  let editTarget = $state<Advance | null>(null);
  let selectedAdvance = $state<Advance | null>(null);
  let showDetailSheet = $state(false);

  function handleOpenDetail(advance: Advance) {
    if (advance.status === 'DRAFT') {
      // Modifier le brouillon dans le sheet de demande
      editTarget = advance;
      showNewRequestForm = true;
      return;
    }
    selectedAdvance = advance;
    showDetailSheet = true;
  }

  /** Ouvrir le sheet de détail quel que soit le statut (depuis le menu kebab) */
  function handleViewDetail(advance: Advance) {
    selectedAdvance = advance;
    showDetailSheet = true;
  }

  function openNewRequest() {
    editTarget = null;
    showNewRequestForm = true;
  }

  // ── Actions (approuver / rejeter / soumettre) 
  let showApproveSheet = $state(false);
  let approveTarget = $state<Advance | null>(null);

  /** Ouvrir le sheet d'approbation avec la config de déduction */
  function handleApprove(advance: Advance) {
    approveTarget = advance;
    showApproveSheet = true;
  }

  /** Rejeter — motif obligatoire via notification.confirm */
  function handleReject(advance: Advance) {
    notification.confirm({
      title: "Rejeter la demande",
      message: `Voulez-vous rejeter la demande d'avance de <strong>${advance.employee_name}</strong> (${advance.amount.toLocaleString('fr-FR')} CDF) ?<br><br>Le motif est obligatoire et sera conservé dans l'historique.`,
      type: 'danger',
      yesText: 'Rejeter',
      noText: 'Annuler',
      inputLabel: 'Motif du rejet',
      inputValue: '',
      onYes: async (reason?: string) => {
        if (!reason?.trim()) {
          notification.toast.error("Le motif du rejet est obligatoire");
          return;
        }
        try {
          await payrollStore.rejectAdvance(advance.id, reason.trim());
          notification.toast.info('Demande d\'avance rejetée');
          await payrollStore.syncFromApi('advances');
        } catch {
          notification.toast.error('Erreur lors du rejet');
        }
      }
    });
  }

  /** Soumettre un brouillon DRAFT → PENDING */
  function handleSubmit(advance: Advance) {
    notification.confirm({
      title: "Soumettre la demande ?",
      message: `Soumettre la demande d'avance de <strong class="text-sm t font-semibold">${advance.employee_name}</strong> (${advance.amount.toLocaleString('fr-FR')} CDF) pour approbation ?`,
      type: 'info',
      yesText: 'Soumettre',
      noText: 'Annuler',
      onYes: async () => {
        try {
          await payrollStore.submitAdvance(advance.id);
          notification.toast.success('Demande soumise pour approbation');
          await payrollStore.syncFromApi('advances');
        } catch {
          notification.toast.error('Erreur lors de la soumission');
        }
      }
    });
  }

  /** Refetch après approbation depuis le sheet */
  async function handleApproveSheet() {
    await payrollStore.syncFromApi('advances');
  }

  async function handleActivate(id: string) {
    try {
      const updated = await payrollStore.activateAdvance(id);
      if (!updated) {
        notification.toast.error('Erreur lors de l\'activation');
        return;
      }
      notification.toast.success('Avance activée — déductible en paie');
    } catch {
      notification.toast.error('Erreur lors de l\'activation');
    }
  }

  // ── Filtres (menu + chips) 
  
  function resetFilters() {
    advancesStore.setSearchQuery('');
    advancesStore.resetFilters();
  }

  function getActiveFilters() {
    const filters: Record<string, string[]> = {};
    if (riskLevelFilters.length > 0) {
      filters.risk = [...riskLevelFilters];
    }
    if (statusFilters.length > 0) {
      filters.status = statusFilters.map(s => ADVANCE_STATUS_LABELS[s]);
    }
    if (searchTerm) {
      filters.search = [searchTerm];
    }
    return filters;
  }

  function handleRemoveFilter(key: string) {
    if (key === 'risk') {
      advancesStore.resetFilters();
    } else if (key === 'status') {
      advancesStore.resetStatusFilters();
    } else if (key === 'search') {
      advancesStore.setSearchQuery('');
    }
  }

  // Enregistrer les actions (filtre + bouton) dans la barre de titre
  $effect(() => {
    ui.addActions('advances', AdvanceActionsSnippet);
    return () => {
      ui.removeActions('advances');
    };
  });
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
        if (key === 'risk') {
          const count = riskLevelFilters.length;
          return count === 1
            ? `Risque: ${ADVANCE_RISK_LABELS[riskLevelFilters[0]]}`
            : `${count} risques`;
        }
        if (key === 'status') {
          const count = statusFilters.length;
          return count === 1
            ? `Statut: ${ADVANCE_STATUS_LABELS[statusFilters[0]]}`
            : `${count} statuts`;
        }
        if (key === 'search') return `Recherche: “${searchTerm}”`;
        return key;
      }}
      onRemove={handleRemoveFilter}
      onReset={resetFilters}
      class="py-1.5 px-6 border-b border-slate-50"
    />

    <!-- Overhead loading bar during refetch -->
    <LoadingBar loading={isRefetching} />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      <AdvanceTable
        advances={filteredAdvances}
        totalCount={filteredAdvances.length}
        hasActiveFilters={activeFiltersCount > 0}
        isLoading={viewState === 'loading'}
        isError={viewState === 'error' || viewState === 'offline'}
        isOffline={viewState === 'offline'}
        onRetry={retry}
        onResetFilters={resetFilters}
        onNew={openNewRequest}
        onClick={handleOpenDetail}
        onApprove={handleApprove}
        onReject={handleReject}
        onActivate={handleActivate}
        onEdit={handleOpenDetail}
        onSubmit={handleSubmit}
        onViewDetail={handleViewDetail}
      />
    </main>
  </div>
</div>


<!-- WRAPPER FOR ui.addActions -->
{#snippet AdvanceActionsSnippet()}
  <AdvanceActions onAdd={openNewRequest} />
{/snippet}


{#snippet Header()}
  <div class="flex items-center justify-between gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
    <div class="flex-1 ml-0.5">
      <SearchBar
        bind:value={advancesStore.searchQuery}
        placeholder="Rechercher une avance par employé ou motif..."
        class="w-125"
        inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
        iconSize={22}
        onSearch={(q) => advancesStore.setSearchQuery(q)}
        onClear={() => advancesStore.setSearchQuery('')}
      />
    </div>

    <!-- Statistiques rapides -->
    {@render QuickStats()}
  </div>
{/snippet}


{#snippet QuickStats()}
  <div class="flex items-center gap-5 px-4 py-1">
    <div class="flex items-center gap-2">
      <AppIcon name="wallet" size={17} class="text-slate-500" />
      <span class="text-sm font-semibold text-slate-800 tabular-nums">{payrollStore.advances.length}</span>
      <span class="text-sm text-slate-500">demandes</span>
    </div>
    <div class="flex items-center gap-2">
      <AppIcon name="clock" size={17} class="text-amber-500" />
      <span class="text-sm font-semibold text-amber-600 tabular-nums">{payrollStore.pendingAdvancesCount}</span>
      <span class="text-sm text-slate-500">en attente</span>
    </div>
    <div class="flex items-center gap-2">
      <AppIcon name="alert-triangle" size={17} class="text-rose-500" />
      <span class="text-sm font-semibold text-rose-600 tabular-nums">{payrollStore.highRiskAdvancesCount}</span>
      <span class="text-sm text-slate-500">haut risque</span>
    </div>
    {#if activeFiltersCount > 0}
      <div class="flex items-center gap-2">
        <AppIcon name="filter" size={17} class="text-blue-500" />
        <span class="text-sm font-semibold text-blue-600 tabular-nums">{activeFiltersCount}</span>
        <span class="text-sm text-slate-500">filtres</span>
      </div>
    {/if}
  </div>
{/snippet}


<AdvanceRequestSheet bind:open={showNewRequestForm} advance={editTarget} />


<AdvanceDetailSheet
  advance={selectedAdvance}
  bind:open={showDetailSheet}
/>


<AdvanceApproveSheet
  advance={approveTarget}
  bind:open={showApproveSheet}
  onApproved={handleApproveSheet}  
/>

