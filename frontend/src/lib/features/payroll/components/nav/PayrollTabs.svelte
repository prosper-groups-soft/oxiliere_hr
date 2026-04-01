<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { page } from '$app/state';
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";

  const TABS = [
    { id: 'payslips', label: 'Bulletins', icon: 'file-text', path: '/payroll/payslips' },
    { id: 'run', label: 'Exécution', icon: 'play-circle', path: '/payroll/run' },
    { id: 'advances', label: 'Avances', icon: 'banknote', path: '/payroll/advances' },
  ];

  const activeTabId = $derived.by(() => {
    const tab = TABS.find(t => page.url.pathname.startsWith(t.path));
    return tab?.id || 'run';
  });

  let tabElements = $state<Record<string, HTMLAnchorElement | null>>({
    run: null,
    payslips: null,
    advances: null
  });
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });
</script>


<div class="border-b border-slate-100 px-4 flex items-center justify-between pr-8">
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

        {#if tab.id === 'advances' && payrollStore.pendingAdvances > 0}
          <span class={cn(
            "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[0.7rem] font-bold",
            activeTabId === tab.id
              ? "bg-primary text-white"
              : "bg-slate-100 text-slate-600 group-hover:bg-slate-200"
          )}>
            {payrollStore.pendingAdvances}
          </span>
        {/if}
      </a>
    {/each}

    <div
      class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out"
      style={indicatorStyle}
    ></div>
  </nav>

  {#if activeTabId === 'payslips'}
    <div class="hidden shrink-0 sm:flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-0.5 shadow-fine">
      <span class="h-1.5 w-1.5 rounded-full bg-blue-500"></span>
      <span class="text-[0.75rem] font-medium text-slate-600">
        {payrollStore.totalCount} bulletin{payrollStore.totalCount > 1 ? 's' : ''}
      </span>
    </div>
  {/if}
</div>

