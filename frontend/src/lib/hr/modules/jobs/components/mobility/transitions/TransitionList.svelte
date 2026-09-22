<script lang="ts">
  import type { Transition, TransitionType } from "../../../types/types";
  import { transitionsStore } from "../../../stores/transitionsStore.svelte";
  import TransitionItem from "./TransitionItem.svelte";
  import Empty from "@/hr/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from "@/hr/components/shared/containers/empty/EmptyButton.svelte";
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import DataPagination from "@/hr/components/layout/elements/DataPagination.svelte";
  import FilterChips from "@/hr/components/shared/elements/FilterChips.svelte";
  import { fade } from "svelte/transition";
  import { getFriendlyErrorMessage } from '@/hr/constants/errors';
  import { TRANSITION_TYPE_CONFIG } from "../../../constants/transition.constants";

  
  let {
    transitions = [],
    onEdit,
    onDelete,
    onNew,
    onRetry,
    isLoading = false,
    isError = false,
    error = null,
    // Pagination props
    totalCount = 0,
    currentPage = 1,
    totalPages = 1,
    perPage = 8,
    onPageChange,
    onPerPageChange,
    onNext,
    onPrev
  } = $props<{
    transitions: Transition[],
    onEdit: (trans: Transition) => void,
    onDelete?: (trans: Transition) => void,
    onNew?: () => void,
    onRetry?: () => void,
    isLoading?: boolean,
    isError?: boolean,
    error?: Error | null,
    // Pagination
    totalCount?: number,
    currentPage?: number,
    totalPages?: number,
    perPage?: number,
    onPageChange?: (page: number) => void,
    onPerPageChange?: (size: number) => void,
    onNext?: () => void,
    onPrev?: () => void,
  }>();
  

  const currentCount = $derived(transitions.length);

  // Build display filters for FilterChips component
  const displayFilters = $derived({
    search: transitionsStore.searchQuery ? [transitionsStore.searchQuery] : [],
    type: transitionsStore.filters.transitionType.map(t => TRANSITION_TYPE_CONFIG[t].label)
  });

  function removeFilter(category: string, value: string) {
    if (category === 'search') {
      transitionsStore.setSearchQuery('');
    } else if (category === 'type') {
      // Find the type value from its label
      const typeEntry = Object.entries(TRANSITION_TYPE_CONFIG).find(([_, config]) => config.label === value);
      if (typeEntry) {
        transitionsStore.toggleTransitionType(typeEntry[0] as TransitionType);
      }
    }
  }
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
  <!-- État: Chargement -->
  {#if isLoading}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <AnimateSpin text="Chargement des mouvements" />
    </div>

  <!-- État: Erreur -->
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

  <!-- État: Données disponibles (header + filters) -->
  {:else}
    <div class="flexx items-center justify-between px-5 py-2  bg-white border-b-none border-slate-100/60 sticky top-0 z-10 backdrop-blur-sm hidden" in:fade={{ duration: 200 }}>
      <span class="text-[0.85rem] font-medium text-slate-600">
        {totalCount} mouvement{totalCount > 1 ? 's' : ''}
      </span>
    </div>

    <!-- FilterChips -->
    <div class="px-5 py-0 bg-white border-slate-100/60 transition-all {transitionsStore.activeFiltersCount > 0 ? "py-1 border-b" : ""}">
      <FilterChips
        filters={displayFilters}
        activeFiltersCount={transitionsStore.activeFiltersCount}
        onRemove={removeFilter}
        onReset={() => transitionsStore.resetFilters()}
      />
    </div>
  {/if}

  <!-- État: Données vides -->
  {#if !isLoading && !isError && transitions.length === 0}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <Empty
        title="Aucun mouvement"
        description={transitionsStore.activeFiltersCount > 0
          ? "Aucun résultat ne correspond à vos critères de recherche."
          : "L'historique des changements est vide."}
        icon={transitionsStore.activeFiltersCount > 0 ? "search-x" : "history"}
        iconSize={28}
        iconStrokeWidth={1.3}
        iconClass="text-slate-300"
      >
        {#if transitionsStore.activeFiltersCount > 0}
          <Button variant="ghost" onclick={() => transitionsStore.resetFilters()} class="h-7 bg-slate-50">
            <AppIcon name="x" size={16} class="text-slate-400" />
            Réinitialiser les filtres
          </Button>
        {:else if onNew}
          <EmptyButton labelElement="un mouvement" {onNew} />
        {/if}
      </Empty>
    </div>

  <!-- État: Données disponibles (list) -->
  {:else if !isLoading && !isError}
    <div class="flex-1 overflow-auto custom-scrollbar flex flex-col" style="--scrollbar-size: 5px" in:fade={{ duration: 200 }}>
      
      <!-- Column Headers -->
      <div class="sticky top-0 z-10 flex items-center h-8! px-6 bg-white border-b border-slate-100">
        <span class="w-[10%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Type</span>
        <span class="w-[16%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
        <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Origine</span>
        <span class="w-[2%]"></span>
        <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Destination</span>
        <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Motif</span>
        <span class="w-[12%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right pr-4">Date</span>
        <span class="w-[6%]"></span>
      </div>

      <div class="flex-1">
        {#each transitions as trans, i (trans.id)}
          <TransitionItem transition={trans} index={i} {onEdit} {onDelete} />
        {/each}
      </div>

      <!-- Pagination -->
      <div class="px-6 py-0.5 border-t border-slate-100 bg-white sticky bottom-0 z-10" in:fade={{ duration: 200 }}>
        <DataPagination
          {currentCount}
          {totalCount}
          {currentPage}
          {totalPages}
          {perPage}
          onPageChange={onPageChange ?? (() => {})}
          onPerPageChange={onPerPageChange ?? (() => {})}
          onNext={onNext ?? (() => {})}
          onPrev={onPrev ?? (() => {})}
          unitLabel="mouvements"
        />
      </div>
    </div>
  {/if}
</div>

