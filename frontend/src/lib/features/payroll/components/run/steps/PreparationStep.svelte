<script lang="ts">
  import { onMount } from "svelte";
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import { payrollRunStore } from "@/features/payroll/stores/runs/payrollRunStore.svelte";
  import { employeesService } from "@/features/employees/services/employees.service";
  import { orgService } from "@/features/jobs/services/org.service";
  import type { Employee } from "@/features/employees/types/types";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";
  import { slide, fade } from "svelte/transition";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { cn } from "@/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { getOrgUnitColor } from "@/features/payroll/constants/orgUnitColors.constants";


  // Liste visible (onglet actif). Mutuellement exclusive : un seul panneau à la
  // fois, re-cliquer sur l'onglet actif replie tout.
  type ActiveList = 'employees' | 'excluded' | null;
  let activeList = $state<ActiveList>(null);
  let isLoading = $state(true);
  let allEmployees = $state<Employee[]>([]);
  let orgUnits = $state<Array<{ id: string; name: string; type: string }>>([]);

  const run = $derived(payrollRunStore.currentRun);
  const selection = $derived(run?.selection);

  // Charger les unités organisationnelles depuis le backend (source de vérité)
  $effect(() => {
    let cancelled = false;
    orgService.listOrgUnits(1, 200)
      .then((res) => {
        if (cancelled) return;
        orgUnits = (res.results || [])
          .map(u => ({ id: u.id, name: u.name, type: u.type }))
          .sort((a, b) => a.name.localeCompare(b.name));
      })
      .catch((err) => {
        if (cancelled) return;
        console.error('Failed to load org units in PreparationStep', err);
      });
    return () => { cancelled = true; };
  });

  function initialsFromName(name: string): string {
    return name.split(' ').map(n => n[0]).filter(Boolean).slice(0, 2).join('').toUpperCase();
  }

  /** Libellé du mode de rémunération (FIXED = salaire fixe, HOURLY = taux horaire). */
  function remunerationLabel(type?: string): string {
    switch (type) {
      case 'FIXED': return 'Salaire fixe';
      case 'HOURLY': return 'Taux horaire';
      default: return '—';
    }
  }

  /** Nature du montant de base affiché : BASE = avant déductions, NET = brutage à appliquer. */
  function salaryKindLabel(base?: string): string {
    switch (base) {
      case 'NET': return 'Net (brutage)';
      default: return 'Salaire de base';
    }
  }

  /** Formate un montant dans la devise du contrat (sans symbole, code ISO). */
  function formatAmount(value?: number | null, currency?: string): string {
    if (value == null || Number.isNaN(Number(value))) return '—';
    const formatted = Number(value).toLocaleString('fr-FR', {
      maximumFractionDigits: 0,
    });
    return currency ? `${formatted} ${currency}` : formatted;
  }

  /**
   * Valeur affichée d'un élément de paie, sourcée : % négocié > montant > % par
   * défaut du catalogue. Un % est appliqué sur le salaire brut (base orchestrateur).
   */
  function formatPayElementValue(el: { custom_percentage?: number | null; custom_amount?: number | null; amount?: number | null; value_type?: string; catalog_percentage?: number | null }, currency?: string): string {
    if (el.custom_percentage != null) return `${el.custom_percentage} % du brut`;
    if (el.custom_amount != null) return formatAmount(Number(el.custom_amount), currency);
    if (el.amount != null) return formatAmount(Number(el.amount), currency);
    if (el.value_type === 'PERCENTAGE' && el.catalog_percentage != null) {
      return `${el.catalog_percentage} % du brut (défaut)`;
    }
    if (el.value_type === 'PERCENTAGE') return '% du brut (défaut config)';
    return 'Montant à configurer';
  }

  /** Bascule l'onglet passé : si déjà actif on replie, sinon on l'affiche. */
  function toggleList(list: Exclude<ActiveList, null>) {
    activeList = activeList === list ? null : list;
  }

  onMount(async () => {
    try {
      isLoading = true;
      allEmployees = await employeesService.getAllForSelect();
    } catch (err) {
      console.error('Failed to load employees in PreparationStep', err);
    } finally {
      isLoading = false;
    }
  });

  // Employés actifs et retenus pour le run
  const activeEmployees = $derived.by(() => {
    const list = allEmployees.filter(e => e.status === 'active' || e.is_active);
    if (selection?.scope === 'employees' && Array.isArray(selection.employee_ids) && selection.employee_ids.length > 0) {
      const set = new Set(selection.employee_ids.map(String));
      return list.filter(e => set.has(String(e.id)));
    }
    return list;
  });

  // Employés exclus (suspendus, inactifs ou hors sélection)
  const excludedEmployees = $derived.by(() => {
    const toExcluded = (e: Employee, reason: string) => ({ emp: e, reason });
    const inactive = allEmployees
      .filter(e => !(e.status === 'active' || e.is_active))
      .map(e => toExcluded(e, e.status === 'suspended' ? 'Contrat suspendu' : 'Employé inactif'));
    if (selection?.scope === 'employees' && Array.isArray(selection.employee_ids)) {
      const set = new Set(selection.employee_ids.map(String));
      const unselectedActive = allEmployees
        .filter(e => (e.status === 'active' || e.is_active) && !set.has(String(e.id)))
        .map(e => toExcluded(e, 'Non sélectionné pour cette paie'));
      return [...inactive, ...unselectedActive];
    }
    return inactive;
  });

  // Répartition par unité organisationnelle (résolue depuis le backend)
  const orgUnitDistribution = $derived.by(() => {
    const dist: Record<string, number> = {};
    const nameById = new Map<string, string>();
    for (const unit of orgUnits) {
      nameById.set(String(unit.id), unit.name);
    }
    for (const emp of activeEmployees) {
      const unit = (emp.orgUnitId != null && nameById.get(String(emp.orgUnitId))) || emp.orgUnit || 'Général';
      dist[unit] = (dist[unit] || 0) + 1;
    }
    return dist;
  });

  // La période est figée une fois le run créé (saisie uniquement au kickoff).
  const periodLabel = $derived(
    run?.period
      || (run?.periodStart && run?.periodEnd ? `${run.periodStart} - ${run.periodEnd}` : '')
      || (payrollStore.currentPeriod ? new Date(payrollStore.currentPeriod + '-01').toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' }) : 'Période en cours')
  );

  /**
   * Éléments de paie réellement appliqués au run.
   * Même règle métier que le backend (get_active_adjustments_for_contract) :
   * is_active ET la période du run tombe dans [start_period, end_period] du contrat.
   */
  function isElementActiveForRun(el: { is_active?: boolean; start_period?: string; end_period?: string | null }): boolean {
    if (!el.is_active) return false;
    const runStart = run?.periodStart;
    const runEnd = run?.periodEnd;
    // Sans période de run connue, on garde uniquement le flag is_active.
    if (!runStart || !runEnd) return true;
    const start = el.start_period ? new Date(el.start_period) : null;
    const end = el.end_period ? new Date(el.end_period) : null;
    const rs = new Date(runStart);
    const re = new Date(runEnd);
    if (start && !Number.isNaN(start.getTime()) && start > re) return false;
    if (end && !Number.isNaN(end.getTime()) && end < rs) return false;
    return true;
  }
</script>


{#snippet EmployeeAvatar(emp: Employee, sizeClass: string)}
  {@const palette = getAvatarPalette(emp.name || '')}
  {@const photo = emp.profile_photo || emp.avatarUrl || null}
  <Avatar class="{sizeClass} rounded-full border border-slate-200">
    {#if photo}
      <AvatarImage src={getMediaUrl(photo)} alt={emp.name} class="object-cover" />
    {/if}
    <AvatarFallback class={cn('font-bold text-[0.72rem]', palette.bg, palette.text)}>
      {getInitials(emp.last_name ?? '', emp.middle_name ?? '', emp.first_name ?? '') || initialsFromName(emp.name)}
    </AvatarFallback>
  </Avatar>
{/snippet}


{#snippet EmployeeRow(emp: Employee, index: number)}
  {@const contract = emp.currentContract}
  {@const hasContract = !!contract}
  {@const currency = contract?.currency}
  {@const payElements = (emp.contractPayElements || []).filter(p => isElementActiveForRun(p))}
  <div
    class="flex flex-col gap-3 border border-r-0 border-l-0 border-slate-100 bg-white rounded-lg px-3.5 py-3 first:border-b-0 last:border-b transition-colors hover:border-slate-200"
    in:fade={{ delay: index * 20 }}
  >
    <div class="flex items-center justify-between gap-3">
      <div class="flex items-center gap-3 min-w-0">
        <div class="relative shrink-0">
          {@render EmployeeAvatar(emp, 'h-9 w-9')}
        </div>
        <div class="flex flex-col min-w-0">
          <span class="text-[0.86rem] text-slate-800 font-semibold truncate">{emp.name}</span>
          <span class="text-[0.8rem] text-slate-500 truncate">{emp.jobTitle || 'Poste non spécifié'}</span>
        </div>
      </div>

      <div class="flex items-center gap-3 shrink-0">
        {#if hasContract}
          <div class="text-right">
            <div class="text-[0.86rem] font-medium uppercase tracking-wide text-slate-400">{salaryKindLabel(contract?.salary_base_type)}</div>
            <div class="text-[0.86rem] text-slate-900 font-bold whitespace-nowrap">
              {formatAmount(contract?.base_salary, currency)}
            </div>
            <div class="text-[0.8rem] text-slate-500">
              {remunerationLabel(contract?.remuneration_type)}
            </div>
          </div>
        {:else}
          <span class="text-[0.86rem] text-slate-400">Sans contrat actif</span>
        {/if}
        <span class="text-[0.86rem] text-slate-600 bg-slate-100 px-2 py-0.5 rounded-full font-semibold">{emp.contractType || '—'}</span>
      </div>
    </div>

    {#if payElements.length > 0}
      <div class="flex items-start gap-2 pt-2 border-t border-slate-50">
        <span class="text-[0.7rem] font-medium uppercase tracking-wide text-slate-400 shrink-0 mt-0.5">
          Éléments actifs
        </span>
        <div class="flex flex-wrap gap-1.5">
          {#each payElements as el}
            <span class="inline-flex items-center gap-1 text-[0.86rem] text-slate-600 bg-slate-50 border border-slate-100 rounded-md px-2 py-1 whitespace-nowrap">
              {el.label}
              <span class="font-semibold text-slate-800 text-[0.86rem]">{formatPayElementValue(el, currency)}</span>
            </span>
          {/each}
        </div>
      </div>
    {/if}
  </div>
{/snippet}


{#snippet OrgUnitBadge(orgUnit: string, count: number)}
  {@const colors = getOrgUnitColor(orgUnit)}
  <span class="inline-flex items-center gap-1.5 px-3 py-1 rounded-full text-[0.86rem] font-medium {colors.bg} {colors.text}">
    <span class="h-2 w-2 rounded-full {colors.dot}"></span>
    {orgUnit} ({count})
  </span>
{/snippet}


<div class="mt-2 space-y-4">
  {#if isLoading}
    <div class="flex items-center justify-center p-12 bg-white rounded-xl border border-slate-100">
      <AnimateSpin text="Chargement des données du personnel" class="text-primary" />
    </div>
  {:else}
    <Card class="border shadow-none">
      <CardHeader class="pb-2">
        <CardTitle class="text-[0.9rem] font-bold flex items-center gap-2 text-slate-800">
          <AppIcon name="calendar" size={18} strokeWidth={1.3} class="text-slate-500" />
          Période de paie
        </CardTitle>
      </CardHeader>
      <CardContent>
        <div class="flex items-center gap-6">
          <div>
            <div class="text-[0.86rem] font-medium text-slate-500 mb-1">
                Période d'exécution
            </div>
            <p class="text-[0.86rem] text-slate-900 font-semibold">{periodLabel}</p>
          </div>
        </div>
      </CardContent>
    </Card>

    <Card class="border shadow-none">
      <CardHeader class="pb-2">
        <div class="flex items-center justify-between">
          <CardTitle class="text-[0.9rem] font-bold flex items-center gap-2 text-slate-800">
            <AppIcon name="users" size={18} strokeWidth={1.3} class="text-slate-500" />
            Analyse des bénéficiaires
          </CardTitle>
          <div class="flex items-center gap-2">
            {#if excludedEmployees.length > 0}
              <button 
                onclick={() => toggleList('excluded')}
                class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-medium transition-colors cursor-pointer {activeList === 'excluded'
                  ? 'border-rose-200 bg-rose-50 text-rose-600'
                  : 'border-slate-200 bg-white text-slate-500 hover:bg-slate-50 hover:text-rose-600'}"
              >
                <AppIcon name="user-minus" size={13} strokeWidth={1.8} />
                {excludedEmployees.length} exclus ce mois
              </button>
            {/if}
            <button 
              onclick={() => toggleList('employees')}
              class="inline-flex items-center gap-1.5 rounded-full border px-3 py-1 text-sm font-medium transition-colors cursor-pointer {activeList === 'employees'
                ? 'border-primary/25 bg-primary/5 text-primary'
                : 'border-slate-200 bg-white text-slate-600 hover:bg-primary/5 hover:text-primary hover:border-primary/25'}"
            >
              <AppIcon name={activeList === 'employees' ? 'eye-off' : 'eye'} size={14} strokeWidth={1.7} />
              {activeList === 'employees' ? 'Masquer les employés' : 'Afficher les employés'}
            </button>
          </div>
        </div>
      </CardHeader>

      <CardContent class="space-y-6">
        <div class="grid grid-cols-1 sm:grid-cols-3 gap-6">
          <div>
            <div class="text-[0.86rem] font-medium text-slate-500">Effectif à payer</div>
            <p class="text-[0.86rem] text-slate-900 font-bold mt-1">
              {activeEmployees.length} employé{activeEmployees.length > 1 ? 's' : ''}
            </p>
          </div>

          <div>
            <div class="text-[0.86rem] font-medium text-slate-500">Mode de sélection</div>
            <p class="text-[0.86rem] text-slate-900 font-semibold mt-1">
              {selection?.scope === 'employees' ? 'Sélection individuelle' : 'Tous les employés actifs'}
            </p>
          </div>

          <div>
            <div class="text-[0.86rem] font-medium text-slate-500">Exclus de ce cycle</div>
            <p class="text-[0.86rem] text-slate-900 font-semibold mt-1">
              {excludedEmployees.length} employé{excludedEmployees.length > 1 ? 's' : ''}
            </p>
          </div>
        </div>

        {#if Object.keys(orgUnitDistribution).length > 0}
          <div class="pt-2">
            <div class="text-[0.86rem] font-medium text-slate-500 mb-2.5 flex items-center gap-2">
              Répartition par unité organisationnelle
              <Separator class="flex-1 opacity-50" />
            </div>
            <div class="flex flex-wrap gap-2">
              {#each Object.entries(orgUnitDistribution) as [orgUnit, count]}
                {@render OrgUnitBadge(orgUnit, count)}
              {/each}
            </div>
          </div>
        {/if}

        {#if activeList === 'excluded' && excludedEmployees.length > 0}
          <div transition:slide class="p-3.5 bg-rose-50/50 border border-rose-100 rounded-lg space-y-2">
            <div class="text-[0.86rem] font-bold text-rose-700 flex items-center gap-2">
              <AppIcon name="user-minus" size={16} /> 
              Collaborateurs non-inclus pour {periodLabel}
            </div>
            {#each excludedEmployees as ex}
              <div class="flex items-center justify-between text-[0.86rem]">
                  <div class="flex items-center gap-2.5 min-w-0">
                    <div class="shrink-0">
                      {@render EmployeeAvatar(ex.emp, 'h-9 w-9')}
                    </div>
                    <div class="flex flex-col min-w-0">
                        <span class="text-slate-700 font-medium text-[0.86rem] truncate">{ex.emp.name}</span>
                        <span class="text-[0.72rem] text-slate-400 truncate">{ex.emp.jobTitle || 'Poste non spécifié'}</span>
                    </div>
                  </div>
                <span class="text-rose-600 font-medium text-[0.86rem]">{ex.reason}</span>
              </div>
            {/each}
          </div>
        {/if}

        {#if activeList === 'employees'}
          <div transition:slide={{ duration: 300 }} class="pt-4 border-t border-slate-100">
            {#each activeEmployees as emp, i}
              {@render EmployeeRow(emp, i)}
            {/each}
          </div>
        {/if}
      </CardContent>
    </Card>
  {/if}
</div>
