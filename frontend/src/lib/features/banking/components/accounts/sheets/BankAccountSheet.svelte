<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Textarea } from "@/components/ui/textarea";
  import { Label } from "@/components/ui/label";
  import * as Select from "@/components/ui/select";
  import Switch from "@/components/ui/switch/switch.svelte";
  import { useAllEmployees } from "@/features/employees/queries/employeeQueries";
  import { CURRENCIES } from "@/constants/finance";
  import { notification } from "@/stores/notification.svelte";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { buildFullName } from "@/utilities/common/employee.utils";
  import { getMediaUrl } from "@/utilities/common/media";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import { cn } from "@/utilities/common/css";
  import type { BankAccount, Currency, AccountType, VerificationStatus } from "../../../types/types";
  import { ACCOUNT_TYPE_LABELS, VERIFICATION_STATUS_LABELS } from "../../../constants";
  import { useCreateAccountMutation, useUpdateAccountMutation, useBanksQuery } from "../../../queries/bankingQueries";
  import { z } from 'zod';
  import { bankAccountSchema } from "../../../schemas/bankAccount.schema";
  import ValidationError from "@/components/ui/validation-error";


  let { open = $bindable(false), account = $bindable(null) }: { open: boolean, account: BankAccount | null } = $props();

  const createMutation = useCreateAccountMutation();
  const updateMutation = useUpdateAccountMutation();
  const banksQuery = useBanksQuery();
  const employeesQuery = useAllEmployees();
  const allEmployees = $derived($employeesQuery.data || []);
  const institutions = $derived($banksQuery.data || []);

  const ALL_CURRENCIES: Currency[] = Object.values(CURRENCIES);

  let formData = $state({
    employeeId: "",
    institutionId: "",
    accountName: "Compte Courant",
    accountNumber: "",
    branchCode: "",
    iban: "",
    currencies: ["USD"] as Currency[],
    defaultCurrency: "USD" as Currency,
    type: "checking" as AccountType,
    isPrimary: true,
    status: "pending" as string,
    notes: "",
  });

  // Load account data for editing
  $effect(() => {
    if (account) {
      formData = {
        employeeId: account.employeeId,
        institutionId: account.institutionId,
        accountName: account.accountName,
        accountNumber: account.accountNumber,
        branchCode: account.branchCode || "",
        iban: account.iban || "",
        currencies: account.currencies,
        defaultCurrency: account.defaultCurrency,
        type: account.type,
        isPrimary: account.isPrimary,
        status: account.status,
        notes: account.notes || "",
      };
    } else {
      resetForm();
    }
  });

  const selectedEmployee = $derived(
    allEmployees.find((e: any) => String(e.id) === formData.employeeId)
  );
  const selectedInstitution = $derived(institutions.find(i => i.id === formData.institutionId));

  // Ensure defaultCurrency stays in currencies list
  $effect(() => {
    if (!formData.currencies.includes(formData.defaultCurrency)) {
      formData.defaultCurrency = formData.currencies[0] || "USD";
    }
  });

  function toggleCurrency(currency: Currency) {
    if (formData.currencies.includes(currency)) {
      // Don't remove if it's the last one
      if (formData.currencies.length <= 1) return;
      const newCurrencies = formData.currencies.filter(c => c !== currency);
      formData.currencies = newCurrencies;
      if (formData.defaultCurrency === currency) {
        formData.defaultCurrency = newCurrencies[0] || "USD";
      }
    } else {
      formData.currencies = [...formData.currencies, currency];
    }
  }

  function resetForm() {
    formData = {
      employeeId: "",
      institutionId: "",
      accountName: "Compte Courant",
      accountNumber: "",
      branchCode: "",
      iban: "",
      currencies: ["USD"],
      defaultCurrency: "USD",
      type: "checking",
      isPrimary: true,
      status: "pending",
      notes: "",
    };
  }

  function mapAccountType(type: AccountType): string {
    switch (type) {
      case 'checking': return 'CHECKING';
      case 'savings': return 'SAVINGS';
      case 'salary': return 'SALARY';
      case 'mobile_money': return 'OTHER';
      default: return 'CHECKING';
    }
  }

  function getAccountTypeLabel(type: AccountType): string {
    switch (type) {
      case 'checking': return 'Courant';
      case 'savings': return 'Épargne';
      case 'salary': return 'Salaire';
      case 'mobile_money': return 'Mobile Money';
    }
  }

  // --- Validation state ---
  let validationErrors = $state<Record<string, string>>({});
  let hasAttemptedSubmit = $state(false);

  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function validateForm(): boolean {
    validationErrors = {};
    
    const result = bankAccountSchema.safeParse({
      employeeId: formData.employeeId,
      institutionId: formData.institutionId,
      accountNumber: formData.accountNumber,
      accountName: formData.accountName,
      branchCode: formData.branchCode || undefined,
      iban: formData.iban || undefined,
      currencies: formData.currencies,
      defaultCurrency: formData.defaultCurrency,
      type: formData.type,
      isPrimary: formData.isPrimary,
      notes: formData.notes || undefined,
    });
    
    if (!result.success) {
      result.error.issues.forEach((err: z.core.$ZodIssue) => {
        const field = err.path.join('.');
        validationErrors = { ...validationErrors, [field]: err.message };
      });
      return false;
    }
    
    return true;
  }

  // Reset validation errors when modal opens
  $effect(() => {
    if (open) {
      validationErrors = {};
      hasAttemptedSubmit = false;
    }
  });

  async function handleSubmit() {
    if (!validateForm()) {
      hasAttemptedSubmit = true;
      notification.toast.error("Veuillez corriger les erreurs du formulaire");
      return;
    }

    try {
      const accountType = mapAccountType(formData.type);

      // Build complete payload for both create and update
      const payload: {
        employee_id: string;
        bank_id: string;
        account_number: string;
        account_name: string;
        account_type: string;
        currencies: string[];
        default_currency: string;
        branch_code?: string;
        iban?: string;
        is_primary: boolean;
        status?: string;
        notes?: string;
      } = {
        employee_id: formData.employeeId,
        bank_id: formData.institutionId,
        account_number: formData.accountNumber,
        account_name: formData.accountName,
        account_type: accountType,
        currencies: formData.currencies,
        default_currency: formData.defaultCurrency,
        branch_code: formData.branchCode || undefined,
        iban: formData.iban || undefined,
        is_primary: formData.isPrimary,
        status: formData.status.toUpperCase(),
        notes: formData.notes || undefined,
      };

      if (account) {
        // PATCH with all form data — backend uses exclude_unset=True so only provided fields are applied
        await $updateMutation.mutateAsync({
          accountId: account.id,
          data: payload,
        });
      } else {
        await $createMutation.mutateAsync(payload);
      }

      open = false;
      account = null;
      resetForm();
    } catch (e) {
      // Error handling is done by the mutation's onError callback
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl p-0 overflow-hidden flex flex-col bg-white h-full">
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="text-[0.95rem] font-bold text-slate-900 text-left">
        {account ? "Modifier le Compte" : "Nouveau Compte Bancaire"}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth custom-scrollbar">
      <!-- Section 1: Propriétaire -->
      <div class="space-y-4">
        <div class="space-y-2">
          <Label for="employee-select" class="text-[0.875rem] font-medium text-slate-700">Titulaire <span class="text-rose-500">*</span></Label>
          <Select.Root type="single" bind:value={formData.employeeId} onValueChange={() => clearValidationError('employeeId')}>
            <Select.Trigger id="employee-select" class={cn(
              "h-10 bg-white border-slate-200 rounded-md w-full shadow-fine font-normal text-[0.875rem] cursor-pointer",
              validationErrors.employeeId && "border-red-500"
            )}>
              {#if selectedEmployee}
                {@const empFullName = buildFullName(selectedEmployee) || ''}
                {@const empPalette = getAvatarPalette(empFullName)}
                {@const empPhoto = getMediaUrl(selectedEmployee.profile_photo || selectedEmployee.avatarUrl || '')}
                <div class="flex items-center gap-2 truncate">
                  <Avatar class="h-8 w-8 rounded-full border border-slate-200 shrink-0">
                    <AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
                    <AvatarFallback class={cn("text-[0.6rem] font-bold", empPalette.bg, empPalette.text)}>
                      {getInitials(selectedEmployee.last_name || '', selectedEmployee.middle_name || '', selectedEmployee.first_name || '')}
                    </AvatarFallback>
                  </Avatar>
                  <span class="text-[0.875rem] font-medium truncate">{empFullName}</span>
                </div>
              {:else}
                <span class="text-slate-400 text-[0.87rem]">Sélectionner un employé...</span>
              {/if}
            </Select.Trigger>
            <Select.Content class="max-h-60 z-100">
              {#if $employeesQuery.isLoading}
                <div class="flex items-center justify-center py-4 text-slate-400 text-[0.85rem]">
                  <AnimateSpin textPosition="right" text="Chargement des employés" class="size-3" />
                </div>
              {:else}
                {#each allEmployees as employee}
                  {@const empFullName = buildFullName(employee) || ''}
                  {@const empPalette = getAvatarPalette(empFullName)}
                  {@const empPhoto = getMediaUrl(employee.profile_photo || employee.avatarUrl || '')}
                  <Select.Item value={employee.id.toString()} class="py-2.5 cursor-pointer">
                    <div class="flex items-center gap-3">
                      <Avatar class="h-8.5 w-8.5 rounded-full border border-slate-200 shrink-0">
                        <AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
                        <AvatarFallback class={cn("text-[0.77rem] font-bold", empPalette.bg, empPalette.text)}>
                          {getInitials(employee.last_name || '', employee.middle_name || '', employee.first_name || '')}
                        </AvatarFallback>
                      </Avatar>
                      <div class="flex flex-col min-w-0">
                        <span class="text-[0.87rem] font-medium truncate">{empFullName}</span>
                        <span class="text-[0.8rem] text-slate-500 truncate">
                          {employee.jobTitle || employee.orgUnit || ''}
                        </span>
                      </div>
                    </div>
                  </Select.Item>
                {/each}
              {/if}
            </Select.Content>
          </Select.Root>
        </div>
      </div>

      <!-- Section 2: Institution -->
      <div class="space-y-4">
        <div class="space-y-2">
          <Label for="bank" class="text-[0.875rem] font-medium text-slate-700">Banque <span class="text-rose-500">*</span></Label>
          <Select.Root type="single" bind:value={formData.institutionId} onValueChange={() => clearValidationError('institutionId')}>
            <Select.Trigger id="bank" class={cn(
              "w-full h-10 border-slate-200 bg-white shadow-fine text-[0.875rem] font-normal",
              validationErrors.institutionId && "border-red-500"
            )}>
              {selectedInstitution?.name || "Sélectionnez une institution"}
            </Select.Trigger>
            <Select.Content class="bg-white border-slate-100 shadow-fine z-100 h-60 overflow-y-auto">
              {#each institutions as bank}
                <Select.Item value={bank.id} label={bank.name}>{bank.name}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
          <ValidationError errors={validationErrors} field="institutionId" />
        </div>

        <!-- Devises supportées (multi-select) -->
        <div class="space-y-2">
          <Label class="text-[0.875rem] font-medium text-slate-700">Devises supportées <span class="text-rose-500">*</span></Label>
          <div class="flex flex-wrap gap-2">
            {#each ALL_CURRENCIES as currency}
              <button
                type="button"
                onclick={() => toggleCurrency(currency)}
                class={cn(
                  "px-3 py-1.5 rounded-lg text-[0.82rem] font-medium border transition-all duration-200 cursor-pointer",
                  formData.currencies.includes(currency)
                    ? "bg-primary/10 border-primary/30 text-primary shadow-sm"
                    : "bg-white border-slate-200 text-slate-500 hover:border-slate-300"
                )}
              >
                {currency}
              </button>
            {/each}
          </div>
          {#if formData.currencies.length === 0}
            <p class="text-[0.78rem] text-rose-500">Sélectionnez au moins une devise</p>
          {/if}
          <ValidationError errors={validationErrors} field="currencies" />
        </div>

        <!-- Devise par défaut -->
        <div class="space-y-2">
          <Label class="text-[0.875rem] font-medium text-slate-700">Devise par défaut</Label>
          <Select.Root type="single" bind:value={formData.defaultCurrency}>
            <Select.Trigger class="w-full h-10 border-slate-200 bg-white shadow-fine uppercase text-[0.875rem] font-normal">
              {formData.defaultCurrency}
            </Select.Trigger>
            <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
              {#each formData.currencies as cur}
                <Select.Item value={cur} label={cur} class="uppercase">{cur}</Select.Item>
              {/each}
            </Select.Content>
          </Select.Root>
        </div>

        <div class="grid grid-cols-2 gap-4">
          <div class="space-y-2">
            <Label class="text-[0.875rem] font-medium text-slate-700">Type de compte</Label>
            <Select.Root type="single" bind:value={formData.type}>
              <Select.Trigger class="w-full h-10 border-slate-200 bg-white shadow-fine flex items-center gap-2 text-[0.875rem] font-normal">
                {getAccountTypeLabel(formData.type)}
              </Select.Trigger>
              <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
                {#each Object.entries(ACCOUNT_TYPE_LABELS) as [value, label]}
                  <Select.Item {value} label={label}>{label}</Select.Item>
                {/each}
              </Select.Content>
            </Select.Root>
          </div>

          <div class="space-y-2 flex flex-col justify-end pb-0.5">
            <div class="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-3 py-1.5 shadow-fine">
              <Label class="text-[0.875rem] font-medium text-slate-700 cursor-pointer">Compte principal</Label>
              <Switch bind:checked={formData.isPrimary} class="cursor-pointer" />
            </div>
          </div>
        </div>
      </div>

      <!-- Statut de vérification -->
      <div class="space-y-2">
        <Label class="text-[0.875rem] font-medium text-slate-700">Statut</Label>
        <Select.Root type="single" bind:value={formData.status}>
          <Select.Trigger class="w-full h-10 border-slate-200 bg-white shadow-fine text-[0.875rem] font-normal">
            {VERIFICATION_STATUS_LABELS[formData.status as VerificationStatus] || formData.status}
          </Select.Trigger>
          <Select.Content class="bg-white border-slate-100 shadow-fine z-100">
            {#each Object.entries(VERIFICATION_STATUS_LABELS) as [value, label]}
              <Select.Item {value} label={label}>{label}</Select.Item>
            {/each}
          </Select.Content>
        </Select.Root>
      </div>

    <!-- Section 3: Coordonnées bancaires -->
      <div class="space-y-4">
        <div class="space-y-2">
          <Label for="accNum" class="text-[0.875rem] font-medium text-slate-700">Numéro de Compte <span class="text-rose-500">*</span></Label>
          <Input id="accNum" bind:value={formData.accountNumber} oninput={() => clearValidationError('accountNumber')} placeholder="Ex: 0001234567..." class={cn(
            "h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]",
            validationErrors.accountNumber && "border-red-500"
          )} maxlength={50} />
          <ValidationError errors={validationErrors} field="accountNumber" />
        </div>

        <div class="space-y-2">
          <Label for="branchCode" class="text-[0.875rem] font-medium text-slate-700">Code guichet / Agence (Optionnel)</Label>
          <Input id="branchCode" bind:value={formData.branchCode} oninput={() => clearValidationError('branchCode')} placeholder="Ex: 00123" class={cn(
            "h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]",
            validationErrors.branchCode && "border-red-500"
          )} maxlength={10} />
          <ValidationError errors={validationErrors} field="branchCode" />
        </div>

        <div class="space-y-2">
          <Label for="iban" class="text-[0.875rem] font-medium text-slate-700">IBAN (Optionnel)</Label>
          <Input id="iban" bind:value={formData.iban} oninput={() => clearValidationError('iban')} placeholder="Ex: CD01..." class={cn(
            "h-10 border-slate-200 bg-white shadow-fine text-[0.875rem]",
            validationErrors.iban && "border-red-500"
          )} maxlength={34} />
          <ValidationError errors={validationErrors} field="iban" />
        </div>
      </div>

      <!-- Section 4: Notes -->
      <div class="space-y-4">
        <div class="space-y-2">
          <Label for="notes" class="text-[0.875rem] font-medium text-slate-700">Notes (Optionnel)</Label>
          <Textarea id="notes" bind:value={formData.notes} placeholder="Informations complémentaires..." class="min-h-20 border-slate-200 bg-white shadow-fine text-[0.875rem]" />
        </div>
      </div>
    </div>

    <Sheet.Footer class="px-6 py-2.5 border-t flex flex-row gap-3 sm:justify-start bg-slate-50/50">
      <Sheet.Close class="flex-1">
        <Button variant="outline" class="w-full h-9 rounded-md text-sm font-medium shadow-fine cursor-pointer" onclick={() => account = null}>
          <AppIcon name="x" size={18} class="text-slate-300" />
          Annuler
        </Button>
      </Sheet.Close>
      <Button 
        onclick={handleSubmit}
        disabled={$createMutation.isPending || $updateMutation.isPending || formData.currencies.length === 0 || (hasAttemptedSubmit && Object.keys(validationErrors).some(k => validationErrors[k]))}
        class="flex-1 h-9 rounded-md bg-primary text-white text-sm font-medium shadow-sm hover:shadow-md transition-all cursor-pointer disabled:opacity-50"
      >
        {#if $createMutation.isPending || $updateMutation.isPending}
          <AnimateSpin class="border-white size-3" text="" />
        {:else}
          <AppIcon name="check" size={18} />
        {/if}
        {account ? "Mettre à jour" : "Enregistrer"}
      </Button>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>




