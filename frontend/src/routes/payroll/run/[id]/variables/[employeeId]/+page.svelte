<script lang="ts">
  import { page } from '$app/stores';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Button } from '@/components/ui/button';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import { Input } from '@/components/ui/input';
  import { Label } from '@/components/ui/label';
  import EmptyState from '@/components/shared/containers/empty/EmptyState.svelte';
  import { payrollStore } from '@/features/payroll/stores/payroll.svelte';
  import AnimateSpin from '@/components/layout/elements/AnimateSpin.svelte';
  import { notification } from '@/stores/notification.svelte';
  import { ui } from '@/stores/ui.svelte';


  const runId = $derived($page.params.id);
  const employeeId = $derived($page.params.employeeId);

  let viewState: 'loading' | 'success' | 'error' | 'offline' = $state('loading');
  let isSaving = $state(false);
  let overtimeStandard = $state(0);
  let overtimeWeekend = $state(0);
  let overtimeHoliday = $state(0);
  let overtimeNight = $state(0);
  let bonusPerformance = $state(0);
  let bonusFunction = $state(0);
  let commission = $state(0);
  let absenceDays = $state(0);
  let advanceDeduction = $state(0);

  let employeeName = $state('');
  let baseSalary = $state(0);

  $effect(() => {
    payrollStore.syncFromApi('payslips', { runId }).then(() => {
      const slip = payrollStore.payslips.find(p => String(p.employee.id) === employeeId);
      if (slip) {
        employeeName = slip.employee.fullName;
        baseSalary = slip.contract.baseSalary;
        viewState = 'success';
      } else {
        viewState = 'error';
      }
    }).catch(() => {
      viewState = 'error';
    });
  });

  function handleSave() {
    isSaving = true;
    setTimeout(() => {
      isSaving = false;
      notification.toast.success('Variables enregistrées');
    }, 600);
  }

  $effect(() => {
    ui.addActions('payroll-variables', SaveAction);
    return () => ui.removeActions('payroll-variables');
  });
</script>


{#snippet SaveAction()}
  <Button size="sm" onclick={handleSave} disabled={isSaving}
    class="h-8 px-3 text-[0.84rem] shadow-fine rounded-lg">
    {#if isSaving}
      <AnimateSpin text="" class="size-3" />
    {:else}
      <AppIcon name="save" size={15} class="mr-1.5" />
    {/if}
    Enregistrer
  </Button>
{/snippet}


<svelte:head>
  <title>Oxiliere HR - Variables {employeeName}</title>
</svelte:head>


<div class="flex h-full flex-col overflow-hidden min-h-0">
  {#if viewState === 'loading'}
    <EmptyState variant="loading" class="h-full" />
  {:else if viewState === 'error' || viewState === 'offline'}
    <EmptyState
      variant={viewState === 'offline' ? 'offline' : 'error'}
      class="h-full"
      onRetry={() => { viewState = 'loading'; payrollStore.syncFromApi('payslips', { runId }).finally(() => viewState = 'success'); }}
    />
  {:else}
    <main class="flex-1 overflow-y-auto min-h-0">
      <div class="max-w-3xl mx-auto px-6 py-6">

      <!-- Employee header -->
      <div class="flex items-center gap-4 mb-6 pb-4 border-b border-slate-100">
        <div class="w-12 h-12 rounded-2xl bg-slate-100 flex items-center justify-center text-sm font-bold text-slate-600">
          {employeeName.split(' ').map(n => n[0]).join('')}
        </div>
        <div>
          <h1 class="text-lg font-extrabold text-slate-900 tracking-tight">{employeeName}</h1>
          <p class="text-[0.78rem] text-slate-400">
            Salaire de base : {baseSalary.toLocaleString('fr-FR')} CDF · Run #{runId}
          </p>
        </div>
      </div>

      <form onsubmit={(e) => { e.preventDefault(); handleSave(); }} class="space-y-5">

        <!-- Overtime -->
        <Card class="border border-slate-200/60 p-5 shadow-sm">
          <CardHeader class="p-0 mb-4">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-lg bg-amber-50 flex items-center justify-center shrink-0">
                <AppIcon name="clock" size={18} class="text-amber-600" />
              </div>
              <div>
                <CardTitle class="text-[0.92rem] font-bold text-slate-800">Heures supplémentaires</CardTitle>
                <p class="text-[0.72rem] text-slate-400">Saisissez les heures supplémentaires effectuées.</p>
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <Label for="ot-standard" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">
                  HS Standard ×1.3
                </Label>
                <Input id="ot-standard" type="number" min="0" bind:value={overtimeStandard}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
              </div>
              <div class="space-y-1.5">
                <Label for="ot-weekend" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">
                  HS Week-end ×2.0
                </Label>
                <Input id="ot-weekend" type="number" min="0" bind:value={overtimeWeekend}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
              </div>
              <div class="space-y-1.5">
                <Label for="ot-holiday" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">
                  HS Jours fériés ×2.0
                </Label>
                <Input id="ot-holiday" type="number" min="0" bind:value={overtimeHoliday}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
              </div>
              <div class="space-y-1.5">
                <Label for="ot-night" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">
                  HS Nuit ×1.5
                </Label>
                <Input id="ot-night" type="number" min="0" bind:value={overtimeNight}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Primes & Commissions -->
        <Card class="border border-slate-200/60 p-5 shadow-sm">
          <CardHeader class="p-0 mb-4">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-lg bg-emerald-50 flex items-center justify-center shrink-0">
                <AppIcon name="trending-up" size={18} class="text-emerald-600" />
              </div>
              <div>
                <CardTitle class="text-[0.92rem] font-bold text-slate-800">Primes &amp; Commissions</CardTitle>
                <p class="text-[0.72rem] text-slate-400">Montants additionnels pour cette période.</p>
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <div class="grid grid-cols-3 gap-4">
              <div class="space-y-1.5">
                <Label for="bonus-perf" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Prime performance</Label>
                <Input id="bonus-perf" type="number" min="0" bind:value={bonusPerformance}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
              </div>
              <div class="space-y-1.5">
                <Label for="bonus-func" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Prime de fonction</Label>
                <Input id="bonus-func" type="number" min="0" bind:value={bonusFunction}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
              </div>
              <div class="space-y-1.5">
                <Label for="commission" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Commissions</Label>
                <Input id="commission" type="number" min="0" bind:value={commission}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Absences & Avances -->
        <Card class="border border-slate-200/60 p-5 shadow-sm">
          <CardHeader class="p-0 mb-4">
            <div class="flex items-center gap-3">
              <div class="w-9 h-9 rounded-lg bg-rose-50 flex items-center justify-center shrink-0">
                <AppIcon name="minus-circle" size={18} class="text-rose-600" />
              </div>
              <div>
                <CardTitle class="text-[0.92rem] font-bold text-slate-800">Déductions</CardTitle>
                <p class="text-[0.72rem] text-slate-400">Absences et retenues sur salaire.</p>
              </div>
            </div>
          </CardHeader>
          <CardContent class="p-0">
            <div class="grid grid-cols-2 gap-4">
              <div class="space-y-1.5">
                <Label for="absence-days" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Jours d'absence</Label>
                <Input id="absence-days" type="number" min="0" bind:value={absenceDays}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
                <p class="text-[0.72rem] text-slate-400 mt-1">Diviseur : 26 jours</p>
              </div>
              <div class="space-y-1.5">
                <Label for="advance-deduction" class="text-[0.65rem] font-bold text-slate-400 uppercase tracking-wider">Retenue avance</Label>
                <Input id="advance-deduction" type="number" min="0" bind:value={advanceDeduction}
                  class="h-10 px-3.5 text-[0.86rem] font-semibold text-slate-800 bg-slate-50 border-slate-200 rounded-xl
                         focus:ring-2 focus:ring-primary/20 focus:border-primary transition-all" />
              </div>
            </div>
          </CardContent>
        </Card>

        <!-- Actions -->
        <div class="flex items-center justify-end gap-2.5">
          <Button variant="outline" size="sm" class="h-9 px-5 text-[0.84rem] rounded-lg">Annuler</Button>
          <Button variant="default" size="sm" onclick={handleSave} disabled={isSaving}
            class="h-9 px-5 text-[0.84rem] shadow-fine rounded-lg">
            {#if isSaving}
              <AnimateSpin text="" class="size-3" />
            {:else}
              <AppIcon name="save" size={15} class="mr-1.5" />
            {/if}
            Enregistrer
          </Button>
        </div>
      </form>
    </div>
  </main>
  {/if}
</div>
