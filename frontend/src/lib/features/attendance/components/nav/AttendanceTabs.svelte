<script lang="ts">
  import { fade } from 'svelte/transition';
  import { ui } from "@/stores/ui.svelte";
  import { cn } from "@/utilities/common/css";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { attendanceStore } from "@/features/attendance/stores/attendance.svelte";
  import { page } from '$app/state';
  import AttendanceSummaryStats from "@/features/attendance/components/shared/AttendanceSummaryStats.svelte";

  const TABS = [
    { id: 'register', label: 'Suivi', icon: 'clipboard-list', path: '/attendance/register' },
    { id: 'config', label: 'Planning', icon: 'calendar-days', path: '/attendance/config' },
    { id: 'policies', label: 'Modèles', icon: 'layout-template', path: '/attendance/policies' },
  ];

  const statusOptions = [
    { value: 'PRESENT', label: 'Présents', color: 'bg-emerald-500' },
    { value: 'LATE', label: 'Retards', color: 'bg-amber-500' },
    { value: 'ABSENT', label: 'Absents', color: 'bg-rose-500' },
  ];

  // Active Tab derived from current URL
  const activeTabId = $derived.by(() => {
    const tab = TABS.find(t => page.url.pathname.startsWith(t.path));
    return tab?.id || 'register';
  });

  // --- Sliding Indicator Logic ---
  let tabElements = $state<Record<string, HTMLAnchorElement | null>>({
    register: null,
    config: null,
    policies: null
  });
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });

  // --- Date formatting ---
  const formattedDate = $derived.by(() => {
    const date = new Date(attendanceStore.filters.dateRange.from);
    return date.toLocaleDateString('fr-FR', { 
      day: 'numeric', 
      month: 'long', 
      year: 'numeric',
      weekday: 'long'
    });
  });

  // Header Stats Integration
  $effect(() => {
    ui.addActions('attendance-stats', AttendanceStatsAction);
    return () => ui.removeActions('attendance-stats');
  });
</script>


<div class="border-b border-slate-100 px-4 flex items-center justify-between">
  <nav class="relative flex items-center gap-5 pt-1">
    {#each TABS as tab}
      <a 
        bind:this={tabElements[tab.id]}
        href={tab.path}
        data-sveltekit-noscroll
        class={cn(
          "relative flex items-center gap-2.5 bg-transparent transition-colors duration-200",
          "px-1 pb-2.5 pt-1 outline-none focus-visible:ring-0",
          "group cursor-pointer",
          activeTabId === tab.id
            ? "text-primary"
            : "text-slate-700 hover:text-slate-800"
        )}
      >
        <AppIcon name={tab.icon} size={18} />
        <span class="text-[0.879rem] tracking-tight">{tab.label}</span>
      </a>
    {/each}

    <!-- Sliding Indicator -->
    <div 
      class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out"
      style={indicatorStyle}
    ></div>
  </nav>

  {#if activeTabId === 'register'}
    <div in:fade={{ duration: 200 }} class="flex items-center gap-4 pr-6">
      <div class="flex items-center gap-1.5">
        {#each statusOptions as opt}
          <button 
            onclick={() => attendanceStore.toggleFilter('status', opt.value)}
            class={cn(
              "flex items-center gap-2 px-3 py-1 cursor-pointer text-[0.77rem] rounded-full border transition-all leading-none",
              attendanceStore.filters.status.includes(opt.value as any)
                ? "border-slate-400 bg-slate-200 text-slate-900 shadow-fine"
                : "border-slate-100 bg-[#f5f6f7] text-slate-600 hover:border-slate-200"
            )}
          >
            <div class={cn("h-1.5 w-1.5 rounded-full", opt.color)}></div>
            {opt.label}
          </button>
        {/each}
      </div>
      <div class="h-6 w-px bg-slate-200"></div>
      <div class="flex items-center gap-2 text-slate-600">
        <AppIcon name="calendar" size={16} class="text-slate-400" />
        <span class="text-[0.85rem] font-medium">{formattedDate}</span>
      </div>
    </div>
  {/if}
</div>


{#snippet AttendanceStatsAction()}
  <AttendanceSummaryStats />
{/snippet}

