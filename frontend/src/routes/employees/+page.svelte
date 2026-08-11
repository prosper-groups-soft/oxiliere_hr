<script lang="ts">
  import { fade } from "svelte/transition";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import EmployeeList from "@/features/employees/components/mgmt/list/EmployeeList.svelte";
  import { employeeStore } from "@/features/employees/stores/employees.svelte";
  import { useEmployeesQuery, syncEmployeesStore } from "@/features/employees/queries";
  import { get } from 'svelte/store';
  import SearchBar from "@/components/shared/elements/SearchBar.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import { ERROR_MESSAGES, getFriendlyErrorMessage } from "@/constants/errors";
  import EmployeesActions from "@/features/employees/components/mgmt/layout/actions/EmployeesActions.svelte";
  import { useOrgUnitsQuery } from "@/features/jobs/queries/orgQueries";
  import { CONTRACT_TYPES } from "@/features/employees/constants/contract";
  import { EMPLOYEE_STATUS_CONFIG } from "@/features/employees/constants/employeeStatus";
  import { ui } from "@/stores/ui.svelte";
  import { goto } from '$app/navigation';
  import LoadingBar from "@/components/layout/elements/LoadingBar.svelte";


  // Charger les données depuis le backend avec tri côté serveur
  const employeesQuery = useEmployeesQuery(
    () => employeeStore.currentPage,
    () => employeeStore.perPage,
    () => employeeStore.searchQuery,
    () => employeeStore.filters,
    () => employeeStore.sortBy,
    () => employeeStore.sortOrder
  );

  // Charger les unités organisationnelles pour les labels de filtres
  const orgUnitsQuery = useOrgUnitsQuery();
  const orgUnits = $derived($orgUnitsQuery.data?.results || []);

  // Synchroniser le store avec les données de la query
  $effect(() => {
    syncEmployeesStore($employeesQuery);
  });

  // Re-fetch quand les filtres, le tri ou la recherche changent
  // Utiliser get() pour éviter la boucle infinie sur la valeur réactive
  $effect(() => {
    employeeStore.filters.orgUnit;
    employeeStore.filters.status;
    employeeStore.filters.location;
    employeeStore.filters.contractType;
    employeeStore.sortBy;
    employeeStore.sortOrder;
    employeeStore.searchQuery;
    employeeStore.currentPage;
    employeeStore.perPage;
    get(employeesQuery).refetch();
  });

  // Créer un objet filters enrichi qui inclut la recherche textuelle
  // pour que FilterChips puisse l'afficher
  const filtersWithSearch = $derived.by(() => {
    const f = { ...employeeStore.filters };
    if (employeeStore.searchQuery) {
      (f as Record<string, string[]>).search = [employeeStore.searchQuery];
    }
    return f;
  });

  // Fonction pour afficher les labels lisibles des filtres
  function getFilterDisplayLabel(key: string, value: string): string {
    switch (key) {
      case 'orgUnit':
        const orgUnit = orgUnits.find(u => u.id === value);
        return orgUnit ? `Unité: ${orgUnit.name}` : `Unité: ${value}`;
      
      case 'status':
        const statusConfig = EMPLOYEE_STATUS_CONFIG[value];
        return statusConfig ? statusConfig.label : value;
      
      case 'contractType':
        const contractType = CONTRACT_TYPES.find(ct => ct.value === value);
        return contractType ? `Contrat: ${contractType.label}` : `Contrat: ${value}`;
      
      case 'location':
        return `Localité: ${value}`;
      
      case 'search':
        return `Recherche: “${value}”`;
      
      default:
        return value;
    }
  }

  // Actions pour les boutons
  function openEmployeeAdd() {
    goto('/employees/onboarding');
  }

  function toggleViewMode() {
    employeeStore.toggleViewMode();
  }

  // Enregistrer les actions dans le store UI
  $effect(() => {
    ui.addActions('employees', EmployeesActionsSnippet);
    return () => {
      ui.removeActions('employees');
    };
  });
</script>


<svelte:head>
  <title>Oxiliere HR - Employés</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {@render Header()}

  <div class="flex flex-1 flex-col overflow-hidden min-h-0">
    <FilterChips 
      filters={filtersWithSearch}
      activeFiltersCount={employeeStore.activeFiltersCount + (employeeStore.searchQuery ? 1 : 0)}
      getDisplayLabel={getFilterDisplayLabel}
      onRemove={(key, value) => {
        if (key === 'search') {
          employeeStore.setSearchQuery('');
        } else {
          employeeStore.toggleFilter(key as any, value);
        }
      }}
      onReset={() => employeeStore.resetFilters()}
      class="py-1 pb-1.5 px-6 border-b border-slate-50"
    />

    <!-- Overhead loading bar during refetch -->
    <LoadingBar loading={$employeesQuery.isFetching} />

    <main class="flex flex-1 flex-col overflow-hidden min-h-0">
      <!-- Loading state -->
      {#if $employeesQuery.isLoading && employeeStore.totalCount === 0}
        <div class="flex justify-center items-center h-full">
          <AnimateSpin text="Chargement des employés" />
        </div>
      
      <!-- Error state -->
      {:else if $employeesQuery.error && employeeStore.totalCount === 0}
        <div class="flex justify-center items-center h-full">
          <Empty 
            icon="alert-circle" 
            title="Erreur de Connexion" 
            description={getFriendlyErrorMessage($employeesQuery.error) || ERROR_MESSAGES.NETWORK.UNKNOWN} 
            iconClass="text-red-400" 
            iconContainerClass="bg-red-50/30"
            iconSize={28}
            iconStrokeWidth={1.3}
          >
            <Button 
              onclick={() => get(employeesQuery).refetch()} 
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
        <div class="flex-1 overflow-y-auto min-h-0" transition:fade={{ duration: 200 }}>
          <EmployeeList 
            employees={employeeStore.paginatedEmployees} 
            viewMode={employeeStore.viewMode}
            activeFiltersCount={employeeStore.activeFiltersCount}
            searchQuery={employeeStore.searchQuery}
            onResetFilters={() => { employeeStore.resetFilters(); employeeStore.setSearchQuery(''); }}
            onAdd={openEmployeeAdd}
          />
        </div>
      {/if}

      {#if employeeStore.totalCount > 0}
        <div class="px-4 bg-slate-50/80 border-t border-[#e9eaea] pr-10">
          <DataPagination 
            currentCount={employeeStore.paginatedEmployees.length}
            totalCount={employeeStore.totalCount}
            currentPage={employeeStore.currentPage}
            totalPages={employeeStore.totalPages}
            perPage={employeeStore.perPage}
            onPageChange={(p) => employeeStore.setPage(p)}
            onPerPageChange={(s) => employeeStore.setPerPage(s)}
            onNext={() => employeeStore.nextPage()}
            onPrev={() => employeeStore.prevPage()}
            unitLabel="profils"
          />
        </div>
      {/if}
    </main>
  </div>
</div>


<!-- WRAPPER FOR ui.addActions -->
{#snippet EmployeesActionsSnippet()}
  <EmployeesActions 
    onAdd={openEmployeeAdd} 
    onToggleViewMode={toggleViewMode} 
  />
{/snippet}


{#snippet Header()}
  <div class="flex flex-col gap-4 pb-2.5 border-b border-slate-100 pt-2.5 px-4 pr-8">
    <div class="flex items-center justify-between">
      <div class="flex-1 ml-0.5">
        <SearchBar 
          bind:value={employeeStore.searchQuery}
          placeholder="Rechercher un profil..." 
          class="w-125"
          inputClass="h-9.5 pl-10 pr-9 rounded-[18px] text-[0.9rem] bg-[#f5f6f7]"
          iconSize={22}
          onClear={() => employeeStore.setSearchQuery("")}
        />
      </div>
      
      <!-- Statistiques rapides -->
      {@render QuickStats()}
    </div>
  </div>
{/snippet}


{#snippet QuickStats()}
  <div class="flex items-center gap-5 px-4 py-1">
    <div class="flex items-center gap-2">
      <AppIcon name="users" size={17} class="text-slate-500" />
      <span class="text-sm font-semibold text-slate-800 tabular-nums">{employeeStore.totalCount}</span>
      <span class="text-sm text-slate-400">total</span>
    </div>
    <div class="flex items-center gap-2">
      <AppIcon name="user-check" size={17} class="text-green-500" />
      <span class="text-sm font-semibold text-green-600 tabular-nums">{employeeStore.employees.filter(e => e.status === 'active').length}</span>
      <span class="text-sm text-slate-400">actifs</span>
    </div>
    {#if employeeStore.activeFiltersCount > 0}
      <div class="flex items-center gap-2">
        <AppIcon name="filter" size={17} class="text-blue-500" />
        <span class="text-sm font-semibold text-blue-600 tabular-nums">{employeeStore.activeFiltersCount}</span>
        <span class="text-sm text-slate-400">filtres</span>
      </div>
    {/if}
  </div>
{/snippet}

