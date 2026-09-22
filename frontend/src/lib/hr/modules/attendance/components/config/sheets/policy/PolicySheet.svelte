<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { attendanceStore } from "../../../../stores/attendance.svelte";
  import { DAYS } from "../../../../constants/attendance.constants";
  import type { DayOfWeek, WorkPolicy } from "../../../../types/types";
  import { useQueryClient } from "@tanstack/svelte-query";
  import { policyQueryKeys } from "../../../../queries/attendanceQueries";
  import {
    createForm, FormView,
    text, number, validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), policy = $bindable<WorkPolicy | null>(null) } = $props<{ open: boolean; policy: WorkPolicy | null }>();

  const queryClient = useQueryClient();

  const fields: FieldConfig[] = [
    text('name', { label: 'Nom du modèle', required: true, placeholder: 'ex: Bureau Standard', validators: [validators.required('Le nom est requis')] }),
    text('description', { label: 'Description', placeholder: 'ex: 8h-17h, 5j/7' }),
    number('targetHours', { label: 'Objectif hebdomadaire (heures)', min: 1, max: 80, placeholder: 'ex: 40' }),
    ({ id: 'pattern', type: 'policyGrid' as any, label: 'Planning hebdomadaire' } as FieldConfig)
  ];

  const form = createForm({
    id: 'policy-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: { type: 'section', sections: [{ title: 'Modèle', fields: ['name', 'description', 'targetHours'] }, { title: 'Planning hebdomadaire', fields: ['pattern'] }] },
    onSubmit: async (data) => {
      if (!policy) return;
      const payload = { ...policy, name: data.name, description: data.description, targetHours: Number(data.targetHours), pattern: data.pattern };
      if (payload.id) await attendanceStore.updatePolicy(payload.id, payload);
      else await attendanceStore.addPolicy(payload);
      queryClient.invalidateQueries({ queryKey: policyQueryKeys.all });
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  const entity = $derived(policy ? { name: policy.name, description: policy.description ?? '', targetHours: policy.targetHours, pattern: policy.pattern } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={policy?.id ? 'Modifier le modèle' : 'Définir un modèle'}
  submitLabel={policy?.id ? 'Enregistrer' : 'Créer le modèle'}
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
