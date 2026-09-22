<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { useSubmitInterviewFeedbackMutation } from "@/hr/modules/recruitment/queries/recruitmentQueries";
  import type { Interview } from "@/hr/modules/recruitment/types/types";
  import {
    createForm, FormView,
    select, textarea, number, text, radio,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), interview = null, onsaved = null } = $props<{ open: boolean; interview: Interview | null; onsaved?: (() => void) | null }>();

  const mutation = useSubmitInterviewFeedbackMutation();

  const fields: FieldConfig[] = [
    select('status', {
      label: 'Statut',
      defaultValue: 'COMPLETED',
      dataSource: { type: 'static', values: [{ value: 'COMPLETED', label: 'Terminé' }, { value: 'NO_SHOW', label: 'Absent' }] }
    }),
    number('score', { label: 'Note globale (0-5)', min: 0, max: 5, defaultValue: 0 }),
    text('strengths', { label: 'Points forts (séparés par virgule)', placeholder: 'ex: Technique, Communication' }),
    text('weaknesses', { label: 'Axes d\'amélioration', placeholder: 'ex: Expérience...' }),
    radio('wouldHire', {
      label: 'Recommandation',
      dataSource: { type: 'static', values: [{ value: 'true', label: 'À embaucher' }, { value: 'false', label: 'Ne pas embaucher' }, { value: '', label: 'Non spécifié' }] },
      defaultValue: ''
    }),
    textarea('feedback', { label: "Notes de l'entretien", placeholder: "Points techniques, soft skills..." }),
    textarea('nextSteps', { label: 'Prochaines étapes', placeholder: 'ex: Entretien technique...' })
  ];

  const form = createForm({
    id: 'feedback-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-md' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Évaluation', fields: ['status', 'score', 'wouldHire'] },
        { title: 'Qualitatif', fields: ['strengths', 'weaknesses', 'feedback', 'nextSteps'] }
      ]
    },
    onSubmit: async (data) => {
      if (!interview) return;
      await $mutation.mutateAsync({
        interviewId: interview.id,
        data: {
          score: Number(data.score),
          feedback: data.feedback || undefined,
          strengths: data.strengths ? String(data.strengths).split(',').map((s: string) => s.trim()).filter(Boolean) : undefined,
          weaknesses: data.weaknesses ? String(data.weaknesses).split(',').map((s: string) => s.trim()).filter(Boolean) : undefined,
          wouldHire: data.wouldHire === 'true' ? true : data.wouldHire === 'false' ? false : undefined,
          nextSteps: data.nextSteps || undefined,
          status: data.status
        }
      });
      onsaved?.();
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    if (open && interview) {
      form.hydrate({
        status: interview.status ?? 'COMPLETED',
        score: interview.feedback?.rating ?? 0,
        strengths: (interview.feedback?.strengths ?? []).join(', '),
        weaknesses: (interview.feedback?.weaknesses ?? []).join(', '),
        wouldHire: interview.feedback?.wouldHire === true ? 'true' : interview.feedback?.wouldHire === false ? 'false' : '',
        feedback: interview.feedback?.feedback ?? '',
        nextSteps: interview.feedback?.nextSteps ?? interview.nextSteps ?? ''
      });
    }
  });
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  title="Feedback d'entretien"
  submitLabel="Enregistrer"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
