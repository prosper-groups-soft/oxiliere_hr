<script lang="ts">
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";

  // RDC Configuration
  const EXCHANGE_RATE = 2850; 
  const payslips = $derived(payrollStore.payslips);

  const orgUnitStats = $derived.by(() => {
    const stats: Record<string, { total: number; count: number }> = {};
    payslips.forEach((p: typeof payslips[number]) => {
      const orgUnit = p.orgUnit || 'Général';
      if (!stats[orgUnit]) stats[orgUnit] = { total: 0, count: 0 };
      stats[orgUnit].total += p.netPay || 0;
      stats[orgUnit].count += 1;
    });
    return Object.entries(stats);
  });

  const orgUnitColors: Record<string, { bg: string; text: string; dot: string }> = {
    'IT': { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
    'RH': { bg: 'bg-rose-50', text: 'text-rose-700', dot: 'bg-rose-500' },
    'Finance': { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
    'Admin': { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' }
  };

  const getOrgUnitColor = (orgUnit: string) => 
    orgUnitColors[orgUnit] || { bg: 'bg-slate-50', text: 'text-slate-600', dot: 'bg-slate-400' };
</script>


{#snippet OrgUnitBadge(orgUnit: string, count: number)}
  {@const colors = getOrgUnitColor(orgUnit)}
  <div class="flex items-center justify-between p-2 rounded-lg border border-slate-200 bg-white shadow-fine">
    <div class="flex items-center gap-2">
      <span class="h-1.5 w-1.5 rounded-full {colors.dot}"></span>
      <span class="text-sm font-medium text-slate-700">{orgUnit}</span>
    </div>
    <span class="text-[0.7rem] font-bold {colors.text} {colors.bg} px-2 py-0.5 rounded-full">
      {count} agents
    </span>
  </div>
{/snippet}


<div class="mt-4 space-y-4 font-sans">
  
  <div class="grid grid-cols-1 md:grid-cols-3 gap-4">
    <!-- Payroll Mass Card -->
    <Card class="border shadow-none border-slate-200 gap-1">
      <CardHeader class="pb-0">
        <CardTitle class="text-sm font-medium text-slate-500 flex items-center gap-2">
          <AppIcon name="banknote" size={20} strokeWidth={1.2} class="text-emerald-500" /> Masse Salariale Net
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-[1.1rem] font-medium text-slate-900">
          {payrollStore.totalNetPay.toLocaleString('en-US', { style: 'currency', currency: 'USD' })}
        </p>
        <p class="text-[0.8rem] text-slate-400 mt-1">1 000 000 CDF</p>
      </CardContent>
    </Card>

    <!-- IPR / DGI Card -->
    <Card class="border shadow-none border-slate-200 gap-1">
      <CardHeader class="pb-0">
        <CardTitle class="text-[0.75rem] font-semibold text-slate-500 uppercase flex items-center gap-2">
          <AppIcon name="landmark" size={20} strokeWidth={1.2} class="text-rose-500" /> IPR à déclarer (DGI)
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-[1.1rem] font-medium text-slate-900">
          {((payrollStore.totalTax || 0) * EXCHANGE_RATE).toLocaleString('fr-CD')} <span class="text-xs uppercase">cdf</span>
        </p>
        <p class="text-[0.8rem] text-rose-500 mt-1 font-medium flex items-center gap-1">
          <AppIcon name="alert-circle" size={17} /> Barème progressif appliqué
        </p>
      </CardContent>
    </Card>

    <!-- CNSS Card -->
    <Card class="border shadow-none border-slate-200 gap-1">
      <CardHeader class="pb-0">
        <CardTitle class="text-[0.75rem] font-semibold text-slate-500 uppercase flex items-center gap-2">
          <AppIcon name="shield-check" size={20} strokeWidth={1.2} class="text-blue-500" /> Cotisations CNSS
        </CardTitle>
      </CardHeader>
      <CardContent>
        <p class="text-[1.1rem] font-medium text-slate-900">
          {((payrollStore.totalSocialSecurity || 0) * EXCHANGE_RATE).toLocaleString('fr-CD')} <span class="text-xs uppercase">cdf</span>
        </p>
        <p class="text-[0.8rem] text-slate-400 mt-1">Part Travailleur (5%)</p>
      </CardContent>
    </Card>
  </div>

  <div class="grid grid-cols-1 md:grid-cols-5 gap-4">
    <!-- Organizational unit Breakdown -->
    <div class="md:col-span-3 space-y-3">
      <div class="flex items-center justify-between px-1">
        <h3 class="text-sm font-bold text-slate-700 flex items-center gap-2">
          <AppIcon name="users" size={18} strokeWidth={1.5} class="text-slate-400" />
          Ventilation par unité organisationnelle
        </h3>
      </div>
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
        {#each orgUnitStats as [orgUnit, data]}
          {@render OrgUnitBadge(orgUnit, data.count)}
        {/each}
      </div>
    </div>

    <!-- Business Rules -->
    <div class="md:col-span-2 border border-slate-200 bg-white rounded-xl shadow-none overflow-hidden">
      <div class="p-3 border-b border-slate-100 bg-slate-50/50">
        <h3 class="text-sm font-bold text-slate-700">Règles métier (RDC)</h3>
      </div>
      <div class="p-4 space-y-3">
        <div class="flex flex-col gap-3">
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 text-slate-500 text-sm">
               <AppIcon name="check-circle-2" size={17} class="text-emerald-500" />
               Logement (max 30% Base)
            </div>
            <span class="font-semibold text-slate-700 text-sm">Exonéré</span>
          </div>
          <Separator class="opacity-50" />
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 text-slate-500 text-sm">
               <AppIcon name="check-circle-2" size={17} class="text-emerald-500" />
               Transport (Légal)
            </div>
            <span class="font-semibold text-slate-700 text-sm">Non Imp.</span>
          </div>
          <Separator class="opacity-50" />
          <div class="flex items-center justify-between">
            <div class="flex items-center gap-2 text-slate-500 text-sm">
               <AppIcon name="info" size={17} class="text-blue-500" />
               ONEM & INPP
            </div>
            <span class="font-semibold text-slate-700 text-sm">Charge Patron.</span>
          </div>
        </div>
      </div>
    </div>
  </div>

  <div class="flex items-center gap-2 p-3 bg-slate-100/50 border border-slate-200 rounded-lg">
    <AppIcon name="lock" size={17} class="text-slate-400" />
    <p class="text-[0.8rem] text-slate-500 font-medium">
      Calcul conforme au Code du Travail Congolais
    </p>
  </div>
</div>

