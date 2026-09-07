<script lang="ts">
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";
  import { cn } from "@/utilities/common/css";

  // Summary financier DRC structuré (GET /runs/:id/summary) — source de vérité.
  const summary = $derived(payrollStore.currentRunSummary?.summary ?? null);
  const payslips = $derived(payrollStore.payslips);
  const run = $derived(payrollStore.currentRun);

  // Devise du run : celle des bulletins générés (CDF en pratique).
  const currency = $derived(payslips[0]?.currency ?? 'CDF');

  /** Formate un montant dans la devise des bulletins du run. */
  function money(value: number | null | undefined): string {
    const n = Number(value ?? 0);
    if (currency && currency.toUpperCase() !== 'CDF') {
      return n.toLocaleString('fr-FR', { maximumFractionDigits: 2 }) + ' ' + currency.toUpperCase();
    }
    return n.toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' CDF';
  }

  /** Ventilation du NET par unité organisationnelle (depuis les bulletins). */
  const orgUnitStats = $derived.by(() => {
    const stats: Record<string, { net: number; count: number }> = {};
    payslips.forEach((p) => {
      const unit = p.employee?.orgUnit || 'Général';
      if (!stats[unit]) stats[unit] = { net: 0, count: 0 };
      stats[unit].net += p.summary?.netPay || 0;
      stats[unit].count += 1;
    });
    return Object.entries(stats).sort((a, b) => b[1].net - a[1].net);
  });

  /** Vrai si les bulletins chargés portent une unité organisationnelle exploitable. */
  const hasOrgUnitInfo = $derived(payslips.some((p) => !!p.employee?.orgUnit));

  const PALETTE = [
    { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
    { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
    { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
    { bg: 'bg-rose-50', text: 'text-rose-700', dot: 'bg-rose-500' },
    { bg: 'bg-indigo-50', text: 'text-indigo-700', dot: 'bg-indigo-500' },
    { bg: 'bg-teal-50', text: 'text-teal-700', dot: 'bg-teal-500' }
  ];
  const colorFor = (name: string) => {
    let h = 0;
    for (const c of name) h = (h * 31 + c.charCodeAt(0)) >>> 0;
    return PALETTE[h % PALETTE.length];
  };
</script>


{#snippet KpiCard(label: string, icon: string, iconClass: string, value: string, sub: string)}
  <Card class="border shadow-none border-slate-200">
    <CardHeader class="pb-0">
      <CardTitle class="text-[0.78rem] font-semibold text-slate-500 uppercase flex items-center gap-2">
        <AppIcon name={icon} size={20} strokeWidth={1.3} class={iconClass} /> {label}
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-2">
      <p class="text-[1.15rem] font-bold text-slate-900 tracking-tight">{value}</p>
      <p class="text-[0.8rem] text-slate-400 mt-1">{sub}</p>
    </CardContent>
  </Card>
{/snippet}


{#snippet OrgUnitBadge(orgUnit: string, net: number, count: number)}
  {@const colors = colorFor(orgUnit)}
  <div class="flex items-center justify-between p-2 rounded-lg border border-slate-200 bg-white shadow-fine">
    <div class="flex items-center gap-2 min-w-0">
      <span class={cn('h-1.5 w-1.5 rounded-full shrink-0', colors.dot)}></span>
      <span class="text-sm font-medium text-slate-700 truncate">{orgUnit}</span>
    </div>
    <div class="flex items-center gap-2 shrink-0">
      <span class="text-[0.8rem] font-semibold text-slate-600">{money(net)}</span>
      <span class={cn('text-[0.7rem] font-bold px-2 py-0.5 rounded-full', colors.text, colors.bg)}>
        {count} agent{count > 1 ? 's' : ''}
      </span>
    </div>
  </div>
{/snippet}


<div class="mt-4 space-y-4 font-sans">
  {#if summary}
    <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
      {@render KpiCard('Masse salariale nette', 'banknote', 'text-emerald-500', money(summary.total_net_salary), `${summary.total_employees} employé${summary.total_employees > 1 ? 's' : ''} payé${summary.total_employees > 1 ? 's' : ''}`)}
      {@render KpiCard('IRPP à verser (DGI)', 'landmark', 'text-rose-500', money(summary.total_ipr_to_pay), 'Impôt sur le revenu retenu sur les salaires')}
      {@render KpiCard('Cotisation CNSS — part salariale', 'shield-check', 'text-blue-500', money(summary.total_cnss_employee), 'Retenue sur les salaires')}
    </div>

    <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
      <!-- Ventilation par unité organisationnelle -->
      <div class="md:col-span-3 space-y-3">
        <h3 class="text-sm font-bold text-slate-700 flex items-center gap-2 px-1">
          <AppIcon name="users" size={18} strokeWidth={1.5} class="text-slate-400" />
          Ventilation du net par unité organisationnelle
        </h3>
        {#if hasOrgUnitInfo}
          <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
            {#each orgUnitStats as [orgUnit, data]}
              {@render OrgUnitBadge(orgUnit, data.net, data.count)}
            {/each}
          </div>
        {:else}
          <p class="text-sm text-slate-400 px-1 flex flex-col items-center justify-center gap-2">
            <AppIcon name="building-2" size={20} class="text-amber-500" />
            {payslips.length > 0 ? 'Unité organisationnelle indisponible sur ces bulletins.' : 'Aucun bulletin chargé.'}
          </p>
        {/if}
      </div>

      <!-- Charges patronales & coût total (données réelles du run) -->
      <div class="md:col-span-2 border border-slate-200 bg-white rounded-xl shadow-none overflow-hidden">
        <div class="p-3 border-b border-slate-100 bg-slate-50/50 flex items-center gap-2">
          <AppIcon name="building-2" size={16} strokeWidth={1.5} class="text-slate-400" />
          <h3 class="text-sm font-bold text-slate-700">Charges patronales & coût</h3>
        </div>
        <div class="p-4 space-y-2.5">
          <div class="flex items-center justify-between">
            <span class="text-slate-500 text-sm">CNSS — part employeur</span>
            <span class="font-semibold text-slate-800 text-sm">{money(summary.total_cnss_employer)}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-500 text-sm">INPP</span>
            <span class="font-semibold text-slate-800 text-sm">{money(summary.total_inpp)}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-500 text-sm">ONEM</span>
            <span class="font-semibold text-slate-800 text-sm">{money(summary.total_onem)}</span>
          </div>
          <Separator class="opacity-60" />
          <div class="flex items-center justify-between">
            <span class="text-slate-500 font-medium text-sm">Total charges patronales</span>
            <span class="font-bold text-slate-900 text-sm">{money(summary.total_employer_liabilities)}</span>
          </div>
          <Separator class="opacity-60" />
          <div class="flex items-center justify-between">
            <span class="text-slate-500 text-sm">Salaire brut (masse)</span>
            <span class="font-semibold text-slate-800 text-sm">{money(summary.total_gross_salary)}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-slate-500 font-medium text-sm">Coût total entreprise (CTC)</span>
            <span class="font-bold text-slate-900 text-sm">{money(summary.total_cost_to_company)}</span>
          </div>
          <p class="text-sm text-slate-400 pt-1">
            Coût total = salaires bruts + charges patronales (CNSS, INPP, ONEM).
          </p>
        </div>
      </div>
    </div>
  {:else}
    <div class="flex items-center justify-center gap-2 p-10 text-sm text-slate-400 border border-slate-200 rounded-xl bg-white">
      <AppIcon name="circle-alert" size={20} class="text-amber-500" />
      Récapitulatif indisponible : le run {run?.period ?? '—'} ne contient pas encore de résultat de calcul.
    </div>
  {/if}
</div>
