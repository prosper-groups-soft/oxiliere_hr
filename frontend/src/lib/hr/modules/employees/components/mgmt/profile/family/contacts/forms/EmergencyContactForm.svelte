<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { RELATION_TYPES } from "@/hr/modules/employees/constants/mappings";
  import type { EmployeeEmergencyContact } from "@/hr/modules/employees/types/types";
  import {
    createForm, FormView,
    text, phone, select, switchField,
    validators
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { onSave, onCancel, initialData = null, isLoading = false } = $props<{
    onSave: (contact: any) => void;
    onCancel: () => void;
    initialData?: EmployeeEmergencyContact | null;
    isLoading?: boolean;
  }>();

  const fields: FieldConfig[] = [
    text('last_name', { label: 'Nom complet', required: true, placeholder: 'Nom du contact', validators: [validators.required('Le nom est requis')] }),
    select('relation', {
      label: 'Relation',
      required: true,
      defaultValue: 'SPOUSE',
      dataSource: { type: 'static', values: RELATION_TYPES.map(r => ({ value: r.value, label: r.label })) },
      validators: [validators.required('La relation est requise')]
    }),
    phone('phone', { label: 'Téléphone', required: true, validators: [validators.required('Le téléphone est requis')] }),
    switchField('is_primary', { label: 'Contact principal', defaultValue: false })
  ];

  const form = createForm({
    id: 'contact-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'inline', variant: 'plain' },
    layout: { type: 'section', sections: [{ title: 'Contact', fields: ['last_name', 'relation', 'phone', 'is_primary'] }] },
    onSubmit: async (data) => { onSave(data); }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    if (initialData) form.hydrate({ last_name: initialData.last_name ?? '', relation: initialData.relation ?? 'SPOUSE', phone: initialData.phone ?? '', is_primary: initialData.is_primary ?? false });
  });
</script>

<FormView {form} fields={fields} showSubmit={false} showReset={false} />

<div class="flex items-center justify-end gap-2 pt-3">
  <button type="button" onclick={onCancel} class="px-3 py-1.5 text-[0.8rem] text-slate-500 hover:bg-slate-100 rounded-md flex items-center gap-1.5 cursor-pointer">
    Annuler
  </button>
  <button type="button" disabled={isLoading} onclick={() => form.submit()} class="px-3 py-1.5 text-[0.8rem] text-white bg-primary hover:bg-primary/90 rounded-md flex items-center gap-1.5 shadow-fine disabled:opacity-50 cursor-pointer">
    {initialData ? 'Enregistrer' : 'Ajouter'}
  </button>
</div>
