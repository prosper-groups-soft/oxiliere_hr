<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import type { Vacancy } from "../../../../types/types";
  import { useCreateVacancyMutation, useUpdateVacancyMutation } from "../../../../queries/vacancyQueries";
  import { usePositionsQuery } from "../../../../queries/jobQueries";
  import {
    createForm, FormView,
    select, date, textarea, position,
    validators, cancel
  } from "@/hr/forms/index.js";
  import { persist } from "@/hr/forms-bindings/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), vacancy = $bindable(null) } = $props<{ open: boolean, vacancy?: Vacancy | null }>();

  const createMutation = useCreateVacancyMutation();
  const updateMutation = useUpdateVacancyMutation();
  const allPositionsQuery = usePositionsQuery();

  const PRIORITY_OPTIONS = [
    { value: 'HIGH', label: 'Haute' },
    { value: 'MEDIUM', label: 'Moyenne' },
    { value: 'LOW', label: 'Basse' }
  ];
  const STATUS_OPTIONS = [
    { value: 'OPEN', label: 'Ouvert' },
    { value: 'IN_PROGRESS', label: 'En cours' },
    { value: 'RECRUITMENT', label: 'Recrutement' },
    { value: 'CANCELLED', label: 'Annulé' }
  ];

  const vacancyFields: FieldConfig[] = [
    position('positionId', {
      out: 'position_id',
      label: 'Poste à pourvoir',
      required: true,
      placeholder: 'Sélectionner un poste...',
      validators: [validators.required('Le poste est requis')]
    }),
    select('priority', {
      label: 'Priorité',
      required: true,
      defaultValue: 'MEDIUM',
      dataSource: { type: 'static', values: PRIORITY_OPTIONS }
    }),
    select('status', {
      label: 'Statut',
      required: true,
      defaultValue: 'OPEN',
      dataSource: { type: 'static', values: STATUS_OPTIONS }
    }),
    date('openedDate', {
      out: 'opened_date',
      label: "Date d'ouverture",
      required: true,
      defaultValue: new Date().toISOString().split('T')[0],
      validators: [validators.required("La date d'ouverture est requise")]
    }),
    date('targetDate', { out: 'target_date', label: 'Date cible' }),
    textarea('reason', { label: 'Motif ou Commentaire', placeholder: 'Précisez les raisons du besoin...' })
  ];

  const form = createForm({
    id: 'vacancy-form',
    fields: vacancyFields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-lg' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Poste', fields: ['positionId'] },
        { title: 'Priorité & Statut', fields: ['priority', 'status'] },
        { title: 'Dates', fields: ['openedDate', 'targetDate'] },
        { title: 'Motif', fields: ['reason'] }
      ]
    },
    onSubmit: persist({
      create: (payload) => $createMutation.mutateAsync(payload as any),
      update: ({ id, data }) => $updateMutation.mutateAsync({ id, data } as any),
      idOf: () => vacancy?.id
    })
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });
</script>

<FormView
  {form}
  fields={vacancyFields}
  bind:open
  entity={vacancy}
  title={vacancy ? 'Modifier le besoin' : 'Nouveau besoin'}
  submitLabel="Enregistrer"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
