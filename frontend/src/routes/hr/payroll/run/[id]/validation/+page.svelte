<script lang="ts">
  import { page } from '$app/stores';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import EmptyState from '@/components/shared/containers/empty/EmptyState.svelte';
  import { payrollStore } from '@/hr/payroll/stores/payroll.svelte';
  import PayrollStats from '@/hr/payroll/components/run/PayrollStats.svelte';
  import { notification } from '$lib/stores/notification.svelte';
  import { ui } from '$lib/stores/ui.svelte';

  const runId = $derived($page.params.id);

  let viewState: 'loading' | 'success' | 'error' | 'offline' = $state('loading');
  let isApproving = $state(false);
  let selectedAnomaly = $state<string | null>(null);

  $effect(() => {
    Promise.all([
      payrollStore.syncFromApi('runDetail', { runId }),
      payrollStore.syncFromApi('payslips', { runId }),
    ]).then(() => {
      viewState = payrollStore.currentRun ? 'success' : 'error';
    }).catch(() => {
      viewState = 'error';
    });
  });

  const summary = {
    totalGross: 15200000,
    totalNet: 13517640,
    totalCnss: 760000,
    totalIrpp: 922360,
    totalEmployer: 2280000,
    totalCost: 17480000,
    employeeCount: 12,
    anomalyCount: 0,
    anomalyItems: [] as { id: string; employee: string; type: 'warning' | 'error'; message: string; detail: string }[],
  };

  function handleApprove() {
    isApproving = true;
    setTimeout(() => {
      isApproving = false;
      notification.toast.success('Paie approuvée avec succès');
    }, 800);
  }

  function handleReject() {
    notification.confirm({
      title: 'Rejeter la paie ?',
      message: 'Tous les bulletins retourneront à l\'étape de calcul.',
      type: 'warning',
      yesText: 'Rejeter',
      noText: 'Annuler',
      onYes: () => notification.toast.info('Paie rejetée'),
    });
  }

  $effect(() => {
    ui.addActions('payroll-validation', ValidationActions);
    return () => ui.removeActions('payroll-validation');
  });
</script>

{#snippet ValidationActions()}
  <div class="flex items-center gap-2">
    <Button variant="ghost" size="sm" class="h-8 px-3 text-[0.84rem] rounded-lg">
      <AppIcon name="download" size={15} class="mr-1.5" />
      Exporter
    </Button>
    <Button variant="outline" size="sm" onclick={handleReject}
      class="h-8 px-3 text-[0.84rem] text-rose-600 border-rose-200 hover:bg-rose-50 rounded-lg">
      <AppIcon name="x-circle" size={15} class="mr-1.5" />
      Rejeter
    </Button>
    <Button variant="default" size="sm" onclick={handleApprove} disabled={isApproving}
      class="h-8 px-4 text-[0.84rem] shadow-fine rounded-lg">
      {#if isApproving}
        <AppIcon name="loader" size={15} class="animate-spin mr-1.5" />
        Approbation...
      {:else}
        <AppIcon name="check-circle" size={15} class="mr-1.5" />
        Approuver
      {/if}
    </Button>
  </div>
{/snippet}

<svelte:head>
  <title>Oxiliere HR - Validation Run {runId}</title>
</svelte:head>

<div class="flex h-full flex-col overflow-hidden min-h-0">
  {#if viewState === 'loading'}
    <EmptyState variant="loading" class="h-full" />
  {:else if viewState === 'error' || viewState === 'offline'}
    <EmptyState
      variant={viewState === 'offline' ? 'offline' : 'error'}
      class="h-full"
      onRetry={() => { viewState = 'loading'; Promise.all([payrollStore.syncFromApi('runDetail', { runId }), payrollStore.syncFromApi('payslips', { runId })]).finally(() => viewState = 'success'); }}
    />
  {:else}
    <main class="flex-1 overflow-y-auto min-h-0">
      <div class="max-w-5xl mx-auto px-6 py-6">

      <!-- Anomalies Alert -->
      {#if summary.anomalyCount > 0}
        <div class="mb-5 flex items-start gap-4 p-4 bg-rose-50 border border-rose-200 rounded-2xl">
          <div class="w-9 h-9 rounded-lg bg-rose-100 flex items-center justify-center shrink-0">
            <AppIcon name="alert-triangle" size={18} class="text-rose-600" />
          </div>
          <div class="flex-1 min-w-0">
            <h3 class="text-[0.86rem] font-bold text-rose-800">{summary.anomalyCount} anomalie{summary.anomalyCount > 1 ? 's' : ''} détectée{summary.anomalyCount > 1 ? 's' : ''}</h3>
            <p class="text-[0.8rem] text-rose-600 mt-0.5">Corrigez les anomalies avant de pouvoir approuver la paie.</p>
          </div>
        </div>
      {/if}

      <!-- Stats -->
      <PayrollStats />

      <!-- Validation Summary -->
      <div class="grid grid-cols-3 gap-4 mt-6 mb-6">
        <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm col-span-2">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
              <AppIcon name="calculator" size={18} class="text-blue-600" />
            </div>
            <div>
              <h2 class="text-[0.92rem] font-bold text-slate-800">Récapitulatif financier</h2>
              <p class="text-[0.72rem] text-slate-400">Résumé des montants calculés pour cette période.</p>
            </div>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between py-1.5 text-[0.84rem]">
              <span class="text-slate-400">Salaire brut total</span>
              <span class="font-bold text-slate-700 tabular-nums">{summary.totalGross.toLocaleString('fr-FR')} CDF</span>
            </div>
            <div class="flex justify-between py-1.5 text-[0.84rem]">
              <span class="text-slate-400">CNSS salariale</span>
              <span class="font-semibold text-slate-600 tabular-nums">−{summary.totalCnss.toLocaleString('fr-FR')} CDF</span>
            </div>
            <div class="flex justify-between py-1.5 text-[0.84rem]">
              <span class="text-slate-400">IRPP</span>
              <span class="font-semibold text-slate-600 tabular-nums">−{summary.totalIrpp.toLocaleString('fr-FR')} CDF</span>
            </div>
            <div class="border-t border-slate-100 pt-2 flex justify-between">
              <span class="text-[0.86rem] font-bold text-slate-700">Net à payer</span>
              <span class="text-[0.95rem] font-extrabold text-emerald-600 tabular-nums">{summary.totalNet.toLocaleString('fr-FR')} CDF</span>
            </div>
          </div>
        </section>

        <!-- Employer Costs -->
        <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center">
              <AppIcon name="building-2" size={18} class="text-amber-600" />
            </div>
            <h2 class="text-[0.92rem] font-bold text-slate-800">Charges patronales</h2>
          </div>
          <div class="space-y-2">
            <div class="flex justify-between py-1 text-[0.84rem]">
              <span class="text-slate-400">CNSS patronale</span>
              <span class="font-semibold text-slate-600 tabular-nums">1 520 000 CDF</span>
            </div>
            <div class="flex justify-between py-1 text-[0.84rem]">
              <span class="text-slate-400">INPP</span>
              <span class="font-semibold text-slate-600 tabular-nums">456 000 CDF</span>
            </div>
            <div class="flex justify-between py-1 text-[0.84rem]">
              <span class="text-slate-400">ONEM</span>
              <span class="font-semibold text-slate-600 tabular-nums">304 000 CDF</span>
            </div>
            <div class="border-t border-slate-100 pt-2 flex justify-between">
              <span class="text-[0.86rem] font-bold text-slate-700">Coût total employeur</span>
              <span class="text-[0.95rem] font-extrabold text-amber-600 tabular-nums">{summary.totalCost.toLocaleString('fr-FR')} CDF</span>
            </div>
          </div>
        </section>
      </div>

      <!-- Anomaly List -->
      <section class="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <div class="px-5 py-3 border-b border-slate-50 bg-slate-50/50 flex items-center justify-between">
          <div class="flex items-center gap-2">
            <AppIcon name="search" size={16} class="text-slate-400" />
            <span class="text-[0.82rem] font-bold text-slate-700">Liste des anomalies</span>
          </div>
          <span class="text-[0.72rem] bg-emerald-100 text-emerald-700 px-2.5 py-0.5 rounded-full font-bold">
            {summary.anomalyCount === 0 ? 'Aucune anomalie' : `${summary.anomalyCount} anomalie(s)`}
          </span>
        </div>

        {#if summary.anomalyItems.length > 0}
          <div class="divide-y divide-slate-50">
            {#each summary.anomalyItems as anomaly}
              <button onclick={() => selectedAnomaly = selectedAnomaly === anomaly.id ? null : anomaly.id}
                class="w-full px-5 py-3.5 text-left hover:bg-slate-50/50 transition-colors cursor-pointer flex items-center gap-3">
                <div class="w-9 h-9 rounded-lg {anomaly.type === 'error' ? 'bg-rose-100' : 'bg-amber-100'} flex items-center justify-center shrink-0">
                  <AppIcon name={anomaly.type === 'error' ? 'x-circle' : 'alert-triangle'} size={18}
                    class={anomaly.type === 'error' ? 'text-rose-600' : 'text-amber-600'} />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-[0.84rem] font-semibold text-slate-700">{anomaly.employee}</p>
                  <p class="text-[0.78rem] text-slate-500">{anomaly.message}</p>
                </div>
                <AppIcon name="chevron-right" size={16} class="text-slate-300" />
              </button>
            {/each}
          </div>
        {:else}
          <div class="px-5 py-12 text-center">
            <div class="w-14 h-14 rounded-full bg-emerald-50 flex items-center justify-center mx-auto mb-3">
              <AppIcon name="check-circle" size={28} class="text-emerald-500" />
            </div>
            <p class="text-[0.9rem] font-bold text-slate-600">Aucune anomalie détectée</p>
            <p class="text-[0.82rem] text-slate-400 mt-0.5">Tous les bulletins sont conformes. Vous pouvez approuver la paie.</p>
          </div>
        {/if}
      </section>

      <!-- Action Bar -->
      <div class="flex items-center justify-between mt-6">
        <p class="text-[0.78rem] text-slate-400">Vérifiez le récapitulatif avant de procéder à l'approbation.</p>
        <div class="flex items-center gap-2">
          <Button variant="outline" size="sm" onclick={handleReject}
            class="h-9 px-4 text-[0.84rem] rounded-lg">
            <AppIcon name="x-circle" size={15} class="mr-1.5" />
            Rejeter
          </Button>
          <Button variant="default" size="sm" onclick={handleApprove} disabled={isApproving || summary.anomalyCount > 0}
            class="h-9 px-5 text-[0.84rem] shadow-fine rounded-lg">
            {#if isApproving}
              <AppIcon name="loader" size={15} class="animate-spin mr-1.5" />
              Approbation...
            {:else}
              <AppIcon name="check-circle" size={15} class="mr-1.5" />
              Approuver la paie
            {/if}
          </Button>
        </div>
      </div>

    </div>
  </main>
  {/if}
</div>
