<script lang="ts">
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import { SALARY_BASE_TYPES, CURRENCIES } from "@/features/employees/constants/contract";

  /**
   * SalaryGroup — composant groupé « Salaire de base ».
   *
   * Le salaire est le champ PRINCIPAL (grand input).
   * Le type de salaire (Brut/Net) et la devise sont des réglages secondaires
   * (petits selects à gauche du champ principal).
   *
   * Réutilisé par ContractStep (onboarding) et EmployeeContractForm (profil).
   */

  let {
    id = "salary-group",
    label = "Salaire de base",
    salary = 0,
    salaryBaseType = "NET",
    currency = "CDF",
    remunerationType = "FIXED",
    required = true,
    onSalaryChange,
    onSalaryBaseTypeChange,
    onCurrencyChange,
  }: {
    id?: string;
    label?: string;
    salary: number;
    salaryBaseType: string;
    currency: string;
    remunerationType?: string;
    required?: boolean;
    onSalaryChange: (val: number) => void;
    onSalaryBaseTypeChange: (val: string) => void;
    onCurrencyChange: (val: string) => void;
  } = $props();

  // Si le type de rémunération est HOURLY, le champ devient « Taux horaire »
  const isHourly = $derived(remunerationType === "HOURLY");
  const fieldLabel = $derived(isHourly ? "Taux horaire" : label);

  const currencySymbol = $derived(() => {
    if (currency === "USD") return "$";
    if (currency === "EUR") return "€";
    return "FC";
  });

  const placeholder = $derived(() => {
    if (isHourly) return currency === "USD" ? "15.50" : currency === "EUR" ? "13.75" : "15.50";
    return currency === "USD" ? "2500" : currency === "EUR" ? "2200" : "2500";
  });
</script>

<div class="space-y-1.5">
  <Label for={id} class="text-[0.83rem] text-slate-900 font-medium">
    {fieldLabel}{required ? " *" : ""}
  </Label>

  <div class="flex items-stretch gap-2">
    <!-- Petit select : Type de salaire (Brut/Net) -->
    <div class="w-28 shrink-0">
      <Select.Root type="single" value={salaryBaseType} onValueChange={(v) => onSalaryBaseTypeChange(v)}>
        <Select.Trigger id={`${id}-base-type`} class="h-9 py-0 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer px-2.5">
          {SALARY_BASE_TYPES.find((t: any) => t.value === salaryBaseType)?.label ?? "Sélectionner"}
        </Select.Trigger>
        <Select.Content class="z-100">
          {#each SALARY_BASE_TYPES as type}
            <Select.SelectItem value={type.value} label={type.label}>
              {type.label}
            </Select.SelectItem>
          {/each}
        </Select.Content>
      </Select.Root>
    </div>

    <!-- Petit select : Devise (label court dans le trigger) -->
    <div class="w-24 shrink-0">
      <Select.Root type="single" value={currency} onValueChange={(v) => onCurrencyChange(v)}>
        <Select.Trigger id={`${id}-currency`} class="h-9 py-0 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-sm cursor-pointer px-2.5">
          {currency}
        </Select.Trigger>
        <Select.Content class="z-100">
          {#each CURRENCIES as c}
            <Select.SelectItem value={c.value} label={c.label}>
              {c.label}
            </Select.SelectItem>
          {/each}
        </Select.Content>
      </Select.Root>
    </div>

    <!-- Champ principal : Salaire de base -->
    <div class="relative flex-1">
      <Input
        {id}
        type="number"
        min="0"
        placeholder={placeholder()}
        value={salary || ''}
        oninput={(e) => onSalaryChange(parseFloat(e.currentTarget.value) || 0)}
        class="h-9 bg-white border-slate-200 focus:ring-1 focus:ring-primary focus:border-primary rounded-md shadow-fine pr-14 text-right text-base font-semibold"
      />
      <span class="absolute right-3 top-1/2 -translate-y-1/2 text-slate-400 font-medium text-sm">
        {currencySymbol()}
      </span>
    </div>
  </div>
</div>
