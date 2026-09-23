<script lang="ts">
  import NavTabs from "@/hr/navigation/components/NavTabs.svelte";
  import { hr } from "@/hr/constants/navigation/navigation";
  import { page } from "$app/state";
  import { payrollStore } from "@/hr/modules/payroll/stores/payroll.svelte";

  const BASE_TABS = [
    { id: 'executions', label: 'Exécutions', icon: 'play-circle', path: hr('/payroll') },
    { id: 'payslips', label: 'Bulletins', icon: 'file-text', path: hr('/payroll/payslips') },
    { id: 'advances', label: 'Avances', icon: 'banknote', path: hr('/payroll/advances') },
    { id: 'settings', label: 'Configuration', icon: 'settings', path: hr('/payroll/payroll-settings') },
  ];

  function shortPeriodLabel(period: string | undefined): string {
    if (!period) return '';
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
    if (!payrollStore.hasCurrentRunTab) return null;
    const run = payrollStore.currentRun;
    const label = payrollStore.hasActiveRun && run ? `Paie ${shortPeriodLabel(run.period)}` : 'Nouvelle paie';
    return { id: 'currentRun', label, icon: 'play-circle', path: hr('/payroll/run') };
  });

  const tabs = $derived.by(() => {
    const base = payrollStore.pendingAdvancesCount > 0 ? BASE_TABS.map(t => t.id === 'advances' ? { ...t, count: payrollStore.pendingAdvancesCount } : t) : BASE_TABS;
    const cr = currentRunTab;
    return cr ? [...base, cr] : [...base];
  });

  const sortedTabs = $derived.by(() => [...tabs].sort((a, b) => b.path.length - a.path.length));

  const activeTabId = $derived.by(() => {
    if (page.url.pathname.startsWith(hr('/payroll/run'))) {
      if (tabs.some(t => t.id === 'currentRun')) return 'currentRun';
      return 'executions';
    }
    return sortedTabs.find(t => page.url.pathname.startsWith(t.path))?.id ?? 'executions';
  });
</script>

<div class="border-b border-slate-100 flex items-center justify-between pl-2 pr-8">
  <div class="flex-1 min-w-0">
    <NavTabs {tabs} activeId={activeTabId} variant="underline" />
  </div>
  {#if activeTabId === 'payslips'}
    <div class="hidden shrink-0 sm:flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-0.5 shadow-fine">
      <span class="h-1.5 w-1.5 rounded-full bg-blue-500"></span>
      <span class="text-[0.75rem] font-medium text-slate-600">{payrollStore.totalCount} bulletin{payrollStore.totalCount > 1 ? 's' : ''}</span>
    </div>
  {/if}
</div>
