<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import { Button } from "@/components/ui/button";
  import type { RunListItem } from "../../types/types";
  import { RUN_LIST_STATUS_LABELS, RUN_LIST_STATUS_COLORS } from "../../types/types";
  import { goToActiveOrNewPayroll } from "@/features/payroll/utils/goToActiveOrNewPayroll";
  import { goto } from "$app/navigation";

  
  let {
    runs = [],
    activeFiltersCount = 0,
    onResetFilters = () => {}
  } = $props<{
    runs: RunListItem[];
    activeFiltersCount?: number;
    onResetFilters?: () => void;
  }>();

  function formatCurrency(value: number) {
    return value.toLocaleString('fr-FR', {
      style: 'currency',
      currency: 'USD',
      maximumFractionDigits: 0,
      minimumFractionDigits: 0
    });
  }

  function getStatusDotColor(run: RunListItem) {
    return RUN_LIST_STATUS_COLORS[run.status].dot;
  }

  function getStatusBadgeClasses(run: RunListItem) {
    const c = RUN_LIST_STATUS_COLORS[run.status];
    return cn(c.bg, c.text);
  }

  function getStatusDotClasses(run: RunListItem) {
    return cn("w-1.5 h-1.5 rounded-full", RUN_LIST_STATUS_COLORS[run.status].dot);
  }

  function getStatusLabel(run: RunListItem) {
    return RUN_LIST_STATUS_LABELS[run.status];
  }

  function getProgressColor(run: RunListItem) {
    if (run.status === 'error') return 'bg-rose-400';
    if (run.employeeCount === run.totalEmployeeCount && run.totalEmployeeCount > 0) return 'bg-emerald-400';
    if (run.employeeCount > 0) return 'bg-amber-400';
    return 'bg-slate-300';
  }

  function getProgressWidth(run: RunListItem) {
    return run.totalEmployeeCount > 0
      ? Math.round((run.employeeCount / run.totalEmployeeCount) * 100)
      : 0;
  }
</script>


<div class="flex-1 flex flex-col min-h-0 bg-white">
  {#if runs.length === 0}
    <!-- Empty states -->
    <div class="flex flex-col items-center justify-center h-full px-6">
      {#if activeFiltersCount > 0}
        <!-- Filtered empty state -->
        <div class="w-16 h-16 rounded-full bg-amber-50 flex items-center justify-center mb-4">
          <AppIcon name="search-x" size={28} class="text-amber-400" />
        </div>
        <h3 class="text-[0.95rem] font-bold text-slate-600 mb-1">Aucun résultat</h3>
        <p class="text-[0.85rem] text-slate-400 text-center max-w-xs mb-5">
          Aucun cycle ne correspond à vos critères de recherche.
        </p>
        <Button variant="outline" size="sm" onclick={onResetFilters} class="rounded-lg">
          <AppIcon name="x" size={15} />
          Effacer les filtres
        </Button>
      {:else}
        <!-- Absolute empty state -->
        <div class="w-20 h-20 rounded-full bg-slate-50 flex items-center justify-center mb-5">
          <AppIcon name="file-text" size={36} class="text-slate-300" />
        </div>
        <h3 class="text-[1.05rem] font-bold text-slate-600 mb-1">Aucune exécution</h3>
        <p class="text-[0.85rem] text-slate-400 text-center max-w-sm mb-6">
          Créez votre premier cycle de paie pour commencer.
        </p>
        <Button
          variant="default"
          size="sm"
          onclick={() => goToActiveOrNewPayroll()}
          class="shadow-fine bg-primary text-white text-[0.83rem] hover:text-white rounded-lg"
        >
          <AppIcon name="play-circle" size={17} />
          Commencer la paie
        </Button>
      {/if}
    </div>

  {:else}
    <!-- Data area -->
    <div class="flex-1 overflow-auto custom-scrollbar flex flex-col" style="--scrollbar-size: 5px">
      <!-- Sticky Column Headers -->
      <div class="sticky top-0 z-10 flex items-center h-8! px-6 bg-white border-b border-slate-100">
        <span class="w-[5%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Statut</span>
        <span class="w-[24%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400">Période</span>
        <span class="w-[15%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-center">Employés</span>
        <span class="w-[18%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right">Brut total</span>
        <span class="w-[18%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-center">Statut</span>
        <span class="w-[10%] text-[0.7rem] font-bold uppercase tracking-widest text-slate-400 text-right">Actions</span>
      </div>

      <!-- Data Rows -->
      <div class="flex-1">
        {#each runs as run (run.id)}
          <div
            class="group flex items-center py-3 px-6 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors"
            onclick={() => goto(`/payroll/run/${run.id}`)}
            role="button"
            tabindex="0"
            onkeydown={(e) => e.key === 'Enter' && goto(`/payroll/run/${run.id}`)}
          >
            <!-- Status dot -->
            <div class="w-[5%] flex items-center">
              <span class="block w-2.5 h-2.5 rounded-full {getStatusDotColor(run)}"></span>
            </div>

            <!-- Period -->
            <div class="w-[24%] flex items-center gap-2 min-w-0">
              <span class="text-[0.9rem] font-semibold text-slate-800 group-hover:text-primary transition-colors truncate">
                {run.periodLabel}
              </span>
              {#if run.status === 'processing'}
                <Badge
                  variant="outline"
                  class="bg-blue-50 text-blue-600 border-0 text-[0.65rem] font-bold px-2 py-0.5 rounded-full shrink-0 flex items-center gap-1"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                  En cours
                </Badge>
              {/if}
            </div>

            <!-- Employee count with progress bar -->
            <div class="w-[15%] flex flex-col items-center justify-center gap-0.5">
              <div class="flex items-center gap-1.5">
                <span class="text-[0.85rem] font-bold text-slate-700 tabular-nums">{run.employeeCount}</span>
                <span class="text-[0.7rem] text-slate-400 font-medium">/ {run.totalEmployeeCount}</span>
              </div>
              <div class="w-20 h-1.5 rounded-full bg-slate-100 overflow-hidden">
                <div
                  class={cn("h-full rounded-full transition-all duration-500", getProgressColor(run))}
                  style="width: {getProgressWidth(run)}%"
                ></div>
              </div>
            </div>

            <!-- Gross total -->
            <div class="w-[18%] text-right">
              <span class={cn(
                "text-[0.9rem] font-extrabold tracking-tight tabular-nums",
                run.grossTotal > 0 ? "text-slate-800" : "text-slate-400"
              )}>
                {run.grossTotal > 0 ? formatCurrency(run.grossTotal) : '—'}
              </span>
            </div>

            <!-- Status badge -->
            <div class="w-[18%] flex justify-center">
              <Badge
                variant="outline"
                class={cn(
                  "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[0.72rem] font-bold uppercase tracking-wider border-0",
                  getStatusBadgeClasses(run)
                )}
              >
                <span class={getStatusDotClasses(run)}></span>
                {getStatusLabel(run)}
              </Badge>
            </div>

            <!-- Actions -->
            <div class="w-[10%] text-right">
              <div class="flex items-center justify-end gap-2 transition-all duration-200">
                <button
                  onclick={(e) => { e.stopPropagation(); goto(`/payroll/run/${run.id}`); }}
                  class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[0.72rem] font-bold text-slate-500 hover:text-primary hover:bg-primary/5 transition-all cursor-pointer"
                >
                  <AppIcon name="eye" size={16} />
                  Détail
                </button>
                {#if run.status === 'error'}
                  <button
                    onclick={(e) => { e.stopPropagation(); goto(`/payroll/run/${run.id}/validation`); }}
                    class="flex items-center gap-1.5 px-2.5 py-1.5 rounded-lg text-[0.72rem] font-bold text-rose-600 hover:text-rose-700 hover:bg-rose-50 transition-all cursor-pointer"
                  >
                    <AppIcon name="triangle-alert" size={15} />
                    Corriger
                  </button>
                {/if}
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>
  {/if}
</div>

