<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { Card, CardContent, CardHeader, CardTitle, CardDescription } from "@/components/ui/card";
  import { Textarea } from "@/components/ui/textarea";

  import { usePositionsQuery, useSeniorityLevelsQuery } from "../../../queries/onboardingQueries";
  import ValidationError from "@/components/ui/validation-error/ValidationError.svelte";
  import { validateStep } from "../../../schemas/onboarding.schema";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { REMUNERATION_TYPES, CONTRACT_TYPES } from "../../../constants/contract";
  import { EMPLOYEE_STATUS_CONFIG } from "@/hr/employees/constants/employeeStatus";
  import { getOrgUnitIcon } from "@/hr/jobs/constants/orgUnit.constants";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import SalaryGroup from "../../shared/SalaryGroup.svelte";
  import ContractPayElementList from '@/hr/employees/components/shared/ContractPayElementList.svelte';
  import { usePayrollAdjustmentsQuery } from "@/hr/payroll/queries/payrollHooks";
  import type { ContractPayElementItem } from "@/hr/employees/types/types";
  import type { PayrollAdjustmentConfig } from "@/hr/payroll/types/types";
  import { formatClassEchelon } from "@/hr/jobs/constants/professionalCategory.constants";
  import { payrollConfigStore } from "@/hr/payroll/stores/configuration/payrollConfigStore.svelte";


  // Options pour le statut initial
  const initialStatusOptions = $derived([
    { value: 'PENDING', label: EMPLOYEE_STATUS_CONFIG['PENDING'].label },
    { value: 'PROBATION', label: EMPLOYEE_STATUS_CONFIG['PROBATION'].label },
    { value: 'ACTIVE', label: EMPLOYEE_STATUS_CONFIG['ACTIVE'].label }
  ]);

  // Charge la configuration (heures légales/semaine) au montage si pas encore en mémoire.
  $effect(() => {
    if (!payrollConfigStore.configuration) {
      payrollConfigStore.syncConfiguration();
    }
  });

  // TanStack Queries
  const positionsQuery = usePositionsQuery();
  const seniorityQuery = $derived(
    useSeniorityLevelsQuery(onboardingStore.data.contract.position_id)
  );

  // Positions formatted for select
  const positionOptions = $derived(
    $positionsQuery.data?.map(p => ({
      value: p.id,
      label: p.name,
      org_unit_name: p.org_unit?.name || '',
      org_unit_type: p.org_unit?.type || ''
    })) ?? []
  );

  let seniorityOptions = $state<Array<{value: string, label: string, echelon?: number | null}>>([]);
  let hasSeniorityLevels = $state(false);

  // Métamodèle (Règle 5) — clauses
  const contractAdjustments = $derived(onboardingStore.data.contract.contract_adjustments);

  // S10 — catalogue des éléments de paie
  const adjustmentsQuery = usePayrollAdjustmentsQuery();
  const catalog = $derived<PayrollAdjustmentConfig[]>($adjustmentsQuery.data ?? []);

  // Classe/Échelon dérivés de la sélection Poste + Séniorité
  const selectedSeniorityInfo = $derived.by(() => {
    const pos = $positionsQuery.data?.find(p => p.id === onboardingStore.data.contract.position_id);
    const sl = pos?.seniority_levels?.find((s: any) => s.id === onboardingStore.data.contract.seniority_level_id);
    if (!sl) return null;
    const seniorityLevel = sl.seniority_level;
    return {
      classe: seniorityLevel?.classe ?? sl.classe ?? null,
      echelon: sl.echelon ?? null,
      salary_min: Number(sl.salary_min) || null,
      salary_max: Number(sl.salary_max) || null
    };
  });

  // Validation salaire >= salary_min (avertissement si en dessous)
  const salaryWarning = $derived.by(() => {
    if (!selectedSeniorityInfo?.salary_min) return null;
    const salary = onboardingStore.data.contract.salary;
    if (salary > 0 && salary < selectedSeniorityInfo.salary_min) {
      return `Le salaire (${salary.toLocaleString('fr-FR')}) est inférieur au minimum de la grille (${selectedSeniorityInfo.salary_min.toLocaleString('fr-FR')} FC).`;
    }
    return null;
  });

  // Ajout d'un élément depuis le picker
  async function handleAddPayElement(payload: any) {
    const adj = catalog.find((a) => a.id === payload.adjustment);
    if (!adj) return;
    const item: ContractPayElementItem = {
      id: crypto.randomUUID(),
      catalog_code: adj.code ?? null,
      label: adj.name,
      value_type: adj.calculation_mode,
      amount: adj.amount != null ? Number(adj.amount) : null,
      custom_amount: payload.custom_amount,
      custom_percentage: payload.custom_percentage,
      is_active: payload.is_active ?? true,
      is_taxable: adj.is_taxable,
      recurrence: 'monthly',
      start_period: payload.start_period,
      end_period: payload.end_period ?? null,
      // Champ interne pour la soumission
      adjustment_id: adj.id,
    } as any;
    onboardingStore.setContractField('contract_adjustments', [...contractAdjustments, item]);
  }

  function handleRemovePayElement(_el: ContractPayElementItem, index: number): Promise<void> {
    const next = [...contractAdjustments];
    next.splice(index, 1);
    onboardingStore.setContractField('contract_adjustments', next);
    return Promise.resolve();
  }

  $effect(() => {
    // Essayer d'abord depuis les données de position sélectionnée
    const selectedPos = $positionsQuery.data?.find(p => p.id === onboardingStore.data.contract.position_id);
    if (selectedPos?.seniority_levels && selectedPos.seniority_levels.length > 0) {
      seniorityOptions = selectedPos.seniority_levels.map((s: any) => {
        const label = s.seniority_level?.label || s.label;
        const level = s.seniority_level?.level || s.level;
        const salaryMin = s.salary_min || 0;
        const salaryMax = s.salary_max || 0;
        
        let salaryText = '';
        if (salaryMin > 0 && salaryMax > 0) {
          salaryText = ` - ${salaryMin} - ${salaryMax} FC`;
        } else if (salaryMin > 0) {
          salaryText = ` - à partir de ${salaryMin} FC`;
        }
        
        return {
          value: s.id,
          label: `${label} (${level})${salaryText}`
        };
      });
      hasSeniorityLevels = true;
    } else if ($seniorityQuery.data && $seniorityQuery.data.length > 0) {
      seniorityOptions = $seniorityQuery.data.map((s: any) => {
        const label = s.seniority_level?.label || s.label;
        const level = s.seniority_level?.level || s.level;
        const salaryMin = s.salary_min || 0;
        const salaryMax = s.salary_max || 0;
        
        let salaryText = '';
        if (salaryMin > 0 && salaryMax > 0) {
          salaryText = ` - ${salaryMin}k - ${salaryMax}k FC`;
        } else if (salaryMin > 0) {
          salaryText = ` - à partir de ${salaryMin}k FC`;
        }
        
        return {
          value: s.id,
          label: `${label} (${level})${salaryText}`
        };
      });
      hasSeniorityLevels = true;
    } else {
      seniorityOptions = [];
      hasSeniorityLevels = false;
    }
  });

  // Selected position details
  const selectedPosition = $derived(
    $positionsQuery.data?.find(p => p.id === onboardingStore.data.contract.position_id)
  );

  // Calcul de l'équivalent mensuel pour le taux horaire.
  // Heures mensuelles lues depuis la configuration (work_hours_per_week × 52 / 12),
  // avec repli sur la valeur légale standard (45 h/sem → 195 h/mois).
  const workHoursPerWeek = $derived(payrollConfigStore.configuration?.work_hours_per_week ?? 45);
  const workHoursPerMonth = $derived(
    payrollConfigStore.configuration?.work_hours_per_month
      ?? Math.round((payrollConfigStore.configuration?.work_hours_per_week ?? 45) * 52 / 12)
  );

  const monthlyEquivalent = $derived(() => {
    if (onboardingStore.data.contract.remuneration_type === 'HOURLY' && onboardingStore.data.contract.salary > 0) {
      const monthly = onboardingStore.data.contract.salary * workHoursPerMonth;
      return new Intl.NumberFormat('fr-FR').format(monthly);
    }
    return null;
  });

  // Obtenir le nom complet de la devise pour les exemples
  const currencyName = $derived(() => {
    switch (onboardingStore.data.contract.currency) {
      case 'USD': return 'USD';
      case 'EUR': return 'EUR';
      case 'CDF': 
      default: return 'FC';
    }
  });

  // Handle position change - clear seniority when position changes
  function handlePositionChange(newPositionId: string) {
    onboardingStore.setContractField('position_id', newPositionId);
    // Reset seniority when position changes
    onboardingStore.setContractField('seniority_level_id', '');
  }

  // Validation errors for contract step
  let validationErrors: Record<string, string> = $state({});

  $effect(() => {
    const validation = validateStep('contract', onboardingStore.data.contract);
    if (!validation.success) {
      const errors: Record<string, string> = {};
      validation.errors.forEach(error => {
        if (error.includes('poste')) errors.position_id = error;
        else if (error.includes('séniorité')) errors.seniority_level_id = error;
        else if (error.includes('contrat')) errors.contract_type = error;
        else if (error.includes('salaire')) errors.salary = error;
        else if (error.includes('début') || error.includes('date')) errors.hire_date = error;
        else if (error.includes('rémunération')) errors.remuneration_type = error;
        else if (error.includes('devise')) errors.currency = error;
      });
      validationErrors = errors;
    } else {
      validationErrors = {};
    }
  });
</script>


{#snippet InputGroup(
  id: string,
  label: string,
  placeholder: string,
  type = "text",
  value: string | number,
  onChange: (val: string) => void
)}
  <div class="space-y-1.5">
    <Label {id} class="text-[0.83rem] text-slate-900 font-medium">{label}</Label>
    <div class="relative">
      <Input
        {id}
        {type}
        {placeholder}
        {value}
        oninput={(e) => onChange(e.currentTarget.value)}
        class="h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
      />
      <ValidationError errors={validationErrors} field={id} />
    </div>
  </div>
{/snippet}


<Card class="border-slate-200 shadow-none rounded-none border-0 py-0">
  <CardHeader class="px-0 pt-0">
    <CardTitle class="text-[0.98rem] font-bold text-slate-900 tracking-tight">
      Détails du contrat
    </CardTitle>
    <CardDescription class="text-[0.875rem]">
      Configurez le poste, le niveau de séniorité et les conditions contractuelles.
    </CardDescription>
  </CardHeader>
  <CardContent class="px-0 py-0 space-y-6">

    <!-- Section 1 : Poste et Organisation -->
    <div class="space-y-3">
      <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
        Poste et Organisation
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
        <!-- Poste (détermine l'unité org) -->
        <div class="space-y-1.5">
          <Label class="text-[0.83rem] text-slate-900 font-medium">
            Poste *
          </Label>
          <Select.Root
            type="single"
            value={onboardingStore.data.contract.position_id}
            onValueChange={handlePositionChange}
            disabled={$positionsQuery.isLoading || $positionsQuery.isError}
          >
            <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer flex items-center justify-between">
              {#if $positionsQuery.isLoading}
                <div class="flex items-center gap-2 text-slate-500">
                  <AnimateSpin class="size-3" textPosition="right" text="Chargement des postes" />
                </div>
              {:else if $positionsQuery.isError}
                <div class="flex items-center gap-2 text-red-500 font-medium">
                  <AppIcon name="alert-circle" size={16} />
                  <span class="text-sm">Erreur de chargement</span>
                </div>
              {:else}
                <span class="text-sm">
                  {selectedPosition?.name ?? "Sélectionner un poste..."}
                </span>
              {/if}
            </Select.Trigger>

            {#if $positionsQuery.isSuccess && positionOptions.length > 0}
              <Select.Content class="max-h-60">
                {#each positionOptions as opt}
                  <Select.SelectItem value={opt.value} label={opt.label}>
                    <div class="flex flex-col">
                      <span class="text-[0.86rem]">{opt.label}</span>
                      <span class="text-[0.86rem] text-slate-400 flex items-center gap-1">
                        <AppIcon name={getOrgUnitIcon(opt.org_unit_type)} size={14} />
                        {opt.org_unit_name}
                      </span>
                    </div>
                  </Select.SelectItem>
                {/each}
              </Select.Content>
            {/if}
          </Select.Root>
          <ValidationError errors={validationErrors} field="position_id" />

          <!-- Affichage unité org (lecture seule) -->
          {#if selectedPosition}
            <div class="flex items-center gap-2 text-[0.82rem] text-slate-500 mt-1">
              <AppIcon name={getOrgUnitIcon(selectedPosition.org_unit?.type || '')} size={15} />
              Unité: {selectedPosition.org_unit?.name}
            </div>
          {/if}
        </div>

        <!-- Niveau de seniorité (dépend du poste) -->
        <div class="space-y-1.5">
          <Label class="text-[0.83rem] text-slate-900 font-medium">
            Niveau de séniorité *
          </Label>
          <Select.Root
            type="single"
            bind:value={onboardingStore.data.contract.seniority_level_id}
            disabled={!onboardingStore.data.contract.position_id || !hasSeniorityLevels || $seniorityQuery.isLoading || $seniorityQuery.isError}
          >
            <Select.Trigger 
              class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer flex items-center justify-between disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed"
            >
              {#if !onboardingStore.data.contract.position_id}
                <span class="text-slate-400 text-sm">Sélectionnez d'abord un poste</span>
              {:else if $seniorityQuery.isLoading}
                <div class="flex items-center gap-2 text-slate-500">
                  <AnimateSpin class="size-3" textPosition="right" text="Chargement des séniorités" />
                </div>
              {:else if $seniorityQuery.isError}
                <div class="flex items-center gap-2 text-red-500 font-medium">
                  <AppIcon name="alert-circle" size={16} />
                  <span class="text-sm">Erreur de chargement</span>
                </div>
              {:else if !hasSeniorityLevels}
                <span class="text-slate-400 text-sm">Aucun niveau défini pour ce poste</span>
              {:else}
                <span class="text-sm">
                  {seniorityOptions.find((o) => o.value === onboardingStore.data.contract.seniority_level_id)?.label ?? "Sélectionner..."}
                </span>
              {/if}
            </Select.Trigger>

            {#if $seniorityQuery.isSuccess && seniorityOptions.length > 0}
              <Select.Content class="max-h-60">
                {#each seniorityOptions as opt (opt.value)}
                  <Select.SelectItem value={opt.value} label={opt.label}>
                    {opt.label}
                  </Select.SelectItem>
                {/each}
              </Select.Content>
            {/if}
          </Select.Root>
          <ValidationError errors={validationErrors} field="seniority_level_id" />

          <!-- Classe/Échelon dérivés + avertissement salaire -->
          {#if selectedSeniorityInfo}
            <div class="flex flex-wrap items-center gap-2 mt-1.5">
              <span class="inline-flex items-center gap-1.5 px-2.5 py-1 rounded-lg bg-indigo-50 text-indigo-700 text-[0.82rem] font-semibold border border-indigo-100">
                <AppIcon name="layers" size={13} />
                {formatClassEchelon(selectedSeniorityInfo.classe, selectedSeniorityInfo.echelon)}
              </span>
              {#if selectedSeniorityInfo.salary_min != null}
                <span class="text-[0.82rem] text-slate-500">
                  Fourchette : {Number(selectedSeniorityInfo.salary_min).toLocaleString('fr-FR')} - {Number(selectedSeniorityInfo.salary_max).toLocaleString('fr-FR')} FC
                </span>
              {/if}
            </div>
            {#if salaryWarning}
              <p class="flex items-center gap-1.5 mt-1 text-[0.82rem] text-amber-600 bg-amber-50 border border-amber-100 rounded-lg px-2.5 py-1.5">
                <AppIcon name="alert-triangle" size={15} />
                {salaryWarning}
              </p>
            {/if}
          {/if}
        </div>
      </div>
    </div>

    <!-- Section 2 : Contrat et Rémunération -->
    <div class="space-y-3">
      <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
        Contrat et Rémunération
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-3 gap-x-8 gap-y-5">
        <!-- Type de contrat -->
        <div class="space-y-1.5">
          <Label class="text-[0.83rem] text-slate-900 font-medium">
            Type de contrat *
          </Label>
          <Select.Root
            type="single"
            bind:value={onboardingStore.data.contract.contract_type}
          >
            <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer">
              {CONTRACT_TYPES.find((t: any) => t.value === onboardingStore.data.contract.contract_type)?.label ?? "Sélectionner..."}
            </Select.Trigger>
            <Select.Content>
              {#each CONTRACT_TYPES as type}
                <Select.SelectItem value={type.value} label={type.label}>
                  {type.label}
                </Select.SelectItem>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>

        <!-- Type de rémunération -->
        <div class="space-y-1.5">
          <Label class="text-[0.83rem] text-slate-900 font-medium">
            Type de rémunération *
          </Label>
          <Select.Root
            type="single"
            bind:value={onboardingStore.data.contract.remuneration_type}
          >
            <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer">
              {REMUNERATION_TYPES.find((t: any) => t.value === onboardingStore.data.contract.remuneration_type)?.label ?? "Sélectionner..."}
            </Select.Trigger>
            <Select.Content>
              {#each REMUNERATION_TYPES as type}
                <Select.SelectItem value={type.value} label={type.label}>
                  {type.label}
                </Select.SelectItem>
              {/each}
            </Select.Content>
          </Select.Root>
          <p class="text-[0.82rem] text-slate-500">
            {#if onboardingStore.data.contract.remuneration_type === 'FIXED'}
              Salaire mensuel fixe, indépendant des heures travaillées
            {:else if onboardingStore.data.contract.remuneration_type === 'HOURLY'}
              Payé à l'heure selon le temps de travail effectif
            {/if}
          </p>
          <ValidationError errors={validationErrors} field="remuneration_type" />
        </div>

        <!-- Statut initial -->
        <div class="space-y-1.5">
          <Label class="text-[0.83rem] text-slate-900 font-medium">
            Statut initial *
          </Label>
          <Select.Root
            type="single"
            bind:value={onboardingStore.data.contract.initial_status}
          >
            <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer">
              {initialStatusOptions.find((o) => o.value === onboardingStore.data.contract.initial_status)?.label ?? "Sélectionner..."}
            </Select.Trigger>
            <Select.Content>
              {#each initialStatusOptions as status}
                <Select.SelectItem value={status.value} label={status.label}>
                  {status.label}
                </Select.SelectItem>
              {/each}
            </Select.Content>
          </Select.Root>
          <p class="text-[0.82rem] text-slate-500">
            {#if onboardingStore.data.contract.initial_status === 'PROBATION'}
              Période d'essai pour évaluer les compétences de l'employé
            {:else}
              L'employé commence directement en statut actif
            {/if}
          </p>
        </div>
      </div>

      <!-- Salaire groupé : montant principal + type de salaire + devise (pleine largeur) -->
      <div class="space-y-1.5">
        <SalaryGroup
          id="salary"
          salary={onboardingStore.data.contract.salary}
          salaryBaseType={onboardingStore.data.contract.salary_base_type}
          currency={onboardingStore.data.contract.currency}
          remunerationType={onboardingStore.data.contract.remuneration_type}
          onSalaryChange={(v) => onboardingStore.setContractField('salary', v)}
          onSalaryBaseTypeChange={(v) => onboardingStore.setContractField('salary_base_type', v as 'BASE' | 'NET')}
          onCurrencyChange={(v) => onboardingStore.setContractField('currency', v as 'CDF' | 'USD' | 'EUR')}
        />
        {#if onboardingStore.data.contract.remuneration_type === 'HOURLY' && monthlyEquivalent()}
          <p class="text-[0.82rem] text-slate-500 mt-1">
            ≈ {monthlyEquivalent()} {currencyName()}/mois
            <span class="text-slate-400" title="Calcul : {workHoursPerWeek} h/semaine × 52 semaines / 12 mois = {workHoursPerMonth} heures/mois">
              (estimation {workHoursPerWeek} h/sem → {workHoursPerMonth} h/mois)
            </span>
          </p>
        {/if}
        <ValidationError errors={validationErrors} field="salary" />
        <ValidationError errors={validationErrors} field="currency" />
      </div>
    </div>

    <!-- Section 3 : Période du contrat -->
    <div class="space-y-3">
      <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
        Période du contrat
      </h4>
      <div class="grid grid-cols-1 md:grid-cols-2 gap-x-8 gap-y-5">
        <!-- Date de début -->
        {@render InputGroup(
          "hire_date",
          "Date de début *",
          "",
          "date",
          onboardingStore.data.contract.hire_date,
          (v) => onboardingStore.setContractField('hire_date', v)
        )}

        <!-- Date de fin (optionnel) -->
        {@render InputGroup(
          "end_date",
          "Date de fin",
          "",
          "date",
          onboardingStore.data.contract.end_date,
          (v) => onboardingStore.setContractField('end_date', v),
        )}
      </div>
    </div>

    <!-- Section 4 : Clauses particulières -->
    <div class="space-y-3">
      <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
        Clauses particulières
      </h4>
      <div class="space-y-1.5">
        <Label for="onb-clauses" class="text-[0.83rem] text-slate-900 font-medium">
          Conditions négociées
        </Label>
        <Textarea
          id="onb-clauses"
          rows={3}
          placeholder="Clause de non-concurrence, période d'essai, avantages spécifiques…"
          bind:value={onboardingStore.data.contract.contractual_clauses}
          class="min-h-20 bg-white border-slate-200 shadow-fine resize-y"
        />
        <p class="text-[0.82rem] text-slate-500">
          Conditions particulières négociées au contrat (facultatif).
        </p>
      </div>
    </div>

    <!-- Section 5 : Éléments de paie -->
    <ContractPayElementList
      {catalog}
      elements={contractAdjustments}
      variant="section"
      showToggle={false}
      onAdd={handleAddPayElement}
      onDelete={handleRemovePayElement}
    />
  </CardContent>
</Card>

