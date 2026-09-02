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
  <div class="flex items-center justify-between border-b border-slate-100 pb-2.5 last:border-0" in:fade={{ delay: index * 20 }}>
    <div class="flex items-center gap-3">
      <div class="relative shrink-0">
        {@render EmployeeAvatar(emp, 'h-9 w-9')}
      </div>
      <div class="flex flex-col">
      <span class="text-[0.86rem] text-slate-800 font-medium">{emp.name}</span>
      <span class="text-[0.86rem] text-slate-500">{emp.jobTitle || emp.positionId ? 'Poste défini' : 'Poste non spécifié'}</span>
    </div>
  </div>
    <div class="flex items-center gap-3">
       <span class="text-[0.86rem] text-slate-600 bg-slate-100 px-2.5 py-0.5 rounded-full font-medium">{emp.contractType || '—'}</span>
    </div>
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
              Répartition par départements
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
