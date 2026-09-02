<script lang="ts">
  import { onMount } from "svelte";
  import { payrollStore } from "@/features/payroll/stores/payroll.svelte";
  import { payrollRunStore } from "@/features/payroll/stores/runs/payrollRunStore.svelte";
  import { updatePayrollRun, type PayrollRunUpdatePayload } from "@/features/payroll/queries/payroll";
  import { notification } from "@/stores/notification.svelte";
  import { orgService } from "@/features/jobs/services/org.service";
  import { employeesService } from "@/features/employees/services/employees.service";

  import PeriodSection from "../kickoff/PeriodSection.svelte";
  import ExchangeRateSection from "../kickoff/ExchangeRateSection.svelte";
  import EmployeesSection from "../kickoff/EmployeesSection.svelte";
  import type { KickOffEmployee } from "../kickoff/EmployeesSection.svelte";


  interface Props {
    onCreated?: () => void;
    submitForm?: (() => void) | undefined;
    canSubmit?: boolean;
    isCreating?: boolean;
  }

  let { 
    onCreated,
    submitForm = $bindable(undefined),
    canSubmit = $bindable(false),
    isCreating = $bindable(false)
  }: Props = $props();

  $effect(() => {
    submitForm = handleSubmit;
  });

  $effect(() => {
    canSubmit = !!(isValid && rateReady && !isCreating);
  });

  const run = payrollRunStore.currentRun;
  const initialSelection = run?.selection;

  // ─── Période ───
  let periodStart = $state(run?.periodStart ?? (run as any)?.start_date ?? '');
  let periodEnd = $state(run?.periodEnd ?? (run as any)?.end_date ?? '');

  // ─── Taux de change ───
  let rateSource: 'auto' | 'manual' = $state<'auto' | 'manual'>(
    run?.exchangeRate ? 'manual' : 'auto'
  );
  let manualRate = $state(run?.exchangeRate ?? 2850);

  // ─── Sélection employés ───
  let includeAllEmployees = $state(
    initialSelection ? initialSelection.scope !== 'employees' : true
  );
  let selectedEmployeeIds: string[] = $state(
    initialSelection?.scope === 'employees' ? [...(initialSelection.employee_ids ?? [])] : []
  );
  let orgUnits = $state<Array<{ id: string; name: string; type: string }>>([]);
  let selectedOrgUnitIds: string[] = $state([]);
  let isLoadingOrgUnits = $state(true);
  let employees = $state<KickOffEmployee[]>([]);
  let isLoadingEmployees = $state(false);
  let employeeSearch = $state('');

  /** Vrai si on édite un run déjà créé (DRAFT) — on patche au lieu de créer. */
  let isEditingExisting = $derived(
    !!payrollRunStore.currentRun && payrollRunStore.currentRun.status === 'draft'
  );

  // Taux de change résolu envoyé au backend : auto (BCC) si disponible, sinon manuel
  const resolvedRate = $derived.by(() => {
    if (rateSource === 'auto') {
      const bccRate = Number(payrollStore.exchangeRateInfo?.rate);
      return Number.isFinite(bccRate) && bccRate > 0 ? bccRate : null;
    }
    return Number(manualRate) > 0 ? Number(manualRate) : null;
  });
  // Le bouton "Lancer" est désactivé tant que le taux auto (BCC) n'est pas chargé
  const rateReady = $derived((rateSource === 'manual' && resolvedRate !== null) || (rateSource === 'auto' && resolvedRate !== null));

  const isValid = $derived(periodStart && periodEnd && periodStart < periodEnd);

  // Charger les unités organisationnelles (toutes, pas seulement les départements)
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
        notification.toast.error(err?.message ?? 'Échec du chargement des unités organisationnelles');
      })
      .finally(() => {
        if (!cancelled) isLoadingOrgUnits = false;
      });
    return () => { cancelled = true; };
  });

  // Charger les employés actifs (toujours affichés dans la liste)
  $effect(() => {
    let cancelled = false;
    isLoadingEmployees = true;
    employeesService.getAllForSelect({ status: ['active'] })
      .then((res) => {
        if (cancelled) return;
        employees.splice(0, employees.length, ...res.map(e => ({
          id: String(e.id),
          name: e.name,
          jobTitle: e.jobTitle || '',
          orgUnit: e.orgUnit || '',
          contractType: e.contractType || '',
          location: e.location || '',
          joinDate: e.joinDate || '',
          status: e.current_status?.status || e.status || '',
          first_name: e.first_name || '',
          middle_name: e.middle_name || null,
          last_name: e.last_name || '',
          photo: e.profile_photo || e.avatarUrl || null,
        })));
      })
      .catch((err) => {
        if (cancelled) return;
        notification.toast.error(err?.message ?? 'Échec du chargement des employés');
      })
      .finally(() => {
        if (!cancelled) isLoadingEmployees = false;
      });
    return () => { cancelled = true; };
  });

  // Charger le taux de change USD → CDF (BCC) au montage si pas déjà chargé.
  // Sans cet appel, exchangeRateInfo reste null et le bouton « Lancer » est
  // désactivé indéfiniment (rateReady = false).
  $effect(() => {
    if (payrollStore.exchangeRateInfo) return;
    payrollStore.refreshExchangeRate();
  });

  // ─── Hydratation depuis le backend (source de vérité) ───
  // Une seule fois au mount (onMount) pour éviter les boucles d'effets réactifs.
  onMount(() => {
    if (!payrollRunStore.currentRun) return; // Pas de run → mode création.
    const runId = payrollRunStore.currentRun.id;

    payrollStore.refreshPayrollRun(runId)
      .then((fresh) => {
        if (!fresh) return;

        // Période — on accepte `periodStart`/`periodEnd` ou fallback sur start/end_date
        periodStart = (fresh as any).periodStart ?? (fresh as any).start_date ?? periodStart;
        periodEnd   = (fresh as any).periodEnd   ?? (fresh as any).end_date   ?? periodEnd;

        // Taux de change
        const exRate = (fresh as any).exchangeRate ?? (fresh as any).exchange_rate_applied;
        if (exRate && Number(exRate) > 0) {
          manualRate = Number(exRate);
          rateSource = 'manual';
        }

        // Sélection employés
        const sel = (fresh as any).selection;
        if (sel) {
          if (sel.scope === 'employees') {
            includeAllEmployees = false;
            selectedEmployeeIds = [...(sel.employee_ids ?? [])];
            selectedOrgUnitIds = [];
          } else {
            // 'all' ou legacy 'org_units'
            includeAllEmployees = true;
            selectedEmployeeIds = [];
            selectedOrgUnitIds = [];
          }
        }
      })
      .catch((err: any) => {
        notification.toast.error(err?.message ?? 'Échec du chargement de l\'exécution');
      });
  });

  // ─── Interactions sélection ───
  function toggleOrgUnit(unitId: string) {
    if (selectedOrgUnitIds.includes(unitId)) {
      selectedOrgUnitIds = selectedOrgUnitIds.filter(u => u !== unitId);
    } else {
      // Sélectionner une unité sort du mode « Tous »
      includeAllEmployees = false;
      selectedOrgUnitIds = [...selectedOrgUnitIds, unitId];
    }
  }

  function clearOrgUnits() {
    selectedOrgUnitIds = [];
  }

  function handleIncludeAllChange(all: boolean) {
    includeAllEmployees = all;
    // Quand on revient à « Tous », on nettoie les sélections précédentes.
    if (all) {
      selectedOrgUnitIds = [];
      selectedEmployeeIds = [];
    }
  }

  function toggleEmployee(id: string) {
    if (selectedEmployeeIds.includes(id)) {
      selectedEmployeeIds = selectedEmployeeIds.filter(e => e !== id);
    } else {
      // Sélectionner un employé sort du mode « Tous »
      includeAllEmployees = false;
      selectedEmployeeIds = [...selectedEmployeeIds, id];
    }
  }

  // ─── Création / mise à jour du run ───
  function handleSubmit() {
    if (!periodStart || !periodEnd) return;
    if (isEditingExisting) {
      updateRun();
    } else {
      createRun();
    }
  }

  /**
   * Construit le payload de sélection à partir de l'état local.
   * Binaire : « Tous » (scope=all, pas d'IDs) ou « Individuel »
   * (scope=employees, IDs cochés). Le filtre par unité dans
   * EmployeesSection n'est qu'un filtre visuel de la liste — l'action
   * de cocher un employé pousse l'ID dans `selectedEmployeeIds`, ce qui
   * bascule automatiquement en scope=employees.
   */
  function buildSelection() {
    return includeAllEmployees
      ? { scope: 'all' as const }
      : { scope: 'employees' as const, employee_ids: selectedEmployeeIds };
  }

  async function createRun() {
    if (!periodStart || !periodEnd) return;
    isCreating = true;
    try {
      const selection = buildSelection();
      await payrollStore.createPayrollRunFromDates(periodStart, periodEnd, resolvedRate ?? null, selection ?? { scope: 'all' });
      notification.toast.success('Exécution de paie créée');
      onCreated?.();
    } catch (err: any) {
      notification.toast.error(err?.message ?? 'Échec de la création de l\'exécution');
    } finally {
      isCreating = false;
    }
  }

  /** PATCH le run DRAFT existant avec la sélection mise à jour. Le backend
   *  fait un merge partiel (seuls les champs présents dans params_snapshot sont touchés). */
  async function updateRun() {
    const run = payrollRunStore.currentRun;
    if (!run) return;
    isCreating = true;
    try {
      const selection = buildSelection();
      const patch: PayrollRunUpdatePayload = {
        start_date: periodStart,
        end_date: periodEnd,
        params_snapshot: { selection },
      };
      await updatePayrollRun(run.id, patch);
      await payrollStore.refreshPayrollRun(run.id);
      notification.toast.success('Sélection mise à jour');
      onCreated?.();
    } catch (err: any) {
      notification.toast.error(err?.message ?? 'Échec de la mise à jour de l\'exécution');
    } finally {
      isCreating = false;
    }
  }
</script>


<form onsubmit={(e) => { e.preventDefault(); handleSubmit(); }} class="space-y-6">
  <PeriodSection
    {periodStart}
    {periodEnd}
    onPeriodStartChange={(v) => periodStart = v}
    onPeriodEndChange={(v) => periodEnd = v}
  />

  <ExchangeRateSection
    {rateSource}
    {manualRate}
    exchangeRateInfo={payrollStore.exchangeRateInfo}
    onRateSourceChange={(s: 'auto' | 'manual') => rateSource = s}
    onManualRateChange={(v: number) => manualRate = v}
    onRefresh={() => payrollStore.refreshExchangeRate(true)}
  />

  <EmployeesSection
    {employees}
    {isLoadingEmployees}
    {orgUnits}
    {isLoadingOrgUnits}
    {includeAllEmployees}
    {selectedEmployeeIds}
    {selectedOrgUnitIds}
    {employeeSearch}
    onIncludeAllChange={handleIncludeAllChange}
    onToggleEmployee={toggleEmployee}
    onToggleOrgUnit={toggleOrgUnit}
    onClearOrgUnits={clearOrgUnits}
    onSearchChange={(v: string) => employeeSearch = v}
  />

  {@render Footer()}

</form>


{#snippet Footer()}
  <div class="flex items-center justify-between gap-2.5 pt-1 text-[0.86rem] text-slate-500">
    {#if includeAllEmployees}
      Tous les employés actifs seront inclus
    {:else if selectedOrgUnitIds.length > 0 && selectedEmployeeIds.length === 0}
      {selectedOrgUnitIds.length} unité{selectedOrgUnitIds.length > 1 ? 's' : ''} sélectionnée{selectedOrgUnitIds.length > 1 ? 's' : ''}
    {:else if selectedEmployeeIds.length > 0}
      {selectedEmployeeIds.length} employé{selectedEmployeeIds.length > 1 ? 's' : ''} sélectionné{selectedEmployeeIds.length > 1 ? 's' : ''}
    {:else}
      Aucun employé sélectionné
    {/if}
  </div>
{/snippet}

