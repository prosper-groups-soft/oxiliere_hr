<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { useScheduleInterviewMutation, useUpdateInterviewMutation } from "@/hr/modules/recruitment/queries/recruitmentQueries";
  import type { Candidate, Interview } from "@/hr/modules/recruitment/types/types";
  import {
    createForm, FormView,
    select, date, text, textarea, employee,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let {
    open = $bindable(false),
    candidate = null,
    interview = null,
    onSuccess = null,
    applicationId = ''
  } = $props<{
    open: boolean;
    candidate?: Candidate | null;
    interview?: Interview | null;
    onSuccess?: () => void;
    applicationId?: string;
  }>();

  const scheduleMutation = useScheduleInterviewMutation();
  const updateMutation = useUpdateInterviewMutation();

  const TYPE_OPTIONS = [
    { value: 'VIDEO', label: 'Visioconférence' },
    { value: 'ONSITE', label: 'Présentiel' },
    { value: 'PHONE', label: 'Téléphonique' }
  ];
  const STATUS_OPTIONS = [
    { value: 'SCHEDULED', label: 'Programmé' },
    { value: 'COMPLETED', label: 'Terminé' },
    { value: 'CANCELLED', label: 'Annulé' }
  ];
  const DURATION_OPTIONS = [
    { value: '15', label: '15 minutes' },
    { value: '30', label: '30 minutes' },
    { value: '45', label: '45 minutes' },
    { value: '60', label: '60 minutes' },
    { value: '90', label: '90 minutes' },
    { value: '120', label: '120 minutes' }
  ];

  const isEdit = $derived(!!interview);
  const defaultDate = new Date(Date.now() + 86400000).toISOString().split('T')[0];

  const fields: FieldConfig[] = [
    select('applicationId', {
      label: 'Poste concerné',
      required: true,
      placeholder: 'Sélectionner le poste...',
      dependencies: { visibleIf: () => !isEdit && !!candidate?.applications?.length }
    }),
    select('status', {
      label: 'Statut',
      defaultValue: 'SCHEDULED',
      dataSource: { type: 'static', values: STATUS_OPTIONS },
      dependencies: { visibleIf: () => isEdit }
    }),
    select('type', {
      label: "Type d'entretien",
      required: true,
      defaultValue: 'VIDEO',
      dataSource: { type: 'static', values: TYPE_OPTIONS },
      validators: [validators.required('Le type est requis')]
    }),
    text('location', {
      label: 'Lieu / Lien / Téléphone',
      placeholder: 'Salle, lien Meet ou téléphone...'
    }),
    date('date', { label: 'Date', required: true, defaultValue: defaultDate, validators: [validators.required('La date est requise')] }),
    text('time', { label: 'Heure', required: true, defaultValue: '10:00', placeholder: 'HH:MM', validators: [validators.required("L'heure est requise")] }),
    select('duration', {
      label: 'Durée',
      defaultValue: '60',
      dataSource: { type: 'static', values: DURATION_OPTIONS }
    }),
    employee('interviewerId', {
      label: 'Interviewer',
      required: true,
      validators: [validators.required("L'interviewer est requis")]
    }),
    textarea('description', { label: 'Notes / Description', placeholder: "Détails sur l'entretien..." })
  ];

  const form = createForm({
    id: 'interview-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-md' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Candidature', fields: ['applicationId', 'status'] },
        { title: 'Entretien', fields: ['type', 'location', 'date', 'time', 'duration', 'interviewerId'] },
        { title: 'Notes', fields: ['description'] }
      ]
    },
    onSubmit: async (data) => {
      if (!candidate && !interview) return;
      const scheduledDate = `${data.date}T${data.time}:00`;
      if (interview) {
        await $updateMutation.mutateAsync({
          interviewId: interview.id,
          data: { interviewerId: data.interviewerId, type: data.type, scheduledDate, duration: Number(data.duration), location: data.location, description: data.description, status: data.status }
        });
      } else {
        if (!data.applicationId && candidate?.applications?.length) throw new Error('Poste requis');
        await $scheduleMutation.mutateAsync({
          applicationId: data.applicationId || applicationId,
          interviewerId: data.interviewerId,
          type: data.type,
          scheduledDate,
          duration: Number(data.duration),
          location: data.location,
          description: data.description
        } as any);
      }
      onSuccess?.();
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  // Dynamic application options + hydrate
  $effect(() => {
    const opts = (candidate?.applications ?? []).map((a: any) => ({
      value: a.id ?? a.applicationId,
      label: a.target_position_name ?? a.targetPositionName ?? 'Poste sans titre'
    }));
    form.setConfig({ fields: fields.map(f => f.id === 'applicationId' ? { ...f, dataSource: { type: 'static', values: opts } } : f) as any });
  });
  $effect(() => {
    if (open) {
      if (interview) {
        const d = new Date(interview.scheduledDate);
        form.hydrate({
          type: interview.type,
          date: d.toISOString().split('T')[0],
          time: d.toISOString().slice(11, 16),
          duration: String(interview.duration ?? 60),
          interviewerId: interview.interviewerId ?? '',
          location: interview.location ?? '',
          description: interview.description ?? '',
          status: interview.status ?? 'SCHEDULED'
        });
      } else {
        form.hydrate({
          applicationId: applicationId || (candidate?.applications?.length === 1 ? (candidate.applications[0] as any).id ?? (candidate.applications[0] as any).applicationId : ''),
          type: 'VIDEO',
          date: defaultDate,
          time: '10:00',
          duration: '60'
        });
      }
    }
  });
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  title={interview ? "Modifier l'entretien" : 'Programmer un entretien'}
  submitLabel={interview ? 'Mettre à jour' : 'Programmer'}
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
