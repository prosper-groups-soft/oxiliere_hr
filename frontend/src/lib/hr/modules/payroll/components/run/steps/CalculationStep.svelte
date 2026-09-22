<script lang="ts">
  import { payrollStore } from "@/hr/modules/payroll/stores/payroll.svelte";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import PayslipList from "@/hr/modules/payroll/components/run/shared/PayslipList.svelte";

  
  // Récapitulatif financier DRC (GET /runs/:id/summary) — source de vérité des agrégats.
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
</script>


{#snippet KPICard(label: string, icon: string, iconClass: string, value: string, sub: string)}
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


<div class="mt-4 space-y-5 font-sans">
  {#if summary}
    <!-- Synthèse financière : masse salariale & coût total -->
    <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
      {@render KPICard('Coût total entreprise (CTC)', 'building-2', 'text-indigo-500', money(summary.total_cost_to_company), 'Salaire brut + charges patronales')}
      {@render KPICard('Salaire brut (masse)', 'banknote', 'text-slate-500', money(summary.total_gross_salary), 'Avant retenues salariales')}
      {@render KPICard('Masse salariale nette', 'circle-check', 'text-emerald-500', money(summary.total_net_salary), `${summary.total_employees} employé${summary.total_employees > 1 ? 's' : ''} payé${summary.total_employees > 1 ? 's' : ''}`)}
      {@render KPICard('IRPP à verser (DGI)', 'landmark', 'text-rose-500', money(summary.total_ipr_to_pay), 'Impôt retenu sur les salaires')}
    </div>

    <!-- Cotisations sociales : part salariale (employé) et part patronale (employeur) -->
    <div>
      <h3 class="text-sm font-bold text-slate-700 flex items-center gap-2 px-1 mb-2">
        <AppIcon name="shield-check" size={18} strokeWidth={1.5} class="text-slate-400" />
        Cotisations sociales
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-3 xl:grid-cols-5 gap-4">
        {@render KPICard('CNSS — part salariale', 'user', 'text-blue-500', money(summary.total_cnss_employee), 'Retenue salarié')}
        {@render KPICard('CNSS — part patronale', 'users', 'text-indigo-500', money(summary.total_cnss_employer), 'Charge employeur')}
        {@render KPICard('INPP — part patronale', 'users', 'text-sky-500', money(summary.total_inpp), 'Charge employeur')}
        {@render KPICard('ONEM — part patronale', 'users', 'text-cyan-500', money(summary.total_onem), 'Charge employeur')}
        {@render KPICard('Total charges patronales', 'calculator', 'text-slate-600', money(summary.total_employer_liabilities), 'CNSS + INPP + ONEM')}
      </div>
    </div>

    <!-- Bulletins de paie du run (accordéon générique, détail chargé au clic) -->
    <PayslipList {payslips} />
  {:else}
    <div class="flex items-center justify-center gap-2 p-10 text-sm text-slate-400 border border-slate-200 rounded-xl bg-white">
      <AppIcon name="circle-alert" size={20} class="text-amber-500" />
      Récapitulatif indisponible : le run {run?.period ?? '—'} ne contient pas encore de résultat de calcul.
    </div>
  {/if}
</div>
