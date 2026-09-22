<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { COUNTRY_OPTIONS } from '@/hr/modules/employees/constants/countries';
  import type { BankInstitution } from "../../../types/types";
  import {
    createForm, FormView,
    text, select, switchField, file,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let {
    open = $bindable(false),
    institution = $bindable(null),
    onCreate,
    onUpdate,
    onUploadLogo,
  }: {
    open: boolean;
    institution: BankInstitution | null;
    onCreate?: (data: any) => Promise<BankInstitution | void>;
    onUpdate?: (id: string, data: any) => Promise<BankInstitution | void>;
    onUploadLogo?: (bankId: string, file: File) => Promise<void>;
  } = $props();

  const TYPE_OPTIONS = [
    { value: 'bank', label: 'Banque Classique' },
    { value: 'mobile_money', label: 'Mobile Money' }
  ];

  const institutionFields: FieldConfig[] = [
    text('name', {
      label: "Nom de l'institution",
      required: true,
      placeholder: 'Ex: Equity BCDC...',
      validators: [validators.required('Le nom est requis')]
    }),
    text('shortName', {
      out: 'shortName',
      label: 'Nom court',
      required: true,
      placeholder: 'Ex: Equity...',
      maxLength: 10,
      validators: [
        validators.required('Le nom court est requis'),
        validators.maxLength(10, 'Le nom court ne doit pas dépasser 10 caractères')
      ]
    }),
    select('country', {
      label: 'Pays',
      required: true,
      defaultValue: 'CD',
      dataSource: { type: 'static', values: COUNTRY_OPTIONS.map(c => ({ value: c.value, label: c.label })) },
      validators: [validators.required('Le pays est requis')]
    }),
    select('type', {
      label: "Type d'entité",
      required: true,
      defaultValue: 'bank',
      dataSource: { type: 'static', values: TYPE_OPTIONS }
    }),
    text('swiftCode', {
      out: 'swiftCode',
      label: 'Code SWIFT / BIC',
      placeholder: 'Ex: EQUIBCKI...',
      maxLength: 11,
      dependencies: {
        visibleIf: (vals: Record<string, any>) => vals.type === 'bank'
      },
      validators: [
        validators.custom((value, ctx) => {
          if (ctx.values.type !== 'bank') return true;
          const v = (value as string)?.trim() ?? '';
          if (!v) return true;
          return v.length === 8 || v.length === 11;
        }, 'Le code SWIFT doit faire exactement 8 ou 11 caractères')
      ]
    }),
    file('logo', {
      label: "Logo de l'institution",
      accept: 'image/*'
    }),
    switchField('isActive', {
      out: 'isActive',
      label: 'Institution active',
      help: "Désactivez pour suspendre l'utilisation de cette institution",
      defaultValue: true
    })
  ];

  const form = createForm({
    id: 'bank-institution-form',
    fields: institutionFields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Identification', fields: ['name', 'shortName', 'country'] },
        { title: "Type & SWIFT", fields: ['type', 'swiftCode'] },
        { title: 'Logo', fields: ['logo'] },
        { title: 'Statut', fields: ['isActive'] }
      ]
    },
    onSubmit: async (data, extra) => {
      const payload = {
        name: data.name,
        shortName: data.shortName,
        country: data.country,
        type: data.type,
        swiftCode: data.swiftCode || '',
        isActive: data.isActive
      };
      let bankId: string | null = null;
      if (institution) {
        await onUpdate?.(institution.id, payload);
        bankId = institution.id;
      } else {
        const result = await onCreate?.(payload);
        bankId = (result as any)?.id ?? null;
      }
      const logoFile: File | undefined = (extra?.files?.logo?.[0] as File) ?? (data.logo as File) ?? undefined;
      if (logoFile && bankId) {
        await onUploadLogo?.(bankId, logoFile);
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });
</script>

<FormView
  {form}
  fields={institutionFields}
  bind:open
  entity={institution}
  title={institution ? "Modifier l'Institution" : "Nouvelle Institution"}
  submitLabel={institution ? "Mettre à jour" : "Enregistrer"}
  submitIcon="check"
  showReset={false}
  actions={[
    cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; institution = null; } })
  ]}
/>
