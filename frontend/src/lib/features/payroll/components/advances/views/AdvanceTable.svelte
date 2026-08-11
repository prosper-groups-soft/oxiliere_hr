<script lang="ts">
  import type { Advance } from "@/features/payroll/types/types";
  import AdvanceRow from "./AdvanceRow.svelte";
  import Empty from "@/components/shared/containers/empty/Empty.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Button } from "@/components/ui/button";
  import DataPagination from "@/components/layout/elements/DataPagination.svelte";
  import { ERROR_MESSAGES } from "@/constants/errors";
  import { fade } from "svelte/transition";


  let {
    advances = [],
    onNew,
    onRetry,
    isLoading = false,
    isError = false,
    isOffline = false,
    hasActiveFilters = false,
    onResetFilters,
    // Pagination props
    totalCount = 0,
    currentPage = 1,
    totalPages = 1,
    perPage = 8,
    onPageChange,
    onPerPageChange,
    onNext,
    onPrev,
    // Row actions
    onClick,
    onApprove,
    onReject,
    onActivate,
    onEdit,
    onSubmit,
    onViewDetail,
  } = $props<{
    advances: Advance[];
    onNew?: () => void;
    onRetry?: () => void;
    isLoading?: boolean;
    isError?: boolean;
    isOffline?: boolean;
    hasActiveFilters?: boolean;
    onResetFilters?: () => void;
    // Pagination
    totalCount?: number;
    currentPage?: number;
    totalPages?: number;
    perPage?: number;
    onPageChange?: (page: number) => void;
    onPerPageChange?: (size: number) => void;
    onNext?: () => void;
    onPrev?: () => void;
    // Row actions
    onClick?: (advance: Advance) => void;
    onApprove?: (advance: Advance) => void;
    onReject?: (advance: Advance) => void;
    onActivate?: (id: string) => void;
    onEdit?: (advance: Advance) => void;
    onSubmit?: (advance: Advance) => void;
    onViewDetail?: (advance: Advance) => void;
  }>();

  const currentCount = $derived(advances.length);
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
  <!-- État: Chargement -->
  {#if isLoading}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <AnimateSpin text="Chargement des avances" />
    </div>

  <!-- État: Erreur (ou hors-ligne) -->
  {:else if isError}
    <div class="flex-1 flex items-center justify-center p-8" in:fade={{ duration: 200 }}>
      <Empty
        title={isOffline ? "Mode hors-ligne" : "Erreur de chargement"}
        description={isOffline ? ERROR_MESSAGES.NETWORK.OFFLINE : "Impossible de charger les avances. Réessayez."}
        icon={isOffline ? "wifi-off" : "alert-circle"}
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
  {:else if advances.length === 0}
    <div class="flex-1 flex items-center justify-center" in:fade={{ duration: 200 }}>
      <Empty
        title="Aucune avance"
        description={hasActiveFilters
          ? "Aucune avance ne correspond à vos critères."
          : "Aucune demande d'avance n'a été enregistrée."}
        icon={hasActiveFilters ? "search-x" : "wallet"}
        iconSize={28}
        iconStrokeWidth={1.3}
        iconClass="text-slate-300"
      >
        {#if hasActiveFilters}
          <Button variant="ghost" onclick={onResetFilters} class="h-7 bg-slate-50">
            <AppIcon name="x" size={16} class="text-slate-400" />
            Réinitialiser les filtres
          </Button>
        {:else if onNew}
          <Button variant="default" onclick={onNew} class="h-7">
            <AppIcon name="plus" size={17} class="text-white" />
            Nouvelle demande
          </Button>
        {/if}
      </Empty>
    </div>

  <!-- État: Données disponibles -->
  {:else}
    <div class="flex-1 overflow-auto custom-scrollbar flex flex-col" style="--scrollbar-size: 5px" in:fade={{ duration: 200 }}>
      <!-- Column Headers -->
      <div class="sticky top-0 z-10 flex items-center h-9! px-6 bg-white border-b border-slate-100">
        <span class="w-[22%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Employé</span>
        <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Montant</span>
        <span class="w-[14%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</span>
        <span class="w-[13%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Risque</span>
        <span class="w-[13%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Solde restant</span>
        <span class="w-[11%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right pr-4">Date</span>
        <span class="w-[8%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right">Actions</span>
      </div>

      <div class="flex-1">
        {#each advances as advance, i (advance.id)}
          <AdvanceRow
            advance={advance}
            index={i}
            {onClick}
            {onApprove}
            {onReject}
            {onActivate}
            {onEdit}
            {onSubmit}
            {onViewDetail}
          />
        {/each}
      </div>

      <!-- Pagination -->
      {#if totalPages > 1}
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
            unitLabel="avances"
          />
        </div>
      {/if}
    </div>
  {/if}
</div>

