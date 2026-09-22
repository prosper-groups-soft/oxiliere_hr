<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { CAMPAIGN_TYPE_LABELS } from '@/hr/modules/performance/constants';
  import { useCreateCampaignMutation, useUpdateCampaignMutation } from '@/hr/modules/performance/queries/performanceQueries';
  import {
    createForm, FormView,
    text, textarea, select, date, number,
    validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), campaign = null, onclose } = $props<{ open: boolean; campaign?: any | null; onclose?: () => void }>();

  const createMutation = useCreateCampaignMutation();
  const updateMutation = useUpdateCampaignMutation();
  const isEdit = $derived(!!campaign);

  const fields: FieldConfig[] = [
    text('name', { label: 'Nom', required: true, placeholder: 'Ex: Campagne Annuelle 2026', validators: [validators.required('Le nom est requis')] }),
    textarea('description', { label: 'Description', placeholder: 'Instructions générales...' }),
    select('campaign_type', {
      label: 'Type de campagne',
      defaultValue: 'SEMESTRIAL',
      dataSource: { type: 'static', values: Object.entries(CAMPAIGN_TYPE_LABELS).map(([value, label]) => ({ value, label })) }
    }),
    date('start_date', { label: 'Début', required: true, validators: [validators.required('La date de début est requise')] }),
    date('end_date', { label: 'Fin', required: true, validators: [validators.required('La date de fin est requise')] }),
    date('submission_deadline', { label: 'Date limite de soumission', required: true, validators: [validators.required('La date limite est requise')] }),
    number('goal_weight', { label: 'Poids objectifs (0-1)', min: 0, max: 1, step: 0.05, defaultValue: 0.6 }),
    number('skill_weight', { label: 'Poids compétences (0-1)', min: 0, max: 1, step: 0.05, defaultValue: 0.4 }),
    ({ id: 'default_goals', type: 'goalEditor' as any, label: 'Objectifs par défaut' } as FieldConfig)
  ];

  const form = createForm({
    id: 'perf-campaign-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-176' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Campagne', fields: ['name', 'description', 'campaign_type'] },
        { title: 'Période', fields: ['start_date', 'end_date', 'submission_deadline'] },
        { title: 'Pondération', fields: ['goal_weight', 'skill_weight'] },
        { title: 'Objectifs', fields: ['default_goals'] }
      ]
    },
    onSubmit: async (data) => {
      if (data.end_date < data.start_date) throw new Error('La date de fin doit être après le début');
      if (data.submission_deadline < data.end_date) throw new Error('La date limite doit être après la fin');
      if (Math.abs(Number(data.goal_weight) + Number(data.skill_weight) - 1) > 0.01) throw new Error('La somme des poids doit être 1');
      const payload = {
        name: data.name.trim(),
        description: data.description?.trim() ?? '',
        campaign_type: data.campaign_type,
        start_date: data.start_date,
        end_date: data.end_date,
        submission_deadline: data.submission_deadline,
        goal_weight: Number(data.goal_weight),
        skill_weight: Number(data.skill_weight),
        default_goals: data.default_goals ?? campaign?.default_goals ?? [],
        default_skills: campaign?.default_skills ?? []
      };
      if (isEdit) await $updateMutation.mutateAsync({ campaignId: campaign.id, data: payload } as any);
      else await $createMutation.mutateAsync(payload as any);
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) notification.toast.error(e.message);
    else notification.toast.error("Veuillez corriger les erreurs");
  });

  const entity = $derived(campaign ? {
    name: campaign.name,
    description: campaign.description ?? '',
    campaign_type: campaign.campaign_type,
    start_date: campaign.start_date,
    end_date: campaign.end_date,
    submission_deadline: campaign.submission_deadline,
    goal_weight: campaign.goal_weight ?? 0.6,
    skill_weight: campaign.skill_weight ?? 0.4,
    default_goals: campaign.default_goals ?? []
  } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={isEdit ? 'Modifier la campagne' : 'Nouvelle campagne'}
  submitLabel={isEdit ? 'Enregistrer' : 'Créer la campagne'}
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; onclose?.(); } })]}
/>
