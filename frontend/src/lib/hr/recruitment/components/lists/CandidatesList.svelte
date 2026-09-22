<script lang="ts">
  import { fade } from 'svelte/transition';
  import Empty from '@/components/shared/containers/empty/Empty.svelte';
  import EmptyButton from '@/components/shared/containers/empty/EmptyButton.svelte';
  import CandidateRow from './views/candidate/CandidateRow.svelte';
  import CandidateSheet from '@/hr/recruitment/components/shared/sheets/candidate/CandidateSheet.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import { getFriendlyErrorMessage } from '@/constants/errors';
  import { recruitmentStore } from '../../stores/recruitment.svelte';
  import type { Candidate } from '../../types/types';
  

  let { 
    candidates = [],
    stageConfig,
    isLoading = false,
    isError = false,
    error = null,
    activeFiltersCount = 0,
    onRetry,
  } = $props<{
    candidates: Candidate[];
    stageConfig: Record<string, { label: string, color: string }>;
    isLoading?: boolean;
    isError?: boolean;
    error?: Error | null;
    activeFiltersCount?: number;
    onRetry?: () => void;
  }>();

  let isAddSheetOpen = $state(false);
  let editingCandidate = $state<Candidate | null>(null);
  let isEditSheetOpen = $state(false);

  function handleEditCandidate(candidate: Candidate) {
    editingCandidate = candidate;
    isEditSheetOpen = true;
  }

  $effect(() => {
    if (!isEditSheetOpen) {
      editingCandidate = null;
    }
  });

  function handleViewProfile(candidateId: string) {
    recruitmentStore.profileSheetCandidateId = candidateId;
    recruitmentStore.profileSheetOpen = true;
  }
</script>


<div class="flex-1 flex flex-col min-h-0 h-full overflow-hidden">

  <!-- État: Chargement -->
  {#if isLoading}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <AnimateSpin text="Chargement des candidats" />
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
  {:else if candidates.length === 0}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <Empty
        title="Aucun candidat"
        description={activeFiltersCount > 0
          ? "Aucun résultat ne correspond à vos critères de recherche."
          : "Commencez par ajouter des candidats à votre pipeline de recrutement."}
        icon={activeFiltersCount > 0 ? "search-x" : "users"}
        iconSize={28}
        iconStrokeWidth={1.3}
        iconClass="text-slate-300"
      >
        {#if activeFiltersCount > 0}
          <Button variant="ghost" onclick={() => recruitmentStore.resetFilters()} class="h-7 bg-slate-50">
            <AppIcon name="x" size={16} class="text-slate-400" />
            Réinitialiser les filtres
          </Button>
        {:else}
          <EmptyButton labelElement="un candidat" onNew={() => isAddSheetOpen = true} />
        {/if}
      </Empty>
    </div>

  <!-- État: Données disponibles -->
  {:else}
    <div class="flex-1 overflow-auto custom-scrollbar">
      <!-- Headers -->
      <div class="sticky top-0 z-10 flex items-center h-8 px-6 bg-white border-b border-slate-100">
        <span class="w-[21%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Candidat</span>
        <span class="w-[10%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Source</span>
        <span class="w-[38%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Poste visé</span>
        <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Compétences</span>
        <span class="w-[10%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Lieu</span>
        <span class="w-[3%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Actions</span>
      </div>

      <div class="divide-y divide-slate-100">
        {#each candidates as candidate (candidate.id)}
          <CandidateRow {candidate} onEdit={handleEditCandidate} onViewProfile={handleViewProfile} />
        {/each}
      </div>
    </div>
  {/if}
</div>


<CandidateSheet bind:open={isAddSheetOpen} />
<CandidateSheet bind:open={isEditSheetOpen} bind:candidate={editingCandidate} />




