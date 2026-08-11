<script lang="ts">
  import { page } from '$app/stores';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import PayrollStats from '$lib/features/payroll/components/run/PayrollStats.svelte';
  import PayrollTable from '$lib/features/payroll/components/run/PayrollTable.svelte';
  import EmptyState from '@/components/shared/containers/empty/EmptyState.svelte';
  import { payrollStore } from '$lib/features/payroll/stores/payroll.svelte';
  import { PAYROLL_STATUS_LABELS, PAYROLL_STATUS_COLORS } from '$lib/features/payroll/types/types';
  import { ui } from '$lib/stores/ui.svelte';

  const runId = $derived($page.params.id);

  let activeView = $state<'summary' | 'employees' | 'actions'>('summary');
  let viewState: 'loading' | 'success' | 'error' | 'offline' = $state('loading');

  $effect(() => {
    payrollStore.syncFromApi('runDetail', { runId }).then(() => {
      viewState = payrollStore.currentRun ? 'success' : 'error';
    }).catch(() => {
      viewState = 'error';
    });
  });

  $effect(() => {
    ui.addActions('payroll-run-detail', RunActions);
    return () => ui.removeActions('payroll-run-detail');
  });
</script>

{#snippet RunActions()}
  <div class="flex items-center gap-2">
    <Button variant="outline" size="sm" class="h-8 px-3 text-[0.84rem] rounded-lg">
      <AppIcon name="download" size={15} class="mr-1.5" />
      Exporter
    </Button>
    <Button variant="outline" size="sm" class="h-8 px-3 text-[0.84rem] rounded-lg">
      <AppIcon name="printer" size={15} class="mr-1.5" />
      Imprimer
    </Button>
    <Button variant="default" size="sm" class="h-8 px-3 text-[0.84rem] shadow-fine rounded-lg">
      <AppIcon name="play" size={15} class="mr-1.5" />
      Continuer
    </Button>
  </div>
{/snippet}


<svelte:head>
  <title>Oxiliere HR - Détail Run {runId}</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {#if viewState === 'loading'}
    <EmptyState variant="loading" class="h-full" />
  {:else if viewState === 'error' || viewState === 'offline'}
    <EmptyState
      variant={viewState === 'offline' ? 'offline' : 'error'}
      class="h-full"
      onRetry={() => { viewState = 'loading'; payrollStore.syncFromApi('runDetail', { runId }).finally(() => viewState = 'success'); }}
    />
  {:else}
    <main class="flex-1 overflow-y-auto min-h-0">
      <div class="max-w-6xl mx-auto px-6 py-6">

      <!-- ─── Header ─── -->
      <div class="flex items-center justify-between mb-6">
        <div class="flex items-center gap-4">
          <div>
            <div class="flex items-center gap-2.5 mb-1">
              <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">
                Exécution #{runId}
              </h1>
              <span class="px-2.5 py-0.5 rounded-full text-[0.7rem] font-bold uppercase tracking-wider bg-blue-50 text-blue-600">
                Juin 2026
              </span>
            </div>
            <p class="text-[0.78rem] text-slate-400">
              01/06/2026 → 30/06/2026 · 12 employés · CDF · Taux BCC: 2 850
            </p>
          </div>
        </div>
      </div>

      <!-- ─── Stats Cards ─── -->
      <PayrollStats />

      <!-- ─── Tabs ─── -->
      <div class="flex items-center gap-1 mt-6 mb-4 bg-slate-100 rounded-xl p-1 w-fit">
        <button onclick={() => activeView = 'summary'}
          class="flex items-center gap-1.5 px-4 py-2 text-[0.84rem] font-semibold rounded-lg transition-all cursor-pointer
                 {activeView === 'summary' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}">
          <AppIcon name="layout-dashboard" size={15} />
          Résumé
        </button>
        <button onclick={() => activeView = 'employees'}
          class="flex items-center gap-1.5 px-4 py-2 text-[0.84rem] font-semibold rounded-lg transition-all cursor-pointer
                 {activeView === 'employees' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}">
          <AppIcon name="users" size={15} />
          Employés
        </button>
        <button onclick={() => activeView = 'actions'}
          class="flex items-center gap-1.5 px-4 py-2 text-[0.84rem] font-semibold rounded-lg transition-all cursor-pointer
                 {activeView === 'actions' ? 'bg-white text-slate-800 shadow-sm' : 'text-slate-500 hover:text-slate-700'}">
          <AppIcon name="activity" size={15} />
          Historique
        </button>
      </div>

      {#if activeView === 'summary'}
        <!-- ─── Summary Cards ─── -->
        <div class="grid grid-cols-2 gap-4 mb-6">
          <!-- Période -->
          <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
                <AppIcon name="calendar-range" size={18} class="text-blue-600" />
              </div>
              <h2 class="text-[0.92rem] font-bold text-slate-800">Période</h2>
            </div>
            <div class="space-y-2">
              <div class="flex justify-between text-[0.84rem]">
                <span class="text-slate-400">Date début</span>
                <span class="font-semibold text-slate-700">01/06/2026</span>
              </div>
              <div class="flex justify-between text-[0.84rem]">
                <span class="text-slate-400">Date fin</span>
                <span class="font-semibold text-slate-700">30/06/2026</span>
              </div>
              <div class="flex justify-between text-[0.84rem]">
                <span class="text-slate-400">Jours calendaires</span>
                <span class="font-semibold text-slate-700">30</span>
              </div>
            </div>
          </section>

          <!-- Statut -->
          <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center">
                <AppIcon name="circle" size={18} class="text-amber-600" />
              </div>
              <h2 class="text-[0.92rem] font-bold text-slate-800">Statut</h2>
            </div>
            <div class="space-y-3">
              <span class="px-3 py-1 rounded-full text-[0.72rem] font-bold uppercase tracking-wider bg-blue-50 text-blue-600">
                En cours
              </span>
              <div class="w-full bg-slate-100 rounded-full h-2">
                <div class="bg-primary h-2 rounded-full" style="width: 40%"></div>
              </div>
              <p class="text-[0.78rem] text-slate-400">Étape 2/5 — Calcul</p>
            </div>
          </section>

          <!-- Anomalies -->
          <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center">
                <AppIcon name="check-circle" size={18} class="text-emerald-600" />
              </div>
              <h2 class="text-[0.92rem] font-bold text-slate-800">Anomalies</h2>
            </div>
            <p class="text-3xl font-extrabold text-emerald-600">0</p>
            <p class="text-[0.78rem] text-slate-400 mt-1">Aucune anomalie détectée</p>
          </section>

          <!-- Snapshot -->
          <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
            <div class="flex items-center gap-3 mb-4">
              <div class="w-9 h-9 rounded-lg bg-purple-50 flex items-center justify-center">
                <AppIcon name="fingerprint" size={18} class="text-purple-600" />
              </div>
              <h2 class="text-[0.92rem] font-bold text-slate-800">Audit</h2>
            </div>
            <p class="text-[0.75rem] font-mono font-semibold text-slate-500 break-all bg-slate-50 rounded-lg p-2">
              a1b2c3d4e5f6...7890
            </p>
            <p class="text-[0.72rem] text-slate-400 mt-1.5">SHA-256 · Généré le 27/07/2026</p>
          </section>
        </div>

      {:else if activeView === 'employees'}
        <PayrollTable />

      {:else if activeView === 'actions'}
        <!-- ─── History Timeline ─── -->
        <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center">
              <AppIcon name="activity" size={18} class="text-slate-600" />
            </div>
            <h2 class="text-[0.92rem] font-bold text-slate-800">Historique des actions</h2>
          </div>
          <div class="space-y-0">
            {#each [
              { action: 'Période définie', user: 'Admin', date: '27/07/2026 14:00', icon: 'calendar-plus', color: 'text-blue-600', bg: 'bg-blue-50' },
              { action: 'Calcul lancé', user: 'Système', date: '27/07/2026 14:05', icon: 'play', color: 'text-emerald-600', bg: 'bg-emerald-50' },
              { action: '12 bulletins générés', user: 'Système', date: '27/07/2026 14:06', icon: 'file-text', color: 'text-amber-600', bg: 'bg-amber-50' },
              { action: 'En attente de révision', user: 'Système', date: '27/07/2026 14:06', icon: 'eye', color: 'text-purple-600', bg: 'bg-purple-50' },
            ] as event}
              <div class="flex gap-3 pb-3 ml-2 border-l-2 border-slate-100 pl-4 relative">
                <div class="w-8 h-8 rounded-lg {event.bg} flex items-center justify-center -ml-[calc(1rem+1rem+4px)] bg-white border-2 border-white">
                  <AppIcon name={event.icon} size={15} class={event.color} />
                </div>
                <div class="flex-1 min-w-0">
                  <p class="text-[0.84rem] font-semibold text-slate-700">{event.action}</p>
                  <p class="text-[0.75rem] text-slate-400">{event.user} · {event.date}</p>
                </div>
              </div>
            {/each}
          </div>
        </section>
      {/if}

    </div>
  </main>
  {/if}
</div>

