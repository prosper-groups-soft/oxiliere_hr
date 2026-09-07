<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Button } from "@/components/ui/button";
  import * as Select from "@/components/ui/select";
  import ValidationError from "@/components/ui/validation-error";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { Switch } from "@/components/ui/switch";
  import { cn } from '@/utilities/common/css';
  import { usePositionsQuery, useSeniorityLevelsQuery } from "@/features/employees/queries/onboardingQueries";
  import { contractSchema } from "@/features/employees/schemas/onboarding.schema";
  import {
    REMUNERATION_TYPES,
    CURRENCIES,
    CONTRACT_TYPES,
    type RemunerationType,
    type SalaryBaseType,
    type Currency,
    type ContractType
  } from "@/features/employees/constants/contract";
  import { getOrgUnitIcon } from "@/features/jobs/constants/orgUnit.constants";
  import type { EmployeeFullProfile } from "@/features/employees/types/types";
  import { notification } from '@/stores/notification.svelte';
  import SalaryGroup from "@/features/employees/components/shared/SalaryGroup.svelte";
  import { payrollConfigStore } from "@/features/payroll/stores/configuration/payrollConfigStore.svelte";

  
  let { employee, onSave } = $props<{
    employee: EmployeeFullProfile;
    onSave: (data: any) => void;
  }>();

  let formData = $state({
    position_id: '',
    seniority_level_id: '',
    contract_type: 'CDI' as ContractType,
    remuneration_type: 'FIXED' as RemunerationType,
    salary: 0,
    salary_base_type: 'NET' as SalaryBaseType,
    currency: 'CDF' as Currency,
    hire_date: '',
    end_date: '',
    is_active: true,
    // Métamodèle : clauses
    contractual_clauses: ''
  });

  // Validation state
  let validationErrors = $state<Record<string, string>>({});
  let isValid = $state(false);

  // Charge la configuration (heures légales/semaine) au montage si elle n'est pas déjà en mémoire.
  $effect(() => {
    if (!payrollConfigStore.configuration) {
      payrollConfigStore.syncConfiguration();
    }
  });

  // Load initial data
  $effect(() => {
    if (employee) {
      const contract = employee.current_contract;
      // Use snake_case to match backend EmployeeFullProfileOut schema
      formData.position_id = employee.position_id || '';
      formData.seniority_level_id = employee.seniority_level_id || '';
      
      formData.contract_type = (contract?.contract_type as ContractType) || 'CDI';
      formData.remuneration_type = (contract?.remuneration_type as RemunerationType) || 'FIXED';
      
      // Map salary based on remuneration type (ensure number parsing)
      formData.salary = contract?.remuneration_type === 'HOURLY' 
        ? parseFloat(String(contract?.hourly_rate || 0)) 
        : parseFloat(String(contract?.base_salary || 0));
        
      formData.salary_base_type = (contract?.salary_base_type as SalaryBaseType) || 'NET';
      formData.currency = (contract?.currency as Currency) || 'CDF';
      
      // Dates: prioritize contract dates over employee hire date for contract form
      const startDate = contract?.start_date || employee.hire_date;
      formData.hire_date = startDate ? startDate.split('T')[0] : '';
      formData.end_date = contract?.end_date ? contract.end_date.split('T')[0] : (employee.termination_date ? employee.termination_date.split('T')[0] : '');
      
      formData.is_active = contract?.is_active ?? true;

      // Métamodèle (Règle 5) — clauses
      formData.contractual_clauses = contract?.contractual_clauses ?? '';
    }
  });

  // Reactive Validation
  $effect(() => {
    const result = contractSchema.safeParse(formData);
    if (!result.success) {
      const errors: Record<string, string> = {};
      result.error.issues.forEach((issue) => {
        const path = issue.path[0] as string;
        if (!errors[path]) errors[path] = issue.message;
      });
      validationErrors = errors;
      isValid = false;
    } else {
      validationErrors = {};
      isValid = true;
    }
  });

  // TanStack Queries
  const positionsQuery = usePositionsQuery();
  const seniorityQuery = $derived(
    useSeniorityLevelsQuery(formData.position_id)
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

  let seniorityOptions = $state<Array<{value: string, label: string}>>([]);
  let hasSeniorityLevels = $state(false);

  $effect(() => {
    const selectedPos = $positionsQuery.data?.find(p => p.id === formData.position_id);
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
          value: s.seniority_level?.id || s.id,
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
          value: s.seniority_level?.id || s.id,
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
    $positionsQuery.data?.find(p => p.id === formData.position_id)
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
    if (formData.remuneration_type === 'HOURLY' && formData.salary > 0) {
      const monthly = formData.salary * workHoursPerMonth;
      return new Intl.NumberFormat('fr-FR').format(monthly);
    }
    return null;
  });

  // Obtenir le nom complet de la devise pour les exemples
  const currencyName = $derived(() => {
    const currency = formData.currency;
    if (currency === CURRENCIES[1].value) return 'USD';
    if (currency === CURRENCIES[2].value) return 'EUR';
    return 'FC';
  });

  // Handle position change - clear seniority when position changes
  function handlePositionChange(newPositionId: string) {
    formData.position_id = newPositionId;
    formData.seniority_level_id = '';
  }

  // Submit logic exposed to parent
  export function submit() {
    const result = contractSchema.safeParse(formData);
    
    if (!result.success) {
      notification.toast.error("Veuillez corriger les erreurs dans le formulaire");
      return;
    }

    // Map UI data to Backend Unified Schema
    const submissionData = {
      ...formData,
      // Backend expects base_salary or hourly_rate depending on remuneration_type
      base_salary: formData.remuneration_type === 'FIXED' ? formData.salary : null,
      hourly_rate: formData.remuneration_type === 'HOURLY' ? formData.salary : null,
    };
    
    onSave(submissionData);
  }
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
        class="h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine"
      />
      <ValidationError errors={validationErrors} field={id} />
    </div>
  </div>
{/snippet}


<div id="contract-form" class="p-1 space-y-8">

  <!-- Section Poste et Seniorité -->
  <div class="space-y-4">
    <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
      Poste et Unité organisationnelle
    </h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Poste -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">
          Poste *
        </Label>
        <Select.Root
          type="single"
          value={formData.position_id}
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
            <Select.Content class="max-h-60 z-100">
              {#each positionOptions as opt}
                <Select.SelectItem value={opt.value} label={opt.label}>
                  <div class="flex flex-col">
                    <span class="text-[0.86rem]">{opt.label}</span>
                    <span class="text-[0.86rem] text-slate-400 flex items-center gap-1">
                      <AppIcon name={getOrgUnitIcon(opt.org_unit_type)} size={15} />
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
          <div class="flex items-center gap-2 text-[0.86rem] text-slate-500 mt-1">
            <AppIcon name={getOrgUnitIcon(selectedPosition.org_unit?.type || '')} size={15} />
            Unité: {selectedPosition.org_unit?.name}
          </div>
        {/if}
      </div>

      <!-- Niveau de seniorité -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">
          Niveau de séniorité *
        </Label>
        <Select.Root
          type="single"
          bind:value={formData.seniority_level_id}
          disabled={!formData.position_id || !hasSeniorityLevels || $seniorityQuery.isLoading || $seniorityQuery.isError}
        >
          <Select.Trigger 
            class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer flex items-center justify-between disabled:bg-slate-50 disabled:text-slate-400 disabled:cursor-not-allowed"
          >
            {#if !formData.position_id}
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
                {seniorityOptions.find((o) => o.value === formData.seniority_level_id)?.label ?? "Sélectionner..."}
              </span>
            {/if}
          </Select.Trigger>

          {#if $seniorityQuery.isSuccess && seniorityOptions.length > 0}
          <Select.Content class="max-h-60 z-100">
              {#each seniorityOptions as opt (opt.value)}
                <Select.SelectItem value={opt.value} label={opt.label}>
                  {opt.label}
                </Select.SelectItem>
              {/each}
            </Select.Content>
          {/if}
        </Select.Root>
        <ValidationError errors={validationErrors} field="seniority_level_id" />
      </div>
    </div>
  </div>

  <!-- Section Type et Rémunération -->
  <div class="space-y-4">
    <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
      Type de contrat et Rémunération
    </h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Type de contrat -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">
          Type de contrat *
        </Label>
        <Select.Root
          type="single"
          bind:value={formData.contract_type}
        >
          <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer truncate">
            {CONTRACT_TYPES.find((t: any) => t.value === formData.contract_type)?.label ?? "Sélectionner..."}
          </Select.Trigger>
          <Select.Content class="z-100">
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
          bind:value={formData.remuneration_type}
        >
          <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer">
            {REMUNERATION_TYPES.find((t: any) => t.value === formData.remuneration_type)?.label ?? "Sélectionner..."}
          </Select.Trigger>
          <Select.Content class="z-100">
            {#each REMUNERATION_TYPES as type}
              <Select.SelectItem value={type.value} label={type.label}>
                {type.label}
              </Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
        <p class="text-[0.77rem] text-slate-500">
          {#if formData.remuneration_type === 'FIXED'}
            Salaire mensuel fixe, indépendant des heures travaillées
          {:else if formData.remuneration_type === 'HOURLY'}
            Payé à l'heure selon le temps de travail effectif
          {/if}
        </p>
        <ValidationError errors={validationErrors} field="remuneration_type" />
      </div>

      <!-- Salaire groupé : montant principal + type de salaire + devise -->
      <div class="md:col-span-3">
        <SalaryGroup
          id="salary"
          salary={formData.salary}
          salaryBaseType={formData.salary_base_type}
          currency={formData.currency}
          remunerationType={formData.remuneration_type}
          onSalaryChange={(v) => formData.salary = v}
          onSalaryBaseTypeChange={(v) => formData.salary_base_type = v as SalaryBaseType}
          onCurrencyChange={(v) => formData.currency = v as Currency}
        />
        {#if formData.remuneration_type === 'HOURLY' && monthlyEquivalent()}
          <p class="text-[0.86rem] text-slate-500 mt-1">
            ≈ {monthlyEquivalent()} {currencyName()}/mois
            <span class="text-slate-400 text-[0.86rem]" title="Calcul : {workHoursPerWeek} h/semaine × 52 semaines / 12 mois = {workHoursPerMonth} heures/mois">
              (Estimation {workHoursPerWeek} h/sem → {workHoursPerMonth} h/mois)
            </span>
          </p>
        {/if}
        <ValidationError errors={validationErrors} field="salary" />
        <ValidationError errors={validationErrors} field="currency" />
      </div>
    </div>
  </div>

  <!-- Section Dates -->
  <div class="space-y-4">
    <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
      Dates du contrat
    </h4>
    <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
      <!-- Date de début -->
      {@render InputGroup(
        "hire_date",
        "Date de début *",
        "",
        "date",
        formData.hire_date,
        (v) => formData.hire_date = v
      )}

      <!-- Date de fin (optionnel) -->
      {@render InputGroup(
        "end_date",
        "Date de fin",
        "",
        "date",
        formData.end_date,
        (v) => formData.end_date = v
      )}
    </div>
  </div>

  <!-- Section Métamodèle (Règle 5) -->
  <div class="space-y-4">
    <!-- Clauses particulières -->
    <div class="space-y-1.5">
      <Label for="contractual_clauses" class="text-[0.83rem] text-slate-900 font-medium">
        Clauses particulières
      </Label>
      <textarea
        id="contractual_clauses"
        rows="4"
        placeholder="Clause de non-concurrence, période d'essai, avantages spécifiques, obligations de confidentialité…"
        value={formData.contractual_clauses}
        oninput={(e) => (formData.contractual_clauses = e.currentTarget.value)}
        class="w-full h-10 min-h-24 rounded-md border border-slate-200 bg-white px-3 py-2 text-sm shadow-fine focus:ring-1 focus:ring-primary focus:border-primary outline-none resize-y"
      ></textarea>
      <p class="text-[0.77rem] text-slate-500">
        Conditions particulières négociées au contrat (facultatif).
      </p>
    </div>
  </div>

  <!-- Section Statut -->
  <div class="space-y-4">
    <h4 class="text-[0.9rem] font-bold text-slate-900 border-b border-slate-100 pb-2">
      Statut du contrat
    </h4>
    <div class="flex items-center justify-between p-4 rounded-xl border border-slate-200 bg-slate-50/30">
      <div class="flex items-center gap-3">
        <div class={cn(
          "w-10 h-10 rounded-lg flex items-center justify-center border",
          formData.is_active ? "bg-emerald-50 text-emerald-600 border-emerald-100" : "bg-slate-100 text-slate-400 border-slate-200"
        )}>
          <AppIcon name={formData.is_active ? "circle-check" : "circle-pause"} size={20} />
        </div>
        <div>
          <div class="text-[0.85rem] font-bold text-slate-900">
            {formData.is_active ? "Contrat actif" : "Contrat suspendu"}
          </div>
          <div class="text-[0.75rem] text-slate-500">
            {formData.is_active ? "L'employé est actuellement sous contrat" : "L'accès et la rémunération sont suspendus"}
          </div>
        </div>
      </div>
      <Switch 
        bind:checked={formData.is_active} 
        id="contract-active" 
        class="cursor-pointer"
      />
    </div>
  </div>
</div>

