<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import type { Transition, TransitionType } from "../../../../types/types";
  import { SENIORITY_LABELS } from "../../../../types/types";
  import { useCreateTransitionMutation, useUpdateTransitionMutation } from "../../../../queries/transitionQueries";
  import { useAllEmployees } from "@/hr/modules/employees/queries/employeeQueries";
  import { usePositionsQuery } from "../../../../queries/jobQueries";
  import {
    createForm, FormView,
    employee, position, select, date, textarea,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), transition = $bindable(null) } = $props<{ open: boolean; transition?: Transition | null }>();

  const createMutation = useCreateTransitionMutation();
  const updateMutation = useUpdateTransitionMutation();
  const allPositionsQuery = usePositionsQuery();
  let positions = $derived($allPositionsQuery.data ?? []);

  const TYPE_OPTIONS = [
    { value: 'TRANSFER', label: 'Mutation' },
    { value: 'PROMOTION', label: 'Promotion' },
    { value: 'HIRE', label: 'Embauche' },
    { value: 'OFFBOARD', label: 'Départ' }
  ];

  const fields: FieldConfig[] = [
    employee('employeeId', {
      out: 'employee_id',
      label: 'Employé concerné',
      required: true,
      validators: [validators.required("L'employé est requis")]
    }),
    select('transitionType', {
      out: 'transition_type',
      label: 'Type de mouvement',
      required: true,
      defaultValue: 'TRANSFER',
      dataSource: { type: 'static', values: TYPE_OPTIONS }
    }),
    position('toPositionId', {
      out: 'to_position_id',
      label: 'Nouveau poste',
      placeholder: 'Choisir un poste...',
      dependencies: { visibleIf: (vals: any) => vals.transitionType !== 'OFFBOARD' }
    }),
    select('toSeniorityLevel', {
      out: 'to_seniority_level_id',
      label: 'Niveau de séniorité',
      placeholder: 'Choisir un niveau...',
      dependencies: { visibleIf: (vals: any) => !!vals.toPositionId && vals.transitionType !== 'OFFBOARD' }
    }),
    date('date', { label: "Date d'effet", required: true, validators: [validators.required('La date est requise')] }),
    textarea('reason', { label: 'Motif ou Commentaire', placeholder: 'Précisez les raisons du mouvement...' })
  ];

  const form = createForm({
    id: 'transition-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-lg' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Mouvement', fields: ['employeeId', 'transitionType'] },
        { title: 'Nouvelle affectation', fields: ['toPositionId', 'toSeniorityLevel'] },
        { title: 'Détails', fields: ['date', 'reason'] }
      ]
    },
    onSubmit: async (data) => {
      const payload: any = {
        employee_id: String(data.employeeId),
        transition_type: data.transitionType,
        to_position_id: data.toPositionId || null,
        to_seniority_level_id: data.toSeniorityLevel || null,
        date: data.date || new Date().toISOString().split('T')[0],
        reason: data.reason || undefined
      };
      if (transition) {
        await $updateMutation.mutateAsync({ id: transition.id, data: { ...payload, from_position_id: transition.from_position?.id ?? null, from_seniority_level_id: transition.from_seniority_level?.id ?? null } });
      } else {
        await $createMutation.mutateAsync(payload);
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  // Dynamic seniority options based on selected position
  $effect(() => {
    const posId = form.values.toPositionId as string | undefined;
    const pos = positions.find(p => p.id === posId);
    const opts = (pos?.seniority_levels ?? [])
      .sort((a: any, b: any) => a.rank - b.rank)
      .map((l: any) => ({ value: l.seniority_level.id, label: `${l.seniority_level.name ?? SENIORITY_LABELS[l.seniority_level.level]} (${l.salary_min}-${l.salary_max} FC)` }));
    form.setConfig({ fields: fields.map(f => f.id === 'toSeniorityLevel' ? { ...f, dataSource: { type: 'static', values: opts } } : f) as any });
  });

  const entity = $derived(transition ? {
    employeeId: transition.employee_id,
    transitionType: transition.transition_type,
    toPositionId: transition.to_position?.id ?? '',
    toSeniorityLevel: transition.to_seniority_level?.id ?? '',
    date: transition.date,
    reason: transition.reason ?? ''
  } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={transition ? 'Modifier le mouvement' : 'Nouveau mouvement'}
  submitLabel="Enregistrer"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
