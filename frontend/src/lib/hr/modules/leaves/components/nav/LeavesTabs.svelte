<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { page } from '$app/state';
  import { hr } from '@/hr/constants/navigation/navigation';
  import { scale, fade } from 'svelte/transition';
  import { useBalanceSummaryQuery, usePendingCountQuery } from "@/hr/modules/leaves/queries/leaveQueries";
  import { auth } from "@/hr/auth/stores/auth.svelte";
  import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';


  const TABS = [
    { id: 'requests', label: 'Mes Congés', icon: 'calendar-days', path: hr('/leaves/requests') },
    { id: 'team', label: 'Équipe', icon: 'users', path: hr('/leaves/team') },
    { id: 'settings', label: 'Configuration', icon: 'settings', path: hr('/leaves/settings') },
  ];

  // Active Tab derived from current URL
  const activeTabId = $derived.by(() => {
    const tab = TABS.find(t => page.url.pathname.startsWith(t.path));
    return tab?.id || 'requests';
  });

  // Current employee ID from auth store — reactive via $derived
  const currentEmployeeId = $derived(auth.currentUser?.id ?? '');

  // Query — wrapped in $derived.by so currentEmployeeId is tracked reactively
  // (avoids the Svelte 5 "state_referenced_locally" warning)
  const balanceQuery = $derived.by(() => useBalanceSummaryQuery('019e5513-31c0-736b-b2de-3cb3a6381e79'));
  const pendingQuery = usePendingCountQuery();

  // Derive annual balance from backend balance data
  const annualBalance = $derived(
    $balanceQuery?.data
      ? {
          type: 'annual' as const,
          allocated: $balanceQuery.data.allocated,
          remaining: $balanceQuery.data.totalAvailable,
          taken: $balanceQuery.data.deducted,
        }
      : null
  );

  // Pending count from dedicated backend endpoint
  const pendingCount = $derived($pendingQuery.data?.count ?? 0);

  // --- Sliding Indicator Logic ---
  let tabElements = $state<Record<string, HTMLAnchorElement | null>>({
    requests: null,
    team: null,
    settings: null,
  });
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });
</script>


<div class="border-b border-slate-100 px-4 flex items-center justify-between">
  <nav class="relative flex items-center gap-8 pt-1">
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

        {#if tab.id === 'requests' && pendingCount > 0}
          <div transition:scale={{ duration: 200, start: 0.8 }}>
            <span class={cn(
              "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[0.7rem] font-bold transition-colors",
              activeTabId === tab.id
                ? "bg-primary text-white"
                : "bg-slate-100 text-slate-600 group-hover:bg-slate-200"
            )}>
              {pendingCount}
            </span>
          </div>
        {/if}
      </a>
    {/each}

    <!-- Sliding Indicator -->
    <div
      class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out"
      style={indicatorStyle}
    ></div>
  </nav>

  {#if activeTabId === "requests"}
    <!-- Minimalist Stats from real backend data -->
    <div in:fade={{ duration: 200 }} class="flex items-center gap-2 pr-6">
      {#if $balanceQuery?.isPending && !$balanceQuery?.isFetched && !!currentEmployeeId}
        <div class="flex items-center gap-2 px-3 py-1 text-[0.77rem] rounded-full border border-slate-100 bg-[#f5f6f7] text-slate-400">
          <AnimateSpin class="border-slate-400 size-2.5" text="Chargement" textPosition="right" />
        </div>
      {:else if annualBalance}
        <button class="group relative flex items-center gap-3 px-3 py-1.5 cursor-default text-[0.85rem] rounded-full border border-slate-100 shadow-fine bg-[#f5f6f7] text-slate-600 transition-all hover:shadow hover:border-slate-200 hover:bg-slate-100 leading-none" title="Solde annuel">
          <div class="flex items-center gap-2">
            <div class="h-1.5 w-1.5 rounded-full bg-blue-500"></div>
            <span class="text-slate-500 font-medium text-[0.85rem]">Annuel</span>
          </div>
          <div class="flex items-baseline gap-1.5">
            <span class="font-bold text-slate-800 text-[0.87rem] tabular-nums">{annualBalance.remaining}</span>
            <span class="text-slate-400 text-[0.85rem]">/ {annualBalance.allocated} j</span>
          </div>
          <!-- Micro barre de progression -->
          <div class="absolute bottom-0 left-2 right-2 h-0.5 rounded-full bg-slate-200 overflow-hidden">
            <div 
              class="h-full rounded-full bg-blue-500 transition-all duration-300" 
              style="width: {Math.min(100, (annualBalance.taken / annualBalance.allocated) * 100)}%"
            ></div>
          </div>
        </button>
      {/if}
    </div>
  {/if}
</div>
