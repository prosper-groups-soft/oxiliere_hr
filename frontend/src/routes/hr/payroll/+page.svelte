<script lang="ts">
  import { fade } from "svelte/transition";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import LoadingBar from "@/components/layout/elements/LoadingBar.svelte";
  import ExecutionTable from '@/hr/payroll/components/run/ExecutionTable.svelte';
  import PayrollActions from '@/hr/payroll/components/run/PayrollActions.svelte';
  import { payrollStore } from '@/hr/payroll/stores/payroll.svelte';
  import { RUN_LIST_STATUS_LABELS } from '@/hr/payroll/types/types';
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { Button } from '@/components/ui/button';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { goToActiveOrNewPayroll } from '@/hr/payroll/utils/goToActiveOrNewPayroll';
  import { ui } from '@/stores/ui.svelte';


  // Page : loading / offline / error. Le vide (absolu ou filtré) vit
  // uniquement dans ExecutionTable (source unique, prend toute la hauteur).
  let viewState: 'loading' | 'success' | 'error' | 'offline' = $state('loading');
  let hasLoadedOnce = $state(false);
  let refreshing = false;

  /** Re-questionne le backend avec les filtres/paramètres courants du store. */
  async function refresh() {
    if (refreshing) return;
    refreshing = true;
    try {
      await payrollStore.fetchRunList();
      hasLoadedOnce = true;
      viewState = 'success';
    } catch (err: any) {
      // Hors ligne détecté par le client API, sinon erreur générique.
      // Pas de toast : la page affiche déjà l'état Empty offline.
      // Le store déduplique les appels concurrents (layout + page) → une seule erreur.
      viewState = err?.message === 'offline' ? 'offline' : 'error';
    } finally {
      refreshing = false;
    }
  }

  // Chaque changement de recherche / statut / période / unité / tri / page /
  // taille déclenche une (re)lecture backend (debounce léger pour la saisie).
  $effect(() => {
    const signature = [
      payrollStore.cycleFilters.status,
      payrollStore.cycleFilters.periodStart,
      payrollStore.cycleFilters.periodEnd,
      payrollStore.cycleFilters.period,
      payrollStore.cycleFilters.search,
      payrollStore.cycleFilters.orgUnit,
      payrollStore.sortBy,
      payrollStore.sortOrder,
      payrollStore.cycleListPage,
      payrollStore.cycleListPerPage,
    ].join('|');
    void signature;
    const timer = setTimeout(() => { refresh(); }, 300);
    return () => clearTimeout(timer);
  });

  function handleClearSearch() {
    payrollStore.setCycleFilter('search', '');
  }

  function handleResetFilters() {
    payrollStore.resetCycleFilters();
  }

  function formatFR(iso: string): string {
    if (!iso) return '';
    const d = new Date(iso + 'T00:00:00');
    if (Number.isNaN(d.getTime())) return iso;
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  // Puces de filtres (compatibles FilterChips : tableaux de valeurs).
  const filtersWithSearch = $derived.by(() => {
    const f: Record<string, string[]> = {};
    if (payrollStore.cycleFilters.status !== 'all') {
      f.status = [payrollStore.cycleFilters.status];
    }
    const ps = payrollStore.cycleFilters.periodStart;
    const pe = payrollStore.cycleFilters.periodEnd;
    if (ps || pe) {
      const label = ps && pe ? `${formatFR(ps)} → ${formatFR(pe)}` : ps ? `Depuis ${formatFR(ps)}` : `Jusqu'au ${formatFR(pe)}`;
      f.period = [label];
    } else if (payrollStore.cycleFilters.period) {
      f.period = [payrollStore.cycleFilters.period];
    }
    if (payrollStore.cycleFilters.orgUnit) {
      f.orgUnit = [payrollStore.cycleFilters.orgUnit];
    }
    if (payrollStore.cycleFilters.search) {
      f.search = [payrollStore.cycleFilters.search];
    }
    return f;
  });

  const activeFiltersWithSearch = $derived(
    payrollStore.activeCycleFiltersCount + (payrollStore.cycleFilters.search ? 1 : 0)
  );

  // Stats rapides dérivées de la liste réelle.
  const totalCycles = $derived(payrollStore.runList.length);
  const processingCycles = $derived(payrollStore.runList.filter(r => r.status === 'processing').length);
  const closedCycles = $derived(payrollStore.runList.filter(r => r.status === 'closed').length);

  function getFilterDisplayLabel(key: string, value: string): string {
    switch (key) {
      case 'status':
        return RUN_LIST_STATUS_LABELS[value as keyof typeof RUN_LIST_STATUS_LABELS] || value;
      case 'period':
        return `Période: ${value}`;
      case 'orgUnit':
        return `Unité: ${value}`;
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
      payrollStore.setCycleFilter('periodStart', '');
      payrollStore.setCycleFilter('periodEnd', '');
    } else if (key === 'orgUnit') {
      payrollStore.setCycleFilter('orgUnit', '');
    }
  }

  // Actions de la barre d'outils (Tri / Statut / Période / Unité / Nouvelle paie)
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
  <PayrollActions />
{/snippet}


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <FilterChips
    filters={filtersWithSearch}
    activeFiltersCount={activeFiltersWithSearch}
    getDisplayLabel={getFilterDisplayLabel}
    onRemove={handleFilterRemove}
    onReset={handleResetFilters}
    class="py-1 pb-1.5 px-6 border-b border-slate-50"
  />

  <!-- Barre de chargement fine pendant les relectures backend -->
  <LoadingBar loading={payrollStore.isFetchingRunList} />

  <main class="flex flex-1 flex-col overflow-hidden min-h-0">
    {#key viewState === 'loading' ? 'loading' : viewState === 'success' && payrollStore.paginatedRunList.length > 0 ? 'table' : 'empty'}
      <div class="flex flex-1 flex-col overflow-hidden min-h-0" in:fade={{ duration: 160 }}>
        {#if viewState === 'loading'}
          <div class="flex-1 min-h-0 flex items-center justify-center">
            <AnimateSpin text="Chargement des paies" />
          </div>
        {:else if viewState === 'error' || viewState === 'offline' || payrollStore.paginatedRunList.length === 0}
      {@const isOffline = viewState === 'offline'}
      {@const isError = viewState === 'error'}
      {@const isEmpty = !isOffline && !isError}
      {@const isFilteredEmpty = isEmpty && activeFiltersWithSearch > 0}
      <div class="flex-1 min-h-0 flex items-center justify-center px-6 py-12">
        <Empty
          icon={isOffline ? 'wifi-off' : isError ? 'alert-triangle' : isFilteredEmpty ? 'search-x' : 'file-text'}
          title={isOffline ? 'Hors connexion' : isError ? 'Une erreur est survenue' : isFilteredEmpty ? 'Aucun cycle trouvé' : 'Aucune exécution'}
          description={isOffline
            ? 'Impossible de charger les exécutions de paie. Vérifiez votre connexion et réessayez.'
            : isError
              ? 'Une erreur est survenue lors du chargement des exécutions de paie.'
              : isFilteredEmpty
                ? 'Aucune exécution de paie ne correspond à vos critères.'
                : 'Créez votre premier cycle de paie pour commencer.'}
          iconContainerClass={isOffline ? 'bg-amber-50' : isError ? 'bg-rose-50' : 'bg-slate-50'}
          iconClass={isEmpty ? 'text-slate-300' : undefined}
          iconSize={isEmpty ? 30 : 32}
          iconStrokeWidth={1.5}
          class={isOffline || isError ? 'h-full' : undefined}
        >
          {#if isOffline || isError}
            <Button onclick={() => refresh()} variant="outline" class="h-7 mt-2 rounded-lg">
              <AppIcon name="refresh-cw" />Réessayer
            </Button>
          {:else if isFilteredEmpty}
            <Button variant="ghost" onclick={handleResetFilters} class="h-7 bg-slate-50">
              <AppIcon name="x" size={16} class="text-slate-400" />Réinitialiser les filtres
            </Button>
          {:else}
            <Button variant="default" onclick={() => goToActiveOrNewPayroll()} class="h-7">
              <AppIcon name="play" size={16} class="text-white" />Commencer une nouvelle paie
            </Button>
          {/if}
        </Empty>
      </div>
    {:else}
      <div class="flex-1 min-h-0 flex flex-col overflow-hidden">
        <ExecutionTable runs={payrollStore.paginatedRunList} />
      </div>

      <footer class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
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
      </footer>
    {/if}
    </div>
    {/key}
  </main>
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
  <header class="flex items-center justify-between pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
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
  </header>
{/snippet}

