<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import EmptyState from '@/components/shared/containers/empty/EmptyState.svelte';
  import { payrollStore } from '$lib/features/payroll/stores/payroll.svelte';
  import { ui } from '$lib/stores/ui.svelte';

  let activeReport = $state<'livre-paie' | 'cnss' | 'onem' | 'inpp' | 'etat-annuel'>('livre-paie');
  let viewState: 'loading' | 'success' | 'error' | 'offline' = $state('loading');

  $effect(() => {
    payrollStore.syncFromApi('runList', { status: 'closed' }).then(() => {
      viewState = 'success';
    }).catch(() => {
      viewState = 'error';
    });
  });

  const reportCards = [
    {
      id: 'livre-paie' as const,
      title: 'Livre de paie',
      desc: 'Registre mensuel détaillé de toutes les rémunérations versées.',
      icon: 'book-open',
      color: 'text-blue-600',
      bg: 'bg-blue-50',
    },
    {
      id: 'cnss' as const,
      title: 'Déclaration CNSS',
      desc: 'État des cotisations sociales salariales et patronales.',
      icon: 'shield',
      color: 'text-emerald-600',
      bg: 'bg-emerald-50',
    },
    {
      id: 'onem' as const,
      title: 'Dénombrement ONEM',
      desc: 'Relevé trimestriel des effectifs pour l\'Office National de l\'Emploi.',
      icon: 'users',
      color: 'text-amber-600',
      bg: 'bg-amber-50',
    },
    {
      id: 'inpp' as const,
      title: 'Déclaration INPP',
      desc: 'Contribution au régime des risques professionnels.',
      icon: 'building-2',
      color: 'text-purple-600',
      bg: 'bg-purple-50',
    },
    {
      id: 'etat-annuel' as const,
      title: 'État annuel',
      desc: 'Récapitulatif fiscal annuel par employé pour la DGI.',
      icon: 'file-text',
      color: 'text-rose-600',
      bg: 'bg-rose-50',
    },
  ];

  let selectedPeriod = $state('Juin 2026');

  $effect(() => {
    ui.addActions('payroll-reports', ActionSnippet);
    return () => ui.removeActions('payroll-reports');
  });
</script>

{#snippet ActionSnippet()}
  <!-- Actions go here -->
{/snippet}

<svelte:head>
  <title>Oxiliere HR - États & Rapports</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {#if viewState === 'loading'}
    <EmptyState variant="loading" class="h-full" />
  {:else if viewState === 'error' || viewState === 'offline'}
    <EmptyState
      variant={viewState === 'offline' ? 'offline' : 'error'}
      class="h-full"
      onRetry={() => { viewState = 'loading'; payrollStore.syncFromApi('runList', { status: 'closed' }).finally(() => viewState = 'success'); }}
    />
  {:else}
    <main class="flex-1 overflow-y-auto min-h-0">
    <div class="max-w-5xl mx-auto px-6 py-6">

      <!-- Header -->
      <div class="flex items-center justify-between mb-6">
        <div>
          <h1 class="text-xl font-extrabold text-slate-900 tracking-tight">États & Rapports</h1>
          <p class="text-[0.78rem] text-slate-400 mt-0.5">
            Livre de paie, déclarations CNSS, ONEM, INPP et états fiscaux.
          </p>
        </div>
        <div class="flex items-center gap-2">
          <label for="report-period" class="text-[0.72rem] font-semibold text-slate-500">Période</label>
          <select id="report-period" bind:value={selectedPeriod}
            class="h-9 px-3.5 text-[0.84rem] font-medium text-slate-700 bg-white border border-slate-200 rounded-lg
                   focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all">
            <option>Juin 2026</option>
            <option>Mai 2026</option>
            <option>Avril 2026</option>
            <option>Mars 2026</option>
            <option>1er trimestre 2026</option>
            <option>Année 2026</option>
          </select>
        </div>
      </div>

      <!-- Report Cards Grid -->
      <div class="grid grid-cols-5 gap-3 mb-6">
        {#each reportCards as card}
          <button onclick={() => activeReport = card.id}
            class="bg-white rounded-xl border p-4 text-left transition-all cursor-pointer hover:shadow-sm
                   {activeReport === card.id
                     ? 'border-primary/40 shadow-sm ring-1 ring-primary/10'
                     : 'border-slate-200/60 shadow-sm'}">
            <div class="w-9 h-9 rounded-lg {card.bg} flex items-center justify-center mb-3">
              <AppIcon name={card.icon} size={18} class={card.color} />
            </div>
            <h3 class="text-[0.84rem] font-bold text-slate-800 mb-0.5">{card.title}</h3>
            <p class="text-[0.72rem] text-slate-400 leading-relaxed">{card.desc}</p>
          </button>
        {/each}
      </div>

      <!-- Report Content -->
      <section class="bg-white rounded-2xl border border-slate-200/60 shadow-sm overflow-hidden">
        <!-- Toolbar -->
        <div class="flex items-center justify-between px-5 py-3 border-b border-slate-50 bg-slate-50/50">
          <div class="flex items-center gap-2">
            <span class="text-[0.82rem] font-bold text-slate-700">
              {reportCards.find(c => c.id === activeReport)?.title} — {selectedPeriod}
            </span>
            <span class="text-[0.72rem] text-slate-400 bg-slate-100 px-2.5 py-0.5 rounded-full">
              {reportCards.find(c => c.id === activeReport)?.id === 'etat-annuel' ? '12 employés' : '8 employés'}
            </span>
          </div>
          <div class="flex items-center gap-1.5">
            <Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.82rem] text-slate-500 hover:text-slate-700 rounded-lg">
              <AppIcon name="printer" size={14} class="mr-1" />
              Imprimer
            </Button>
            <Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.82rem] text-slate-500 hover:text-slate-700 rounded-lg">
              <AppIcon name="download" size={14} class="mr-1" />
              PDF
            </Button>
            <Button variant="ghost" size="sm" class="h-7 px-2.5 text-[0.82rem] text-slate-500 hover:text-slate-700 rounded-lg">
              <AppIcon name="file-spreadsheet" size={14} class="mr-1" />
              Excel
            </Button>
          </div>
        </div>

        <!-- Table -->
        <div class="overflow-auto">
          <table class="w-full text-left">
            <thead class="bg-slate-50/80">
              <tr>
                <th class="px-5 py-3 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Employé</th>
                <th class="px-5 py-3 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Matricule</th>
                <th class="px-5 py-3 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Dépt.</th>
                <th class="px-5 py-3 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider text-right">Brut</th>
                <th class="px-5 py-3 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider text-right">CNSS</th>
                <th class="px-5 py-3 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider text-right">
                  {activeReport === 'cnss' ? 'Patronale' : 'IRPP'}
                </th>
                <th class="px-5 py-3 text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider text-right">Net</th>
              </tr>
            </thead>
            <tbody class="divide-y divide-slate-50">
              {#each [
                { name: 'MUTOMBO Kalenga', mat: 'EMP-2024-001', dept: 'IT', brut: 4500000, cnss: 225000, irpp: 385560, net: 3889440 },
                { name: 'KABASELE Tshilombo', mat: 'EMP-2024-002', dept: 'Finance', brut: 3200000, cnss: 160000, irpp: 192500, net: 2847500 },
                { name: 'LUMUMBA Ndaya', mat: 'EMP-2024-003', dept: 'RH', brut: 2800000, cnss: 140000, irpp: 143800, net: 2516200 },
                { name: 'TSHIBANGU Mbuyi', mat: 'EMP-2024-004', dept: 'Production', brut: 2500000, cnss: 125000, irpp: 112300, net: 2262700 },
                { name: 'KASONGO Ilunga', mat: 'EMP-2024-005', dept: 'Commercial', brut: 2200000, cnss: 110000, irpp: 88200, net: 2001800 },
              ] as row}
                <tr class="hover:bg-slate-50/50 transition-colors">
                  <td class="px-5 py-3">
                    <div class="flex items-center gap-2.5">
                      <div class="w-8 h-8 rounded-lg bg-slate-100 flex items-center justify-center text-[0.7rem] font-bold text-slate-600">
                        {row.name.split(' ').map(n => n[0]).join('')}
                      </div>
                      <span class="text-[0.84rem] font-semibold text-slate-800">{row.name}</span>
                    </div>
                  </td>
                  <td class="px-5 py-3">
                    <span class="text-[0.8rem] font-mono text-slate-500">{row.mat}</span>
                  </td>
                  <td class="px-5 py-3">
                    <span class="text-[0.78rem] font-bold text-slate-400 bg-slate-50 px-2.5 py-0.5 rounded-md uppercase tracking-tight">{row.dept}</span>
                  </td>
                  <td class="px-5 py-3 text-right">
                    <span class="text-[0.84rem] font-semibold text-slate-700 tabular-nums">
                      {row.brut.toLocaleString('fr-FR')} CDF
                    </span>
                  </td>
                  <td class="px-5 py-3 text-right">
                    <span class="text-[0.84rem] font-medium text-slate-600 tabular-nums">
                      {row.cnss.toLocaleString('fr-FR')} CDF
                    </span>
                  </td>
                  <td class="px-5 py-3 text-right">
                    <span class="text-[0.84rem] font-medium text-slate-600 tabular-nums">
                      {row.irpp.toLocaleString('fr-FR')} CDF
                    </span>
                  </td>
                  <td class="px-5 py-3 text-right">
                    <span class="text-[0.86rem] font-bold text-emerald-600 tabular-nums">
                      {row.net.toLocaleString('fr-FR')} CDF
                    </span>
                  </td>
                </tr>
              {/each}
            </tbody>
            <tfoot>
              <tr class="bg-slate-50/80 border-t-2 border-slate-100">
                <td class="px-5 py-3 text-[0.82rem] font-bold text-slate-700" colspan="3">Totaux (5 employés)</td>
                <td class="px-5 py-3 text-right text-[0.84rem] font-extrabold text-slate-800 tabular-nums">15 200 000 CDF</td>
                <td class="px-5 py-3 text-right text-[0.84rem] font-bold text-slate-700 tabular-nums">760 000 CDF</td>
                <td class="px-5 py-3 text-right text-[0.84rem] font-bold text-slate-700 tabular-nums">922 360 CDF</td>
                <td class="px-5 py-3 text-right text-[0.86rem] font-extrabold text-emerald-600 tabular-nums">13 517 640 CDF</td>
              </tr>
            </tfoot>
          </table>
        </div>
      </section>

      <!-- History Panel -->
      <section class="mt-6 bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
        <div class="flex items-center gap-3 mb-4">
          <div class="w-9 h-9 rounded-lg bg-slate-100 flex items-center justify-center">
            <AppIcon name="history" size={18} class="text-slate-600" />
          </div>
          <div>
            <h2 class="text-[0.92rem] font-bold text-slate-800">Historique des rapports générés</h2>
            <p class="text-[0.72rem] text-slate-400">Derniers exports et déclarations.</p>
          </div>
        </div>
        <div class="space-y-1">
          {#each [
            { label: 'Livre de paie — Juin 2026', date: '27 juil. 2026 14:30', format: 'PDF' },
            { label: 'Déclaration CNSS — T2 2026', date: '15 juil. 2026 09:15', format: 'Excel' },
            { label: 'Dénombrement ONEM — T2 2026', date: '15 juil. 2026 09:20', format: 'PDF' },
            { label: 'Livre de paie — Mai 2026', date: '30 juin 2026 16:45', format: 'PDF' },
          ] as entry}
            <div class="flex items-center justify-between px-3 py-2.5 rounded-lg hover:bg-slate-50 transition-colors">
              <div class="flex items-center gap-3">
                <AppIcon name="file-text" size={16} class="text-slate-400" />
                <span class="text-[0.84rem] font-medium text-slate-700">{entry.label}</span>
                <span class="text-[0.72rem] text-slate-400">{entry.date}</span>
              </div>
              <div class="flex items-center gap-2">
                <span class="text-[0.72rem] font-bold text-slate-400 bg-slate-100 px-2.5 py-0.5 rounded-full uppercase">{entry.format}</span>
                <button class="text-slate-400 hover:text-primary transition-colors cursor-pointer">
                  <AppIcon name="download" size={15} />
                </button>
              </div>
            </div>
          {/each}
        </div>
      </section>

    </div>
  </main>
  {/if}
</div>
