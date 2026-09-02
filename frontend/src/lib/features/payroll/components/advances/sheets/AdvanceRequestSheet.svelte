<script lang="ts">
  import * as Sheet from "@/components/ui/sheet";
  import { Button } from "@/components/ui/button";
  import { Input } from "@/components/ui/input";
  import { Label } from "@/components/ui/label";
  import { Select, SelectContent, SelectItem, SelectTrigger } from "@/components/ui/select";
  import AppIcon from "@/components/layout/elements/AppIcon.svelte";
  import { notification } from "@/stores/notification.svelte";
  import { payrollStore } from "../../../stores/payroll.svelte";
  import { useAllEmployees } from "@/features/employees/queries/employeeQueries";
  import { employeesService } from "@/features/employees/services/employees.service";
  import { buildFullName } from "@/utilities/common/employee.utils";
  import { Avatar, AvatarFallback, AvatarImage } from "@/components/ui/avatar";
  import { getInitials } from "@/utilities/common/string";
  import { getAvatarPalette } from "@/utilities/common/func";
  import { getMediaUrl } from "@/utilities/common/media";
  import { cn } from "@/utilities/common/css";
  import { fade } from "svelte/transition";
  import AnimateSpin from "@/components/layout/elements/AnimateSpin.svelte";
  import ValidationError from "@/components/ui/validation-error";
  import { Textarea } from "@/components/ui/textarea";
  import * as DropdownMenu from "@/components/ui/dropdown-menu";
  import { payrollConfigStore } from "../../../stores/configuration/payrollConfigStore.svelte";
  import type { EmployeeFullProfile } from "@/features/employees/types/types";
  import type { Advance } from "../../../types/types";


  let {
    open = $bindable(false),
    advance = null as Advance | null
  }: {
    open: boolean;
    advance?: Advance | null;
  } = $props();

  const isEdit = $derived(!!advance);

  // --- Form state ---
  let formEmployeeId = $state<string | undefined>(undefined);
  let formAmount = $state('');
  let formReason = $state('');

  // Devise du montant (défaut : devise du contrat de l'employé sélectionné)
  let currency = $state<'CDF' | 'USD'>('CDF');

  // Employés réels issus de la base de données.
  // On ne propose que les employés ayant un contrat actif : le backend garantit
  // qu'ils sont en activité (suspendus, offboardés, résiliés ou sans contrat exclus).
  const employeesQuery = useAllEmployees(() => ({ has_active_contract: true }));
  const allEmployees = $derived($employeesQuery.data || []);

  const selectedEmployeeObj = $derived(
    formEmployeeId
      ? allEmployees.find(e => String(e.id) === formEmployeeId)
      : undefined
  );

  // Profil détaillé → contrat actif (salaire réel, devise, base de déduction)
  // Pattern réactif du projet : fetch impératif dans un $effect (fiabilité Svelte 5)
  let employeeDetail = $state<EmployeeFullProfile | null>(null);
  let employeeDetailLoading = $state(false);

  $effect(() => {
    const empId = formEmployeeId;
    if (!empId) {
      employeeDetail = null;
      return;
    }
    let cancelled = false;
    employeeDetailLoading = true;
    employeesService.getEmployeeDetail(empId)
      .then((profile) => {
        if (!cancelled) {
          employeeDetail = profile;
          employeeDetailLoading = false;
        }
      })
      .catch(() => {
        if (!cancelled) {
          employeeDetail = null;
          employeeDetailLoading = false;
        }
      });
    return () => { cancelled = true; };
  });

  // Le backend précharge le "latest contract" (trié -is_active, -start_date), mais il peut
  // renvoyer un contrat suspendu/résilié s'il n'y a pas d'actif. On ne retient que l'actif.
  const currentContract = $derived(
    employeeDetail?.current_contract && employeeDetail.current_contract.is_active
      ? employeeDetail.current_contract
      : null
  );

  // Salaire réel du contrat (brut ou net selon salary_base_type)
  const contractSalary = $derived(
    currentContract?.remuneration_type === 'HOURLY'
      ? (currentContract.hourly_rate ?? 0)
      : (currentContract?.base_salary ?? 0)
  );

  // Devise du contrat
  const contractCurrency = $derived((currentContract?.currency || 'CDF') as 'CDF' | 'USD');

  // --- Formulaire ---
  const parsedAmount = $derived(parseFloat(formAmount) || 0);

  const exchangeRate = $derived(
    currency === 'CDF' ? 1 : (payrollConfigStore.exchangeRate || 0)
  );

  // Montant ramené dans la devise du contrat pour comparer au salaire (règle RDC)
  // Le taux courant (BCC) donne USD→CDF ; on l'inverse pour CDF→USD.
  const amountInContractCurrency = $derived.by(() => {
    if (parsedAmount <= 0) return 0;
    const rate = exchangeRate || 0;
    if (currency === contractCurrency) return parsedAmount;
    if (currency === 'USD' && contractCurrency === 'CDF') return rate > 0 ? parsedAmount * rate : parsedAmount;
    if (currency === 'CDF' && contractCurrency === 'USD') return rate > 0 ? parsedAmount / rate : parsedAmount;
    return parsedAmount;
  });

  // Salaire réel (dans la devise du contrat) — pour le calcul du % de retenue
  const effectiveSalary = $derived(
    contractSalary > 0 ? contractSalary : 0
  );

  // Plafond RDC : 50 % du salaire de base (même règle que le backend, sur la devise du contrat)
  const maxAmount = $derived(
    effectiveSalary > 0 ? Math.floor(effectiveSalary * 0.5) : 0
  );
  const exceedsCap = $derived(maxAmount > 0 && amountInContractCurrency > maxAmount);

  // --- Validation state ---
  let validationErrors = $state<Record<string, string>>({});

  function clearValidationError(field: string) {
    validationErrors = { ...validationErrors, [field]: '' };
  }

  function validateForm(): boolean {
    validationErrors = {};

    if (!formEmployeeId) {
      validationErrors = { ...validationErrors, employee_id: 'Veuillez sélectionner un employé' };
    }
    if (!parsedAmount || parsedAmount <= 0) {
      validationErrors = { ...validationErrors, amount: 'Veuillez entrer un montant valide' };
    }
    if (exceedsCap) {
      validationErrors = { ...validationErrors, amount: `Le montant ne peut pas dépasser 50 % du salaire (${maxAmount.toLocaleString('fr-FR')} ${currency})` };
    }
    if (!formReason.trim()) {
      validationErrors = { ...validationErrors, reason: 'Veuillez indiquer le motif de la demande' };
    }

    return Object.keys(validationErrors).length === 0;
  }

  // Reset validation errors when sheet opens
  $effect(() => {
    if (open) {
      validationErrors = {};
    }
  });

  // Reset / pré-remplissage quand le sheet s'ouvre
  $effect(() => {
    if (open) {
      if (advance) {
        // Mode édition: préremplir depuis le brouillon
        formEmployeeId = typeof advance.employee === 'object' && advance.employee?.id
          ? String(advance.employee.id)
          : undefined;
        formAmount = String(advance.amount ?? '');
        formReason = advance.reason ?? '';
        currency = (advance.currency as 'CDF' | 'USD') || 'CDF';
      } else {
        // Mode création
        formEmployeeId = undefined;
        formAmount = '';
        formReason = '';
        currency = 'CDF';
      }
      validationErrors = {};
    }
  });

  // Quand un employé est sélectionné → initialiser la devise depuis son contrat
  $effect(() => {
    if (currentContract && formEmployeeId) {
      currency = contractCurrency;
    }
  });

  let isSaving = $state(false);

  async function handleSubmit(submit: boolean) {
    if (!validateForm()) {
      notification.toast.error('Veuillez corriger les erreurs du formulaire');
      return;
    }

    isSaving = true;
    try {
      if (isEdit && advance) {
        // Édition d'un brouillon → PATCH (montant + motif uniquement)
        await payrollStore.updateAdvanceFields(advance.id, {
          amount: parsedAmount,
          reason: formReason,
        });
        // Si l'utilisateur choisit "Soumettre", on passe DRAFT → PENDING
        if (submit) {
          await payrollStore.submitAdvance(advance.id);
        }
        notification.toast.success(submit ? "Demande soumise pour approbation" : "Brouillon mis à jour");
      } else {
        await payrollStore.requestAdvance({
          employee: formEmployeeId as string,
          amount: parsedAmount,
          reason: formReason,
          currency,
          submit,
        });
        notification.toast.success(submit ? "Demande d'avance soumise avec succès" : "Brouillon enregistré");
      }
      open = false;
    } catch {
      // Erreur déjà gérée par le store
    } finally {
      isSaving = false;
    }
  }
</script>


<Sheet.Root bind:open>
  <Sheet.Content side="right" class="sm:max-w-xl bg-white p-0 flex flex-col h-full overflow-hidden">
    <!-- Header aligned with TransitionSheet -->
    <Sheet.Header class="px-6 py-2.5 border-b bg-slate-50/50">
      <Sheet.Title class="text-[1rem] text-slate-900 truncate font-bold">
        {isEdit ? "Modifier le brouillon" : "Nouvelle demande d'avance"}
      </Sheet.Title>
    </Sheet.Header>

    <div class="flex-1 overflow-y-auto custom-scrollbar">
      <div class="p-4 space-y-7" in:fade={{ duration: 200 }}>

        <!-- Employé (Select Pattern) -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Employé <span class="text-red-500">*</span></Label>
          <Select type="single" value={formEmployeeId} onValueChange={(v) => { formEmployeeId = v; clearValidationError('employee_id'); }}>
            <SelectTrigger disabled={isEdit} class={cn(
              "h-10 w-full bg-white border-slate-200 shadow-fine rounded-md cursor-pointer",
              isEdit && "opacity-60 cursor-not-allowed",
              validationErrors.employee_id && "border-red-500"
            )}>
              {#if selectedEmployeeObj}
                {@const empFullName = buildFullName(selectedEmployeeObj) || ''}
                {@const empPalette = getAvatarPalette(empFullName)}
                <div class="flex items-center gap-2 truncate">
                  <Avatar class="h-8 w-8 rounded-full border border-slate-200 shrink-0">
                    <AvatarImage src={getMediaUrl(selectedEmployeeObj.profile_photo || selectedEmployeeObj.avatarUrl || '')} alt={empFullName} class="object-cover" />
                    <AvatarFallback class={cn("text-[0.6rem] font-bold", empPalette.bg, empPalette.text)}>
                      {getInitials(selectedEmployeeObj.last_name || '', selectedEmployeeObj.middle_name || '', selectedEmployeeObj.first_name || '')}
                    </AvatarFallback>
                  </Avatar>
                  <span class="text-sm font-medium truncate">{empFullName}</span>
                  {#if selectedEmployeeObj.orgUnit}
                    <span class="text-sm text-slate-400">({selectedEmployeeObj.orgUnit})</span>
                  {/if}
                </div>
              {:else}
                <span class="text-sm font-medium text-slate-400">Sélectionner un employé...</span>
              {/if}
            </SelectTrigger>
            <SelectContent class="z-9999 max-h-72">
              {#if $employeesQuery.isLoading}
                <AnimateSpin class="size-3 my-3" text="Chargement des employés" textPosition="right" />
              {:else if allEmployees.length === 0}
                <div class="px-3 py-3 text-slate-400 text-xs text-center flex items-center justify-center gap-1">
                  <AppIcon name="circle-x" size={15} class="text-slate-300" />
                  Aucun employé disponible
                </div>
              {:else}
                {#each allEmployees as employee}
                  {@const empFullName = buildFullName(employee) || ''}
                  {@const empPalette = getAvatarPalette(empFullName)}
                  {@const empPhoto = getMediaUrl(employee.profile_photo || employee.avatarUrl || '')}
                  <SelectItem value={employee.id.toString()} class="text-[0.85rem] py-2.5">
                    <div class="flex items-center gap-2.5 w-full min-w-0">
                      <Avatar class="h-9 w-9 rounded-full border border-slate-200 shrink-0">
                        <AvatarImage src={empPhoto} alt={empFullName} class="object-cover" />
                        <AvatarFallback class={cn("text-[0.6rem] font-bold", empPalette.bg, empPalette.text)}>
                          {getInitials(employee.last_name || '', employee.middle_name || '', employee.first_name || '')}
                        </AvatarFallback>
                      </Avatar>
                      <div class="flex flex-col min-w-0 flex-1">
                        <span class="text-sm font-medium text-slate-800 truncate">{empFullName}</span>
                        {#if employee.orgUnit || employee.jobTitle}
                          <span class="text-sm text-slate-500 truncate">
                            {employee.jobTitle || ''} {employee.orgUnit ? `(${employee.orgUnit})` : ''}
                          </span>
                        {/if}
                      </div>
                    </div>
                  </SelectItem>
                {/each}
              {/if}
            </SelectContent>
          </Select>
          {#if isEdit}
            <p class="text-[0.85rem] text-slate-500">
              L'employé ne peut pas être modifié sur un brouillon existant.
            </p>
          {/if}
          <ValidationError errors={validationErrors} field="employee_id" />
        </div>

        <!-- Salaire & plafond (rechargé à chaque sélection d'employé) -->
        {#if formEmployeeId}
          {#if effectiveSalary > 0}
            <div class={cn(
              "flex items-center justify-between rounded-lg px-3 py-2 text-[0.82rem] space-y-0",
              exceedsCap ? "bg-rose-50 text-rose-700 border border-rose-200" : "bg-slate-50 text-slate-500 border border-slate-100"
            )}>
              <span class="flex items-center gap-1.5 text-sm">
                <AppIcon name={exceedsCap ? "alert-circle" : "shield-check"} size={16} class={exceedsCap ? "text-rose-500" : "text-emerald-500"} />
                Salaire ({currentContract?.salary_base_type === 'GROSS' ? 'brut' : 'net'}) : {effectiveSalary.toLocaleString('fr-FR')} {contractCurrency}
              </span>
              <span class="font-semibold text-sm">50 % du salaire autorisé : {maxAmount.toLocaleString('fr-FR')} {contractCurrency}</span>
            </div>
          {:else if employeeDetailLoading}
            <div class="flex items-center gap-2 text-[0.82rem] text-slate-400 px-1">
              <AnimateSpin class="size-3" text="Chargement du salaire" textPosition="right"/>
            </div>
          {:else}
            <div class="flex items-center gap-2 text-[0.82rem] text-slate-400 px-1">
              <AppIcon name="info" size={16} />
              Aucun contrat actif trouvé pour l'employé.
            </div>
          {/if}
        {/if}

        <!-- Devise -->
        <div class="space-y-2.5">
          <Label class="text-slate-900">Devise</Label>
          <div class="flex gap-2">
            <button
              type="button"
              onclick={() => currency = 'CDF'}
              class={cn(
                "flex-1 h-10 rounded-md border text-sm font-medium transition-all cursor-pointer",
                currency === 'CDF' ? "border-primary bg-primary/5 text-primary" : "border-slate-200 text-slate-400 hover:border-slate-300"
              )}
            >
              🇨🇩 Franc Congolais (CDF)
            </button>
            <button
              type="button"
              onclick={() => currency = 'USD'}
              class={cn(
                "flex-1 h-10 rounded-md border text-sm font-medium transition-all cursor-pointer",
                currency === 'USD' ? "border-primary bg-primary/5 text-primary" : "border-slate-200 text-slate-400 hover:border-slate-300"
              )}
            >
              🇺🇸 Dollar US (USD)
            </button>
          </div>
          {#if currentContract && currency !== contractCurrency}
            <p class="text-sm text-amber-600 flex items-center gap-1">
              <AppIcon name="info" size={13} />
              Le salaire de {selectedEmployeeObj ? buildFullName(selectedEmployeeObj) : 'cet employé'} est en {contractCurrency} — le plafond sera comparé après conversion.
            </p>
          {/if}
        </div>

        <!-- Montant -->
        <div class="space-y-2.5">
          <Label for="adv-amount" class="text-slate-900">Montant demandé ({currency}) <span class="text-red-500">*</span></Label>
          <div class="relative">
            <span class="absolute left-3 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-bold">
              {currency === 'USD' ? '$' : 'FC'}
            </span>
            <Input
              id="adv-amount"
              type="number"
              min="1"
              bind:value={formAmount}
              oninput={() => clearValidationError('amount')}
              placeholder={currency === 'USD' ? 'Ex: 500' : 'Ex: 500 000'}
              class={cn(
                "h-10 bg-white border-slate-200 focus:ring-1 focus:ring-primary rounded-md shadow-fine text-sm font-semibold pl-8",
                validationErrors.amount && "border-red-500 focus:ring-red-500"
              )}
            />
          </div>
          <ValidationError errors={validationErrors} field="amount" />
        </div>

        <!-- Motif -->
        <div class="space-y-2.5">
          <Label for="adv-reason" class="text-slate-900">Motif de la demande <span class="text-red-500">*</span></Label>
          <Textarea
            id="adv-reason"
            bind:value={formReason}
            oninput={() => clearValidationError('reason')}
            class={cn(
              "w-full h-28 rounded-lg border border-slate-200 px-3.5 py-3 text-[0.88rem] leading-relaxed focus:ring-4 focus:ring-primary/30 focus:border-primary focus:outline-none bg-white shadow-fine resize-none transition-all placeholder:text-slate-400",
              validationErrors.reason && "border-red-500 focus:ring-red-500"
            )}
            placeholder="Précisez le motif de la demande (ex: Urgence médicale, réparation véhicule...)"
          />
          <ValidationError errors={validationErrors} field="reason" />
        </div>
      </div>
    </div>

    <!-- Footer aligned with TransitionSheet -->
    <Sheet.Footer class="px-6 py-2.5 border-t bg-slate-50/50 flex flex-col gap-3">
      <div class="flex gap-3 w-full">
        <Sheet.Close class="flex-1">
          <Button variant="outline" class="w-full h-9 bg-white border-slate-200 shadow-fine text-slate-600 font-medium text-[0.88rem]">
            <AppIcon name="x" size={18} class="text-slate-300" />
            Annuler
          </Button>
        </Sheet.Close>

        <!-- Bouton split : Enregistrer (doux) en priorité + chevron (Soumettre) -->
        <div class="flex-1 flex items-stretch">
          <Button
            onclick={() => handleSubmit(false)}
            disabled={isSaving}
            class="flex-1 bg-primary! text-white font-medium h-9 shadow-fine text-[0.88rem] hover:opacity-90 transition-all disabled:opacity-70 rounded-r-none"
          >
            {#if isSaving}
              <AnimateSpin text="" class="size-3 border-white" />
            {:else}
              <AppIcon name="save" size={17} />
            {/if}
            Enregistrer comme brouillon
          </Button>
          <DropdownMenu.Root>
            <DropdownMenu.Trigger class="h-9 bg-primary! text-white rounded-l-none rounded-r-md border-l border-white/20 px-2.5 shadow-fine hover:opacity-90 transition-all cursor-pointer disabled:opacity-70">
              <AppIcon name="chevron-down" size={16} />
            </DropdownMenu.Trigger>
            <DropdownMenu.Content align="end" class="w-72 p-1 z-100">
              <DropdownMenu.Label class="text-[0.75rem] font-semibold text-slate-500 uppercase tracking-wider px-2 py-1.5">
                Actions
              </DropdownMenu.Label>
              <DropdownMenu.Item
                onclick={() => handleSubmit(true)}
                disabled={isSaving}
                class="text-[0.86rem] py-2 cursor-pointer flex items-center gap-2 bg-primary/10! text-primary! font-semibold"
              >
                <AppIcon name="send" size={15} />
                Soumettre la demande
              </DropdownMenu.Item>
              <DropdownMenu.Separator />
              <p class="px-2 py-1.5 text-[0.82rem] leading-relaxed text-slate-400">
                La soumission engage la demande : elle entre dans la file d'approbation RH et ne sera plus modifiable.
              </p>
            </DropdownMenu.Content>
          </DropdownMenu.Root>
        </div>
      </div>
    </Sheet.Footer>
  </Sheet.Content>
</Sheet.Root>

