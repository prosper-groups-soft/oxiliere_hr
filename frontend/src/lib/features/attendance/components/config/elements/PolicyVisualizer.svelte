<script lang="ts">
  import type { WorkPolicy, WorkPeriod, DayPattern, DayOfWeek } from "../../../types/types";
  import { slide } from 'svelte/transition';
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { cn } from "@/utilities/common/css";

  let { 
    policy, 
    overlayPolicy = null,
    showDetails = true 
  } = $props<{ 
    policy: WorkPolicy;
    overlayPolicy?: WorkPolicy | null;
    showDetails?: boolean;
  }>();

  let expanded = $state({
    planning: true,
    details: true,
    stats: true
  });

  $effect(() => {
    expanded.details = showDetails;
  });

  function toggleSection(section: keyof typeof expanded) {
    expanded[section] = !expanded[section];
  }

  const days: { label: string; index: DayOfWeek }[] = [
    { label: "Lundi", index: 1 },
    { label: "Mardi", index: 2 },
    { label: "Mercredi", index: 3 },
    { label: "Jeudi", index: 4 },
    { label: "Vendredi", index: 5 },
    { label: "Samedi", index: 6 },
    { label: "Dimanche", index: 0 },
  ];

  // --- Logic Helpers ---
  function calculateHours(periods: WorkPeriod[], type: 'work' | 'break' = 'work') {
    if (!periods) return 0;
    return periods
      .filter(p => p.type === type)
      .reduce((total, p) => {
        const [sH, sM] = p.startTime.split(':').map(Number);
        const [eH, eM] = p.endTime.split(':').map(Number);
        return total + ((eH * 60 + eM) - (sH * 60 + sM));
      }, 0) / 60;
  }

  function formatTimeCompact(time: string) {
    if (!time) return '';
    const [h, m] = time.split(':');
    const hours = parseInt(h);
    return `${hours}:${m}`;
  }

  function getWorkRange(periods: WorkPeriod[]) {
    const work = periods?.filter(p => p.type === 'work') || [];
    if (work.length === 0) return "OFF";
    return {
        start: formatTimeCompact(work[0].startTime),
        end: formatTimeCompact(work[work.length - 1].endTime)
    };
  }

  function getStats(p: WorkPolicy) {
    const patterns = Object.values(p.pattern) as DayPattern[];
    const work = patterns.reduce((acc, pattern) => acc + (pattern ? calculateHours(pattern.periods, 'work') : 0), 0);
    const breaks = patterns.reduce((acc, pattern) => acc + (pattern ? calculateHours(pattern.periods, 'break') : 0), 0);
    const total = work + breaks;
    
    return {
      activeDays: patterns.filter(pattern => pattern && !pattern.isOff).length,
      workHours: work,
      breakHours: breaks,
      ratio: total > 0 ? (work / total) * 100 : 0
    };
  }

  const baseStats = $derived(getStats(policy));
  const overlayStats = $derived(overlayPolicy ? getStats(overlayPolicy) : null);
</script>


<div class="space-y-6">
  <!-- 1. Grid of days (Superposition) -->
  <section class="space-y-3">
    <div class="flex items-center justify-between mb-1">
      <button 
        class="flex items-center gap-2 group cursor-pointer outline-none"
        onclick={() => toggleSection('planning')}
      >
        <div class={cn(
            "transition-transform duration-200 text-slate-400 group-hover:text-slate-500",
            expanded.planning ? "rotate-90" : "rotate-0"
        )}>
            <AppIcon name="chevron-right" size={14} />
        </div>
        <h4 class="text-[0.81rem] font-semibold text-slate-400 uppercase tracking-widest group-hover:text-slate-500 transition-colors">
            Planning Hebdomadaire
        </h4>
      </button>

      {#if overlayPolicy && expanded.planning}
        <div class="flex items-center gap-3" transition:slide>
          <div class="flex items-center gap-1.5">
            <div class="w-2 h-2 rounded-sm bg-blue-100 border border-blue-200"></div>
            <span class="text-[0.7rem] text-slate-500 font-medium uppercase tracking-tight">Base</span>
          </div>
          <div class="flex items-center gap-1.5">
            <div class="w-2 h-2 rounded-sm bg-primary"></div>
            <span class="text-[0.7rem] text-slate-500 font-medium uppercase tracking-tight">Shift</span>
          </div>
        </div>
      {/if}
    </div>

    {#if expanded.planning}
      <div class="grid grid-cols-7 gap-2" transition:slide>
        {#each days as day}
          {@const baseRange = getWorkRange(policy.pattern[day.index]?.periods)}
          {@const overlayRange = overlayPolicy ? getWorkRange(overlayPolicy.pattern[day.index]?.periods) : null}
          {@const hasOverlay = !!overlayPolicy && !!overlayRange && overlayRange !== "OFF"}
          {@const isBaseOff = baseRange === "OFF"}

          <div class="text-center group">
            <div class="text-[0.7rem] font-medium text-slate-500 mb-1.5 uppercase tracking-tighter transition-colors group-hover:text-slate-500">
              {day.label.slice(0, 3)}
            </div>
            
            <div class="relative aspect-square flex flex-col items-center justify-center rounded-lg border transition-all duration-200
              {hasOverlay 
              ? 'bg-white border-primary/30 ring-1 ring-primary/5' 
              : isBaseOff ? 'bg-slate-50 border-slate-100 text-slate-400' : 'bg-blue-100/30 border-blue-200 text-blue-600'}"
              >
                {#if hasOverlay}
                  <!-- Overlay Present -->
                  <div class="flex flex-col items-center gap-0.5 py-1">
                    <div class="flex flex-col items-center opacity-30 scale-90 line-through decoration-slate-400/50">
                      {@render CompactRange({ range: baseRange, variant: 'base' })}
                    </div>
                    {@render CompactRange({ range: overlayRange, variant: 'overlay' })}
                  </div>
                  {:else}
                  <!-- No Overlay -->
                  <div class="py-1">
                    {@render CompactRange({ range: baseRange, variant: 'base' })}
                  </div>
                {/if}
            </div>
          </div>
        {/each}
      </div>
    {/if}
  </section>

  <!-- 2. Detailed Periods -->
  {#if showDetails}
    <section class="space-y-3">
      <button 
        class="flex items-center gap-2 group cursor-pointer outline-none"
        onclick={() => toggleSection('details')}
      >
        <div class={cn(
          "transition-transform duration-200 text-slate-400 group-hover:text-slate-500",
          expanded.details ? "rotate-90" : "rotate-0"
        )}>
          <AppIcon name="chevron-right" size={14} />
        </div>
        <h4 class="text-[0.81rem] font-semibold text-slate-400 uppercase tracking-widest group-hover:text-slate-500 transition-colors flex items-center gap-1.5">
          <AppIcon name="list" size={13} />
            Détails des périodes
          </h4>
      </button>
      
      {#if expanded.details}
        <div class="space-y-3 max-h-[450px] overflow-y-auto px-0.5 custom-scrollbar" transition:slide>
          {#each days as day}
            {@const basePattern = policy.pattern[day.index]}
            {@const overlayPattern = overlayPolicy?.pattern[day.index]}
            {@const hasOverlay = !!overlayPolicy && !!overlayPattern}
            {@const baseActive = basePattern && !basePattern.isOff && basePattern.periods?.length > 0}
            {@const overlayActive = overlayPattern && !overlayPattern.isOff && overlayPattern.periods?.length > 0}

            {#if baseActive || overlayActive}
              <div class={cn(
                  "p-3 rounded-md border transition-all duration-200 bg-white",
                  hasOverlay ? "border-primary/10 bg-primary/2" : "border-slate-100 shadow-fine shadow-slate-200/50"
              )}>
                <div class="flex items-center justify-between border-b border-slate-50 pb-2 mb-2.5">
                  <div class="flex items-center gap-2">
                    <span class="text-[0.85rem] font-semibold text-slate-700">{day.label}</span>
                    {#if hasOverlay}
                      <AppIcon name="zap" size={11} class="text-primary/70" />
                    {/if}
                  </div>
                  
                  <div class="flex items-center gap-2">
                    {#if baseActive}
                      <span class={cn(
                        "text-[0.75rem] font-medium px-2 py-0.5 rounded",
                        hasOverlay ? "text-blue-300 line-through" : "bg-blue-100/50 text-blue-600 border border-blue-200"
                      )}>
                        {calculateHours(basePattern.periods).toFixed(1)}h
                      </span>
                    {/if}
                      
                    {#if hasOverlay && overlayActive}
                      <AppIcon name="arrow-right" size={11} class="text-slate-400" />
                      <span class="text-[0.75rem] font-bold px-2 py-0.5 rounded bg-primary text-white">
                        {calculateHours(overlayPattern.periods).toFixed(1)}h
                      </span>
                    {/if}
                  </div>
                </div>

                <!-- Periods Row -->
                <div class="grid grid-cols-1 md:grid-cols-2 gap-3">
                  <!-- Base Periods -->
                  {#if baseActive}
                    <div class={cn("space-y-1", hasOverlay && "opacity-20 grayscale pointer-events-none")}>
                      {#each basePattern.periods as period}
                        {@render PeriodRow({ period, variant: 'base' })}
                      {/each}
                    </div>
                  {/if}

                  <!-- Split divider or Next section -->
                  {#if hasOverlay && overlayActive}
                    <div class="space-y-1">
                      {#each overlayPattern.periods as period}
                        {@render PeriodRow({ period, variant: 'overlay' })}
                      {/each}
                    </div>
                  {:else if hasOverlay && !overlayActive}
                    <div class="flex items-center justify-center p-3 rounded-lg border border-dashed border-red-200 bg-red-50/50">
                      <span class="text-[0.75rem] font-bold text-red-600 uppercase tracking-widest">
                        Repos
                      </span>
                    </div>
                  {/if}
                </div>
              </div>
            {/if}
          {/each}
        </div>
      {/if}
    </section>
  {/if}

  <!-- 3. Stats Summary -->
  <section class="space-y-3">
    <button 
      class="flex items-center gap-2 group cursor-pointer outline-none"
      onclick={() => toggleSection('stats')}
    >
      <div class={cn(
        "transition-transform duration-200 text-slate-400 group-hover:text-slate-500",
        expanded.stats ? "rotate-90" : "rotate-0"
      )}>
        <AppIcon name="chevron-right" size={14} />
      </div>
      <h4 class="text-[0.81rem] font-medium text-slate-400 uppercase tracking-widest group-hover:text-slate-500 transition-colors">
        Impact Hebdomadaire
      </h4>
    </button>
    
    {#if expanded.stats}
      <div class="grid grid-cols-2 gap-3" transition:slide>
        {@render StatCard({ 
          icon: 'clock', 
          label: 'Travail', 
          baseValue: baseStats.workHours, 
          newValue: overlayStats?.workHours,
          iconColor: 'bg-slate-100 text-slate-500 border border-slate-200' 
        })}
        {@render StatCard({ 
          icon: 'coffee', 
          label: 'Pause', 
          baseValue: baseStats.breakHours, 
          newValue: overlayStats?.breakHours,
          iconColor: 'bg-slate-100 text-slate-500 border border-slate-200' 
        })}
      </div>
    {/if}
  </section>
</div>


{#snippet CompactRange({ range, variant }: { range: any, variant: 'base' | 'overlay' })}
  <div class="flex flex-col items-center justify-center min-h-[32px]">
    {#if range === "OFF"}
      <span class="text-[0.65rem] font-semibold tracking-wider text-slate-400 uppercase">Repos</span>
    {:else}
      <div class="flex flex-col items-center -space-y-0.5">
        <span class={cn(
          "text-[0.78rem] font-semibold tracking-tight tabular-nums",
          variant === 'overlay' ? "text-primary" : "text-slate-600"
        )}>{range.start}</span>
        <div class={cn(
          "w-1.5 h-0.5 rounded-full my-0.5",
          variant === 'overlay' ? "bg-primary/30" : "bg-slate-300/50"
        )}></div>
        <span class={cn(
          "text-[0.78rem] font-semibold tracking-tight tabular-nums",
          variant === 'overlay' ? "text-primary" : "text-slate-600"
        )}>{range.end}</span>
      </div>
    {/if}
  </div>
{/snippet}


{#snippet PeriodRow({ period, variant }: { period: WorkPeriod, variant: 'base' | 'overlay' })}
  {@const isWork = period.type === 'work'}
  <div class={cn(
    "flex items-center justify-between px-2 py-1.5 rounded border bg-white",
    variant === 'overlay' 
    ? (isWork ? "border-primary/20 hover:border-primary/40" : "border-amber-100")
    : "border-slate-50"
  )}>
    <div class="flex items-center gap-2 min-w-0 flex-1">
      <div class={cn(
        "w-1.5 h-1.5 rounded-full shrink-0",
        isWork 
        ? (variant === 'overlay' ? "bg-primary" : "bg-slate-400") 
        : "bg-amber-500"
      )}></div>
      <span class="text-[0.83rem] font-medium text-slate-600 truncate">
        {period.name || (isWork ? 'Travail' : 'Pause')}
      </span>
    </div>
    <div class="flex items-center gap-2 shrink-0">
      <span class="text-[0.83rem] text-slate-500 font-medium tabular-nums">
        {period.startTime} — {period.endTime}
      </span>
    </div>
  </div>
{/snippet}


{#snippet StatCard({ icon, label, baseValue, newValue, iconColor }: { icon: string, label: string, baseValue: number, newValue?: number, iconColor: string })}
  <div class="p-3.5 rounded-md border border-slate-100 bg-white shadow-sm shadow-slate-200/40 transition-all hover:border-slate-200">
    <div class="flex items-center justify-between mb-2">
      <span class="text-[0.65rem] font-semibold text-slate-400 uppercase tracking-wider">{label}</span>
      <div class={cn("p-1 rounded", iconColor)}>
        <AppIcon name={icon} size={15} />
      </div>
    </div>
    
    <div class="flex items-baseline gap-2">
      <div class={cn("text-[1rem] font-semibold tabular-nums", newValue !== undefined ? "text-slate-400 line-through" : "text-slate-700")}>
        {baseValue.toFixed(1)}h
      </div>
      
      {#if newValue !== undefined}
        <AppIcon name="arrow-right" size={14} class="text-slate-400" />
        <div class="text-[1rem] font-semibold text-primary tabular-nums">
          {newValue.toFixed(1)}h
        </div>
      {/if}
    </div>
    
    {#if newValue !== undefined}
      {@const diff = newValue - baseValue}
      <div class={cn(
        "mt-1 text-[0.65rem] font-medium flex items-center gap-1",
        diff > 0 ? "text-emerald-500" : diff < 0 ? "text-rose-400" : "text-slate-300"
      )}>
        {diff > 0 ? '+' : ''}{diff.toFixed(1)}h / sem
      </div>
    {/if}
  </div>
{/snippet}


<style>
  .custom-scrollbar::-webkit-scrollbar {
    width: 5px;
  }
  .custom-scrollbar::-webkit-scrollbar-thumb {
    background: #e2e8f0;
    border-radius: 10px;
  }
  .custom-scrollbar::-webkit-scrollbar-track {
    background: transparent;
  }
</style>

