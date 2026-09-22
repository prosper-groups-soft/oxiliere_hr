<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { useCreateAssignmentMutation, useUpdateAssignmentMutation, usePoliciesQuery } from "../../../../queries/attendanceQueries";
  import { RECURRENCE_MODE_LABELS } from "../../../../constants/attendance.constants";
  import type { RecurrenceMode } from "../../../../constants/attendance.constants";
  import type { Employee } from "@/hr/modules/employees/types/types";
  import type { WorkPolicy, PolicyAssignment } from "../../../../types/types";
  import {
    createForm, FormView,
    select, date, validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  type EmployeeWithAssignment = Employee & {
    baseAssignment?: PolicyAssignment;
    overrideAssignment?: PolicyAssignment;
  };

  let { open = $bindable(false), employee = $bindable<EmployeeWithAssignment | null>(null) } = $props<{ open: boolean; employee: EmployeeWithAssignment | null }>();

  const policiesQuery = usePoliciesQuery();
  let policies = $derived($policiesQuery.data ?? []);

  const createMutation = useCreateAssignmentMutation();
  const updateMutation = useUpdateAssignmentMutation();
  const isEditing = $derived(!!employee?.baseAssignment?.id);

  // Recurrence local state (extras)
  let recurrenceMode = $state<RecurrenceMode>('none');
  let recurrenceCount = $state(4);
  let hasNoEndDate = $state(true);

  const fields: FieldConfig[] = [
    select('basePolicy', {
      label: 'Modèle de base',
      required: true,
      placeholder: 'Sélectionner un modèle',
      validators: [validators.required('Le modèle de base est requis')]
    }),
    date('startDate', { label: 'Date de début', required: true, defaultValue: new Date().toISOString().split('T')[0] }),
    date('endDate', { label: 'Date de fin', placeholder: 'Illimité' }),
    select('overridePolicy', { label: 'Modèle de remplacement (optionnel)', placeholder: 'Aucun' }),
    date('overrideStart', { label: 'Début remplacement', defaultValue: new Date().toISOString().split('T')[0] }),
    date('overrideEnd', { label: 'Fin remplacement' })
  ];

  const form = createForm({
    id: 'assignment-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Affectation', fields: ['basePolicy', 'startDate', 'endDate'] },
        { title: 'Remplacement', fields: ['overridePolicy', 'overrideStart', 'overrideEnd'] }
      ]
    },
    onSubmit: async (data) => {
      if (!employee || !data.basePolicy) throw new Error('Missing data');
      const computedEnd = recurrenceMode !== 'none' ? computeEnd(data.overrideStart, recurrenceMode, recurrenceCount) : data.overrideEnd;
      const payload = {
        policy_id: data.basePolicy,
        start_date: data.startDate,
        end_date: hasNoEndDate ? null : data.endDate || null,
        recurrence: 'NONE',
        override_policy_id: data.overridePolicy || null,
        override_valid_from: data.overridePolicy ? data.overrideStart : null,
        override_valid_until: computedEnd || null,
        override_recurrence: data.overridePolicy ? recurrenceMode.toUpperCase() : 'NONE',
        override_recurrence_count: data.overridePolicy && recurrenceMode !== 'none' ? recurrenceCount : null
      };
      if (isEditing && employee.baseAssignment?.id) {
        await $updateMutation.mutateAsync({ assignmentId: employee.baseAssignment.id, data: payload });
        notification.toast.success(`Affectation mise à jour pour ${employee.name}`);
      } else {
        await $createMutation.mutateAsync({ ...payload, employee_id: String(employee.id) });
        notification.toast.success(`Modèle affecté à ${employee.name}`);
      }
      document.dispatchEvent(new CustomEvent('assignments-changed'));
    }
  });

  function computeEnd(start: string, mode: RecurrenceMode, count: number): string {
    if (mode === 'none' || !start) return '';
    const d = new Date(start);
    if (mode === 'weekly') d.setDate(d.getDate() + 7 * count);
    else if (mode === 'biweekly') d.setDate(d.getDate() + 14 * count);
    else if (mode === 'monthly') d.setMonth(d.getMonth() + count);
    else if (mode === 'quarterly') d.setMonth(d.getMonth() + 3 * count);
    return d.toISOString().split('T')[0];
  }

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  // Sync policies into select dataSource + hydrate on open
  $effect(() => {
    const opts = policies.map(p => ({ value: p.id!, label: p.name }));
    form.setConfig({ fields: fields.map(f => f.id === 'basePolicy' || f.id === 'overridePolicy' ? { ...f, dataSource: { type: 'static', values: opts } } : f) as any });
  });
  $effect(() => {
    if (open && employee) {
      form.hydrate({
        basePolicy: employee.baseAssignment?.policyId ?? '',
        startDate: employee.baseAssignment?.startDate ?? new Date().toISOString().split('T')[0],
        endDate: employee.baseAssignment?.endDate ?? '',
        overridePolicy: employee.overrideAssignment?.policyId ?? '',
        overrideStart: employee.overrideAssignment?.startDate ?? new Date().toISOString().split('T')[0],
        overrideEnd: employee.overrideAssignment?.endDate ?? ''
      });
      hasNoEndDate = !employee.baseAssignment?.endDate;
      const rec = employee.overrideAssignment?.recurrence;
      recurrenceMode = rec && rec !== 'NONE' ? (rec.toLowerCase() as RecurrenceMode) : 'none';
      recurrenceCount = employee.overrideAssignment?.recurrenceCount ?? 4;
    }
  });

  const entity = $derived(employee ? { name: employee.name } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={isEditing ? "Modifier l'affectation" : "Affecter un modèle"}
  submitLabel={isEditing ? "Mettre à jour" : "Affecter"}
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
>
  {#snippet extras()}
    {#if form.values.overridePolicy}
      <div class="space-y-2">
        <p class="text-[0.85rem] font-medium">Récurrence</p>
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
            <span class="text-[0.82rem] text-blue-600">→ jusqu'au {computeEnd(form.values.overrideStart, recurrenceMode, recurrenceCount)}</span>
          </div>
        {/if}
      </div>
    {/if}
    <label class="flex items-center gap-2 text-[0.85rem]"><input type="checkbox" bind:checked={hasNoEndDate} /> Illimité</label>
  {/snippet}
</FormView>
