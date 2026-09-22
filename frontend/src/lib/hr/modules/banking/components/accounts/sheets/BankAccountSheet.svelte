<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { CURRENCIES } from "@/hr/constants/finance";
  import type { BankAccount, Currency } from "../../../types/types";
  import { useCreateAccountMutation, useUpdateAccountMutation } from "../../../queries/bankingQueries";
  import {
    createForm, FormView,
    employee, bankInstitution, select, switchField, text, textarea,
    validators, cancel, regSelect
  } from "@/hr/forms/index.js";
  import { persist } from "@/hr/forms-bindings/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), account = $bindable(null) }: { open: boolean, account: BankAccount | null } = $props();

  const createMutation = useCreateAccountMutation();
  const updateMutation = useUpdateAccountMutation();

  const CURRENCY_OPTIONS = Object.values(CURRENCIES).map((c) => ({ value: c, label: c }));

  const accountFields: FieldConfig[] = [
    employee('employeeId', { 
      out: 'employee_id', 
      label: 'Titulaire', 
      required: true, 
      validators: [validators.required("L'employé est requis")] 
    }),
    bankInstitution('institutionId', { 
      out: 'bank_id', 
      label: 'Banque', 
      required: true, 
      validators: [validators.required("La banque est requise")] 
    }),
    select('currencies', {
      label: 'Devises supportées',
      required: true,
      placeholder: 'Sélectionner les devises…',
      dataSource: { type: 'static', values: CURRENCY_OPTIONS },
      behaviors: [{ type: 'multiSelect' }],
      defaultValue: ['USD'],
      validators: [validators.required("Sélectionnez au moins une devise")]
    }),
    select('defaultCurrency', {
      out: 'default_currency',
      label: 'Devise par défaut',
      required: true,
      placeholder: 'Sélectionner…',
      dataSource: { type: 'static', values: CURRENCY_OPTIONS },
      defaultValue: 'USD',
      validators: [validators.required("La devise par défaut est requise")],
      // Cascade : la devise par défaut doit rester dans la liste supportée.
      dependencies: {
        dependsOn: 'currencies',
        compute: (values: Record<string, any>) => {
          const cs: Currency[] = values.currencies ?? [];
          const cur = values.defaultCurrency as Currency | null;
          return cur && cs.includes(cur) ? cur : (cs[0] ?? null);
        }
      }
    }),
    regSelect('bankAccountType', 'type', { out: 'account_type', label: 'Type de compte', required: true, defaultValue: 'checking', searchable: false }),
    switchField('isPrimary', { out: 'is_primary', label: 'Compte principal', defaultValue: true }),
    regSelect('bankAccountStatus', 'status', { label: 'Statut', defaultValue: 'pending', searchable: false }),
    text('accountNumber', {
      out: 'account_number',
      label: 'Numéro de compte',
      required: true,
      placeholder: 'Ex: 0001234567…',
      maxLength: 50,
      validators: [validators.required('Le numéro de compte est requis'), validators.maxLength(50, 'Le numéro de compte ne doit pas dépasser 50 caractères')]
    }),
    text('branchCode', {
      out: 'branch_code',
      label: 'Code guichet / Agence (Optionnel)',
      placeholder: 'Ex: 00123',
      maxLength: 10,
      validators: [validators.maxLength(10, 'Le code guichet ne doit pas dépasser 10 caractères')]
    }),
    text('iban', {
      label: 'IBAN (Optionnel)',
      placeholder: 'Ex: CD01…',
      maxLength: 34,
      validators: [validators.maxLength(34, "L'IBAN ne doit pas dépasser 34 caractères")]
    }),
    textarea('notes', { label: 'Notes (Optionnel)', placeholder: 'Informations complémentaires…' })
  ];

  const form = createForm({
    id: 'bank-account-form',
    fields: accountFields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-150' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Titulaire', fields: ['employeeId'] },
        { title: 'Institution & devises', fields: ['institutionId', 'currencies', 'defaultCurrency'] },
        { title: 'Type & statut', fields: ['type', 'isPrimary', 'status'] },
        { title: 'Coordonnées bancaires', fields: ['accountNumber', 'branchCode', 'iban'] },
        { title: 'Notes', fields: ['notes'] }
      ]
    },
    // Submit : tout le processus est dans le moteur (validation, payload avec
    // clés `out` + transform registre, isSubmitting, closeOnSubmit) — persist()
    // route le payload prêt vers les mutations (invalidation + toasts déjà
    // portés par la couche queries). account_name : champ volontairement hors
    // formulaire (parité avec l'ancien UI).
    onSubmit: persist({
      create: (payload) => $createMutation.mutateAsync(payload as any),
      update: ({ id, data }) => $updateMutation.mutateAsync({ accountId: id, data } as any),
      idOf: () => account?.id,
      merge: (data) => ({ ...data, account_name: account?.accountName ?? 'Compte Courant' })
    })
  });

  // Toast réservé aux erreurs de validation (l'objet d'erreurs est un objet
  // plat) — un échec de mutation émet une Error, déjà toastée par son onError.
  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });
</script>

<FormView
  {form}
  fields={accountFields}
  bind:open
  entity={account}
  title={account ? "Modifier le Compte" : "Nouveau Compte Bancaire"}
  submitLabel={account ? "Mettre à jour" : "Enregistrer"}
  submitIcon="check"
  showReset={false}
  actions={[
    cancel('Annuler', {
      icon: 'x',
      variant: 'secondary',
      handler: () => { open = false; account = null; }
    })
  ]}
/>
