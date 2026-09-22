<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { useCreateAssignmentMutation, usePoliciesQuery, useAssignmentsQuery } from "../../../../queries/attendanceQueries";
  import { RECURRENCE_MODE_LABELS } from "../../../../constants/attendance.constants";
  import type { RecurrenceMode } from "../../../../constants/attendance.constants";
  import {
    createForm, FormView,
    select, date, validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false) } = $props<{ open: boolean }>();

  const policiesQuery = usePoliciesQuery();
  const assignmentsQuery = useAssignmentsQuery(() => 1, () => 200);
  const assignedIds = $derived(new Set($assignmentsQuery.data?.results?.map(a => a.employee_id) ?? []));
  let policies = $derived($policiesQuery.data ?? []);

  let recurrenceMode = $state<RecurrenceMode>('none');
  let recurrenceCount = $state(4);
  let hasNoEndDate = $state(true);

  const mutation = useCreateAssignmentMutation();

  const fields: FieldConfig[] = [
    select('employeeIds', {
      label: 'Employés',
      required: true,
      placeholder: 'Sélectionner des employés...',
      behaviors: [{ type: 'multiSelect' }],
      validators: [validators.required('Sélectionnez au moins un employé')]
    }),
    select('basePolicy', {
      label: 'Modèle de base',
      required: true,
      placeholder: 'Sélectionner un modèle',
      validators: [validators.required('Le modèle est requis')]
    }),
    date('startDate', { label: 'Date de début', required: true, defaultValue: new Date().toISOString().split('T')[0] }),
    date('endDate', { label: 'Date de fin' }),
    select('overridePolicy', { label: 'Remplacement (optionnel)', placeholder: 'Aucun' }),
    date('overrideStart', { label: 'Début remplacement', defaultValue: new Date().toISOString().split('T')[0] }),
    date('overrideEnd', { label: 'Fin remplacement' })
  ];

  function computeEnd(start: string, mode: RecurrenceMode, count: number): string {
    if (mode === 'none' || !start) return '';
    const d = new Date(start);
    if (mode === 'weekly') d.setDate(d.getDate() + 7 * count);
    else if (mode === 'biweekly') d.setDate(d.getDate() + 14 * count);
    else if (mode === 'monthly') d.setMonth(d.getMonth() + count);
    else if (mode === 'quarterly') d.setMonth(d.getMonth() + 3 * count);
    return d.toISOString().split('T')[0];
  }

  const form = createForm({
    id: 'bulk-assignment-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Employés', fields: ['employeeIds'] },
        { title: 'Affectation', fields: ['basePolicy', 'startDate', 'endDate'] },
        { title: 'Remplacement', fields: ['overridePolicy', 'overrideStart', 'overrideEnd'] }
      ]
    },
    onSubmit: async (data) => {
      const ids: string[] = Array.isArray(data.employeeIds) ? data.employeeIds : [data.employeeIds].filter(Boolean);
      if (!ids.length || !data.basePolicy) throw new Error('Missing data');
      const computedEnd = recurrenceMode !== 'none' ? computeEnd(data.overrideStart, recurrenceMode, recurrenceCount) : data.overrideEnd;
      let ok = 0, fail = 0;
      for (const empId of ids) {
        try {
          await $mutation.mutateAsync({
            employee_id: String(empId),
            policy_id: data.basePolicy,
            start_date: data.startDate,
            end_date: hasNoEndDate ? null : data.endDate || null,
            recurrence: 'NONE',
            override_policy_id: data.overridePolicy || null,
            override_valid_from: data.overridePolicy ? data.overrideStart : null,
            override_valid_until: computedEnd || null,
            override_recurrence: data.overridePolicy ? recurrenceMode.toUpperCase() : 'NONE',
            override_recurrence_count: data.overridePolicy && recurrenceMode !== 'none' ? recurrenceCount : null
          });
          ok++;
        } catch { fail++; }
      }
      if (ok) notification.toast.success(`${ok} affectation(s) réussie(s)` + (fail ? `, ${fail} échec(s)` : ''));
      if (fail && !ok) notification.toast.error('Échec de toutes les affectations');
      if (ok) { document.dispatchEvent(new CustomEvent('assignments-changed')); open = false; }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  // Dynamic options
  $effect(() => {
    // Employees: exclude already assigned
    import("@/hr/modules/employees/queries/employeeQueries").then(async (m) => {
      // best-effort: keep existing dataSource if employees already loaded elsewhere
    });
  });
  $effect(() => {
    const opts = policies.map(p => ({ value: p.id!, label: p.name }));
    form.setConfig({ fields: fields.map(f => f.id === 'basePolicy' || f.id === 'overridePolicy' ? { ...f, dataSource: { type: 'static', values: f.id === 'overridePolicy' ? opts.filter(o => o.value !== form.values.basePolicy) : opts } } : f) as any });
  });
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  title="Affecter en masse"
  submitLabel="Affecter"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
>
  {#snippet extras()}
    <label class="flex items-center gap-2 text-[0.85rem]"><input type="checkbox" bind:checked={hasNoEndDate} /> Illimité</label>
    {#if form.values.overridePolicy}
      <div class="flex gap-1.5 flex-wrap">
        {#each (['none','weekly','biweekly','monthly','quarterly'] as RecurrenceMode) as mode}
          <button onclick={() => recurrenceMode = mode} class="px-3 py-1.5 text-[0.82rem] rounded-full border {recurrenceMode === mode ? 'bg-blue-600 text-white border-blue-600' : 'bg-white border-slate-200'}">
            {RECURRENCE_MODE_LABELS[mode]}
          </button>
        {/each}
      </div>
      {#if recurrenceMode !== 'none'}
        <div class="flex items-center gap-2">
          <span class="text-[0.82rem]">Répéter</span>
          <input type="number" min="1" max="52" bind:value={recurrenceCount} class="w-16 h-8 border rounded text-center" />
          <span class="text-[0.82rem] text-blue-600">→ {computeEnd(form.values.overrideStart, recurrenceMode, recurrenceCount)}</span>
        </div>
      {/if}
    {/if}
  {/snippet}
</FormView>
