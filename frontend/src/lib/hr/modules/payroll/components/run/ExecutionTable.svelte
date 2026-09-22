<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Badge } from "@/components/ui/badge";
  import type { RunListItem } from "../../types/types";
  import { RUN_LIST_STATUS_LABELS, RUN_LIST_STATUS_COLORS } from "../../types/types";
  import RunDetailSheet from "./sheets/RunDetailSheet.svelte";

  
  let selectedRun = $state<RunListItem | null>(null);
  let detailOpen = $state(false);
  function openDetail(run: RunListItem) {
    selectedRun = run;
    detailOpen = true;
  }

  
  let {
    runs = [],
  } = $props<{
    runs: RunListItem[];
  }>();

  // Les montants des runs sont en CDF (devise locale) — jamais en USD.
  function formatCurrency(value: number) {
    return value.toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' CDF';
  }

  /** Date ISO (YYYY-MM-DD…) → court « JJ/MM ». */
  function shortDate(iso?: string): string {
    const raw = iso ? iso.slice(0, 10) : '';
    if (!raw) return '';
    const d = new Date(raw + 'T00:00:00');
    if (Number.isNaN(d.getTime())) return raw;
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit' });
  }

  /** « 2026-09-01 - 2026-09-30 » → début/fin parsées. */
  function periodBounds(label?: string): { start: string; end: string } {
    const parts = (label || '').split(' - ');
    return { start: parts[0] ? parts[0].slice(0, 10) : '', end: parts[1] ? parts[1].slice(0, 10) : '' };
  }

  /** Libellé mois/année lisible (« septembre 2026 ») à partir du début de période. */
  function periodMonthLabel(label?: string): string {
    const { start } = periodBounds(label);
    const y = Number(start.slice(0, 4));
    const m = Number(start.slice(5, 7));
    if (start && Number.isInteger(y) && Number.isInteger(m)) {
      return new Date(y, m - 1, 1).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' });
    }
    return label || '';
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


<div class="flex-1 flex flex-col min-h-0 bg-white h-full">
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
          {@const pb = periodBounds(run.periodLabel)}
          <div
            class="group flex items-center py-3 px-6 border-b border-slate-50 hover:bg-indigo-50/30 cursor-pointer transition-colors"
            onclick={() => openDetail(run)}
            role="button"
            tabindex="0"
            onkeydown={(e) => e.key === 'Enter' && openDetail(run)}
          >
            <!-- Status dot -->
            <div class="w-[5%] flex items-center">
              <span class="block w-2.5 h-2.5 rounded-full {getStatusDotColor(run)}"></span>
            </div>            
            <!-- Period -->
            <div class="w-[24%] flex items-center gap-2 min-w-0">
              <div class="min-w-0">
                <span class="block text-[0.9rem] font-semibold text-slate-800 group-hover:text-primary transition-colors truncate capitalize">
                  {periodMonthLabel(run.periodLabel)}
                </span>
                {#if pb.start && pb.end}
                  <span class="block text-sm text-slate-500 tabular-nums">
                    {shortDate(pb.start)} → {shortDate(pb.end)} {pb.start.slice(0, 4)}
                  </span>
                {/if}
              </div>
              {#if run.status === 'processing'}
                <Badge
                  variant="outline"
                  class="bg-blue-50 text-blue-600 border-0 text-sm font-bold px-2 py-0.5 rounded-full shrink-0 flex items-center gap-1"
                >
                  <span class="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse"></span>
                  En cours
                </Badge>
              {/if}
            </div>

            <!-- Employee count with progress bar -->
            <div class="w-[15%] flex flex-col items-center justify-center gap-0.5">
              <div class="flex items-center gap-1.5">
                <span class="text-sm font-bold text-slate-700 tabular-nums">{run.employeeCount}</span>
                <span class="text-sm text-slate-500 font-medium">/ {run.totalEmployeeCount}</span>
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
                run.grossTotal > 0 ? "text-slate-800" : "text-slate-500"
              )}>
                {run.grossTotal > 0 ? formatCurrency(run.grossTotal) : '—'}
              </span>
            </div>

            <!-- Status badge -->
            <div class="w-[18%] flex justify-center">
              <Badge
                variant="outline"
                class={cn(
                  "inline-flex items-center gap-1.5 px-3 py-1.5 rounded-full text-[0.74rem] font-bold uppercase tracking-wider border-0",
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
                  onclick={(e) => { e.stopPropagation(); openDetail(run); }}
                  class="flex items-center justify-center gap-1.5 px-2.5 py-1.5 rounded-lg text-sm font-medium text-slate-500 hover:text-primary hover:bg-primary/5 transition-all cursor-pointer"
                >
                  <AppIcon name="eye" size={16} />
                  <span class="text-sm">Détail</span>
                </button>
              </div>
            </div>
          </div>
        {/each}
      </div>
    </div>

  <RunDetailSheet run={selectedRun} bind:open={detailOpen} />
</div>

