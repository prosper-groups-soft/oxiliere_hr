<script lang="ts">
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import { type Payslip } from "@/features/payroll/types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Input } from "@/components/ui/input";
  import PayslipList from "@/features/payroll/components/run/shared/PayslipList.svelte";

  
  const currentStatus = $derived(payrollStore.currentRun?.status ?? 'draft');
  const payslips = $derived(payrollStore.payslips);
  const summary = $derived(payrollStore.currentRunSummary?.summary ?? null);

  // Devise du run : celle des bulletins générés (CDF en pratique).
  const currency = $derived(payslips[0]?.currency ?? 'CDF');

  function money(value: number | null | undefined): string {
    const n = Number(value ?? 0);
    if (currency && currency.toUpperCase() !== 'CDF') {
      return n.toLocaleString('fr-FR', { maximumFractionDigits: 2 }) + ' ' + currency.toUpperCase();
    }
    return n.toLocaleString('fr-FR', { maximumFractionDigits: 0 }) + ' CDF';
  }

  // Totaux autoritaires issus du summary backend (sinon repli sur les bulletins).
  const employeeCount = $derived(summary?.total_employees ?? payslips.length);
  const totalNet = $derived(
    summary?.total_net_salary != null
      ? Number(summary.total_net_salary)
      : payslips.reduce((s, p) => s + Number(p.summary?.netPay ?? 0), 0)
  );
  const irppToPay = $derived(summary?.total_ipr_to_pay != null ? Number(summary.total_ipr_to_pay) : null);

  /** Raison de contrôle d'un bulletin — signale les montants invalides avant validation. */
  function anomalyReason(p: Payslip): string | null {
    const net = Number(p.summary?.netPay);
    const gross = Number(p.summary?.grossSalary);
    if (p.summary == null || !Number.isFinite(net)) return 'Montants absents';
    if (net < 0) return 'Net négatif';
    if (net === 0 && gross === 0) return 'Bulletin vierge (brut et net nuls)';
    if (net === 0 && gross > 0) return 'Net nul (100 % retenus)';
    return null;
  }

  const anomalies = $derived.by(() => {
    const found: Array<{ id: string; name: string; reason: string }> = [];
    for (const p of payslips) {
      const reason = anomalyReason(p);
      if (reason) {
        const e = (p.employee ?? {}) as any;
        found.push({ id: p.id, name: e.fullName || 'Employé', reason });
      }
    }
    return found;
  });
  const anomalyCount = $derived(anomalies.length);

  // Recherche simple par employé (filtre visuel uniquement — l'action de
  // révision reste GLOBALE via la barre d'actions du run).
  let searchTerm = $state('');
  const filteredPayslips = $derived.by(() => {
    const q = searchTerm.trim().toLowerCase();
    if (!q) return payslips;
    return payslips.filter(p => {
      const e = (p.employee ?? {}) as any;
      return (
        (e.fullName ?? '').toLowerCase().includes(q) ||
        (e.orgUnit ?? '').toLowerCase().includes(q) ||
        (e.jobTitle ?? '').toLowerCase().includes(q)
      );
    });
  });
</script>


{#snippet StatCard(title: string, icon: string, iconClass: string, value: string, sub: string)}
  <Card class="border shadow-none border-slate-200">
    <CardHeader class="pb-0">
      <CardTitle class="text-[0.78rem] font-semibold text-slate-500 uppercase flex items-center gap-2">
        <AppIcon name={icon} size={18} strokeWidth={1.4} class={iconClass} /> {title}
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-2">
      <p class="text-[1.1rem] font-bold text-slate-900 tracking-tight">{value}</p>
      <p class="text-[0.8rem] text-slate-400 mt-1">{sub}</p>
    </CardContent>
  </Card>
{/snippet}


<div class="mt-2 space-y-4 font-sans">
  <!-- Synthèse de la révision (totaux du summary backend) -->
  <div class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-3">
    {@render StatCard('Bulletins', 'users', 'text-blue-500', String(employeeCount), 'À vérifier avant validation')}
    {@render StatCard('Net à payer global', 'banknote', 'text-emerald-500', money(totalNet), 'À verser aux employés')}
    {@render StatCard('IRPP à verser (DGI)', 'landmark', 'text-rose-500', irppToPay != null ? money(irppToPay) : '—', 'Impôt retenu sur les salaires')}
    {@render StatCard('À vérifier', anomalyCount === 0 ? 'circle-check' : 'alert-circle', anomalyCount > 0 ? 'text-rose-500' : 'text-emerald-500', anomalyCount === 0 ? 'Aucun' : String(anomalyCount), anomalyCount > 0 ? 'Bulletin(s) à corriger' : 'Tous les bulletins sont cohérents')}
  </div>

  {#if anomalyCount > 0}
    <div class="rounded-xl border border-rose-200 bg-rose-50/50 px-4 py-3">
      <div class="flex items-center gap-2 mb-1.5">
        <AppIcon name="alert-circle" size={16} class="text-rose-500" />
        <p class="text-sm font-semibold text-rose-800">Anomalies détectées ({anomalyCount})</p>
      </div>
      <ul class="space-y-1 text-[0.85rem] text-rose-700">
        {#each anomalies as a (a.id)}
          <li class="flex items-center gap-2">
            <span class="w-1.5 h-1.5 rounded-full bg-rose-400 shrink-0"></span>
            <span class="font-medium">{a.name}</span>
            <span class="text-rose-500">— {a.reason}</span>
          </li>
        {/each}
      </ul>
    </div>
  {/if}

  <!-- Statut & rappel de l'action de révision (globale, barre d'actions) -->
  {#if currentStatus === 'reviewed'}
    <div class="flex items-start gap-3 rounded-xl border border-amber-100 bg-amber-50/40 px-4 py-3">
      <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white border border-amber-100">
        <AppIcon name="eye" size={17} class="text-amber-600" />
      </div>
      <div class="min-w-0">
        <p class="text-sm font-semibold text-slate-800">En cours de révision</p>
        <p class="text-[0.86rem] text-slate-600 mt-0.5 leading-snug">
          Vérifiez chaque bulletin (cliquez dessus pour afficher le détail). Les montants sont
          déjà figés : quand tout est conforme, utilisez <strong class="text-sm">Passer à l'approbation</strong>
          dans la barre d'actions du run.
        </p>
      </div>
    </div>
  {:else if ['calculated'].includes(currentStatus)}
    <div class="flex items-start gap-3 rounded-xl border border-blue-100 bg-blue-50/30 px-4 py-3">
      <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white border border-blue-100">
        <AppIcon name="eye" size={17} class="text-blue-600" />
      </div>
      <div class="min-w-0">
        <p class="text-sm font-semibold text-slate-800">Révision requise</p>
        <p class="text-sm text-slate-600 mt-0.5 leading-snug">
          Utilisez <strong class="text-sm">Passer à la révision</strong> dans la barre d'actions du run pour
          verrouiller la paie et accéder à la révision.
        </p>
      </div>
    </div>
  {:else if ['approved', 'paid'].includes(currentStatus)}
    <div class="flex items-start gap-3 rounded-xl border border-emerald-100 bg-emerald-50/40 px-4 py-3">
      <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white border border-emerald-100">
        <AppIcon name="circle-check" size={17} class="text-emerald-600" />
      </div>
      <div class="min-w-0">
        <p class="text-sm font-semibold text-slate-800">Révision terminée</p>
        <p class="text-[0.86rem] text-slate-600 mt-0.5 leading-snug">
          Les bulletins sont verrouillés. Toute modification nécessite de réinitialiser le cycle.
        </p>
      </div>
    </div>
  {/if}

  <!-- Recherche (filtre visuel de la liste) -->
  {#if payslips.length > 1}
    <div class="relative">
      <AppIcon name="search" size={15} class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
      <Input
        type="text"
        value={searchTerm}
        oninput={(e) => (searchTerm = (e.currentTarget as HTMLInputElement).value)}
        placeholder="Rechercher un employé…"
        class="h-9 pl-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
      />
    </div>
  {/if}

  <PayslipList
    payslips={filteredPayslips}
    title="Bulletins à réviser"
    hint="Cliquez sur un bulletin pour vérifier son détail."
    emptyText={searchTerm ? 'Aucun bulletin ne correspond à votre recherche.' : 'Aucun bulletin à réviser.'}
  />
</div>
