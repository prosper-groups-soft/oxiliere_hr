<script lang="ts">
  import { payrollStore } from "@/hr/payroll/stores/payroll.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Button } from "@/components/ui/button";
  import { notification } from "@/stores/notification.svelte";

  
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

  function fmtDay(value?: string | null): string {
    if (!value) return '—';
    const raw = String(value).slice(0, 10);
    const d = new Date(raw + 'T00:00:00');
    if (Number.isNaN(d.getTime())) return raw;
    return d.toLocaleDateString('fr-FR', { day: '2-digit', month: '2-digit', year: 'numeric' });
  }

  const totalNet = $derived(
    summary?.total_net_salary != null
      ? Number(summary.total_net_salary)
      : payslips.reduce((s, p) => s + Number(p.summary?.netPay ?? 0), 0)
  );
  const employeeCount = $derived(summary?.total_employees ?? payslips.length);

  // Méthode réellement utilisée par le moteur (portée par les bulletins).
  const methodKey = $derived(String((payslips[0] as any)?.payment_method || '').toUpperCase());
  const METHOD_LABELS: Record<string, string> = {
    CASH: 'Espèces (Cash)',
    BANK_TRANSFER: 'Virement bancaire',
    MOBILE_MONEY: 'Mobile Money'
  };
  const availableMethods = [
    { value: 'CASH', label: 'Espèces (Cash)', desc: 'Paiement en espèces' },
    { value: 'BANK_TRANSFER', label: 'Virement bancaire', desc: 'Virement vers les comptes bancaires' },
    { value: 'MOBILE_MONEY', label: 'Mobile Money', desc: 'Orange Money, M-Pesa ou Airtel Money' }
  ];
  const methodLabel = $derived(METHOD_LABELS[methodKey] || null);

  const paidDate = $derived.by(() => {
    const at = payrollStore.currentRun?.paidAt;
    if (!at) return '';
    const d = new Date(at);
    return Number.isNaN(d.getTime()) ? '' : d.toLocaleDateString('fr-FR', { day: '2-digit', month: 'long', year: 'numeric' });
  });

  let isPaying = $state(false);
  async function confirmPayment() {
    if (isPaying) return;
    isPaying = true;
    try {
      const ok = await payrollStore.processPayment();
      if (ok) notification.toast.success('Paiement effectué avec succès');
      else notification.toast.error('Échec du paiement');
    } catch (e: any) {
      notification.toast.error(e?.message ?? 'Échec du paiement');
    } finally {
      isPaying = false;
    }
  }
</script>


{#snippet Row(label: string, value: string, strong = false, tone: 'default' | 'emerald' | 'muted' = 'default')}
  <div class="flex items-center justify-between gap-3 py-1">
    <span class="text-sm text-slate-500">{label}</span>
    <span
      class={[
        'whitespace-nowrap text-sm',
        strong ? 'font-bold text-slate-900' : 'font-semibold text-slate-800',
        tone === 'emerald' && 'text-emerald-600',
        tone === 'muted' && 'text-slate-400'
      ].join(' ')}
    >{value}</span>
  </div>
{/snippet}


<div class="mt-4 space-y-5 font-sans">
  {#if currentStatus === 'approved'}
    <!-- Pré-paiement -->
    <div class="space-y-4">
      <div class="flex items-start gap-3 rounded-xl border border-purple-100 bg-purple-50/40 px-4 py-3">
        <div class="flex h-9 w-9 shrink-0 items-center justify-center rounded-full bg-white border border-purple-100">
          <AppIcon name="banknote" size={17} class="text-purple-600" />
        </div>
        <div class="min-w-0">
          <p class="text-sm font-semibold text-slate-800">Prêt pour paiement</p>
          <p class="text-sm text-slate-600 mt-0.5 leading-snug">
            La paie est approuvée. Confirmez pour finaliser : le run passera à « Payé » puis à
            l'écran de clôture.
          </p>
        </div>
      </div>

      <Card class="border shadow-none border-slate-200">
        <CardHeader class="pb-0">
          <CardTitle class="text-sm font-semibold text-slate-500 uppercase flex items-center gap-2">
            <AppIcon name="circle-check" size={18} strokeWidth={1.4} class="text-purple-500" />
            Montant à payer
          </CardTitle>
        </CardHeader>
        <CardContent class="pt-2 space-y-1">
          {@render Row('Période', `${fmtDay(payrollStore.currentRun?.periodStart)} → ${fmtDay(payrollStore.currentRun?.periodEnd)}`)}
          {@render Row('Employés', `${employeeCount} payé${employeeCount > 1 ? 's' : ''}`)}
          {#if methodLabel}
            {@render Row('Méthode de paiement', methodLabel, false, 'muted')}
          {/if}
          {@render Row('Net total à verser', money(totalNet), true, 'emerald')}
        </CardContent>
      </Card>

      <div class="flex justify-end">
        <Button onclick={confirmPayment} disabled={isPaying} class="bg-purple-600 hover:bg-purple-700 text-white h-9 px-5 text-[0.88rem]">
          <AppIcon name="banknote" size={17} />
          {isPaying ? 'Paiement en cours…' : 'Confirmer le paiement'}
        </Button>
      </div>
    </div>

  {:else if ['paid', 'closed'].includes(currentStatus) && summary}
    <!-- Post-paiement : clôture -->
    <div class="flex items-start gap-3 rounded-xl border border-emerald-100 bg-emerald-50/40 px-4 py-3">
      <div class="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-white border border-emerald-100">
        <AppIcon name="circle-check" size={20} class="text-emerald-600" />
      </div>
      <div class="min-w-0">
        <p class="text-sm font-bold text-slate-800">Paiement effectué</p>
        <p class="text-sm text-slate-600 mt-0.5 leading-snug">
          {#if paidDate}Effectué le {paidDate}.{/if}
          Clôturez cette exécution pour revenir à la liste des exécutions.
        </p>
      </div>
    </div>

    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <Card class="border shadow-none border-slate-200">
        <CardHeader class="pb-0">
          <CardTitle class="text-sm font-semibold text-slate-500 uppercase flex items-center gap-2">
            <AppIcon name="banknote" size={18} strokeWidth={1.4} class="text-emerald-500" />
            Paiement des salaires
          </CardTitle>
        </CardHeader>
        <CardContent class="pt-2 space-y-1">
          {@render Row('Début de période', fmtDay(payrollStore.currentRun?.periodStart), false, 'muted')}
          {@render Row('Fin de période', fmtDay(payrollStore.currentRun?.periodEnd), false, 'muted')}
          {@render Row('Employés payés', `${employeeCount}`)}
          {@render Row('Net total versé', money(totalNet), true, 'emerald')}
          {#if methodLabel}
            {@render Row('Méthode', methodLabel, false, 'muted')}
          {/if}
          {#if paidDate}
            {@render Row('Paiement effectué le', paidDate, false, 'muted')}
          {/if}
        </CardContent>
      </Card>

      <Card class="border shadow-none border-slate-200">
        <CardHeader class="pb-0">
          <CardTitle class="text-sm font-semibold text-slate-500 uppercase flex items-center gap-2">
            <AppIcon name="landmark" size={18} strokeWidth={1.4} class="text-rose-500" />
            À reverser aux organismes
          </CardTitle>
        </CardHeader>
        <CardContent class="pt-2 space-y-1">
          {@render Row('IRPP (DGI)', money(summary.total_ipr_to_pay))}
          {@render Row('CNSS — part salariale', money(summary.total_cnss_employee))}
          {@render Row('CNSS — part patronale', money(summary.total_cnss_employer))}
          {@render Row('INPP', money(summary.total_inpp))}
          {@render Row('ONEM', money(summary.total_onem))}
          <div class="pt-1">
            {@render Row('Coût total entreprise (CTC)', money(summary.total_cost_to_company), true)}
          </div>
        </CardContent>
      </Card>
    </div>

    <!-- Méthode de paiement utilisée (lecture seule) -->
    <Card class="border shadow-none border-slate-200">
      <CardHeader class="pb-0">
        <CardTitle class="text-sm font-semibold text-slate-500 uppercase flex items-center gap-2">
          <AppIcon name="credit-card" size={18} strokeWidth={1.4} class="text-slate-500" />
          Méthode de paiement
        </CardTitle>
      </CardHeader>
      <CardContent class="pt-2 grid grid-cols-1 sm:grid-cols-3 gap-2">
        {#each availableMethods as m (m.value)}
          {@const active = m.value === methodKey}
          <div
            class={[
              'flex items-start gap-2 rounded-lg border px-3 py-2.5',
              active ? 'border-emerald-200 bg-emerald-50/50' : 'border-slate-100 bg-white'
            ].join(' ')}
          >
            <span class={[
              'mt-0.5 flex h-4 w-4 shrink-0 items-center justify-center rounded-full border',
              active ? 'border-emerald-500 bg-emerald-500 text-white' : 'border-slate-300'
            ].join(' ')}>
              {#if active}
                <AppIcon name="check" size={11} />
              {/if}
            </span>
            <span class="min-w-0">
              <span class={['block text-sm font-semibold', active ? 'text-emerald-700' : 'text-slate-700'].join(' ')}>{m.label}</span>
              <span class="block text-sm text-slate-400 leading-snug">{m.desc}</span>
            </span>
          </div>
        {/each}
        {#if !methodLabel}
          <p class="sm:col-span-3 text-sm text-slate-400">
            Aucune méthode enregistrée sur les bulletins de ce run.
          </p>
        {/if}
      </CardContent>
    </Card>

  {:else}
    <div class="flex items-center justify-center gap-2 p-10 text-sm text-slate-400 border border-slate-200 rounded-xl bg-white">
      <AppIcon name="circle-alert" size={20} class="text-amber-500" />
      Paiement indisponible : le run n'est pas encore prêt à être payé.
    </div>
  {/if}
</div>

