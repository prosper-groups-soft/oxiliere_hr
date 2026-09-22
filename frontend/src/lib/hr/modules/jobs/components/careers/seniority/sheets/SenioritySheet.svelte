<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { jobsStore } from "../../../../stores/jobs.svelte";
  import { SENIORITY_LABELS } from "../../../../types/types";
  import type { SeniorityLevel, SeniorityLevelDefinition } from "../../../../types/types";
  import {
    createForm, FormView,
    select, number, text, validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let {
    open = $bindable(false),
    level = $bindable(null),
    onSave
  } = $props<{
    open: boolean,
    level?: SeniorityLevelDefinition | null,
    onSave?: (data: Omit<SeniorityLevelDefinition, 'id'>, levelId?: string | null) => Promise<void> | void
  }>();

  const SENIORITY_OPTIONS = Object.entries(SENIORITY_LABELS).map(([value, label]) => ({ value, label: `${value} - ${label}` }));
  const CLASSE_OPTIONS = [
    { value: '', label: 'Non défini' },
    ...[1,2,3,4,5,6,7].map(c => ({ value: String(c), label: `Classe ${c}` }))
  ];

  const seniorityFields: FieldConfig[] = [
    select('level', {
      label: 'Niveau de séniorité',
      required: true,
      defaultValue: 'TRAINEE',
      dataSource: { type: 'static', values: SENIORITY_OPTIONS },
      validators: [validators.required('Le niveau est requis')]
    }),
    text('requirements', {
      label: 'Compétences & Exigences',
      placeholder: 'Ajouter une exigence...',
      help: 'Appuyez sur Entrée pour ajouter',
      behaviors: [{ type: 'repeater' } as any]
    }),
    number('rank', {
      label: 'Rang hiérarchique',
      required: true,
      min: 1,
      defaultValue: 1,
      validators: [validators.required('Le rang est requis'), validators.min(1, 'Le rang doit être >= 1')]
    }),
    select('classe', {
      label: 'Classe professionnelle (RDC)',
      help: 'Grille des catégories professionnelles — optionnel.',
      placeholder: 'Non défini',
      dataSource: { type: 'static', values: CLASSE_OPTIONS }
    })
  ];

  const form = createForm({
    id: 'seniority-form',
    fields: seniorityFields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-140' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Niveau', fields: ['level'] },
        { title: 'Compétences', fields: ['requirements'] },
        { title: 'Hiérarchie', fields: ['rank', 'classe'] }
      ]
    },
    onSubmit: async (data) => {
      // Validations d'unicité (même logique que l'ancien validate())
      const existingLevels = jobsStore.seniorityLevels.filter(l => !level || l.id !== level.id).map(l => l.level);
      if (existingLevels.includes(data.level)) {
        notification.toast.error('Ce niveau de séniorité existe déjà');
        throw new Error('Duplicate level');
      }
      const existingRanks = jobsStore.seniorityLevels.filter(l => !level || l.id !== level.id).map(l => l.rank);
      if (existingRanks.includes(Number(data.rank))) {
        notification.toast.error('Ce rang est déjà attribué à un autre niveau');
        throw new Error('Duplicate rank');
      }
      const payload: Omit<SeniorityLevelDefinition, 'id'> = {
        level: data.level as SeniorityLevel,
        name: SENIORITY_LABELS[data.level as SeniorityLevel],
        rank: Number(data.rank),
        requirements: Array.isArray(data.requirements) ? data.requirements : (data.requirements ? [data.requirements] : []),
        classe: data.classe ? Number(data.classe) : null
      };
      if (onSave) {
        await onSave(payload, level?.id ?? null);
      } else {
        if (level) {
          jobsStore.updateSeniorityLevel(level.id, payload);
          notification.toast.success(`Le niveau ${payload.name} a été mis à jour.`);
        } else {
          jobsStore.addSeniorityLevel(payload);
          notification.toast.success(`Le niveau ${payload.name} a été créé.`);
        }
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });

  // Entity mapping : classe number -> string pour le select, requirements array
  const entity = $derived(level ? {
    ...level,
    classe: level.classe != null ? String(level.classe) : '',
    requirements: level.requirements
  } : null);
</script>

<FormView
  {form}
  fields={seniorityFields}
  bind:open
  entity={entity}
  title={level ? 'Modifier le niveau' : 'Nouveau niveau'}
  submitLabel="Enregistrer"
  submitIcon="check"
  showReset={false}
  actions={[
    cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })
  ]}
/>
