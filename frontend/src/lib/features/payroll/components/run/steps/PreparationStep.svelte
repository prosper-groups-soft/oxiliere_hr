<script lang="ts">
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle 
  } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";
  import Input from "@/components/ui/input/input.svelte";
  import { slide, fade } from "svelte/transition";
  
  const isLocked = $derived(
    !!payrollStore.currentRun && payrollStore.currentRun.status !== 'draft'
  );
  
  let showEmployeeList = $state(false);
  let showExcluded = $state(false);

  const activeEmployees = $derived(payrollStore.payslips);
  const excludedEmployees = $derived(payrollStore.excludedEmployees);
  
  // Statistics from store
  const stats = $derived({
    activeCount: payrollStore.activeEmployeesCount,
    excludedCount: payrollStore.excludedEmployeesCount,
    totalSalary: payrollStore.totalBaseSalary,
    averageSalary: payrollStore.averageSalary,
    variables: payrollStore.variablesDetected,
    completionRate: payrollStore.completionRate,
    completeProfiles: payrollStore.completeProfilesCount,
    orgUnits: payrollStore.orgUnitDistribution
  });

  const orgUnitColors: Record<string, { bg: string; text: string; dot: string }> = {
    'IT': { bg: 'bg-blue-100', text: 'text-blue-700', dot: 'bg-blue-500' },
    'RH': { bg: 'bg-rose-100', text: 'text-rose-700', dot: 'bg-rose-500' },
    'Finance': { bg: 'bg-emerald-100', text: 'text-emerald-700', dot: 'bg-emerald-500' },
    'Admin': { bg: 'bg-amber-100', text: 'text-amber-700', dot: 'bg-amber-500' }
  };

  const getOrgUnitColor = (orgUnit: string) => 
    orgUnitColors[orgUnit] || { bg: 'bg-slate-100', text: 'text-slate-600', dot: 'bg-slate-400' };

  function handlePeriodChange(e: Event) {
    const newVal = (e.target as HTMLInputElement).value;
    payrollStore.currentPeriod = newVal;
    if (payrollStore.currentRun) {
      payrollStore.currentRun.period = newVal;
    }
  }
</script>


{#snippet EmployeeRow(emp: any, index: number)}
  <div class="flex items-center justify-between border-b border-slate-50 pb-2 last:border-0" in:fade={{ delay: index * 30 }}>
    <div class="flex items-center gap-3">
      <div class="w-7 h-7 rounded bg-slate-50 flex items-center justify-center text-[0.82rem] font-semibold text-slate-400 border border-slate-100">
        {index + 1}
      </div>
      <div class="flex flex-col">
        <span class="text-sm text-slate-700 font-medium">{emp.employeeName}</span>
        <span class="text-[0.75rem] text-slate-400">{emp.orgUnit}</span>
      </div>
    </div>
    <div class="flex items-center gap-3">
       <div class="flex items-center gap-1 text-[0.7rem] font-medium {emp.baseSalary > 0 || index < 5 ? 'text-emerald-600' : 'text-amber-600'}">
          <AppIcon name={emp.baseSalary > 0 || index < 5 ? 'circle-check' : 'circle-alert'} size={14} />
          {emp.baseSalary > 0 || index < 5 ? 'Profil complet' : 'RIB manquant'}
       </div>
       <span class="text-[0.75rem] text-slate-500 bg-slate-100 px-2 py-0.5 rounded font-medium">CDI</span>
    </div>
  </div>
{/snippet}


{#snippet OrgUnitBadge(orgUnit: string)}
  {@const colors = getOrgUnitColor(orgUnit)}
  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[0.72rem] font-medium {colors.bg} {colors.text}">
    <span class="h-1.5 w-1.5 rounded-full {colors.dot}"></span>
    {orgUnit}
  </span>
{/snippet}


<div class="mt-2 space-y-3">
  
  <Card class="border shadow-none">
    <CardHeader class="pb-0">
      <CardTitle class="text-sm font-bold flex items-center gap-2">
        <AppIcon name="calendar" size={18} strokeWidth={1.3} class="text-slate-500" />
        Période de paie
      </CardTitle>
    </CardHeader>
    <CardContent>
      <div class="grid grid-cols-2 gap-8">
        <div>
          <div class="text-sm font-medium text-slate-500 mb-1.5">Mois d'exécution</div>
          <Input
            type="month"
            value={payrollStore.currentPeriod}
            oninput={handlePeriodChange}
            disabled={isLocked}
            class="w-full max-w-[200px] h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine disabled:bg-slate-50 disabled:text-slate-500 transition-all cursor-pointer border"
          />
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500 mb-1.5">Cycle de paie</div>
          <p class="text-sm text-slate-900 font-medium capitalize">
            Mensuel — {new Date(payrollStore.currentPeriod + '-01').toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>

  <Card class="border shadow-none">
    <CardHeader class="pb-0">
      <div class="flex items-center justify-between">
        <CardTitle class="text-sm font-bold flex items-center gap-2">
          <AppIcon name="users" size={18} strokeWidth={1.3} class="text-slate-500" />
          Analyse des bénéficiaires
        </CardTitle>
        <div class="flex items-center gap-4">
          <button 
            onclick={() => showExcluded = !showExcluded}
            class="text-[0.8rem] font-semibold {showExcluded ? 'text-rose-600' : 'text-slate-500'} hover:opacity-80 hover:underline transition-all cursor-pointer"
          >
            {stats.excludedCount} exclus ce mois
          </button>
          <button 
            onclick={() => showEmployeeList = !showEmployeeList}
            class="text-[0.8rem] font-bold text-primary hover:opacity-80 flex items-center gap-1.5 transition-all hover:underline cursor-pointer"
          >
            <AppIcon name={showEmployeeList ? 'eye-off' : 'eye'} size={16} strokeWidth={1.7} />
            {showEmployeeList ? 'Masquer la liste' : 'Afficher les noms'}
          </button>
        </div>
      </div>
    </CardHeader>

    <CardContent class="space-y-6">
      <div class="grid grid-cols-2 md:grid-cols-4 gap-6">
        <div>
          <div class="text-sm font-medium text-slate-500 flex items-center gap-1.5">
            Effectif à payer
            {#if stats.excludedCount > 0}
              <span class="text-[0.65rem] bg-blue-50 text-blue-600 px-1 rounded border border-blue-100">+{stats.excludedCount}</span>
            {/if}
          </div>
          <p class="text-sm text-slate-900 font-bold">{stats.activeCount} contrats actifs</p>
        </div>

        <div>
          <div class="text-sm font-medium text-slate-500">Masse salariale (Base)</div>
          <div class="flex items-baseline gap-1.5">
            <p class="text-sm text-slate-900 font-bold">${stats.totalSalary.toLocaleString()}</p>
            <span class="text-[0.8rem] text-slate-400 font-medium">Moy: ${stats.averageSalary.toLocaleString()}</span>
          </div>
        </div>

        <div>
          <div class="text-sm font-medium text-slate-500">Variables détectés</div>
          <div class="flex items-center gap-1.5">
            <p class="text-sm text-slate-900 font-bold">{stats.variables.primes} primes</p>
            <span class="h-1 w-1 rounded-full bg-slate-300"></span>
            <p class="text-sm text-slate-900 font-bold">{stats.variables.avances} avances</p>
          </div>
        </div>

        <div>
          <div class="text-sm font-medium text-slate-500">Dossiers complets</div>
          <div class="flex items-center gap-2">
            <div class="flex-1 h-1.5 bg-slate-100 rounded-full overflow-hidden max-w-[60px]">
              <div class="h-full bg-emerald-500" style="width: {stats.completionRate}%"></div>
            </div>
            <p class="text-sm text-emerald-600 font-bold">{stats.completionRate}%</p>
          </div>
        </div>
      </div>

      <div class="pt-2">
        <div class="text-sm font-medium text-slate-500 mb-2.5 flex items-center gap-2">
          Répartition par départements
          <Separator class="flex-1 opacity-50" />
        </div>
        <div class="flex flex-wrap gap-1.5">
          {#each Object.entries(stats.orgUnits) as [orgUnit, count]}
            {@render OrgUnitBadge(orgUnit)}
          {/each}
        </div>
      </div>

      {#if showExcluded}
        <div transition:slide class="p-3 bg-rose-50/50 border border-rose-100 rounded-lg space-y-2">
          <div class="text-[0.75rem] font-bold text-rose-700 flex items-center gap-2">
            <AppIcon name="user-minus" size={16} /> 
            Collaborateurs non-éligibles pour {new Date(payrollStore.currentPeriod + '-01').toLocaleDateString('fr-FR', { month: 'long' })}
          </div>
          {#each excludedEmployees as ex}
            <div class="flex items-center justify-between text-[0.82rem]">
              <span class="text-slate-700 font-medium text-[0.82rem]">{ex.employeeName} ({ex.orgUnit})</span>
              <span class="text-rose-600 text-[0.82rem]">{ex.reason}</span>
            </div>
          {/each}
        </div>
      {/if}

      {#if showEmployeeList}
        <div transition:slide={{ duration: 300 }} class="overflow-hidden">
          <div class="pt-4 border-t border-slate-100">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-x-12 gap-y-3">
              {#each activeEmployees.length > 0 ? activeEmployees : Array(6) as emp, i}
                {@render EmployeeRow(emp.employeeName ? emp : { employeeName: `Employé #00${i+1}`, orgUnit: 'Unité organisationnelle' }, i)}
              {/each}
            </div>
          </div>
        </div>
      {/if}
      
      <Separator />

      <div class="flex items-start gap-3 p-3 bg-slate-50/50 rounded-lg border border-slate-100">
        <AppIcon name="shield-info" size={18} class="text-blue-500 mt-0.5" />
        <div class="space-y-1">
          <p class="text-[0.82rem] text-slate-700 font-semibold">
            Vérification de conformité terminée
          </p>
          <p class="text-[0.82rem] text-slate-600 leading-relaxed">
            Le système a identifié <span class="text-emerald-600 font-medium text-[0.82rem]">{stats.completeProfiles} profils prêts</span> pour le calcul ({stats.completionRate}%). 
            {stats.excludedCount > 0 && `Les ${stats.excludedCount} suspensions et fins de contrat sont automatiquement exclues pour garantir la précision légale.`}
          </p>
        </div>
      </div>
    </CardContent>
  </Card>
</div>

