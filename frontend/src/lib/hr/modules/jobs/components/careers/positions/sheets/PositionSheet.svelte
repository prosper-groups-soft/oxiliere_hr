<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { jobsStore } from "../../../../stores/jobs.svelte";
  import type { JobPosition } from "../../../../types/types";
  import { SENIORITY_LABELS } from "../../../../types/types";
  import {
    createForm, FormView,
    text, orgUnit, validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let {
    open = $bindable(false),
    position = $bindable(null),
    prefilledOrgUnitId = '',
    onSave,
    onCreateJobFamily,
    onUpdateJobFamily,
    onDeleteJobFamily
  } = $props<{
    open: boolean;
    position?: JobPosition | null;
    prefilledOrgUnitId?: string;
    onSave?: (data: any, positionId?: string) => Promise<any>;
    onCreateJobFamily?: (name: string, description?: string) => Promise<any>;
    onUpdateJobFamily?: (id: string, name: string, description?: string) => Promise<any>;
    onDeleteJobFamily?: (id: string, name: string) => void;
  }>();

  // --- Simple fields (declarative) ---
  const fields: FieldConfig[] = [
    text('title', {
      label: 'Intitulé du poste',
      required: true,
      placeholder: 'ex: Comptable',
      validators: [validators.required("L'intitulé est requis")]
    }),
    text('familyName', {
      label: 'Famille de métier',
      required: true,
      placeholder: 'ex: Finance',
      validators: [validators.required('La famille est requise')]
    }),
    orgUnit('orgUnitId', {
      label: 'Unité organisationnelle',
      placeholder: 'Choisir une unité...'
    }),
    text('requirements', {
      label: 'Exigences (une par ligne)',
      placeholder: 'Diplôme, années d\'exp...',
      behaviors: [{ type: 'repeater' } as any]
    }),
    text('skills', {
      label: 'Compétences clés',
      placeholder: 'ex: React, SQL...',
      behaviors: [{ type: 'repeater' } as any]
    })
  ];

  const form = createForm({
    id: 'position-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-142' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Poste', fields: ['title', 'familyName', 'orgUnitId'] },
        { title: 'Profil recherché', fields: ['requirements', 'skills'] }
      ]
    },
    onSubmit: async (data) => {
      if (!onSave) return;
      // Keep seniority levels from local state (managed in extras)
      const payload = {
        title: data.title.trim(),
        familyName: data.familyName.trim(),
        orgUnitId: data.orgUnitId || null,
        seniority_levels: seniorityLevels,
        requirements: Array.isArray(data.requirements) ? data.requirements : [],
        skills: Array.isArray(data.skills) ? data.skills.map((s: any) => typeof s === 'string' ? { name: s, level: 3 } : s) : []
      };
      await onSave(payload, position?.id);
      open = false;
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  const entity = $derived(position ? {
    title: position.name,
    familyName: position.job_family?.name ?? '',
    orgUnitId: position.org_unit?.id ?? prefilledOrgUnitId ?? '',
    requirements: position.requirements ?? [],
    skills: (position.skills ?? []).map(s => s.name)
  } : prefilledOrgUnitId ? { orgUnitId: prefilledOrgUnitId } : null);

  // --- Seniority levels (local repeater, simplified) ---
  let seniorityLevels = $state<any[]>([]);
  $effect(() => {
    if (position?.seniority_levels?.length) {
      seniorityLevels = position.seniority_levels.map((sl: any) => ({
        seniority_level: sl.seniority_level.level,
        salary_min: sl.salary_min,
        salary_max: sl.salary_max,
        echelon: sl.echelon ?? null,
        rank: sl.rank,
        is_active: sl.is_active
      }));
    } else if (!position && open) {
      seniorityLevels = [];
    }
  });
  let newLevel = $state({ seniority_level: 'TRAINEE', salary_min: 0, salary_max: 0, echelon: null as number | null });
  function addLevel() {
    if (seniorityLevels.find(l => l.seniority_level === newLevel.seniority_level)) {
      notification.toast.error(`Le niveau ${newLevel.seniority_level} existe déjà`);
      return;
    }
    seniorityLevels = [...seniorityLevels, { ...newLevel, rank: seniorityLevels.length + 1, is_active: true }];
    newLevel = { seniority_level: 'TRAINEE', salary_min: 0, salary_max: 0, echelon: null };
  }
  function removeLevel(idx: number) {
    seniorityLevels = seniorityLevels.filter((_, i) => i !== idx).map((l, i) => ({ ...l, rank: i + 1 }));
  }
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={position ? 'Modifier le poste' : 'Nouveau poste'}
  submitLabel="Enregistrer"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
>
  {#snippet extras()}
    <div class="space-y-3">
      <h4 class="text-[0.9rem] font-semibold">Niveaux de séniorité ({seniorityLevels.length})</h4>
      {#each seniorityLevels as level, idx}
        <div class="flex items-center gap-2 p-2 rounded-lg border bg-white text-[0.85rem]">
          <span class="font-medium">{SENIORITY_LABELS[level.seniority_level] ?? level.seniority_level}</span>
          <span class="text-slate-400">{level.salary_min} - {level.salary_max} FC</span>
          {#if level.echelon}<span class="text-indigo-600">Éch. {level.echelon}</span>{/if}
          <button onclick={() => removeLevel(idx)} class="ml-auto text-red-500 hover:text-red-700 p-1">×</button>
        </div>
      {/each}
      <div class="flex gap-2 items-end">
        <select bind:value={newLevel.seniority_level} class="h-8 border rounded px-2 text-[0.85rem]">
          {#each Object.entries(SENIORITY_LABELS) as [code, label]}<option value={code}>{code} - {label}</option>{/each}
        </select>
        <input type="number" bind:value={newLevel.salary_min} placeholder="Min" class="h-8 w-24 border rounded px-2 text-[0.85rem]" />
        <input type="number" bind:value={newLevel.salary_max} placeholder="Max" class="h-8 w-24 border rounded px-2 text-[0.85rem]" />
        <button onclick={addLevel} class="h-8 px-3 bg-primary text-white rounded text-[0.85rem]">Ajouter</button>
      </div>
    </div>
  {/snippet}
</FormView>
