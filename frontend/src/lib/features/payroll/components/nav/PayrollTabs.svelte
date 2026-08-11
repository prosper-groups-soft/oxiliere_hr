<script lang="ts">
  import { cn } from "@/utilities/common/css";
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { page } from '$app/state';
  import { goto } from '$app/navigation';
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import * as Tabs from '@/components/ui/tabs';


  const TABS = [
    { id: 'executions', label: 'Exécutions', icon: 'play-circle', path: '/payroll' },
    { id: 'payslips', label: 'Bulletins', icon: 'file-text', path: '/payroll/payslips' },
    { id: 'advances', label: 'Avances', icon: 'banknote', path: '/payroll/advances' },
    { id: 'settings', label: 'Configuration', icon: 'settings', path: '/payroll/payroll-settings' },
  ];

  // Trier par longueur de chemin (le plus long d'abord) pour 
  // éviter que '/payroll' ne matche tous les '/payroll/*'
  const SORTED_TABS = $derived([...TABS].sort((a, b) => b.path.length - a.path.length));

  const activeTabId = $derived.by(() => {
    const tab = SORTED_TABS.find(t => page.url.pathname.startsWith(t.path));
    return tab?.id || 'executions';
  });

  const handleTabChange = (value: string) => {
    const tab = TABS.find(t => t.id === value);
    if (tab) goto(tab.path);
  };

  let tabElements = $state<Record<string, HTMLElement | null>>({
    executions: null,
    payslips: null,
    advances: null,
    settings: null
  });
  let indicatorStyle = $state('');

  $effect(() => {
    const activeEl = tabElements[activeTabId];
    if (activeEl) {
      indicatorStyle = `left: ${activeEl.offsetLeft}px; width: ${activeEl.offsetWidth}px;`;
    }
  });
</script>


{#snippet TabTrigger(tab: typeof TABS[0])}
  <Tabs.Trigger
    value={tab.id}
    bind:ref={tabElements[tab.id]}
    class={cn(
      "relative flex items-center gap-2.5 bg-transparent shadow-none transition-all duration-300",
      "rounded-none border-none px-1 pb-2.5 outline-none focus-visible:ring-0",
      "font-bold group cursor-pointer text-slate-800",
      "data-[state=active]:text-primary data-[state=active]:bg-transparent",
      "data-[state=active]:hover:bg-transparent data-[state=active]:hover:text-primary",
      "data-[state=active]:focus:bg-transparent"
    )}
  >
    <AppIcon name={tab.icon} size={18} class="text-slate-500 group-data-[state=active]:text-primary" />
    <span class="text-[0.879rem] tracking-tight">{tab.label}</span>

    {#if tab.id === 'advances' && payrollStore.pendingAdvancesCount > 0}
      <span class={cn(
        "flex h-5 min-w-5 items-center justify-center rounded-full px-1.5 text-[0.7rem] font-bold transition-colors",
        activeTabId === tab.id
          ? "bg-primary text-white"
          : "bg-slate-100 text-slate-600"
      )}>
        {payrollStore.pendingAdvancesCount}
      </span>
    {/if}
  </Tabs.Trigger>
{/snippet}


<div class="border-b border-slate-100 flex items-center justify-between pl-2 pr-8">
  <div class="flex-1 min-w-0">
    <Tabs.Root value={activeTabId} onValueChange={handleTabChange} class="w-full">
      <Tabs.List class="relative bg-transparent w-full justify-start rounded-none h-auto p-0 gap-8 border-none">
        {#each TABS as tab}
          {@render TabTrigger(tab)}
        {/each}

        <div
          class="absolute bottom-0 h-1 rounded-full bg-primary transition-all duration-300 ease-in-out z-10 pointer-events-none"
          style={indicatorStyle}
        ></div>
      </Tabs.List>
    </Tabs.Root>
  </div>

  {#if activeTabId === 'payslips'}
    <div class="hidden shrink-0 sm:flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-0.5 shadow-fine">
      <span class="h-1.5 w-1.5 rounded-full bg-blue-500"></span>
      <span class="text-[0.75rem] font-medium text-slate-600">
        {payrollStore.totalCount} bulletin{payrollStore.totalCount > 1 ? 's' : ''}
      </span>
    </div>
  {/if}
</div>
