<script lang="ts">
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { positionsStore } from "../../../stores/positionsStore.svelte";
  import type { JobPosition } from "../../../types/types";
  import { fade } from "svelte/transition";
  import { jobsStore } from "../../../stores/jobs.svelte";
  import PositionRow from "./views/PositionRow.svelte";
  import FilterChips from "@/components/shared/elements/FilterChips.svelte";
  import { Button } from "@/components/ui/button";
  import { getFriendlyErrorMessage } from '@/constants/errors';

  let {
    onEdit,
    onDelete,
    onNew,
    onRetry,
    isLoading = false,
    isError = false,
    error = null,
    searchQuery = ''
  } = $props<{
    onEdit?: (pos: JobPosition) => void,
    onDelete?: (pos: JobPosition) => void,
    onNew?: () => void,
    onRetry?: () => void,
    isLoading?: boolean,
    isError?: boolean,
    error?: Error | null,
    searchQuery?: string
  }>();

  // Synchroniser la prop searchQuery avec le store
  $effect(() => {
    positionsStore.setSearchQuery(searchQuery);
  });

  // Positions déjà filtrées par le store (recherche + filtres)
  const positions = $derived(positionsStore.filteredPositions);

  // Filtres avec recherche incluse comme un filtre virtuel pour FilterChips
  const displayFilters = $derived({
    ...positionsStore.filters,
    search: positionsStore.searchQuery ? [positionsStore.searchQuery] : []
  });
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
  <!-- État: Chargement -->
  {#if isLoading}
    <div class="flex-1 flex items-center justify-center" transition:fade={{ duration: 200 }}>
      <AnimateSpin text="Chargement des postes" />
    </div>

  <!-- État: Erreur -->
  {:else if isError}
    <div class="flex-1 flex items-center justify-center p-8" transition:fade={{ duration: 200 }}>
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
    <div class="flexx items-center justify-between px-5 py-2 bg-white border-b-none border-slate-100/60 sticky top-0 z-10 backdrop-blur-sm hidden" in:fade={{ duration: 200 }}>
      <span class="text-[0.85rem] font-medium text-slate-600">
        {positions.length} poste{positions.length > 1 ? 's' : ''}
      </span>
    </div>

    <!-- FilterChips -->
    <div class="px-5 py-0 bg-white border-slate-100/60 transition-all {positionsStore.activeFiltersCount > 0 ? "py-1 border-b" : ""}">
      <FilterChips
        filters={displayFilters}
        activeFiltersCount={positionsStore.activeFiltersCount}
        getDisplayLabel={(key, value) => {
          if (key === 'search') return `Recherche: "${value}"`;
          if (key === 'orgUnit') return jobsStore.getOrgUnitById(value)?.name || value;
          if (key === 'seniority') {
            const level = jobsStore.seniorityLevels.find(l => l.level === value);
            return level?.name || value;
          }
          return value;
        }}
        onRemove={(key, value) => {
          if (key === 'search') {
            positionsStore.setSearchQuery('');
          } else {
            positionsStore.toggleFilter(key as any, value);
          }
        }}
        onReset={() => positionsStore.resetFilters()}
        badgeClass="bg-indigo-50 text-indigo-600 hover:bg-indigo-100 border-indigo-100/50 text-[0.78rem]"
      />
    </div>
  {/if}

  <!-- État: Données vides -->
  {#if !isLoading && !isError && positions.length === 0}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <Empty
        title="Aucun poste"
        description={positionsStore.activeFiltersCount > 0
          ? "Aucun résultat ne correspond à vos critères de recherche."
          : "Aucun poste n'a été créé."}
        icon={positionsStore.activeFiltersCount > 0 ? "search-x" : "inbox"}
        iconSize={28}
        iconStrokeWidth={1.3}
        iconClass="text-slate-300"
      >
        {#if positionsStore.activeFiltersCount > 0}
          <Button variant="ghost" onclick={() => positionsStore.resetFilters()} class="h-7 bg-slate-50">
            <AppIcon name="x" size={16} class="text-slate-400" />
            Réinitialiser les filtres
          </Button>
        {:else if onNew}
          <EmptyButton labelElement="un poste" {onNew} />
        {/if}
      </Empty>
    </div>

  <!-- État: Données disponibles -->
  {:else if !isLoading && !isError}
    <div class="flex-1 overflow-auto custom-scrollbar flex flex-col" style="--scrollbar-size: 5px" transition:fade={{ duration: 200 }}>
      <!-- Column Headers -->
      <div class="sticky top-0 z-10 flex items-center h-8 px-6 bg-white border-b border-slate-100">
        <span class="w-[25%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Séniorité</span>
        <span class="w-[20%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Poste</span>
        <span class="w-[27.5%] px-2 text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Compétences</span>
        <span class="w-[27.5%] px-2 text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Exigences</span>
        <span class="w-[5%]"></span>
      </div>

      <div class="flex-1">
        {#each positions as pos, i (pos.id)}
          <PositionRow {pos} index={i} {onEdit} {onDelete} />
        {/each}
      </div>
    </div>
  {/if}
</div>

