<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { payrollStore } from "../../../stores/payroll.svelte.js";
  import { employeesService } from "@/hr/modules/employees/services/employees.service";
  import { payrollConfigStore } from "../../../stores/configuration/payrollConfigStore.svelte";
  import type { Advance } from "../../../types/types";
  import type { EmployeeFullProfile } from "@/hr/modules/employees/types/types";
  import {
    createForm, FormView,
    employee, number, textarea, select,
    validators, invariant, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), advance = null as Advance | null } = $props<{ open: boolean; advance?: Advance | null }>();

  const isEdit = $derived(!!advance);

  // --- Salary context (single source of truth for validation) ---
  let profile = $state<EmployeeFullProfile | null>(null);
  let loadingProfile = $state(false);

  async function loadProfile(employeeId: string) {
    if (!employeeId) { profile = null; return; }
    loadingProfile = true;
    try { profile = await employeesService.getEmployeeDetail(employeeId); }
    catch { profile = null; }
    finally { loadingProfile = false; }
  }

  const contract = $derived(profile?.current_contract?.is_active ? profile.current_contract : null);
  const salary = $derived(contract?.remuneration_type === 'HOURLY' ? (contract.hourly_rate ?? 0) : (contract?.base_salary ?? 0));
  const contractCurrency = $derived((contract?.currency ?? 'CDF') as 'CDF' | 'USD');
  const maxAmount = $derived(salary > 0 ? Math.floor(salary * 0.5) : 0);

  // --- Fields ---
  const fields: FieldConfig[] = [
    employee('employeeId', {
      out: 'employee',
      label: 'Employé',
      required: true,
      disabled: isEdit,
      dataSource: { type: 'function', fn: () => import("@/hr/modules/employees/queries/employeeQueries").then(m => m.useAllEmployees) } as any,
      validators: [validators.required('Veuillez sélectionner un employé')]
    }),
    select('currency', {
      label: 'Devise',
      required: true,
      defaultValue: 'CDF',
      dataSource: { type: 'static', values: [{ value: 'CDF', label: '🇨🇩 Franc Congolais (CDF)' }, { value: 'USD', label: '🇺🇸 Dollar US (USD)' }] }
    }),
    number('amount', {
      label: 'Montant demandé',
      required: true,
      min: 1,
      placeholder: 'Ex: 500 000',
      validators: [validators.required('Le montant est requis'), validators.min(1, 'Montant invalide')]
    }),
    textarea('reason', {
      label: 'Motif de la demande',
      required: true,
      placeholder: 'Précisez le motif (ex: Urgence médicale...)',
      validators: [validators.required('Le motif est requis')]
    })
  ];

  const form = createForm({
    id: 'advance-request-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Bénéficiaire', fields: ['employeeId'] },
        { title: 'Montant', fields: ['currency', 'amount'] },
        { title: 'Motif', fields: ['reason'] }
      ]
    },
    validators: [
      invariant((values) => {
        if (!values.amount || !salary || maxAmount <= 0) return { valid: true };
        const rate = payrollConfigStore.exchangeRate || 2850;
        const amt = Number(values.amount);
        const cur = values.currency as 'CDF' | 'USD';
        let inContract = amt;
        if (cur !== contractCurrency) {
          inContract = cur === 'USD' ? amt * rate : amt / rate;
        }
        if (inContract > maxAmount) return { valid: false, field: 'amount' };
        return { valid: true };
      }, `Le montant ne peut pas dépasser 50% du salaire (${maxAmount} ${contractCurrency})`)
    ],
    onSubmit: async (data) => {
      // Determine submit intent via flag set by action handler
      const submit = (data as any).__submit === true;
      if (isEdit && advance) {
        await payrollStore.updateAdvanceFields(advance.id, { amount: Number(data.amount), reason: data.reason });
        if (submit) await payrollStore.submitAdvance(advance.id);
        notification.toast.success(submit ? "Demande soumise pour approbation" : "Brouillon mis à jour");
      } else {
        await payrollStore.requestAdvance({
          employee: String(data.employeeId),
          amount: Number(data.amount),
          reason: data.reason,
          currency: data.currency,
          submit
        });
        notification.toast.success(submit ? "Demande soumise avec succès" : "Brouillon enregistré");
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });

  // Keep currency in sync with contract + load profile on employee change
  $effect(() => {
    const empId = form.values.employeeId as string | undefined;
    if (empId) loadProfile(String(empId));
  });
  $effect(() => {
    if (contract && form.values.employeeId) {
      if (form.values.currency !== contractCurrency) form.setValue('currency' as any, contractCurrency as any);
    }
  });

  const entity = $derived(advance ? {
    employeeId: typeof advance.employee === 'object' ? String((advance.employee as any)?.id ?? '') : String(advance.employee ?? ''),
    amount: advance.amount,
    reason: advance.reason ?? '',
    currency: (advance.currency as string) ?? 'CDF'
  } : null);

  let submitIntent = $state(false);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={isEdit ? "Modifier le brouillon" : "Nouvelle demande d'avance"}
  submitLabel={submitIntent ? "Soumettre" : "Enregistrer comme brouillon"}
  submitIcon={submitIntent ? "send" : "save"}
  showReset={false}
  actions={[
    cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } }),
    { type: 'custom', label: submitIntent ? 'Brouillon' : 'Soumettre', variant: 'secondary', handler: async () => {
      submitIntent = !submitIntent;
      // toggle submit flag then submit programmatically
      (form.values as any).__submit = submitIntent;
      await form.submit();
      (form.values as any).__submit = false;
    }} as any
  ]}
>
  {#snippet extras()}
    {#if form.values.employeeId}
      {#if loadingProfile}
        <p class="text-[0.82rem] text-slate-400">Chargement du salaire…</p>
      {:else if salary > 0}
        <div class="rounded-lg px-3 py-2 text-[0.82rem] border {Number(form.values.amount) > 0 && maxAmount > 0 && (() => { const rate = payrollConfigStore.exchangeRate || 2850; const amt = Number(form.values.amount); const cur = form.values.currency; let ic = amt; if (cur !== contractCurrency) ic = cur === 'USD' ? amt*rate : amt/rate; return ic > maxAmount; })() ? 'bg-rose-50 text-rose-700 border-rose-200' : 'bg-slate-50 text-slate-500 border-slate-100'}">
          Salaire ({contract?.salary_base_type === 'BASE' ? 'base' : 'net'}) : {salary.toLocaleString('fr-FR')} {contractCurrency} · Plafond 50% : {maxAmount.toLocaleString('fr-FR')} {contractCurrency}
        </div>
      {:else}
        <p class="text-[0.82rem] text-amber-600">Aucun contrat actif pour cet employé.</p>
      {/if}
    {/if}
  {/snippet}
</FormView>
