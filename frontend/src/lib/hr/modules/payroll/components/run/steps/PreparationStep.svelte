<script lang="ts">
  import { onMount } from "svelte";
  import { payrollStore } from "@/hr/modules/payroll/stores/payroll.svelte";
  import { payrollRunStore } from "@/hr/modules/payroll/stores/runs/payrollRunStore.svelte";
  import { employeesService } from "@/hr/modules/employees/services/employees.service";
  import { fetchRunPresence, type EmployeePresence } from "@/hr/modules/payroll/queries/payroll";
  import { orgService } from "@/hr/modules/jobs/services/org.service";
  import type { Employee } from "@/hr/modules/employees/types/types";
  import AppIcon from "@/hr/components/layout/elements/AppIcon.svelte";
  import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
  import { Separator } from "@/components/ui/separator";
  import { slide, fade } from "svelte/transition";
  import AnimateSpin from "@/hr/components/layout/elements/AnimateSpin.svelte";
  import { cn } from "@/hr/utilities/common/css";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/hr/utilities/common/string";
  import { getAvatarPalette } from "@/hr/utilities/common/func";
  import { getMediaUrl } from "@/hr/utilities/common/media";
  import { getOrgUnitColor } from "@/hr/modules/payroll/constants/orgUnitColors.constants";


  // Liste visible (onglet actif). Mutuellement exclusive : un seul panneau à la
  // fois, re-cliquer sur l'onglet actif replie tout.
  type ActiveList = 'employees' | 'excluded' | null;
  let activeList = $state<ActiveList>('employees');
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

  // Employés actifs et retenus pour le run.
  // Éligibilité : être actif ET avoir un contrat courant qui CHEVAUCHE la période
  // du run — même règle que le moteur (contract_active_on_period). Un employé
  // dont le contrat ne couvre pas la période n'est JAMAIS compté dans « à payer »
  // (il apparaît dans les exclus). Cohérent avec EmployeesSection (kickoff).
  function isActiveEmployee(e: Employee): boolean {
    return e.status === 'active' || !!e.is_active;
  }
  function isEligibleForRun(e: Employee): boolean {
    const rs = run?.periodStart?.slice(0, 10);
    const re = run?.periodEnd?.slice(0, 10);
    // Sans période de run connue, on ne bloque rien (rétro-compat).
    if (!rs || !re) return true;
    const cs = e.currentContract?.start_date?.slice(0, 10) ?? null;
    if (!cs) return false;
    const ce = e.currentContract?.end_date?.slice(0, 10) ?? null;
    return cs <= re && (ce === null || ce >= rs);
  }

  const eligibleEmployees = $derived(
    allEmployees.filter(e => isActiveEmployee(e) && isEligibleForRun(e))
  );

  // Effectif à payer : employés éligibles retenus par la sélection.
  const activeEmployees = $derived.by(() => {
    if (selection?.scope === 'employees' && Array.isArray(selection.employee_ids) && selection.employee_ids.length > 0) {
      const set = new Set(selection.employee_ids.map(String));
      return eligibleEmployees.filter(e => set.has(String(e.id)));
    }
    return eligibleEmployees;
  });

  // Employés exclus (inactifs, contrat hors période, ou non sélectionnés)
  const excludedEmployees = $derived.by(() => {
    const toExcluded = (e: Employee, reason: string) => ({ emp: e, reason });
    const paidIds = new Set(activeEmployees.map(e => String(e.id)));
    const excluded: { emp: Employee; reason: string }[] = [];
    for (const e of allEmployees) {
      if (paidIds.has(String(e.id))) continue;
      if (!isActiveEmployee(e)) {
        excluded.push(toExcluded(e, e.status === 'suspended' ? 'Contrat suspendu' : 'Employé inactif'));
      } else if (!isEligibleForRun(e)) {
        excluded.push(toExcluded(e, e.currentContract?.start_date ? 'Contrat hors de la période de paie' : 'Aucun contrat actif'));
      } else if (selection?.scope === 'employees') {
        excluded.push(toExcluded(e, 'Non sélectionné pour cette paie'));
      }
    }
    return excluded;
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

  // ─── Présence & absences (aperçu avant calcul) ───
  // Source : endpoint /payroll/runs/{id}/presence/ qui reproduit la logique de
  // l'orchestrateur (seules les présences finalisées sont comptées). Lecture
  // seule — la finalisation se fait côté présence, pas ici.
  let presenceMap = $state<Record<string, EmployeePresence>>({});
  let presenceLoading = $state(false);
  let presenceError = $state('');

  $effect(() => {
    const rid = run?.id;
    const rs = run?.periodStart?.slice(0, 10);
    const re = run?.periodEnd?.slice(0, 10);
    if (!rid || !rs || !re) {
      presenceMap = {};
      presenceLoading = false;
      presenceError = '';
      return;
    }
    let cancelled = false;
    presenceLoading = true;
    presenceError = '';
    fetchRunPresence(String(rid))
      .then((data) => {
        if (cancelled) return;
        const map: Record<string, EmployeePresence> = {};
        for (const entry of data.employees || []) {
          map[String(entry.employee_id)] = entry;
        }
        presenceMap = map;
      })
      .catch(() => {
        if (cancelled) return;
        presenceError = 'Impossible de charger la présence pour cette période.';
      })
      .finally(() => {
        if (!cancelled) presenceLoading = false;
      });
    return () => { cancelled = true; };
  });

  const presenceOf = (e: Employee): EmployeePresence | undefined => presenceMap[String(e.id)];

  /** Jours de présence non finalisés agrégés sur les employés retenus. */
  const unfinalizedTotal = $derived(
    activeEmployees.reduce((acc, e) => acc + (presenceOf(e)?.unfinalized_days || 0), 0)
  );
  const presenceEmployees = $derived(
    activeEmployees.filter((e) => (presenceOf(e)?.unfinalized_days || 0) > 0)
  );

  function fmtDays(v: number | undefined): string {
    const n = Number(v ?? 0);
    return n > 0 ? String(n) : '0';
  }
  function fmtHours(v: number | undefined): string {
    const n = Number(v ?? 0);
    return n > 0 ? n.toLocaleString('fr-FR', { maximumFractionDigits: 1 }) : '0';
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
        <div class="flex items-center justify-between gap-3">
          <CardTitle class="text-[0.9rem] font-bold flex items-center gap-2 text-slate-800">
            <AppIcon name="activity" size={18} strokeWidth={1.4} class="text-slate-500" />
            Présence &amp; absences
          </CardTitle>
          <div class="flex items-center gap-2">
            {#if presenceLoading}
              <AnimateSpin text="Chargement…" class="text-primary" textPosition="right" />
            {:else if presenceEmployees.length > 0}
              <span class="inline-flex items-center gap-1.5 rounded-full border border-amber-200 bg-amber-50 px-3 py-1 text-sm font-semibold text-amber-700">
                <AppIcon name="alert-triangle" size={13} strokeWidth={2} />
                {unfinalizedTotal} jour{unfinalizedTotal > 1 ? 's' : ''} à finaliser
              </span>
            {:else}
              <span class="inline-flex items-center gap-1.5 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-sm font-semibold text-emerald-700">
                <AppIcon name="check" size={13} strokeWidth={2} />
                Présence à jour
              </span>
            {/if}
          </div>
        </div>
      </CardHeader>
      <CardContent>
        <p class="text-sm text-slate-500 mb-4 leading-snug">
          Lecture seule — récapitulatif de la présence par employé pour {periodLabel}. Seuls les
          registres <span class="font-semibold text-slate-700">finalisés</span> sont pris en compte
          (c'est exactement la source utilisée par le calcul de la paie). La finalisation se fait
          depuis l'écran de présence.
        </p>

        {#if presenceEmployees.length > 0}
          <div class="mb-4 rounded-lg border border-amber-200 bg-amber-50/60 px-3.5 py-3">
            <div class="flex items-start gap-2.5">
              <AppIcon name="alert-triangle" size={17} strokeWidth={2} class="mt-0.5 shrink-0 text-amber-500" />
              <p class="text-sm leading-snug text-amber-800">
                {presenceEmployees.length} employé{presenceEmployees.length > 1 ? 's' : ''} a{presenceEmployees.length > 1 ? 'ont' : ''} {unfinalizedTotal}
                jour{unfinalizedTotal > 1 ? 's' : ''} de présence <b>non finalisé{unfinalizedTotal > 1 ? 's' : ''}</b> sur la période.
                Ces jours ne seront comptés ni comme travaillés ni comme absents au moment du calcul. Pour un
                bulletin exact, finalisez la présence avant de lancer la paie.
              </p>
            </div>
          </div>
        {/if}

        {#if presenceError}
          <div class="mb-4 flex items-center gap-2 rounded-lg border border-rose-200 bg-rose-50/60 px-3.5 py-2.5 text-sm text-rose-700">
            <AppIcon name="circle-x" size={16} class="shrink-0" /> {presenceError}
          </div>
        {/if}

        {#if presenceLoading}
          <div class="flex items-center justify-center py-8">
            <AnimateSpin text="Chargement de la présence" class="text-primary" textPosition="right" />
          </div>
        {:else if activeEmployees.length > 0}
          <div class="overflow-x-auto">
            <table class="w-full border-separate border-spacing-0 text-sm">
              <thead>
                <tr class="text-left">
                  <th class="min-w-55 py-2 pr-3 text-[0.78rem] font-semibold uppercase tracking-wide text-slate-500">Employé</th>
                  <th class="px-2 py-2 text-right text-[0.78rem] font-semibold uppercase tracking-wide text-slate-500">Jours travaillés</th>
                  <th class="px-2 py-2 text-right text-[0.78rem] font-semibold uppercase tracking-wide text-slate-500">Absences</th>
                  <th class="px-2 py-2 text-right text-[0.78rem] font-semibold uppercase tracking-wide text-slate-500">Heures sup.</th>
                  <th class="px-2 py-2 text-right text-[0.78rem] font-semibold uppercase tracking-wide text-slate-500">Heures fériées</th>
                  <th class="px-2 py-2 text-right text-[0.78rem] font-semibold uppercase tracking-wide text-slate-500">Congés payés</th>
                  <th class="px-2 py-2 text-right text-[0.78rem] font-semibold uppercase tracking-wide text-slate-500">Congés non payés</th>
                  <th class="py-2 pl-3 text-right text-[0.78rem] font-semibold uppercase tracking-wide text-slate-500">Statut présence</th>
                </tr>
              </thead>
              <tbody>
                {#each activeEmployees as emp}
                  {@const p = presenceOf(emp)}
                  <tr class="border-t border-slate-100">
                    <td class="py-2.5 pr-3">
                      <div class="flex items-center gap-2.5">
                        {@render EmployeeAvatar(emp, 'h-8 w-8')}
                        <div class="flex min-w-0 flex-col">
                          <span class="truncate text-sm font-semibold text-slate-800">{emp.name}</span>
                          <span class="truncate text-[0.85rem] text-slate-500">{emp.jobTitle || 'Poste non spécifié'}</span>
                        </div>
                      </div>
                    </td>
                    <td class="px-2 py-2.5 text-right font-medium text-slate-700 text-sm">{p ? fmtDays(p.worked_days) : '—'}</td>
                    <td class="px-2 py-2.5 text-right font-medium text-slate-700 text-sm">{p ? fmtDays(p.absence_days) : '—'}</td>
                    <td class="px-2 py-2.5 text-right font-medium text-slate-700 text-sm">{p ? fmtHours(p.overtime_hours_standard) : '—'}</td>
                    <td class="px-2 py-2.5 text-right font-medium text-slate-700 text-sm">{p ? fmtHours(p.overtime_hours_holiday) : '—'}</td>
                    <td class="px-2 py-2.5 text-right font-medium text-slate-700 text-sm">{p ? fmtDays(p.paid_leave_days) : '—'}</td>
                    <td class="px-2 py-2.5 text-right font-medium text-slate-700 text-sm">{p ? fmtDays(p.unpaid_leave_days) : '—'}</td>
                    <td class="py-2.5 pl-3 text-right">
                      {#if p && p.unfinalized_days > 0}
                        <span class="inline-flex items-center gap-1 whitespace-nowrap rounded-full border border-amber-200 bg-amber-50 px-2 py-0.5 text-xs font-semibold text-amber-700">
                          <AppIcon name="clock" size={15} strokeWidth={2} /> {p.unfinalized_days} j à finaliser
                        </span>
                      {:else if p && p.has_attendance}
                        <span class="whitespace-nowrap font-semibold text-emerald-600 text-sm">Présence OK</span>
                      {:else if p}
                        <span class="whitespace-nowrap text-slate-500 text-sm">Aucun pointage</span>
                      {:else}
                        <span class="whitespace-nowrap text-slate-400">—</span>
                      {/if}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
        {:else}
          <p class="py-4 text-center text-sm text-slate-500">Aucun employé à payer sur cette période.</p>
        {/if}
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
