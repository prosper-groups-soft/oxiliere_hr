<script lang="ts">
  import { payrollStore } from "@/hr/payroll/stores/payroll.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import PayslipList from "@/hr/payroll/components/run/shared/PayslipList.svelte";

  
  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');
  const summary = $derived(payrollStore.currentRunSummary?.summary ?? null);
  const payslips = $derived(payrollStore.payslips);

  // Devise du run : celle des bulletins générés (CDF en pratique).
  const currency = $derived(payslips[0]?.currency ?? 'CDF');

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
        <AppIcon name={icon} size={19} strokeWidth={1.4} class={iconClass} /> {label}
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-2">
      <p class="text-[1.05rem] font-bold text-slate-900 tracking-tight">{value}</p>
      <p class="text-[0.8rem] text-slate-400 mt-1">{sub}</p>
    </CardContent>
  </Card>
{/snippet}


{#if !summary}
  <div class="flex items-center justify-center gap-2 p-10 text-sm text-slate-400 border border-slate-200 rounded-xl bg-white mt-4">
    <AppIcon name="circle-alert" size={20} class="text-amber-500" />
    Aucun résultat à approuver : le run ne contient pas encore de calcul.
  </div>
{:else}
  <div class="mt-4 space-y-5 font-sans">
    <!-- Synthèse à valider pour l'approbation -->
    <div>
      <h3 class="text-sm font-bold text-slate-700 flex items-center gap-2 px-1 mb-2">
        <AppIcon name="clipboard-list" size={18} strokeWidth={1.5} class="text-slate-400" />
        Montants à approuver
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {@render KPICard('Net à verser (employés)', 'banknote', 'text-emerald-500', money(summary.total_net_salary), `${summary.total_employees} employé${summary.total_employees > 1 ? 's' : ''}`)}
        {@render KPICard('IRPP à verser (DGI)', 'landmark', 'text-rose-500', money(summary.total_ipr_to_pay), 'Impôt retenu sur les salaires')}
        {@render KPICard('CNSS — part salariale', 'user', 'text-blue-500', money(summary.total_cnss_employee), 'Retenue salarié')}
        {@render KPICard('Coût total entreprise (CTC)', 'building-2', 'text-indigo-500', money(summary.total_cost_to_company), 'Brut + charges patronales')}
      </div>
    </div>

    <!-- Charges patronales (à déclarer) -->
    <div>
      <h3 class="text-sm font-bold text-slate-700 flex items-center gap-2 px-1 mb-2">
        <AppIcon name="shield-check" size={18} strokeWidth={1.5} class="text-slate-400" />
        Charges patronales à déclarer
      </h3>
      <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-4">
        {@render KPICard('CNSS — part patronale', 'users', 'text-indigo-500', money(summary.total_cnss_employer), 'Charge employeur')}
        {@render KPICard('INPP', 'users', 'text-sky-500', money(summary.total_inpp), 'Charge employeur')}
        {@render KPICard('ONEM', 'users', 'text-cyan-500', money(summary.total_onem), 'Charge employeur')}
        {@render KPICard('Total charges patronales', 'calculator', 'text-slate-600', money(summary.total_employer_liabilities), 'CNSS + INPP + ONEM')}
      </div>
    </div>

    <!-- Statut d'approbation -->
    {#if currentStatus === 'reviewed'}
      <div class="flex items-start gap-3 rounded-xl border border-amber-100 bg-amber-50/50 px-4 py-3">
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white border border-amber-100">
          <AppIcon name="alert-circle" size={17} class="text-amber-600" />
        </div>
        <div class="min-w-0">
          <p class="text-sm font-semibold text-slate-800">Prêt pour approbation</p>
          <p class="text-[0.86rem] text-slate-600 mt-0.5 leading-snug">
            Vérifiez attentivement les montants ci-dessus. Une fois approuvée, la paie est
            verrouillée pour le paiement. Utilisez l'action <strong>Approuver</strong> dans la
            barre d'actions du run.
          </p>
        </div>
      </div>
    {:else if ['approved', 'paid'].includes(currentStatus)}
      <div class="flex items-start gap-3 rounded-xl border border-emerald-100 bg-emerald-50/40 px-4 py-3">
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white border border-emerald-100">
          <AppIcon name="circle-check" size={17} class="text-emerald-600" />
        </div>
        <div class="min-w-0">
          <p class="text-sm font-semibold text-slate-800">Paie approuvée</p>
          <p class="text-[0.86rem] text-slate-600 mt-0.5 leading-snug">
            Les montants ci-dessus ont été approuvés et la paie est prête pour le paiement.
          </p>
        </div>
      </div>
    {/if}

    <!-- Bulletins du run (vérification avant approbation) -->
    <PayslipList {payslips} title="Bulletins à approuver" />
  </div>
{/if}

