<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Input } from '@/components/ui/input';
  import { Badge } from '@/components/ui/badge';
  import { Label } from '@/components/ui/label';
  import { Select, SelectContent, SelectItem, SelectTrigger } from '@/components/ui/select';
  import { Button } from '@/components/ui/button';
  import CurrencyToggle from '@/hr/components/ui/currency-toggle';
  import type { PayrollConfiguration, SMIGConfiguration, OvertimeRule, LeaveDeductionMode, LegalAllowanceConfig, SocialContributionRate } from '@/hr/modules/payroll/types/types';
  import { payrollStore } from '@/hr/modules/payroll/stores/payroll.svelte';
  import { LEAVE_DEDUCTION_MODES, OVERTIME_RULE_LABELS, ALLOWANCE_TYPE_LABELS } from '../../../constants/settings.constants';
  import SettingSection from '../SettingSection.svelte';
  import SettingsField from '../SettingsField.svelte';
  import * as Tooltip from '@/components/ui/tooltip';


  let {
    config,
    smig,
    overtimeRules,
    legalAllowances,
    onChange,
    onOvertimeChange,
    onAllowanceChange,
    onResetAllowances,
    socialContributions = [],
  }: {
    config: PayrollConfiguration | null;
    smig: SMIGConfiguration | null;
    overtimeRules: OvertimeRule[];
    legalAllowances: LegalAllowanceConfig[];
    socialContributions: SocialContributionRate[];
    onChange: (field: keyof PayrollConfiguration, value: string | number | boolean | null) => void;
    onOvertimeChange: (ruleId: string, data: { multiplier: number }) => void;
    onAllowanceChange: (allowanceId: string, data: { base_amount: number | null }) => void;
    onResetAllowances: () => void;
  } = $props();

  const inputClass =
    'h-10 bg-white border-slate-200 rounded-md shadow-fine font-normal text-sm focus:ring-1 focus:ring-primary focus:border-primary';

  /** Formate le coefficient HS : 1.3 → « 1,30 » */
  const formatMultiplier = (m: number): string =>
    m.toLocaleString('fr-FR', { minimumFractionDigits: 2, maximumFractionDigits: 2 });

  /** Devise d'affichage des montants SMIG (toggle local à la section) */
  let displayCurrency = $state<'CDF' | 'USD'>('CDF');

  /**
   * Taux USD → CDF : provient uniquement de l'endpoint backend dédié
   * GET /api/payroll/configuration/exchange-rate/ (BCC en priorité).
   * Le fallback 2800 ne sert que de garde-fou si l'API n'a pas encore répondu.
   */
  const usdToCdf = $derived(Number(payrollStore.exchangeRateInfo?.rate) || 2800);

  /** Convertit un montant CDF vers la devise d'affichage */
  function formatAmount(cdf: number, suffix: string): string {
    const value =
      displayCurrency === 'USD' ? cdf / usdToCdf : cdf;
    const formatted = value.toLocaleString('fr-FR', {
      minimumFractionDigits: displayCurrency === 'USD' ? 2 : 0,
      maximumFractionDigits: displayCurrency === 'USD' ? 2 : 0,
    });
    return `${formatted} ${displayCurrency === 'USD' ? 'USD' : 'CDF'} / ${suffix}`;
  }

  /** Id de l'allocation en cours d'édition (null = aucune) */
  let editingAllowanceId = $state<string | null>(null);
  let editingAllowanceValue = $state<string>('');

  /** État de confirmation du bouton Réinitialiser */
  let confirmReset = $state(false);

  /** Ouvre l'édition inline d'une allocation à paramétrer */
  function startEditAllowance(allowance: LegalAllowanceConfig): void {
    editingAllowanceId = allowance.id;
    editingAllowanceValue = allowance.base_amount != null ? String(Number(allowance.base_amount)) : '';
  }

  /** Enregistre la nouvelle valeur de base (montant fixe en CDF) */
  function saveAllowanceEdit(allowanceId: string): void {
    const value = Number(editingAllowanceValue);
    onAllowanceChange(allowanceId, { base_amount: Number.isFinite(value) ? value : null });
    editingAllowanceId = null;
  }
</script>


<Tooltip.Provider delayDuration={500}>
  <div class="space-y-4">
  
    <!-- SMIG -->
    <SettingSection
      icon="ruler"
      title="SMIG"
      description="Salaire minimum légal de référence en RDC — fixé par décret, non modifiable."
      iconClass="bg-blue-50"
    >
      <div class="flex items-center justify-start gap-1.5 mb-3">
        <CurrencyToggle
          currency={displayCurrency}
          onChange={(c) => (displayCurrency = c)}
          size="sm"
        />
        {#if payrollStore.exchangeRateInfo}
          <Button
            type="button"
            variant="outline"
            size="sm"                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                          
            class="h-7 px-2 text-[0.78rem] font-medium text-slate-600 hover:text-slate-900 bg-white border border-slate-200 hover:border-slate-300 transition-colors"
            onclick={() => payrollStore.refreshExchangeRate()}
            aria-label="Recharger le taux de change"
            title="Recharger le taux de change"
          >
            <AppIcon name="refresh-cw" size={13} class="shrink-0" />
            Recharger
          </Button>
          <span class="inline-flex items-center gap-1 px-2 py-0.5 rounded-md text-[0.78rem] font-medium whitespace-nowrap {payrollStore.exchangeRateInfo.source === 'bcc'
            ? 'bg-emerald-50 border border-emerald-100 text-emerald-700'
            : 'bg-amber-50 border border-amber-100 text-amber-700'}">
            <AppIcon name={payrollStore.exchangeRateInfo.source === 'bcc' ? 'zap' : 'settings'} size={11} />
            {payrollStore.exchangeRateInfo.source === 'bcc'
              ? 'Taux officiel BCC (en direct)'
              : 'Taux manuel (configuration)'}
          </span>  
          <span class="inline-flex items-center gap-1.5 text-[0.8rem] text-slate-500 whitespace-nowrap">
            <AppIcon name="banknote" size={13} class="text-slate-400" />
            Taux de change : 1 USD = {Number(payrollStore.exchangeRateInfo.rate).toLocaleString('fr-FR')} CDF
          </span>
        {/if}
      </div>

      <div class="grid grid-cols-2 gap-3">
        <SettingsField label="Montant journalier" id="smig-daily">
          <Input
            id="smig-daily"
            type="number"
            min={0}
            value={displayCurrency === 'USD' ? Number((smig?.daily_rate ?? 21500) / usdToCdf).toFixed(2) : smig?.daily_rate ?? 21500}
            disabled
            class="{inputClass} disabled:bg-slate-50 disabled:text-slate-800 disabled:font-medium"
          />
        </SettingsField>
      </div>

      {#if smig}
        <div class="mt-3 flex flex-wrap items-center gap-2">
          <span class="text-[0.84rem] font-bold uppercase tracking-wider text-slate-500">
            Équivalents :&nbsp;
          </span>
          <span class="inline-flex items-center gap-1 text-[0.84rem] font-medium text-slate-600 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">
            {formatAmount(Number(smig.monthly_rate), 'mois')}
          </span>
          <span class="inline-flex items-center gap-1 text-[0.84rem] font-medium text-slate-600 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">
            {formatAmount(Number(smig.weekly_rate), 'semaine')}
          </span>
          <span class="inline-flex items-center gap-1 text-[0.84rem] font-medium text-slate-600 bg-slate-50 border border-slate-100 px-2 py-0.5 rounded-md">
            {formatAmount(Number(smig.annual_rate), 'an')}
          </span>
        </div>
      {/if}

      <div class="text-slate-500 mt-3 flex items-start gap-1.5">
        <AppIcon name="scale" size={13} class="mt-0.5 shrink-0" />
        <p class="text-[0.84rem] wrap-break-word min-w-0">
          Référence légale : <span class="font-semibold text-slate-500 text-[0.84rem]">Décret n° 25/22</span> fixant le SMIG en RDC.
          {#if smig}
            <span class="inline-flex items-center gap-1 text-[0.84rem] font-medium text-emerald-600 bg-emerald-50 border border-emerald-100 px-2 py-0.5 rounded-md">
              <AppIcon name="calendar" size={12} />
              En vigueur depuis le {new Date(smig.effective_date + 'T00:00:00').toLocaleDateString('fr-FR')}
            </span>
          {/if}
        </p>
      </div>
    </SettingSection>

    <!-- Déduction des absences -->
    <SettingSection
      icon="calendar-x"
      title="Déduction des absences"
      description="Comment les jours d'absence non payés sont retirés du salaire du mois."
      iconClass="bg-amber-50"
    >
      <!-- Liste déroulante des modes (exclusifs par construction) -->
      <div class="mb-3 space-y-1.5">
        <Label for="leave-deduction-mode" class="text-[0.84rem] font-semibold text-slate-700">
          Mode de déduction
        </Label>
        <Select
          type="single"
          value={config?.leave_deduction_mode ?? 'DISABLED'}
          onValueChange={(mode) => {
            onChange('leave_deduction_mode', mode as LeaveDeductionMode);
            // Exclusivité : le forfait n'a de sens qu'en mode FIXED_AMOUNT
            if (mode !== 'FIXED_AMOUNT') {
              onChange('fixed_deduction_per_absent_day', null);
            }
            // Le diviseur reste mémorisé (il réapparaît si on revient en DAILY_RATE)
          }}
        >
          <SelectTrigger
            id="leave-deduction-mode"
            class="h-10 w-full bg-white border-slate-200 rounded-md shadow-fine cursor-pointer"
          >
            <span class="truncate text-[0.85rem] font-medium">
              {LEAVE_DEDUCTION_MODES.find((m) => m.value === (config?.leave_deduction_mode ?? 'DISABLED'))?.label}
            </span>
          </SelectTrigger>
          <SelectContent class="z-9999">
            {#each LEAVE_DEDUCTION_MODES as mode}
              <SelectItem value={mode.value} class="text-[0.85rem]">
                <div class="flex w-full flex-col py-0.5">
                  <span class="text-[0.85rem] font-medium">{mode.label}</span>
                  <span class="text-[0.78rem] text-slate-500 wrap-break-word">{mode.description}</span>
                </div>
              </SelectItem>
            {/each}
          </SelectContent>
        </Select>
        <div class="text-slate-500 flex items-start gap-1.5">
          <AppIcon name="info" size={13} class="mt-0.5 shrink-0" />
          <p class="text-[0.84rem] wrap-break-word min-w-0">
            {LEAVE_DEDUCTION_MODES.find((m) => m.value === (config?.leave_deduction_mode ?? 'DISABLED'))?.description}
          </p>
        </div>
      </div>

      {#if config?.leave_deduction_mode === 'DAILY_RATE'}
        <!-- Diviseur fixe (modifiable, avec retour à la valeur légale) -->
        <div class="p-3 bg-amber-50/60 border border-amber-100 rounded-lg space-y-2">
          <div class="flex items-end gap-3">
            <div class="flex-1 space-y-1.5">
              <Label for="leave-deduction-divisor" class="text-[0.84rem] font-semibold text-slate-700">
                Diviseur (jours)
              </Label>
              <div class="flex items-center gap-2">
                <Input
                  id="leave-deduction-divisor"
                  type="number"
                  min={1}
                  max={31}
                  step={1}
                  value={config?.leave_deduction_divisor ?? 26}
                  class="w-32 h-10 bg-white border-slate-200 rounded-md shadow-fine font-normal text-sm focus:ring-1 focus:ring-primary focus:border-primary"
                  oninput={(e) => {
                    const val = e.currentTarget.value;
                    const num = val === '' ? 26 : Number(val);
                    onChange('leave_deduction_divisor', num);
                  }}
                />
                <Button
                  type="button"
                  variant="outline"
                  class="inline-flex items-center gap-1.5 px-3 h-10 rounded-md text-[0.84rem] font-semibold text-amber-700 bg-white border border-amber-200 hover:bg-amber-50 transition-colors"
                  onclick={() => onChange('leave_deduction_divisor', 26)}
                >
                  <AppIcon name="rotate-ccw" size={13} />
                  Valeur légale (26)
                </Button>
              </div>
            </div>
          </div>
          <p class="text-[0.84rem] text-slate-500 wrap-break-word">
            Valeur d'un jour = salaire mensuel ÷ {config?.leave_deduction_divisor ?? 26}. Par défaut 26 jours de
            prestation (référence légale RDC). Un bouton permet de revenir à la valeur légale.
          </p>
        </div>
      {/if}

      {#if config?.leave_deduction_mode === 'CALENDAR_DAYS'}
        <div class="p-3 bg-amber-50/60 border border-amber-100 rounded-lg">
          <p class="text-[0.84rem] text-slate-500 wrap-break-word">
            Valeur d'un jour = salaire mensuel ÷ <span class="text-[0.84rem] font-semibold text-slate-700">nombre réel de jours du mois</span>.
            Le diviseur est calculé automatiquement à chaque période de paie (ex. 31 jours en janvier, 28 en février).
          </p>
        </div>
      {/if}

      {#if config?.leave_deduction_mode === 'FIXED_AMOUNT'}
        <!-- Montant forfaitaire par jour -->
        <div class="p-3 bg-amber-50/60 border border-amber-100 rounded-lg space-y-2">
          <Label for="leave-deduction-fixed" class="text-[0.84rem] font-semibold text-slate-700">
            Montant forfaitaire par jour d'absence (CDF)
          </Label>
          <Input
            id="leave-deduction-fixed"
            type="number"
            min={0}
            step={100}
            value={config?.fixed_deduction_per_absent_day ?? ''}
            placeholder="Ex. 50 000"
            class="w-full h-10 bg-white border-slate-200 rounded-md shadow-fine font-normal text-sm focus:ring-1 focus:ring-primary focus:border-primary"
            oninput={(e) => {
              const val = e.currentTarget.value;
              const num = val === '' ? null : Number(val);
              onChange('fixed_deduction_per_absent_day', num);
            }}
          />
          <p class="text-[0.84rem] text-slate-500 wrap-break-word">
            Un montant fixe en CDF est déduit pour chaque jour d'absence, indépendamment du salaire.
          </p>
        </div>
      {/if}

      {#if config?.leave_deduction_mode === 'ATTENDANCE_DAYS'}
        <div class="p-3 bg-amber-50/60 border border-amber-100 rounded-lg">
          <p class="text-[0.86rem] text-slate-500 wrap-break-word">
            Valeur d'un jour = salaire mensuel ÷ <span class="text-[0.86rem] font-semibold text-slate-700">jours théoriques de présence</span>.
          </p>
          <div class="text-[0.86rem] text-slate-500 mt-1.5 flex items-start gap-1.5">
            <AppIcon name="calendar" size={13} class="mt-0.5 shrink-0" />
            <p class="wrap-break-word min-w-0 text-[0.86rem]">
              Le planning hebdomadaire de l'employé est étendu à toute la période du bulletin (ex. : un employé
              qui travaille du lundi au vendredi aura ~22 jours de présence sur un mois), puis les fériés et
              jours non travaillés en sont retirés.
            </p>
          </div>
          <div class="text-[0.86rem] text-slate-500 mt-1.5 flex items-start gap-1.5">
            <AppIcon name="scale" size={13} class="mt-0.5 shrink-0" />
            <p class="wrap-break-word min-w-0 text-[0.86rem]">
              Si l'employé n'a pas de planning d'attendance, le diviseur calendaire est utilisé par sécurité.
            </p>
          </div>
        </div>
      {/if}
    </SettingSection>

    <!-- Heures supplémentaires -->
    <SettingSection
      icon="clock"
      title="Heures supplémentaires"
      description="Réglez le paiement des heures supplémentaires (130 % à 200 % selon Code du travail)."
      iconClass="bg-violet-50"
    >
      <div class="text-slate-500 mb-3 flex items-start gap-1.5">
        <AppIcon name="info" size={13} class="text-violet-500 mt-0.5 shrink-0" />
        <p class="text-[0.86rem] wrap-break-word min-w-0">
          Les heures supplémentaires sont payées au <span class="font-bold text-slate-700 text-[0.86rem]">taux horaire x coefficient</span>.
          Ex. : 1 h à 130 % → 1,3 x taux horaire; le dimanche à 200 % → 2 x taux.
        </p>
      </div>

      <div class="mb-4 p-3 bg-violet-50/50 border border-violet-100 rounded-lg space-y-2">
        <SettingsField
          label="Heures de travail / semaine"
          id="work-hours"
          hint="Code du travail RDC : 45 heures maximum par semaine."
        >
          <Input
            id="work-hours"
            type="number"
            min={1}
            max={168}
            value={config?.work_hours_per_week ?? 45}
            oninput={(e) => onChange('work_hours_per_week', Number(e.currentTarget.value) || 45)}
            class="w-full h-10 bg-white border-slate-200 rounded-md shadow-fine font-normal text-sm focus:ring-1 focus:ring-primary focus:border-primary"
          />
        </SettingsField>
        <div class="text-slate-500 flex items-start gap-1.5">
          <AppIcon name="info" size={13} class="mt-0.5 shrink-0" />
          <p class="text-[0.84rem] wrap-break-word">
            Ce champ sert à calculer le <span class="font-semibold text-slate-600 text-[0.84rem]">taux horaire</span> :
            salaire mensuel ÷ heures mensuelles (45 h/semaine → 195 h/mois). Chaque heure supplémentaire
            est payée à ce taux × le coefficient choisi ci-dessous.
          </p>
        </div>
      </div>

      <div class="space-y-2.5">
        {#each overtimeRules as rule (rule.id)}
          <div
            class="flex items-center justify-between gap-4 p-3 rounded-lg border {rule.is_active
              ? 'bg-white border-slate-200'
              : 'bg-slate-50/60 border-slate-100 opacity-70'}"
          >
            <div class="flex items-center gap-2.5 min-w-0">
              <span
                class="inline-flex items-center gap-1 px-2 py-1 rounded-md text-[0.84rem] font-bold text-nowrap {rule.is_active
                  ? 'bg-violet-50 text-violet-700'
                  : 'bg-slate-100 text-slate-500'}"
              >
                {OVERTIME_RULE_LABELS[rule.rule_type]?.short ?? rule.rule_type}
              </span>
              <div class="min-w-0">
                <p class="text-[0.86rem] font-semibold text-slate-700 wrap-break-word">
                  {OVERTIME_RULE_LABELS[rule.rule_type]?.label ?? rule.rule_type}
                </p>
                {#if rule.description}
                  <p class="text-[0.86rem] text-slate-500 wrap-break-word">{rule.description}</p>
                {/if}
              </div>
            </div>
            <div class="flex items-center gap-2 shrink-0">
              <Tooltip.Root>
                <Tooltip.Trigger class="cursor-help flex items-center gap-1.5">
                  <span class="text-[0.86rem] font-bold text-slate-600">
                    x {formatMultiplier(rule.multiplier)}
                  </span>
                </Tooltip.Trigger>
                <Tooltip.Content side="top" class="max-w-56 text-[0.84rem] leading-relaxed">
                  Taux horaire x coefficient ({formatMultiplier(rule.multiplier)}) = valeur d'1 h d'heures supplémentaires.
                </Tooltip.Content>
              </Tooltip.Root>
              <Input
                type="number"
                min={1}
                max={3}
                step="0.05"
                value={rule.multiplier}
                disabled={!rule.is_active}
                class="w-20 h-9 text-center bg-white border-slate-200 rounded-md shadow-fine font-bold text-[0.86rem] focus:ring-1 focus:ring-primary focus:border-primary disabled:bg-slate-50 disabled:text-slate-500"
                onchange={(e) =>
                  onOvertimeChange(rule.id, { multiplier: Number(e.currentTarget.value) || 1 })}
              />
            </div>
          </div>
        {:else}
          <p class="py-4 text-center flex items-center justify-center gap-2">
            <AppIcon name="clock" size={15} class="text-slate-500 mt-0.5 shrink-0" />
            <span class="text-[0.84rem] text-slate-500">
              Aucune règle d'heures supplémentaires chargée.
            </span>
          </p>
        {/each}
      </div>

      <div class="text-slate-500 mt-3 flex items-start gap-1.5">
        <AppIcon name="info" size={15} class="mt-0.5 shrink-0" />
        <p class="text-[0.84rem] wrap-break-word min-w-0">
          Règles RDC : <span class="font-semibold text-slate-500 text-[0.84rem]">130 % pour les 6 premières heures, 160 % au-delà, 200 % week-end/fériés, 150 % nuit.</span>
        </p>
      </div>

      <div class="text-slate-500 mt-2 flex items-start gap-1.5">
        <AppIcon name="scale" size={15} class="mt-0.5 shrink-0" />
        <p class="text-[0.84rem] wrap-break-word min-w-0">
          Source légale : <span class="font-semibold text-slate-500 text-[0.84rem]">Code du travail RDC — Loi n° 15/2002</span>,
          qui impose ces majorations pour compenser la pénibilité, dissuader l'abus d'heures supplémentaires et indemniser
          le repos perdu.
        </p>
      </div>
    </SettingSection>

    <!-- Allocations légales (Familiale, Logement, Transport) -->
    <SettingSection
      icon="home"
      title="Allocations légales"
      description="Indemnités dues en plus du salaire : allocations familiales, logement et transport."
      iconClass="bg-emerald-50"
    >
      <div class="flex items-center justify-between gap-2 mb-2">
        <p class="text-[0.8rem] text-slate-500">
          Valeurs par défaut issues des textes légaux RDC.
        </p>
        {#if confirmReset}
          <div class="flex items-center gap-1.5">
            <span class="text-[0.78rem] text-rose-600 font-medium">Réinitialiser ?</span>
            <Button
              size="sm"
              class="h-7 px-2 text-[0.85rem] bg-rose-600 hover:bg-rose-700 text-white"
              onclick={() => {
                confirmReset = false;
                onResetAllowances();
              }}
            >
              Oui
            </Button>
            <Button
              size="sm"
              variant="ghost"
              class="h-7 px-2 text-[0.85rem]"
              onclick={() => (confirmReset = false)}
            >
              Non
            </Button>
          </div>
        {:else}
          <Button
            size="sm"
            variant="outline"
            class="h-7 px-2.5 text-[0.85rem] text-slate-500 hover:text-rose-600 hover:border-rose-200"
            onclick={() => (confirmReset = true)}
          >
            <AppIcon name="rotate-ccw" size={15} />
            Réinitialiser
          </Button>
        {/if}
      </div>
      {#if legalAllowances.length === 0}
        <p class="py-4 text-center flex items-center justify-center gap-2">
          <AppIcon name="info" size={13} class="text-slate-500 mt-0.5 shrink-0" />
          <span class="text-[0.84rem] text-slate-500">
            Aucune allocation légale chargée.
          </span>
        </p>
      {:else}
        <div class="space-y-2.5">
          {#each legalAllowances as allowance (allowance.id)}
            <div class="p-3 rounded-lg border {allowance.is_active ? 'bg-white border-slate-200' : 'bg-slate-50/60 border-slate-100 opacity-70'}">
              <div class="flex flex-wrap items-start justify-between gap-3">
                <div class="min-w-0 flex-1">
                  <p class="text-[0.86rem] font-semibold text-slate-700">
                    {ALLOWANCE_TYPE_LABELS[allowance.allowance_type] ?? allowance.allowance_type}
                  </p>
                  {#if allowance.formula_description}
                    <p class="text-[0.85rem] text-slate-500 wrap-break-word">{allowance.formula_description}</p>
                  {/if}
                </div>
                <div class="flex items-center gap-1.5 shrink-0">
                  <Badge
                    variant="outline"
                    class="border-0 text-[0.7rem] font-bold uppercase tracking-wide px-2.5 py-1 shadow-none rounded-full whitespace-nowrap flex items-center gap-1.5 transition-colors {allowance.is_taxable
                      ? 'bg-amber-50 text-amber-700'
                      : 'bg-emerald-50 text-emerald-700'}"
                  >
                    <AppIcon name={allowance.is_taxable ? 'receipt' : 'shield-check'} size={13} />
                    {allowance.is_taxable ? 'Imposable' : 'Exonérée'}
                  </Badge>

                  {#if editingAllowanceId === allowance.id}
                    <div class="flex items-center gap-1.5">
                      <Input
                        type="number"
                        min="0"
                        value={editingAllowanceValue}
                        oninput={(e) => (editingAllowanceValue = e.currentTarget.value)}
                        class="h-8 w-28 text-[0.84rem] tabular-nums"
                        placeholder="Montant CDF"
                      />
                      <span class="text-[0.72rem] text-slate-500">CDF</span>
                      <Button
                        size="sm"
                        class="h-8 px-2 text-[0.78rem]"
                        onclick={() => saveAllowanceEdit(allowance.id)}
                      >
                        OK
                      </Button>
                      <Button
                        size="sm"
                        variant="ghost"
                        class="h-8 px-2 text-[0.78rem]"
                        onclick={() => (editingAllowanceId = null)}
                      >
                        Annuler
                      </Button>
                    </div>
                  {:else}
                    <span class="text-[0.84rem] font-bold text-slate-600 tabular-nums whitespace-nowrap">
                      {allowance.base_amount != null && Number(allowance.base_amount) > 0
                        ? `${Number(allowance.base_amount).toLocaleString('fr-FR')} CDF`
                        : allowance.taxable_threshold_percentage != null
                          ? `${Number(allowance.taxable_threshold_percentage).toLocaleString('fr-FR')} %`
                          : 'À paramétrer'}
                    </span>
                    <Button
                      size="sm"
                      variant="ghost"
                      class="h-8 px-2 text-[0.78rem] text-slate-500 hover:text-slate-700"
                      onclick={() => startEditAllowance(allowance)}
                    >
                      <AppIcon name="edit" size={13} />
                      Modifier
                    </Button>
                  {/if}
                </div>
              </div>
            </div>
          {/each}
        </div>

        <p class="text-slate-500 mt-3 flex items-start gap-1.5">
          <AppIcon name="scale" size={15} class="mt-0.5 shrink-0" />
          <span class="text-[0.85rem]">
            Plafond logement : <span class="font-semibold text-slate-500 text-[0.84rem]">30 % du salaire de base</span> —
            la partie exonérée d'impôt est limitée à ce plafond ; au-delà, l'indemnité devient imposable à l'IRPP.
          </span>
        </p>
      {/if}
    </SettingSection>

    <!-- Cotisations sociales (informatif — taux légaux CNSS / ONEM / INPP) -->
    <SettingSection
      icon="landmark"
      title="Cotisations sociales"
      description="Taux légaux RDC appliqués sur le brut — informations fournies par les organismes (CNSS, ONEM, INPP), non modifiables ici."
      iconClass="bg-violet-50"
    >
      <div class="space-y-2.5">
        {#if socialContributions.length === 0}
          <p class="py-4 text-center flex items-center justify-center gap-2">
            <AppIcon name="info" size={13} class="text-slate-500 mt-0.5 shrink-0" />
            <span class="text-[0.84rem] text-slate-500">Aucune cotisation sociale chargée.</span>
          </p>
        {:else}
          <div class="overflow-hidden rounded-lg border border-slate-200 bg-white">
            <table class="w-full text-[0.84rem]">
              <thead>
                <tr class="bg-slate-50 text-left uppercase tracking-wide text-slate-500">
                  <th class="px-3 py-2 font-semibold text-[0.8rem]">Organisme</th>
                  <th class="px-3 py-2 font-semibold text-right text-[0.8rem]">Taux total</th>
                  <th class="px-3 py-2 font-semibold text-right text-[0.8rem]">Part salariale</th>
                  <th class="px-3 py-2 font-semibold text-right text-[0.8rem]">Part patronale</th>
                  <th class="px-3 py-2 font-semibold text-right text-[0.8rem]">Plafond</th>
                  <th class="px-3 py-2 font-semibold text-right text-[0.8rem]">Effectifs</th>
                </tr>
              </thead>
              <tbody>
                {#each socialContributions.filter(c => c.is_active) as rate (rate.id)}
                  <tr class="border-t border-slate-100">
                    <td class="px-3 py-2 font-medium text-slate-700 text-[0.78rem]">{rate.contribution_type}</td>
                    <td class="px-3 py-2 text-right tabular-nums text-slate-600 text-[0.82rem]">{Number(rate.rate_percentage).toLocaleString('fr-FR')} %</td>
                    <td class="px-3 py-2 text-right tabular-nums text-slate-600 text-[0.82rem]">{Number(rate.employee_portion).toLocaleString('fr-FR')} %</td>
                    <td class="px-3 py-2 text-right tabular-nums text-slate-600 text-[0.82rem]">{Number(rate.employer_portion).toLocaleString('fr-FR')} %</td>
                    <td class="px-3 py-2 text-right tabular-nums text-slate-600 text-[0.82rem]">
                      {rate.ceiling_amount != null
                        ? `${Number(rate.ceiling_amount).toLocaleString('fr-FR')} CDF`
                        : '—'}
                    </td>
                    <td class="px-3 py-2 text-right text-slate-600 text-[0.78rem]">
                      {rate.company_size_min != null && rate.company_size_max != null
                        ? `${rate.company_size_min}–${rate.company_size_max}`
                        : rate.company_size_min != null
                          ? `${rate.company_size_min}+`
                          : '—'}
                    </td>
                  </tr>
                {/each}
              </tbody>
            </table>
          </div>
          <p class="text-slate-500 flex items-start gap-1.5">
            <AppIcon name="info" size={15} class="mt-0.5 shrink-0" />
            <span class="text-[0.85rem]">
              Les cotisations sont retenues sur le bulletin selon le salaire brut ; la CNSS est plafonnée à 175 000 FC. L'allocation familiale (8 100 FC/enfant/mois) est versée directement par la CNSS au travailleur, hors paie employeur.
            </span>
          </p>
        {/if}
      </div>
    </SettingSection>
  </div>
</Tooltip.Provider>

