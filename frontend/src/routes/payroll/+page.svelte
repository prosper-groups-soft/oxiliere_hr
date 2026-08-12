<script lang="ts">
  import { fade } from "svelte/transition";
  import { goto } from '$app/navigation';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import ExecutionTable from '@/features/payroll/components/run/ExecutionTable.svelte';
  import PayrollActions from '@/features/payroll/components/run/PayrollActions.svelte';
  import { payrollStore } from '@/features/payroll/stores/payroll.svelte';
  import { RUN_LIST_STATUS_LABELS } from '@/features/payroll/types/types';
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { Button } from '@/components/ui/button';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { ui } from '@/stores/ui.svelte';


  let viewState: 'loading' | 'success' | 'empty' | 'error' | 'offline' = $state('loading');

  $effect(() => {
    payrollStore.syncFromApi('runList').then(() => {
      if (payrollStore.filteredRunList.length > 0) {
        viewState = 'success';
      } else {
        viewState = 'empty';
      }
    }).catch(() => {
      viewState = payrollStore.filteredRunList.length > 0 ? 'success' : 'error';
    });
  });

  function handleSearch(query: string) {
    payrollStore.setCycleFilter('search', query);
  }

  function handleClearSearch() {
    payrollStore.setCycleFilter('search', '');
  }

  function handleResetFilters() {
    payrollStore.resetCycleFilters();
  }

  // Build filters object in FilterChips-compatible format (arrays of values)
  const filtersWithSearch = $derived.by(() => {
    const f: Record<string, string[]> = {};
    if (payrollStore.cycleFilters.status !== 'all') {
      f.status = [payrollStore.cycleFilters.status];
    }
    if (payrollStore.cycleFilters.period) {
      f.period = [payrollStore.cycleFilters.period];
    }
    if (payrollStore.cycleFilters.search) {
      f.search = [payrollStore.cycleFilters.search];
    }
    return f;
  });

  const activeFiltersWithSearch = $derived(
    payrollStore.activeCycleFiltersCount + (payrollStore.cycleFilters.search ? 1 : 0)
  );

  // Quick stats derived from the run list
  const totalCycles = $derived(payrollStore.runList.length);
  const processingCycles = $derived(payrollStore.runList.filter(r => r.status === 'processing').length);
  const closedCycles = $derived(payrollStore.runList.filter(r => r.status === 'closed').length);

  function getFilterDisplayLabel(key: string, value: string): string {
    switch (key) {
      case 'status':
        return RUN_LIST_STATUS_LABELS[value as keyof typeof RUN_LIST_STATUS_LABELS] || value;
      case 'period':
        return `Période: ${value}`;
      case 'search':
        return `Recherche: "${value}"`;
      default:
        return value;
    }
  }

  function handleFilterRemove(key: string, value: string) {
    if (key === 'search') {
      payrollStore.setCycleFilter('search', '');
    } else if (key === 'status') {
      payrollStore.setCycleFilter('status', 'all' as any);
    } else if (key === 'period') {
      payrollStore.setCycleFilter('period', '');
    }
  }

  /** Export CSV de la liste des cycles */
  function handleExportCsv() {
    const headers = ['Période', 'Employés', 'Brut total', 'Statut'];
    const rows = payrollStore.filteredRunList.map(r => [
      r.periodLabel,
      `${r.employeeCount}/${r.totalEmployeeCount}`,
      r.grossTotal.toLocaleString('fr-FR'),
      RUN_LIST_STATUS_LABELS[r.status as keyof typeof RUN_LIST_STATUS_LABELS] || r.status,
    ]);
    const csv = [headers, ...rows].map(row => row.join(';')).join('\n');
    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `cycles_paie_${new Date().toISOString().slice(0, 10)}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }

	// Enregistrer les actions dans le store UI
	$effect(() => {
		ui.addActions('payroll-run-list', PayrollActionsSnippet);
		return () => {
			ui.removeActions('payroll-run-list');
		};
	});
</script>


<svelte:head>
  <title>Oxiliere HR - Exécutions de paie</title>
</svelte:head>


{#snippet PayrollActionsSnippet()}
	<PayrollActions onAdd={() => goto('/payroll/new-run')} onExport={handleExportCsv} />
{/snippet}


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips
      filters={filtersWithSearch}
      activeFiltersCount={activeFiltersWithSearch}
      getDisplayLabel={getFilterDisplayLabel}
      onRemove={handleFilterRemove}
      onReset={handleResetFilters}
      class="py-1 pb-1.5 px-6 border-b border-slate-50"
    />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      {#if viewState === 'loading'}
        <div class="flex-1 min-h-0 flex items-center justify-center">
          <AnimateSpin text="Chargement des exécutions de paie en cours..." />
        </div>
      {:else if viewState === 'error' || viewState === 'offline'}
        <Empty
          icon={viewState === 'offline' ? 'wifi-off' : 'alert-triangle'}
          title={viewState === 'offline' ? 'Hors connexion' : 'Une erreur est survenue'}
          description={viewState === 'offline'
            ? 'Impossible de charger les exécutions de paie. Vérifiez votre connexion et réessayez.'
            : 'Une erreur est survenue lors du chargement des exécutions de paie.'}
          iconContainerClass={viewState === 'offline' ? 'bg-amber-50' : 'bg-rose-50'}
          class="h-full"
          iconSize={32}
          iconStrokeWidth={1.5}
        />

      {:else if viewState === 'empty' && payrollStore.filteredRunList.length === 0}
        <Empty
          icon="inbox"
          title="Aucune donnée"
          description="Aucune exécution de paie ne correspond à vos critères."
          iconContainerClass="bg-slate-50"
          class="h-full"
          iconSize={30}
          iconStrokeWidth={1.5}
        >
          <Button variant="default" size="sm" onclick={() => goto('/payroll/new-run')} class="shadow-fine bg-primary text-white text-[0.84rem] hover:text-white rounded-lg inline-flex items-center gap-2">
            <AppIcon name="play" size={16} />
            Commencer une nouvelle paie
          </Button>
        </Empty>

      {:else}
        <div class="flex-1 overflow-y-auto min-h-0" transition:fade={{ duration: 200 }}>
          {#if payrollStore.filteredRunList.length > 0}
            <ExecutionTable
              runs={payrollStore.paginatedRunList}
              activeFiltersCount={activeFiltersWithSearch}
              onResetFilters={handleResetFilters}
            />
          {:else}
            <div class="flex justify-center items-center h-full">
              <Empty
                icon="clipboard-x"
                title="Aucun cycle trouvé"
                description="Aucune exécution de paie ne correspond à vos critères."
                iconContainerClass="bg-slate-50/50"
                iconSize={28}
                iconStrokeWidth={1.3}
              />
            </div>
          {/if}
        </div>
      {/if}

      {#if payrollStore.filteredRunList.length > 0}
        <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
          <DataPagination
            currentCount={payrollStore.paginatedRunList.length}
            totalCount={payrollStore.runListTotalItems}
            currentPage={payrollStore.cycleListPage}
            totalPages={payrollStore.runListTotalPages}
            perPage={payrollStore.cycleListPerPage}
            onPageChange={(p) => payrollStore.setCycleListPage(p)}
            onPerPageChange={(s) => { payrollStore.cycleListPerPage = s; payrollStore.setCycleListPage(1); }}
            onNext={() => payrollStore.setCycleListPage(payrollStore.cycleListPage + 1)}
            onPrev={() => payrollStore.setCycleListPage(payrollStore.cycleListPage - 1)}
            unitLabel="cycles"
          />
        </div>
      {/if}
    </main>
  </div>
</div>


{#snippet QuickStats()}
  <div class="flex items-center gap-5 px-4 py-1">
    <div class="flex items-center gap-2">
      <AppIcon name="calendar-range" size={17} class="text-slate-500" />
      <span class="text-sm font-semibold text-slate-800 tabular-nums">{totalCycles}</span>
      <span class="text-xs text-slate-400">cycles</span>
    </div>
    {#if processingCycles > 0}
      <div class="flex items-center gap-2">
        <AppIcon name="loader" size={17} class="text-amber-500" />
        <span class="text-sm font-semibold text-amber-600 tabular-nums">{processingCycles}</span>
        <span class="text-xs text-slate-400">en cours</span>
      </div>
    {/if}
    <div class="flex items-center gap-2">
      <AppIcon name="check-circle" size={17} class="text-green-500" />
      <span class="text-sm font-semibold text-green-600 tabular-nums">{closedCycles}</span>
      <span class="text-xs text-slate-400">clôturés</span>
    </div>
    {#if activeFiltersWithSearch > 0}
      <div class="flex items-center gap-2">
        <AppIcon name="filter" size={17} class="text-blue-500" />
        <span class="text-sm font-semibold text-blue-600 tabular-nums">{activeFiltersWithSearch}</span>
        <span class="text-xs text-slate-400">filtres</span>
      </div>
    {/if}
  </div>
{/snippet}


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
    <div class="flex items-center justify-between">
      <div class="flex-1 ml-0.5">
        <SearchBar
          bind:value={payrollStore.cycleFilters.search}
          placeholder="Rechercher une période..."
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={handleClearSearch}
        />
      </div>

      <!-- Quick stats -->
      {@render QuickStats()}
    </div>
  </div>
{/snippet}

