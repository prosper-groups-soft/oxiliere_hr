<script lang="ts">
  import { goto } from '$app/navigation';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import { payrollStore } from '@/features/payroll/stores/payroll.svelte';
  import { ui } from '@/stores/ui.svelte';
  import { notification } from '@/stores/notification.svelte';
  import { orgService } from '@/features/jobs/services/org.service';

  
  let periodStart = $state('');
  let periodEnd = $state('');
  let currency: 'CDF' | 'USD' = $state('CDF');
  let exchangeRate = $state(2850);
  let includeAllEmployees = $state(true);
  let selectedOrgUnits: string[] = $state([]);
  let isSubmitting = $state(false);
  let orgUnits = $state<string[]>([]);
  let isLoadingOrgUnits = $state(true);

  // Unités organisationnelles chargées depuis le backend (/api/organization/units)
  // Dans ce système, les départements sont une catégorie d'unité organisationnelle (type = DEPARTMENT)
  $effect(() => {
    let cancelled = false;
    orgService.listOrgUnits(1, 200)
      .then((res) => {
        if (cancelled) return;
        orgUnits = (res.results || [])
          .filter(u => u.type === 'DEPARTMENT')
          .map(u => u.name)
          .sort((a, b) => a.localeCompare(b));
      })
      .catch((err) => {
        if (cancelled) return;
        notification.toast.error(err?.message ?? 'Échec du chargement des unités organisationnelles');
      })
      .finally(() => {
        if (!cancelled) isLoadingOrgUnits = false;
      });
    return () => { cancelled = true; };
  });

  function toggleOrgUnit(unit: string) {
    if (selectedOrgUnits.includes(unit)) {
      selectedOrgUnits = selectedOrgUnits.filter(u => u !== unit);
    } else {
      selectedOrgUnits = [...selectedOrgUnits, unit];
    }
  }

  function handleSubmit() {
    if (!periodStart || !periodEnd) return;
    // La validation d'overlap est gérée côté backend (ValidationError 400)
    createRun();
  }

  async function createRun() {
    if (!periodStart || !periodEnd) return;
    isSubmitting = true;
    try {
      await payrollStore.createPayrollRunFromDates(periodStart, periodEnd, currency === 'USD' ? exchangeRate : null);
      notification.toast.success('Exécution de paie créée');
      await goto('/payroll/run');
    } catch (err: any) {
      notification.toast.error(err?.message ?? 'Échec de la création de l\'exécution');
    } finally {
      isSubmitting = false;
    }
  }

  const isValid = $derived(periodStart && periodEnd && periodStart < periodEnd);
  const periodDays = $derived(() => {
    if (!periodStart || !periodEnd) return 0;
    const s = new Date(periodStart);
    const e = new Date(periodEnd);
    return Math.round((e.getTime() - s.getTime()) / 86400000) + 1;
  });

  $effect(() => {
    ui.addActions('payroll-new-run', ActionsSnippet);
    return () => ui.removeActions('payroll-new-run');
  });
</script>

{#snippet ActionsSnippet()}
  <!-- Actions go here -->
{/snippet}

<svelte:head>
  <title>Oxiliere HR - Nouvelle exécution de paie</title>
</svelte:head>

<div class="flex h-full flex-col overflow-hidden min-h-0">
  <main class="flex-1 overflow-y-auto min-h-0">
    <div class="max-w-3xl mx-auto px-6 py-6">

      <form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-6">

        <!-- ─── Section Période ─── -->
        <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-9 h-9 rounded-lg bg-blue-50 flex items-center justify-center">
              <AppIcon name="calendar-range" size={18} class="text-blue-600" />
            </div>
            <div>
              <h2 class="text-[0.92rem] font-bold text-slate-800">Période de paie</h2>
              <p class="text-[0.72rem] text-slate-400">Définissez la période couverte par cette exécution.</p>
            </div>
          </div>

          <div class="grid grid-cols-2 gap-4">
            <div>
              <label for="period-start" class="block text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                Date début
              </label>
              <input id="period-start" type="date" bind:value={periodStart}
                class="w-full h-10 px-3.5 text-[0.86rem] font-medium text-slate-800 bg-slate-50 border border-slate-200 rounded-xl
                       focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
            </div>
            <div>
              <label for="period-end" class="block text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                Date fin
              </label>
              <input id="period-end" type="date" bind:value={periodEnd}
                class="w-full h-10 px-3.5 text-[0.86rem] font-medium text-slate-800 bg-slate-50 border border-slate-200 rounded-xl
                       focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
            </div>
          </div>

          {#if periodDays() > 0}
            <div class="mt-3 flex items-center gap-2.5 px-3 py-2 bg-slate-50 rounded-lg">
              <AppIcon name="info" size={15} class="text-slate-400" />
              <span class="text-[0.8rem] text-slate-500">
                {periodDays()} jours calendaires
                <span class="text-slate-300 mx-1.5">·</span>
                {periodStart} → {periodEnd}
              </span>
            </div>
          {/if}
        </section>

        <!-- ─── Section Devise ─── -->
        <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center">
              <AppIcon name="banknote" size={18} class="text-emerald-600" />
            </div>
            <div>
              <h2 class="text-[0.92rem] font-bold text-slate-800">Devise</h2>
              <p class="text-[0.72rem] text-slate-400">Monnaie de calcul et taux de change applicable.</p>
            </div>
          </div>

          <div class="flex gap-2 mb-3">
            <button type="button" onclick={() => currency = 'CDF'}
              class="flex-1 h-10 rounded-xl border-2 font-semibold text-[0.84rem] transition-all cursor-pointer
                     {currency === 'CDF' ? 'border-primary bg-primary/5 text-primary' : 'border-slate-200 text-slate-400 hover:border-slate-300'}">
              🇨🇩 Franc Congolais (CDF)
            </button>
            <button type="button" onclick={() => currency = 'USD'}
              class="flex-1 h-10 rounded-xl border-2 font-semibold text-[0.84rem] transition-all cursor-pointer
                     {currency === 'USD' ? 'border-primary bg-primary/5 text-primary' : 'border-slate-200 text-slate-400 hover:border-slate-300'}">
              🇺🇸 Dollar US (USD)
            </button>
          </div>

          {#if currency === 'USD'}
            <div>
              <label for="exchange-rate" class="block text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider mb-1.5">
                Taux de change USD → CDF
              </label>
              <div class="relative">
                <input id="exchange-rate" type="number" bind:value={exchangeRate}
                  class="w-full h-10 px-3.5 pr-16 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border border-slate-200 rounded-xl
                         focus:outline-none focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
                <span class="absolute right-3 top-1/2 -translate-y-1/2 text-[0.72rem] font-bold text-slate-400">CDF/USD</span>
              </div>
              <p class="text-[0.72rem] text-slate-400 mt-1 flex items-center gap-1">
                <AppIcon name="info" size={12} />
                Taux officiel BCC — mise à jour automatique.
              </p>
            </div>
          {/if}
        </section>

        <!-- ─── Section Employés ─── -->
        <section class="bg-white rounded-2xl border border-slate-200/60 p-5 shadow-sm">
          <div class="flex items-center gap-3 mb-4">
            <div class="w-9 h-9 rounded-lg bg-purple-50 flex items-center justify-center">
              <AppIcon name="users" size={18} class="text-purple-600" />
            </div>
            <div>
              <h2 class="text-[0.92rem] font-bold text-slate-800">Employés</h2>
              <p class="text-[0.72rem] text-slate-400">Sélection des contrats à inclure dans le calcul.</p>
            </div>
          </div>

          <label class="flex items-center gap-3 p-3.5 bg-slate-50 rounded-xl cursor-pointer hover:bg-slate-100 transition-colors">
            <input type="checkbox" bind:checked={includeAllEmployees}
              class="w-5 h-5 rounded-md border-slate-300 text-primary focus:ring-primary/20 cursor-pointer" />
            <div>
              <span class="text-[0.86rem] font-semibold text-slate-700">Tous les employés actifs</span>
              <p class="text-[0.75rem] text-slate-400 mt-0.5">
                Inclut automatiquement tous les contrats actifs sur la période.
              </p>
            </div>
          </label>

          {#if !includeAllEmployees}
            <div class="mt-3">
              <p class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider mb-2">Filtrer par département</p>
              <div class="flex flex-wrap gap-2">
                {#if isLoadingOrgUnits}
                  <span class="text-[0.78rem] text-slate-400 italic">Chargement des départements…</span>
                {:else if orgUnits.length === 0}
                  <span class="text-[0.78rem] text-slate-400 italic">Aucun département disponible.</span>
                {:else}
                  {#each orgUnits as unit}
                    <button type="button" onclick={() => toggleOrgUnit(unit)}
                      class="px-3.5 py-1.5 text-[0.78rem] font-bold rounded-full border-2 transition-all cursor-pointer
                             {selectedOrgUnits.includes(unit) ? 'border-primary bg-primary/5 text-primary' : 'border-slate-200 text-slate-400 hover:border-slate-300'}">
                      {unit}
                    </button>
                  {/each}
                {/if}
              </div>
            </div>
          {/if}
        </section>

        <!-- ─── Actions ─── -->
        <div class="flex items-center justify-end gap-2.5">
          <button type="button" onclick={() => goto('/payroll')}
            class="h-9 px-5 text-[0.84rem] font-semibold text-slate-500 bg-white border border-slate-200 rounded-lg hover:bg-slate-50 transition-colors cursor-pointer">
            Annuler
          </button>
          <Button type="submit" variant="default" size="sm"
            disabled={!isValid || isSubmitting}
            class="h-9 px-5 text-[0.84rem] shadow-fine rounded-lg">
            {#if isSubmitting}
              <AppIcon name="loader" size={15} class="animate-spin mr-1.5" />
              Création...
            {:else}
              <AppIcon name="play" size={15} class="mr-1.5" />
              Lancer l'exécution
            {/if}
          </Button>
        </div>
      </form>
    </div>
  </main>
</div>

