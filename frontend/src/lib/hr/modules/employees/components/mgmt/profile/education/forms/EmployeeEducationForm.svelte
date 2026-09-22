<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { ACADEMIC_LEVELS } from "@/hr/modules/employees/constants/education";
  import {
    createForm, FormView,
    text, select, number,
    validators
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { initialData = null, onSave, onCancel, isLoading = false } = $props<{
    initialData?: any | null;
    onSave: (data: any) => Promise<void>;
    onCancel: () => void;
    isLoading?: boolean;
  }>();

  const fields: FieldConfig[] = [
    select('degree', {
      label: 'Diplôme / Titre',
      required: true,
      dataSource: { type: 'static', values: ACADEMIC_LEVELS.map(l => ({ value: l.value, label: l.label })) },
      validators: [validators.required('Le diplôme est requis')]
    }),
    text('institute', { label: 'Institution / École', required: true, placeholder: 'Ex: Université de Paris', validators: [validators.required("L'institution est requise")] }),
    text('major', { label: 'Spécialité / Domaine', placeholder: 'Ex: Génie Logiciel' }),
    text('location', { label: 'Lieu (Ville, Pays)', placeholder: 'Ex: Paris, France' }),
    number('start_year', { label: 'Année de début', min: 1950, max: 2099, placeholder: 'Ex: 2018' }),
    number('end_year', { label: 'Année de fin', min: 1950, max: 2099, placeholder: 'Ex: 2021' })
  ];

  const form = createForm({
    id: 'education-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'inline', variant: 'plain' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Formation', fields: ['degree', 'institute'] },
        { title: 'Détails', fields: ['major', 'location'] },
        { title: 'Période', fields: ['start_year', 'end_year'] }
      ]
    },
    onSubmit: async (data) => {
      const payload: any = { ...data };
      if (payload.start_year) payload.start_year = Number(payload.start_year); else delete payload.start_year;
      if (payload.end_year) payload.end_year = Number(payload.end_year); else delete payload.end_year;
      await onSave(payload);
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    if (initialData) form.hydrate({ degree: initialData.degree ?? '', institute: initialData.institute ?? '', major: initialData.major ?? '', location: initialData.location ?? '', start_year: initialData.start_year ?? '', end_year: initialData.end_year ?? '' });
  });
</script>

<FormView {form} fields={fields} showSubmit={false} showReset={false} />

<div class="flex items-center justify-end gap-2.5 pt-4 border-t mt-4">
  <button type="button" onclick={onCancel} disabled={isLoading} class="h-8.5 px-4 text-[0.84rem] border rounded-md hover:bg-slate-50 disabled:opacity-50 cursor-pointer">Annuler</button>
  <button type="button" onclick={() => form.submit()} disabled={isLoading} class="h-8.5 px-5 text-[0.84rem] bg-primary text-white rounded-md shadow-fine disabled:opacity-50 cursor-pointer">
    {initialData ? 'Mettre à jour' : 'Ajouter'}
  </button>
</div>
