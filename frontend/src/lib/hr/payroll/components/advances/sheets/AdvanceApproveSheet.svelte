<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { cn } from "@/utilities/common/css";
  import { Button } from "@/components/ui/button";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { employeesService } from "@/hr/employees/services/employees.service";
  import { payrollStore } from "../../../stores/payroll.svelte";
  import type { Advance, AdvanceDeductionBase, AdvanceDeductionWindow, AdvanceTaxTiming } from "../../../types/types";
  import { Label } from "@/components/ui/label";
  import { Input } from "@/components/ui/input";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import ValidationError from "@/components/ui/validation-error";

  
  let {
    advance = null as Advance | null,
    open = $bindable(false),
    onApproved
  }: {
    advance: Advance | null;
    open: boolean;
    onApproved?: (advance: Advance) => void;
  } = $props();

  // ── Configuration de déduction saisie par la RH à l'approbation ──
  let repaymentPercentage = $state(20);
  let deductionBase = $state<AdvanceDeductionBase>('NET');
  let taxTiming = $state<AdvanceTaxTiming>('AFTER_TAX');
  let deductionWindow = $state<AdvanceDeductionWindow>('ALL_MONTHS');
  let deductionStart = $state('');
  let deductionEnd = $state('');
  let priorityOrder = $state(1);
  let isSavingConfig = $state(false);

  // ── Plan de remboursement (estimation sur le net contractuel) ──
  // Deux unités : étaler sur un nombre de mois OU fixer un % mensuel. On
  // estime toujours l'autre (option A) à partir du net contractuel de l'employé.
  let planMode = $state<'percent' | 'months'>('percent');
  let planMonths = $state(3);
  // Mois de début (YYYY-MM) ; vide = dès le prochain cycle.
  let planStartMonth = $state('');
  let referenceSalary = $state(0);
  let referenceCurrency = $state('CDF');

  // Récupère le net contractuel de l'employé (base de référence de l'estimation).
  $effect(() => {
    const empId = advance?.employee?.id;
    if (!empId) {
      referenceSalary = 0;
      referenceCurrency = 'CDF';
      return;
    }
    let cancelled = false;
    employeesService.getEmployeeDetail(String(empId))
      .then((profile: any) => {
        if (cancelled) return;
        const c = profile?.current_contract;
        const contract = c && c.is_active ? c : null;
        referenceSalary = contract
          ? Number(contract.remuneration_type === 'HOURLY' ? (contract.hourly_rate ?? 0) : (contract.base_salary ?? 0))
          : 0;
        referenceCurrency = contract?.currency || 'CDF';
      })
      .catch(() => { if (!cancelled) referenceSalary = 0; });
    return () => { cancelled = true; };
  });

  // Montant principal de l'avance (en unités numériques, devise du contrat supposée).
  const advanceAmount = $derived(Number(advance?.amount ?? 0));

  function clampPct(v: number): number {
    if (!Number.isFinite(v)) return 1;
    return Math.min(100, Math.max(1, v));
  }

  /** Nombre de mois estimés pour un % donné : ceil(montant / (net × %/100)). */
  function monthsForPercent(pct: number): number | null {
    if (pct <= 0 || referenceSalary <= 0) return null;
    const monthly = referenceSalary * (pct / 100);
    if (monthly <= 0) return null;
    return Math.max(1, Math.ceil(advanceAmount / monthly));
  }

  /** % mensuel nécessaire pour rembourser sur `months` mois. */
  function percentForMonths(months: number): number | null {
    if (!months || months <= 0 || referenceSalary <= 0) return null;
    return clampPct((advanceAmount / (referenceSalary * months)) * 100);
  }

  // L'affiché est dérivé du mode actif (pas circulaire).
  const estimatedMonths = $derived(
    planMode === 'percent' ? monthsForPercent(repaymentPercentage) : planMonths
  );
  const shownPercent = $derived.by(() => {
    if (planMode === 'months') {
      const p = percentForMonths(planMonths);
      return p != null ? Math.round(p * 100) / 100 : null;
    }
    return repaymentPercentage;
  });

  // Mensualité estimée (~) pour l'aperçu.
  const estimatedMonthly = $derived.by(() => {
    if (referenceSalary <= 0 || advanceAmount <= 0) return null;
    if (planMode === 'months' && planMonths > 0) return advanceAmount / planMonths;
    const pct = shownPercent;
    if (pct == null) return null;
    return referenceSalary * (pct / 100);
  });

  // Synchronise le % effectif (ce que le moteur utilisera) selon le mode.
  function applyMonthsMode() {
    const m = Math.max(1, Math.floor(planMonths || 1));
    planMonths = m;
    const p = percentForMonths(m);
    if (p != null) repaymentPercentage = p;
  }
  function switchToMonths() {
    const est = monthsForPercent(repaymentPercentage);
    planMonths = est ?? planMonths;
    planMode = 'months';
    applyMonthsMode();
  }
  function switchToPercent() {
    const p = percentForMonths(planMonths);
    if (p != null) repaymentPercentage = p;
    planMode = 'percent';
  }

  /** Ajoute `months` mois à une date ISO (YYYY-MM-DD) et renvoie YYYY-MM-DD. */
  function addMonths(iso: string, months: number): string {
    const [y, m] = iso.slice(0, 7).split('-').map(Number);
    if (!y || !m) return iso;
    const d = new Date(y, m - 1 + months, 1);
    return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, '0')}-01`;
  }

  // Plafond de durée raisonnable pour une avance sur salaire.
  const MAX_MONTHS = 24;
  // Libellé de la référence selon la base de déduction choisie.
  const referenceLabel = $derived(deductionBase === 'GROSS' ? 'Salaire brut contractuel' : 'Net contractuel');

  // Règle de cohérence : signale un plan trop long / impossible.
  const planWarning = $derived.by(() => {
    if (advanceAmount <= 0 || referenceSalary <= 0) return null;
    if (planMode === 'percent') {
      const m = estimatedMonths;
      if (m != null && m > MAX_MONTHS) {
        return `Ce plan s'étale sur environ ${m} mois (au-delà du plafond de ${MAX_MONTHS}). Envisagez un pourcentage plus élevé ou vérifiez le montant.`;
      }
      return null;
    }
    const p = percentForMonths(planMonths);
    if (p == null) {
      return `Impossible : même à 100 %/mois, le montant ne peut pas être remboursé en ${planMonths} mois sur la base actuelle.`;
    }
    return null;
  });

  // Erreurs bloquantes : interdisent l'approbation tant qu'elles ne sont pas
  // résolues (ex. pourcentage à 0, nombre de mois invalide, plan irréalisable).
  const configErrors = $derived.by(() => {
    const err: Record<string, string> = {};
    const pct = Number(repaymentPercentage) || 0;
    if (planMode === 'percent') {
      if (pct < 1 || pct > 100) err.percent = 'Le pourcentage doit être compris entre 1 et 100 %.';
    } else {
      const m = Math.floor(Number(planMonths) || 0);
      if (m < 1) {
        err.months = 'Le nombre de mois doit être d’au moins 1.';
      } else if (percentForMonths(m) == null) {
        err.months = 'Impossible : le montant ne peut pas être remboursé dans ce délai, même à 100 %. Rallongez la durée.';
      }
    }
    if (!(advanceAmount > 0)) err.global = 'Montant de l’avance invalide.';
    return err;
  });
  const canApprove = $derived(Object.keys(configErrors).length === 0);

  // Initialiser depuis l'avance quand elle change
  $effect(() => {
    if (advance) {
      repaymentPercentage = advance.repayment_percentage ?? 20;
      deductionBase = (advance.salary_base_for_deduction as AdvanceDeductionBase) ?? 'NET';
      taxTiming = (advance.tax_timing as AdvanceTaxTiming) ?? 'AFTER_TAX';
      deductionWindow = (advance.deduction_window as AdvanceDeductionWindow) ?? 'ALL_MONTHS';
      deductionStart = advance.deduction_start_date ?? '';
      deductionEnd = advance.deduction_end_date ?? '';
    }
  });

  function formatAmount(v: number): string {
    return v.toLocaleString('fr-FR', { maximumFractionDigits: 0 });
  }

  async function handleApprove() {
    if (!advance) return;
    if (!canApprove) {
      notification.toast.error('Configuration de remboursement invalide. Corrigez les erreurs avant d\'approuver.');
      return;
    }
    isSavingConfig = true;
    try {
      // En mode « mois », s'assurer que le % envoyé au moteur est cohérent.
      if (planMode === 'months') applyMonthsMode();

      // Fenêtre de déduction : si un mois de début est choisi, on ouvre une
      // période (début → fin estimée selon la durée) ; sinon « tous les mois ».
      let window: AdvanceDeductionWindow = deductionWindow;
      let start = deductionStart;
      let end = deductionEnd;
      if (planStartMonth) {
        const dur = Math.max(1, (planMode === 'months' ? planMonths : estimatedMonths) || planMonths || 1);
        window = 'CUSTOM_PERIOD';
        start = planStartMonth + '-01';
        end = addMonths(start, dur);
      } else {
        window = 'ALL_MONTHS';
        start = '';
        end = '';
      }

      // 1. Enregistrer la configuration de déduction via la route dédiée
      const configPayload = {
        repayment_percentage: repaymentPercentage,
        salary_base_for_deduction: deductionBase,
        tax_timing: taxTiming,
        deduction_window: window,
        ...(window === 'CUSTOM_PERIOD' ? { deduction_start_date: start, deduction_end_date: end } : {}),
        priority_order: priorityOrder,
        is_active: true,
      };

      // 1. Approuver (PENDING → APPROVED).
      const updated = await payrollStore.approveAdvance(advance.id);
      // 2. Enregistrer la config APRÈS l'approbation : l'avance étant APPROVED,
      //    le backend la bascule automatiquement en ACTIVE (déductible).
      await payrollStore.updateAdvanceConfig(advance.id, configPayload);

      notification.toast.success("Demande d'avance approuvée");
      onApproved?.(updated ?? advance);
      open = false;
    } catch {
      notification.toast.error("Erreur lors de l'approbation de l'avance");
    } finally {
      isSavingConfig = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl p-0 overflow-hidden flex flex-col bg-white h-full">
    {#if advance}
      <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/60 flex flex-row items-center justify-between">
        <Sheet.Title class="text-base font-bold text-slate-900 text-left">
          Approuver l'avance
        </Sheet.Title>
      </Sheet.Header>

      <div class="flex-1 overflow-y-auto p-6 space-y-6 custom-scrollbar">
        <!-- Récapitulatif -->
        <div class="space-y-1.5">
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-slate-500 uppercase tracking-wider">Montant</span>
            <span class="text-[0.95rem] font-medium text-slate-900">{formatAmount(advance.amount)} {advance.currency || 'CDF'}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-slate-500 uppercase tracking-wider">Employé</span>
            <span class="text-sm font-semibold text-slate-900">{advance.employee_name}</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-slate-500 uppercase tracking-wider">Prélèvement proposé</span>
            <span class="text-sm font-semibold text-slate-800">{advance.repayment_percentage}% / mois</span>
          </div>
          <div class="flex items-center justify-between">
            <span class="text-sm font-medium text-slate-500 uppercase tracking-wider">Date de demande</span>
            <span class="text-sm font-semibold text-slate-800">{new Date(advance.requested_date).toLocaleDateString('fr-FR')}</span>
          </div>
        </div>

        <!-- Configuration de la déduction (saisie RH à l'approbation) -->
        <div class="space-y-3 mt-4">
          <div class="flex items-center gap-2">
            <AppIcon name="settings" size={15} class="text-slate-500" />
            <h4 class="text-sm font-bold text-slate-700 uppercase tracking-wider">Configuration de la déduction</h4>
            <span class="ml-auto text-sm text-slate-400">Saisie RH</span>
          </div>

          {#if referenceSalary > 0}
            <p class="text-sm text-slate-400">
              {referenceLabel} de référence : <span class="font-semibold text-slate-700 text-sm">{formatAmount(referenceSalary)} {referenceCurrency}</span>
            </p>
          {:else}
            <p class="text-sm text-slate-400">
              Aucun contrat actif trouvé : l'estimation durée/% est indisponible. Saisissez le % manuellement.
            </p>
          {/if}

          <!-- Mode : pourcentage OU nombre de mois (estimations réciproques) -->
          <div class="relative flex h-9 rounded-lg bg-slate-100 p-1 select-none">
            <!-- Curseur qui glisse entre les deux options -->
            <span
              aria-hidden="true"
              class="absolute top-1 bottom-1 rounded-md bg-white shadow-fine transition-transform duration-200 ease-out"
              style="left: 0.25rem; width: calc((100% - 0.5rem) / 2); transform: translateX({planMode === 'percent' ? 0 : '100%'});"
            ></span>
            <button
              type="button"
              onclick={switchToPercent}
              class={cn('relative z-10 flex-1 rounded-md text-sm font-semibold transition-colors cursor-pointer',
                planMode === 'percent' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700')}
            >En % par mois</button>
            <button
              type="button"
              onclick={switchToMonths}
              class={cn('relative z-10 flex-1 rounded-md text-sm font-semibold transition-colors cursor-pointer',
                planMode === 'months' ? 'text-slate-900' : 'text-slate-500 hover:text-slate-700')}
            >En nombre de mois</button>
          </div>

          <div class="grid grid-cols-2 gap-3">
            {#if planMode === 'percent'}
              <div class="space-y-1.5">
                <Label for="plan-percent" class="text-sm text-slate-600">Pourcentage mensuel</Label>
                <Input
                  id="plan-percent"
                  type="number"
                  min="1"
                  max="100"
                  value={repaymentPercentage}
                  oninput={(e) => { repaymentPercentage = clampPct(parseFloat((e.currentTarget as HTMLInputElement).value) || 1); }}
                  class={cn('h-9 bg-white border-slate-200 rounded-md text-sm', configErrors.percent && 'border-red-500 focus:ring-red-500')}
                />
                <ValidationError errors={configErrors} field="percent" class="[&_span]:text-sm" />
              </div>
              <div class="space-y-1.5">
                <Label class="text-sm text-slate-600">Durée estimée</Label>
                <div class="h-9 flex items-center rounded-md bg-slate-50 border border-slate-200 px-3 text-sm font-semibold text-slate-700">
                  {estimatedMonths ? `${estimatedMonths} mois` : '—'}
                </div>
              </div>
            {:else}
              <div class="space-y-1.5">
                <Label for="plan-months" class="text-sm text-slate-600">Nombre de mois</Label>
                <Input
                  id="plan-months"
                  type="number"
                  min="1"
                  max="120"
                  value={planMonths}
                  oninput={(e) => { planMonths = Math.max(1, Math.floor(parseFloat((e.currentTarget as HTMLInputElement).value) || 1)); applyMonthsMode(); }}
                  class={cn('h-9 bg-white border-slate-200 rounded-md text-sm', configErrors.months && 'border-red-500 focus:ring-red-500')}
                />
                <ValidationError errors={configErrors} field="months" class="[&_span]:text-sm" />
              </div>
              <div class="space-y-1.5">
                <Label class="text-sm text-slate-600">Pourcentage estimé</Label>
                <div class="h-9 flex items-center rounded-md bg-slate-50 border border-slate-200 px-3 text-sm font-semibold text-slate-700">
                  {shownPercent != null ? `${shownPercent} % / mois` : '—'}
                </div>
              </div>
            {/if}
          </div>

          <!-- Mois de début du remboursement -->
          <div class="space-y-1.5">
            <Label for="plan-start" class="text-sm text-slate-600">Mois de début du remboursement</Label>
            <Input
              id="plan-start"
              type="month"
              value={planStartMonth}
              oninput={(e) => (planStartMonth = (e.currentTarget as HTMLInputElement).value)}
              class="h-9 bg-white border-slate-200 rounded-md text-sm"
            />
            <p class="text-sm text-slate-400">Laisser vide pour commencer dès le prochain cycle.</p>
          </div>

          {#if estimatedMonthly != null}
            <div class="flex items-center justify-between rounded-lg bg-indigo-50/60 border border-indigo-100 px-3 py-2">
              <span class="text-sm text-slate-600">Mensualité estimée</span>
              <span class="text-sm font-bold text-slate-800">≈ {formatAmount(estimatedMonthly)} {referenceCurrency}/mois</span>
            </div>
          {/if}

          {#if planWarning}
            <div class="flex items-start gap-2 rounded-lg bg-amber-50/70 border border-amber-200 px-3 py-2">
              <AppIcon name="alert-circle" size={16} class="text-amber-500 shrink-0 mt-0.5" />
              <p class="text-sm text-amber-700">{planWarning}</p>
            </div>
          {/if}

          <div class="grid grid-cols-2 gap-3">
            <div class="space-y-1.5">
              <Label for="config-priority" class="text-sm text-slate-600">Priorité</Label>
              <Input
                id="config-priority"
                type="number"
                min="1"
                bind:value={priorityOrder}
                class="h-9 bg-white border-slate-200 rounded-md text-sm"
              />
            </div>

            <div class="space-y-1.5">
              <Label class="text-sm text-slate-600">Base de déduction</Label>
              <Select type="single" value={deductionBase} onValueChange={(v) => deductionBase = v as AdvanceDeductionBase}>
                <SelectTrigger class="h-9 w-full bg-white border-slate-200 rounded-md text-sm cursor-pointer">
                  {deductionBase === 'GROSS' ? 'Salaire brut' : 'Salaire net'}
                </SelectTrigger>
                <SelectContent class="z-9999">
                  <SelectItem value="GROSS" label="Salaire brut" class="text-sm">Salaire brut</SelectItem>
                  <SelectItem value="NET" label="Salaire net" class="text-sm">Salaire net</SelectItem>
                </SelectContent>
              </Select>
            </div>
          </div>

          <div class="space-y-1.5">
            <Label class="text-sm text-slate-600">Moment de la retenue</Label>
            <Select type="single" value={taxTiming} onValueChange={(v) => taxTiming = v as AdvanceTaxTiming}>
              <SelectTrigger class="h-9 w-full bg-white border-slate-200 rounded-md text-sm cursor-pointer">
                {taxTiming === 'BEFORE_TAX' ? 'Avant impôt' : 'Après impôt'}
              </SelectTrigger>
              <SelectContent class="z-9999">
                <SelectItem value="BEFORE_TAX" label="Avant impôt" class="text-sm">Avant impôt (réduit le taxable)</SelectItem>
                <SelectItem value="AFTER_TAX" label="Après impôt" class="text-sm">Après impôt (sans impact fiscal)</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </div>

      <Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 bg-slate-50/60">
        <Button
          variant="outline"
          onclick={() => open = false}
          class="flex-1 h-9 border-slate-200 text-slate-600 hover:bg-slate-50 font-medium cursor-pointer"
        >
          <AppIcon name="x" size={16} />
          Annuler
        </Button>
        <Button
          onclick={handleApprove}
          disabled={isSavingConfig || !canApprove}
          class="flex-1 h-9 bg-emerald-600 hover:bg-emerald-700 text-white font-medium shadow-fine cursor-pointer disabled:opacity-60 disabled:cursor-not-allowed"
        >
          {#if isSavingConfig}
            <AnimateSpin text="" class="size-3 border-white" />
          {:else}
            <AppIcon name="check-circle" size={16} />
          {/if}
          Approuver
        </Button>
      </Sheet.Footer>
    {/if}
  </Sheet.Content>
</Sheet.Root>

