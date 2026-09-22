<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { useCampaignsQuery, useCreateReviewMutation, useUpdateEmployeeReviewMutation, useUpdateManagerReviewMutation } from '../../../queries/performanceQueries';
  import {
    createForm, FormView,
    select, textarea,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), review = null, mode = 'employee' } = $props<{ open: boolean; review?: any | null; mode?: 'employee' | 'manager' }>();

  const isEdit = $derived(!!review);
  const createMutation = useCreateReviewMutation();
  const updateEmployeeMutation = useUpdateEmployeeReviewMutation();
  const updateManagerMutation = useUpdateManagerReviewMutation();
  const campaignsQuery = useCampaignsQuery(() => 1, () => ({ status: 'ACTIVE' }));
  let campaigns = $derived($campaignsQuery.data?.results ?? []);

  const fields: FieldConfig[] = [
    select('campaign_id', {
      label: 'Campagne (en cours)',
      required: true,
      placeholder: 'Choisir une campagne...',
      validators: [validators.required('La campagne est requise')],
      dependencies: { visibleIf: () => !isEdit }
    }),
    select('employee_id', {
      label: 'Participant évalué',
      required: true,
      placeholder: 'Choisir un employé...',
      validators: [validators.required("L'employé est requis")],
      dependencies: { visibleIf: () => !isEdit }
    }),
    textarea('employee_comment', { label: mode === 'manager' ? "Commentaire de l'évaluateur" : 'Votre commentaire', placeholder: "Commentaire sur l'évaluation..." }),
    ({ id: 'goals', type: 'goalEditor' as any, label: 'Objectifs' } as FieldConfig)
  ];

  const form = createForm({
    id: 'review-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Évaluation', fields: ['campaign_id', 'employee_id'] },
        { title: 'Objectifs', fields: ['goals'] },
        { title: 'Commentaire', fields: ['employee_comment'] }
      ]
    },
    onSubmit: async (data) => {
      if (isEdit && review) {
        if (mode === 'manager') {
          await $updateManagerMutation.mutateAsync({ reviewId: review.id, data: { manager_comment: data.employee_comment, goals: data.goals } as any });
        } else {
          await $updateEmployeeMutation.mutateAsync({ reviewId: review.id, data: { employee_comment: data.employee_comment, goals: data.goals } as any });
        }
      } else {
        await $createMutation.mutateAsync({ campaign_id: data.campaign_id, employee_id: data.employee_id, employee_comment: data.employee_comment, goals: data.goals } as any);
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  // Dynamic campaign options
  $effect(() => {
    const campOpts = campaigns.map((c: any) => ({ value: c.id, label: c.name }));
    form.setConfig({ fields: fields.map(f => f.id === 'campaign_id' ? { ...f, dataSource: { type: 'static', values: campOpts } } : f) as any });
  });
  // Employee options depend on selected campaign (simplified: static, real filtering via API in extras)
  $effect(() => {
    const campId = form.values.campaign_id as string | undefined;
    if (!campId) return;
    import('../../../queries/performanceQueries').then(async (m) => {
      // Best-effort: keep review flow simple, goals/skills edited in dedicated editors
    });
  });

  const entity = $derived(review ? { employee_comment: mode === 'manager' ? review.managerComment ?? '' : review.employeeComment ?? '', goals: review.goals ?? [] } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={isEdit ? (mode === 'manager' ? "Évaluation de l'évaluateur" : "Modifier l'auto-évaluation") : 'Créer une évaluation'}
  submitLabel={isEdit ? 'Enregistrer' : "Créer l'évaluation"}
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
