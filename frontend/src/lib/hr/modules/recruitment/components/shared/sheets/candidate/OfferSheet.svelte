<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { useUpdateApplicationOfferMutation } from "@/hr/modules/recruitment/queries/recruitmentQueries";
  import type { CandidateApplication } from "@/hr/modules/recruitment/types/types";
  import {
    createForm, FormView,
    number, select, date,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), application = null, onSuccess = null } = $props<{ open: boolean; application: CandidateApplication | null; onSuccess?: () => void }>();

  const mutation = useUpdateApplicationOfferMutation();

  const fields: FieldConfig[] = [
    number('salaryMin', { label: 'Salaire min', min: 0, defaultValue: 0 }),
    number('salaryMax', { label: 'Salaire max', min: 0, defaultValue: 0 }),
    select('salaryCurrency', {
      label: 'Devise',
      defaultValue: 'USD',
      dataSource: { type: 'static', values: [{ value: 'USD', label: 'USD' }, { value: 'EUR', label: 'EUR' }, { value: 'CDF', label: 'CDF' }] }
    }),
    date('offerStartDate', { out: 'offerStartDate', label: 'Date de début prévue', required: true, validators: [validators.required('La date est requise')] })
  ];

  const form = createForm({
    id: 'offer-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-md' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Rémunération', fields: ['salaryMin', 'salaryMax', 'salaryCurrency'] },
        { title: 'Prise de poste', fields: ['offerStartDate'] }
      ]
    },
    onSubmit: async (data) => {
      if (!application) return;
      await $mutation.mutateAsync({
        applicationId: application.applicationId,
        data: { salaryMin: Number(data.salaryMin), salaryMax: Number(data.salaryMax), salaryCurrency: data.salaryCurrency, offerStartDate: data.offerStartDate }
      });
      onSuccess?.();
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    if (open && application) {
      form.hydrate({
        salaryMin: application.salaryMin ?? 0,
        salaryMax: application.salaryMax ?? application.salaryMin ?? 0,
        salaryCurrency: application.salaryCurrency ?? 'USD',
        offerStartDate: application.offerStartDate ?? ''
      });
    }
  });
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  title="Créer une offre d'emploi"
  submitLabel="Créer l'offre"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
