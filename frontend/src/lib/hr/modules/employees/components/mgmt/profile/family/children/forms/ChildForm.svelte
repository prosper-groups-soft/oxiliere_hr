<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import type { EmployeeChild } from "@/hr/modules/employees/types/types";
  import {
    createForm, FormView,
    text, date, select, switchField,
    validators
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { onSave, onCancel, initialData = null, isLoading = false, error = null } = $props<{
    onSave: (child: any) => void;
    onCancel: () => void;
    initialData?: EmployeeChild | null;
    isLoading?: boolean;
    error?: any;
  }>();

  const fields: FieldConfig[] = [
    text('last_name', { label: 'Nom', required: true, validators: [validators.required('Le nom est requis')] }),
    date('birthdate', { label: 'Date de naissance' }),
    select('gender', {
      label: 'Genre',
      defaultValue: 'MALE',
      dataSource: { type: 'static', values: [{ value: 'MALE', label: 'M' }, { value: 'FEMALE', label: 'F' }, { value: 'NOT_SPECIFIED', label: '—' }] }
    }),
    switchField('is_dependent', { label: 'À charge', defaultValue: true })
  ];

  const form = createForm({
    id: 'child-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'inline', variant: 'plain' },
    layout: { type: 'section', sections: [{ title: 'Enfant', fields: ['last_name', 'birthdate', 'gender', 'is_dependent'] }] },
    onSubmit: async (data) => { onSave(data); }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    if (initialData) form.hydrate({ last_name: initialData.last_name ?? '', birthdate: initialData.birthdate ?? '', gender: (initialData.gender as any) ?? 'MALE', is_dependent: initialData.is_dependent ?? true });
  });
  $effect(() => {
    if (error) {
      const data = error.response?.data ?? error.data ?? error;
      Object.entries(data ?? {}).forEach(([k, v]) => form.getField(k)?.setError(String(v)));
    }
  });
</script>

<FormView {form} fields={fields} showSubmit={false} showReset={false} />

<div class="flex items-center justify-end gap-2 pt-3">
  <button type="button" onclick={onCancel} class="px-3 py-1.5 text-[0.8rem] text-slate-500 hover:bg-slate-100 rounded-md cursor-pointer">Annuler</button>
  <button type="button" disabled={isLoading} onclick={() => form.submit()} class="px-3 py-1.5 text-[0.8rem] text-white bg-primary rounded-md shadow-fine disabled:opacity-50 cursor-pointer">
    {initialData ? 'Enregistrer' : 'Ajouter'}
  </button>
</div>
