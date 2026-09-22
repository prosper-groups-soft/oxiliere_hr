<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { DOCUMENT_TYPES } from "@/hr/modules/employees/constants/documents";
  import {
    createForm, FormView,
    text, select, date, file,
    validators
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { onSave, onCancel, initialData = null, isLoading = false } = $props<{
    onSave: (data: any) => void;
    onCancel: () => void;
    initialData?: any | null;
    isLoading?: boolean;
  }>();

  const fields: FieldConfig[] = [
    select('document_type', {
      label: 'Catégorie',
      required: true,
      defaultValue: 'OTHER',
      dataSource: { type: 'static', values: DOCUMENT_TYPES.map(t => ({ value: t.value, label: t.label })) },
      validators: [validators.required('La catégorie est requise')]
    }),
    text('document_number', { label: 'Nom / Référence', placeholder: 'ex: Attestation de domicile...' }),
    date('issue_date', { label: 'Délivré le (optionnel)' }),
    date('expiry_date', { label: 'Expire le (optionnel)' }),
    file('file', { label: 'Fichier', accept: '.pdf,.jpg,.jpeg,.png,.webp', required: !initialData, validators: initialData ? [] : [validators.required('Le fichier est requis')] })
  ];

  const form = createForm({
    id: 'document-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'inline', variant: 'plain' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Document', fields: ['document_type', 'document_number', 'issue_date', 'expiry_date'] },
        { title: 'Fichier', fields: ['file'] }
      ]
    },
    onSubmit: async (data, extra) => {
      const f = extra?.files?.file?.[0] ?? data.file;
      if (!f && !initialData) { notification.toast.error('Le fichier est requis'); throw new Error('Missing file'); }
      onSave({ document_type: data.document_type, document_number: data.document_number, issue_date: data.issue_date || undefined, expiry_date: data.expiry_date || undefined, file: f ?? data.file });
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    if (initialData) form.hydrate({ document_type: initialData.document_type, document_number: initialData.document_number ?? '', issue_date: initialData.issue_date?.split('T')[0] ?? '', expiry_date: initialData.expiry_date?.split('T')[0] ?? '' });
  });
</script>

<FormView {form} fields={fields} showSubmit={false} showReset={false} />

<div class="flex justify-end gap-2 mt-4 pt-3 border-t">
  <button type="button" onclick={onCancel} class="px-4 py-1.5 text-[0.84rem] text-slate-700 hover:bg-slate-50 rounded-md cursor-pointer">Annuler</button>
  <button type="button" disabled={isLoading} onclick={() => form.submit()} class="px-6 py-1.5 bg-primary text-white rounded-md text-[0.84rem] shadow-fine disabled:opacity-50 cursor-pointer">
    {initialData ? "Mettre à jour" : "Enregistrer"}
  </button>
</div>
