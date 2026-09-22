<script lang="ts">
  import { cn } from "@/hr/utilities/common/css";
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { page } from '$app/state';
  import { hr } from '@/hr/constants/navigation/navigation';
  import { goto } from '$app/navigation';
  import { payrollStore } from "@/hr/modules/payroll/stores/payroll.svelte";
  import * as Tabs from '@/components/ui/tabs';


  const BASE_TABS = [
    { id: 'executions', label: 'Exécutions', icon: 'play-circle', path: hr('/payroll') },
    { id: 'payslips', label: 'Bulletins', icon: 'file-text', path: hr('/payroll/payslips') },
    { id: 'advances', label: 'Avances', icon: 'banknote', path: hr('/payroll/advances') },
    { id: 'settings', label: 'Configuration', icon: 'settings', path: hr('/payroll/payroll-settings') },
  ];

  /** Abréviation 3 lettres du mois en français pour un label compact d'onglet. */
  function shortPeriodLabel(period: string | undefined): string {
    if (!period) return '';
    // period est souvent "2026-08-28 - 2026-10-11" ou "Août 2026 - Octobre 2026"
    const parts = period.split(' - ');
    const fmt = (s: string) => {
      const d = new Date(s.trim());
      if (isNaN(d.getTime())) return s.trim().slice(0, 3);
      return d.toLocaleDateString('fr-FR', { month: 'short' }).replace('.', '');
    };
    const start = fmt(parts[0]);
    if (parts.length < 2) return start.charAt(0).toUpperCase() + start.slice(1);
    const end = fmt(parts[1]);
    if (start === end) return start.charAt(0).toUpperCase() + start.slice(1);
    return `${start.charAt(0).toUpperCase() + start.slice(1)}–${end.charAt(0).toUpperCase() + end.slice(1)}`;
  }

  const currentRunTab = $derived.by(() => {
    // Onglet visible si run backend actif OU démarrage client (KickoffStep).
    if (!payrollStore.hasCurrentRunTab) return null;

    const run = payrollStore.currentRun;
    const label = payrollStore.hasActiveRun && run
      ? `Paie ${shortPeriodLabel(run.period)}`
      : 'Nouvelle paie';
    return {
      id: 'currentRun',
      label,
      icon: 'play-circle',
      path: hr('/payroll/run'),
    };
  });

  const TABS = $derived.by(() => {
    const tab = currentRunTab;
    return tab ? [...BASE_TABS, tab] : [...BASE_TABS];
  });

  // Trier par longueur de chemin (le plus long d'abord) pour 
  // éviter que '/hr/payroll' ne matche tous les '/payroll/*'
  const SORTED_TABS = $derived.by(() => [...TABS].sort((a, b) => b.path.length - a.path.length));

  const activeTabId = $derived.by(() => {
    // Sur la page d'exécution : forcer l'onglet courant uniquement s'il existe
    // (un run finalisé consulté depuis l'historique ne doit pas laisser
    //  un onglet actif fantôme).
    if (page.url.pathname.startsWith(hr('/payroll/run'))) {
      if (TABS.some(t => t.id === 'currentRun')) return 'currentRun';
      return 'executions';
    }
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
    settings: null,
    currentRun: null,
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

