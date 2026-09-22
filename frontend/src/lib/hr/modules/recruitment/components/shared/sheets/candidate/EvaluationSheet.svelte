<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { useUpdateApplicationEvaluationMutation } from "@/hr/modules/recruitment/queries/recruitmentQueries";
  import type { CandidateApplication, EvaluationCriterion } from "@/hr/modules/recruitment/types/types";
  import {
    createForm, FormView,
    number, textarea,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let {
    open = $bindable(false),
    application = null,
    evaluationTemplate = null,
    onsaved = null
  } = $props<{
    open: boolean;
    application: CandidateApplication | null;
    evaluationTemplate?: EvaluationCriterion[] | null;
    onsaved?: (() => void) | null;
  }>();

  const mutation = useUpdateApplicationEvaluationMutation();
  const criteria = $derived((evaluationTemplate ?? []).filter(c => c.weight > 0));

  const fields = $derived<FieldConfig[]>([
    ({ id: 'scores', type: 'scoring' as any, label: 'Critères', dataSource: { type: 'static', values: criteria.map(c => ({ value: c.name, label: c.name, weight: c.weight, source: c.source })) } } as FieldConfig),
    textarea('evaluationNotes', { label: "Notes d'évaluation", placeholder: 'Points forts, points faibles...' })
  ]);

  const form = $derived(createForm({
    id: 'evaluation-form',
    fields: fields as FieldConfig[],
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-md' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Critères', fields: ['scores'] },
        { title: 'Notes', fields: ['evaluationNotes'] }
      ]
    },
    onSubmit: async (data) => {
      if (!application) return;
      await $mutation.mutateAsync({ applicationId: application.applicationId, data: { scores: data.scores ?? {}, evaluationNotes: data.evaluationNotes } });
      onsaved?.();
    }
  }));

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    if (open && application) {
      form.hydrate({ scores: application.scores ?? {}, evaluationNotes: application.evaluationNotes ?? '' });
    }
  });
</script>

{#if criteria.length === 0}
  <!-- Pas de FormView si aucun critère : message seul dans le sheet -->
  <FormView {form} fields={fields} bind:open title="Évaluer le candidat" submitLabel="Enregistrer" submitIcon="check" showReset={false} actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]} />
{:else}
  <FormView {form} fields={fields} bind:open title="Évaluer le candidat" submitLabel="Enregistrer" submitIcon="check" showReset={false} actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]} />
{/if}
