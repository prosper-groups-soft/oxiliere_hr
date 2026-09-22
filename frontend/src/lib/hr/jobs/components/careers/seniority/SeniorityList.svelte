<script lang="ts">
  import { fade } from 'svelte/transition';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { jobsStore } from "../../../stores/jobs.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import type { SeniorityLevelDefinition } from "../../../types/types";
  import { Button } from "@/components/ui/button";
  import SeniorityRow from "./views/SeniorityRow.svelte";
  import { getFriendlyErrorMessage } from '@/constants/errors';
  

  let {
    onEdit,
    onDelete,
    onNew,
    onRetry,
    onClearSearch,
    isLoading = false,
    isError = false,
    error = null,
    searchQuery = ''
  } = $props<{
    onEdit?: (level: SeniorityLevelDefinition) => void
    onDelete?: (level: SeniorityLevelDefinition) => void
    onNew?: () => void
    onRetry?: () => void
    onClearSearch?: () => void
    isLoading?: boolean
    isError?: boolean
    error?: Error | null
    searchQuery?: string
  }>();

  // Filtrer et trier les niveaux
  const levels = $derived(
    [...jobsStore.seniorityLevels]
      .filter(l =>
        !searchQuery ||
        l.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
        l.level.toLowerCase().includes(searchQuery.toLowerCase()) ||
        l.requirements.some(r => r.toLowerCase().includes(searchQuery.toLowerCase()))
      )
      .sort((a, b) => a.rank - b.rank)
  );

  // Nombre de filtres actifs (seulement la recherche pour ce composant)
  const activeFiltersCount = $derived(searchQuery ? 1 : 0);
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
  <!-- État: Chargement -->
  {#if isLoading}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <AnimateSpin text="Chargement des niveaux" />
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

  <!-- État: Données vides -->
  {:else if levels.length === 0}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <Empty
        title="Aucun niveau"
        description={activeFiltersCount > 0
          ? "Aucun résultat ne correspond à votre recherche."
          : "Aucun palier de carrière n'a été créé."}
        icon={activeFiltersCount > 0 ? "search-x" : "layers"}
        iconSize={28}
        iconStrokeWidth={1.3}
        iconClass="text-slate-300"
      >
        {#if activeFiltersCount > 0}
          <Button variant="ghost" onclick={() => onClearSearch?.()} class="h-7 bg-slate-50">
            <AppIcon name="x" size={16} class="text-slate-400" />
            Effacer la recherche
          </Button>
        {:else if onNew}
          <EmptyButton labelElement="un niveau" {onNew} />
        {/if}
      </Empty>
    </div>

  <!-- État: Données disponibles (header caché + list) -->
  {:else}
    <div class="flexx items-center justify-between px-5 py-2 bg-white border-b-none border-slate-100/60 sticky top-0 z-10 backdrop-blur-sm hidden" in:fade={{ duration: 200 }}>
      <span class="text-[0.85rem] font-medium text-slate-600">
        {levels.length} palier{levels.length > 1 ? 's' : ''}
      </span>
    </div>

    <!-- Area: Scrollable List -->
    <div class="flex-1 overflow-auto custom-scrollbar" style="--scrollbar-size: 5px" in:fade={{ duration: 200 }}>
      {#each levels as level, i (level.id)}
        <SeniorityRow {level} index={i} {onEdit} {onDelete} />
      {/each}
    </div>

  {/if}
</div>

