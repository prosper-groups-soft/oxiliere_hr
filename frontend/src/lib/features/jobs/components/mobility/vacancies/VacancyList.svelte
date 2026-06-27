<script lang="ts">
  import type { Vacancy } from "../../../types/types";
  import VacancyItem from "./VacancyItem.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from "@/components/shared/containers/empty/EmptyButton.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import { fade } from "svelte/transition";
  import { getFriendlyErrorMessage } from '@/constants/errors';
  import { vacanciesStore } from "../../../stores/vacanciesStore.svelte";
  import { 
    VACANCY_PRIORITY_OPTIONS, 
    VACANCY_STATUS_OPTIONS 
  } from "../../../constants/vacancy.constants";

  let { 
    vacancies = [],
    onEdit,
    onDelete,
    onNew,
    onRetry,
    isLoading = false,
    isError = false,
    error = null,
    totalCount = 0,
    currentPage = 1,
    totalPages = 1,
    perPage = 8,
    onPageChange,
    onPerPageChange,
    onNext,
    onPrev
  } = $props<{ 
    vacancies: Vacancy[];
    onEdit: (vac: Vacancy) => void;
    onDelete?: (vac: Vacancy) => void;
    onNew?: () => void;
    onRetry?: () => void;
    isLoading?: boolean;
    isError?: boolean;
    error?: any;
    totalCount?: number;
    currentPage?: number;
    totalPages?: number;
    perPage?: number;
    onPageChange?: (page: number) => void;
    onPerPageChange?: (size: number) => void;
    onNext?: () => void;
    onPrev?: () => void;
  }>();

  // Compute active filters for FilterChips (object format with arrays)
  const displayFilters = $derived({
    search: vacanciesStore.searchQuery ? [vacanciesStore.searchQuery] : [],
    priority: vacanciesStore.filters.priority ? [vacanciesStore.filters.priority] : [],
    status: vacanciesStore.filters.status ? [vacanciesStore.filters.status] : []
  });

  function getDisplayLabel(key: string, value: any) {
    if (key === 'search') return `Recherche: "${value}"`;
    if (key === 'priority') return VACANCY_PRIORITY_OPTIONS.find(p => p.value === value)?.label || value;
    if (key === 'status') return VACANCY_STATUS_OPTIONS.find(s => s.value === value)?.label || value;
    return String(value);
  }

  function handleRemoveFilter(key: string, value: any) {
    if (key === 'search') vacanciesStore.clearSearch();
    if (key === 'priority') vacanciesStore.clearPriority();
    if (key === 'status') vacanciesStore.clearStatus();
  }

  function handleClearAllFilters() {
    vacanciesStore.resetFilters();
  }
</script>


<div class="flex flex-col h-full flex-1 overflow-hidden bg-white">
  <!-- Loading State -->
  {#if isLoading}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <AnimateSpin text="Chargement des besoins" />
    </div>

  <!-- Error State -->
  {:else if isError}
    <div class="flex-1 flex items-center justify-center p-8" in:fade={{ duration: 200 }}>
      <Empty
        title="Erreur de chargement"
        description={getFriendlyErrorMessage(error)}
        icon="alert-circle"
        iconClass="text-red-400"
        iconSize={28}
        iconStrokeWidth={1.3}
        iconContainerClass="bg-red-50/30"
      >
        <Button onclick={onRetry} variant="outline" class="h-7 rounded-lg">
          <AppIcon name="refresh-cw" />
          Réessayer
        </Button>
      </Empty>
    </div>

  <!-- Data Available (header + filters) -->
  {:else}
    <div class="flexx items-center justify-between px-5 py-2 bg-white border-b border-slate-100/60 sticky top-0 z-10 backdrop-blur-sm hidden" in:fade={{ duration: 200 }}>
      <span class="text-[0.85rem] font-medium text-slate-600">
        {totalCount} besoin{totalCount > 1 ? 's' : ''}
      </span>
    </div>

    <!-- FilterChips -->
    <div class="px-5 py-0 border-slate-100/60 bg-white {vacanciesStore.activeFiltersCount > 0 ? "py-1 border-b" : ""}">
      <FilterChips
        filters={displayFilters}
        activeFiltersCount={vacanciesStore.activeFiltersCount}
        getDisplayLabel={getDisplayLabel}
        onRemove={handleRemoveFilter}
        onReset={handleClearAllFilters}
      />
    </div>
  {/if}

  <!-- Empty State -->
  {#if !isLoading && !isError && vacancies.length === 0}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <Empty
        title="Aucun besoin identifié"
        description={vacanciesStore.hasActiveFilters
          ? "Aucun résultat ne correspond aux filtres sélectionnés."
          : "Tous les postes critiques sont actuellement pourvus."}
        icon={vacanciesStore.hasActiveFilters ? "search-x" : "inbox"}
        iconSize={28}
        iconStrokeWidth={1.3}
        iconClass="text-slate-300"
      >
        {#if vacanciesStore.hasActiveFilters}
          <Button variant="ghost" onclick={() => vacanciesStore.resetFilters()} class="h-7.5 bg-slate-50">
            <AppIcon name="x" size={16} class="text-slate-400" />
            Réinitialiser les filtres
          </Button>
        {:else if onNew}
          <EmptyButton labelElement="un besoin" {onNew} />
        {/if}
      </Empty>
    </div>

  <!-- Data List -->
  {:else if !isLoading && !isError}
    <div class="flex-1 overflow-y-auto" in:fade={{ duration: 200 }}>
      {#each vacancies as vac (vac.id)}
        <VacancyItem vacancy={vac} {onEdit} {onDelete} />
      {/each}
    </div>

    <!-- Pagination -->
    <div class="px-6 py-0.5 border-t border-slate-100 bg-white sticky bottom-0 z-10" in:fade={{ duration: 200 }}>
      <DataPagination
        currentCount={vacancies.length}
        {totalCount}
        {currentPage}
        {totalPages}
        {perPage}
        onPageChange={onPageChange ?? (() => {})}
        onPerPageChange={onPerPageChange ?? (() => {})}
        onNext={onNext ?? (() => {})}
        onPrev={onPrev ?? (() => {})}
        unitLabel="besoins"
      />
    </div>
  {/if}
</div>

