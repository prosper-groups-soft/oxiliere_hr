<script lang="ts">
  import { onboardingStore } from "../../../stores/onboarding.svelte";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { 
    Card, 
    CardContent, 
    CardHeader, 
    CardTitle, 
    CardDescription 
  } from "@/components/ui/card";

  import { usePositionsQuery, useSeniorityLevelsQuery } from "../../../queries/onboardingQueries";
  import ValidationError from "@/components/ui/validation-error/ValidationError.svelte";
  import { validateStep } from "../../../schemas/onboarding.schema";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import {
    REMUNERATION_TYPES,
    PAYMENT_PERIODS,
    SALARY_BASE_TYPES,
    CURRENCIES,
    CONTRACT_TYPES
  } from "../../../constants/contract";
  import { EMPLOYEE_STATUS_CONFIG } from "@/features/employees/constants/employeeStatus";
  import { getOrgUnitIcon } from "@/features/jobs/constants/orgUnit.constants";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";

  // Options pour le statut initial
  const initialStatusOptions = $derived([
    { value: 'PENDING', label: EMPLOYEE_STATUS_CONFIG['PENDING'].label },
    { value: 'PROBATION', label: EMPLOYEE_STATUS_CONFIG['PROBATION'].label },
    { value: 'ACTIVE', label: EMPLOYEE_STATUS_CONFIG['ACTIVE'].label }
  ]);

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

  let seniorityOptions = $state<Array<{value: string, label: string}>>([]);
  let hasSeniorityLevels = $state(false);

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

  // Logique conditionnelle selon le type de rémunération
  const showSalaryField = $derived(
    onboardingStore.data.contract.remuneration_type === 'FIXED'
  );
  const showHourlyRateField = $derived(
    onboardingStore.data.contract.remuneration_type === 'HOURLY'
  );

  // Calcul de l'équivalent mensuel pour le taux horaire
  const monthlyEquivalent = $derived(() => {
    if (showHourlyRateField && onboardingStore.data.contract.salary > 0) {
      // Estimation basée sur 160 heures/mois (standard)
      const monthly = onboardingStore.data.contract.salary * 160;
      return new Intl.NumberFormat('fr-FR').format(monthly);
    }
    return null;
  });

  // Obtenir le symbole monétaire selon la devise
  const currencySymbol = $derived(() => {
    switch (onboardingStore.data.contract.currency) {
      case 'USD': return '$';
      case 'EUR': return '€';
      case 'CDF': 
      default: return 'FC';
    }
  });

  // Obtenir le placeholder selon la devise
  const salaryPlaceholder = $derived(() => {
    switch (onboardingStore.data.contract.currency) {
      case 'USD': return '2500';
      case 'EUR': return '2200';
      case 'CDF': 
      default: return '2500';
    }
  });

  const hourlyPlaceholder = $derived(() => {
    switch (onboardingStore.data.contract.currency) {
      case 'USD': return '15.50';
      case 'EUR': return '13.75';
      case 'CDF': 
      default: return '15.50';
    }
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
        else if (error.includes('période')) errors.payment_period = error;
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
        class="h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine {id === 'salary' || id === 'hourly_rate' ? 'pr-12' : ''}"
      />
      {#if id === 'salary' || id === 'hourly_rate'}
        <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 font-medium text-xs">
          {currencySymbol()}
        </span>
      {/if}
    </div>
    <ValidationError errors={validationErrors} field={id} />
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
  <CardContent class="px-0 py-0 space-y-5">
    <!-- Section Poste et Seniorité -->
    <div class="space-y-4">
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
            <div class="flex items-center gap-2 text-[0.8rem] text-slate-500 mt-1">
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
        </div>
      </div>
    </div>

    <!-- Section Type et Salaire -->
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
        <p class="text-[0.77rem] text-slate-500">
          {#if onboardingStore.data.contract.remuneration_type === 'FIXED'}
            Salaire mensuel fixe, indépendant des heures travaillées
          {:else if onboardingStore.data.contract.remuneration_type === 'HOURLY'}
            Payé à l'heure selon le temps de travail effectif
          {:else if onboardingStore.data.contract.remuneration_type === 'GROSS_UP'}
            Salaire calculé à partir du Net souhaité (Net à Brut)
          {/if}
        </p>
        <ValidationError errors={validationErrors} field="remuneration_type" />
      </div>

      <!-- Salaire ou taux horaire (conditionnel) -->
      {#if showSalaryField}
        {@render InputGroup(
          "salary",
          "Salaire de base *",
          salaryPlaceholder(),
          "number",
          onboardingStore.data.contract.salary,
          (v) => onboardingStore.setContractField('salary', parseFloat(v) || 0)
        )}
      {:else if showHourlyRateField}
        <div class="space-y-1.5">
          {@render InputGroup(
            "hourly_rate",
            "Taux horaire *",
            hourlyPlaceholder(),
            "number",
            onboardingStore.data.contract.salary,
            (v) => onboardingStore.setContractField('salary', parseFloat(v) || 0)
          )}
          <p class="text-[0.77rem] text-slate-500">
            {#if onboardingStore.data.contract.currency === 'USD'}
              Ex: 10.25 $/heure × 160h = ~1.640 $/mois
            {:else if onboardingStore.data.contract.currency === 'EUR'}
              Ex: 9.50 €/heure × 160h = ~1.520 €/mois
            {:else}
              Ex: 15.50 FC/heure × 160h = ~2.480 FC/mois
            {/if}
            {#if monthlyEquivalent()}
              <br>≈ {monthlyEquivalent()} {currencyName()}/mois (estimation 160h)
            {/if}
          </p>
        </div>
      {/if}

      <!-- Période de paiement -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">
          Période de paiement *
        </Label>
        <Select.Root
          type="single"
          bind:value={onboardingStore.data.contract.payment_period}
        >
          <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer">
            {PAYMENT_PERIODS.find((t: any) => t.value === onboardingStore.data.contract.payment_period)?.label ?? "Sélectionner..."}
          </Select.Trigger>
          <Select.Content>
            {#each PAYMENT_PERIODS as period}
              <Select.SelectItem value={period.value} label={period.label}>
                {period.label}
              </Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
        <p class="text-[0.77rem] text-slate-500">
          {#if onboardingStore.data.contract.payment_period === 'MONTHLY'}
            Payé une fois par mois (généralement fin de mois)
          {:else if onboardingStore.data.contract.payment_period === 'BIWEEKLY'}
            Payé toutes les 2 semaines (Quinzaine)
          {:else if onboardingStore.data.contract.payment_period === 'WEEKLY'}
            Payé chaque semaine
          {:else if onboardingStore.data.contract.payment_period === 'DAILY'}
            Payé à la fin de chaque journée de travail
          {:else if onboardingStore.data.contract.payment_period === 'PER_TASK'}
            Payé à la livraison de la tâche ou forfaitairement
          {/if}
        </p>
        <ValidationError errors={validationErrors} field="payment_period" />
      </div>

      <!-- Type de salaire -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">
          Base de calcul *
        </Label>
        <Select.Root
          type="single"
          bind:value={onboardingStore.data.contract.salary_base_type}
        >
          <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer">
            {SALARY_BASE_TYPES.find((t: any) => t.value === onboardingStore.data.contract.salary_base_type)?.label ?? "Sélectionner..."}
          </Select.Trigger>
          <Select.Content>
            {#each SALARY_BASE_TYPES as type}
              <Select.SelectItem value={type.value} label={type.label}>
                {type.label}
              </Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
        <p class="text-[0.77rem] text-slate-500">
          {#if onboardingStore.data.contract.salary_base_type === 'GROSS'}
            Salaire avant déduction des impôts et charges sociales (IPR, CNSS)
          {:else}
            Salaire après déduction, montant réellement perçu par l'employé
          {/if}
        </p>
      </div>

      <!-- Devise -->
      <div class="space-y-1.5">
        <Label class="text-[0.83rem] text-slate-900 font-medium">
          Devise *
        </Label>
        <Select.Root
          type="single"
          bind:value={onboardingStore.data.contract.currency}
        >
          <Select.Trigger class="h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer">
            {CURRENCIES.find((t: any) => t.value === onboardingStore.data.contract.currency)?.label ?? "Sélectionner..."}
          </Select.Trigger>
          <Select.Content>
            {#each CURRENCIES as currency}
              <Select.SelectItem value={currency.value} label={currency.label}>
                {currency.label}
              </Select.SelectItem>
            {/each}
          </Select.Content>
        </Select.Root>
        <ValidationError errors={validationErrors} field="currency" />
      </div>

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
        <p class="text-[0.77rem] text-slate-500">
          {#if onboardingStore.data.contract.initial_status === 'PROBATION'}
            Période d'essai pour évaluer les compétences de l'employé
          {:else}
            L'employé commence directement en statut actif
          {/if}
        </p>
      </div>
    </div>
  </CardContent>
</Card>

