<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { leavesStore } from "@/features/leaves/stores/leaves.svelte";
  import { page } from '$app/state';
  import { scale, fade } from 'svelte/transition';

  const TABS = [
    { id: 'requests', label: 'Mes Congés', icon: 'calendar-days', path: '/leaves/requests' },
    { id: 'team', label: 'Équipe', icon: 'users', path: '/leaves/team' },
  ];

  // Active Tab derived from current URL
  const activeTabId = $derived.by(() => {
    const tab = TABS.find(t => page.url.pathname.startsWith(t.path));
    return tab?.id || 'requests';
  });

  // Fetch balances for minimalist stats
  const balances = $derived(leavesStore.getBalancesForEmployee());
  const annualBalance = $derived(balances.find(b => b.type === 'annual'));
  const sickBalance = $derived(balances.find(b => b.type === 'sick'));

  // --- Sliding Indicator Logic ---
  let tabElements = $state<Record<string, HTMLAnchorElement | null>>({
    requests: null,
    team: null,
    policies: null
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

        {#if tab.id === 'requests' && leavesStore.pendingCount > 0}
          <div transition:scale={{ duration: 200, start: 0.8 }}>
            <span class={cn(
              "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[0.7rem] font-bold transition-colors",
              activeTabId === tab.id 
                ? "bg-primary text-white" 
                : "bg-slate-100 text-slate-600 group-hover:bg-slate-200"
            )}>
              {leavesStore.pendingCount}
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
    <!-- Minimalist Stats -->
    <div in:fade={{ duration: 200 }} class="flex items-center gap-2 pr-6">
      {#if annualBalance}
        <div class="flex items-center gap-2 px-3 py-1 cursor-default text-[0.77rem] rounded-full border border-slate-100 bg-[#f5f6f7] text-slate-600 transition-all leading-none">
          <div class="h-1.5 w-1.5 rounded-full bg-blue-500"></div>
          Annuel : <span class="font-bold text-slate-800 text-[0.77rem]">{annualBalance.remaining}/{annualBalance.allocated} j</span>
        </div>
      {/if}
      
      {#if sickBalance}
        <div class="flex items-center gap-2 px-3 py-1 cursor-default text-[0.77rem] rounded-full border border-slate-100 bg-[#f5f6f7] text-slate-600 transition-all leading-none">
          <div class="h-1.5 w-1.5 rounded-full bg-rose-500"></div>
          Maladie : <span class="font-bold text-slate-800 text-[0.77rem]">{sickBalance.remaining}/{sickBalance.allocated} j</span>
        </div>
      {/if}
    </div>
  {/if}
</div>

