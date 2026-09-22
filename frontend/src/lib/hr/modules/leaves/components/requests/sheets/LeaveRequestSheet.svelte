<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { LEAVE_TYPE_LABELS, CIRCUMSTANCE_TYPE_LABELS, CIRCUMSTANCE_TYPE_OPTIONS, BACKEND_CIRCUMSTANCE_TYPES } from '../../../constants/leaves';
  import type { LeaveType, CircumstanceType, WorkingDaysCount } from '../../../types/types';
  import type { BalanceSummary } from '../../../api/leaveRequests.endpoints';
  import { useCreateLeaveRequestMutation, useUpdateLeaveRequestMutation, leaveQueryKeys } from '../../../queries/leaveQueries';
  import { useQueryClient } from '@tanstack/svelte-query';
  import { leaveRequestsEndpoint } from '../../../api/leaveRequests.endpoints';
  import { DEFAULT_LEAVE_CONFIG } from '@/hr/modules/leaves/types/leaveSettings.types';
  import { useLeaveConfigQuery } from '../../../queries/leaveQueries';
  import {
    createForm, FormView,
    employee, select, date, textarea, file,
    validators, invariant, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false), request = $bindable(null) } = $props<{ open: boolean; request?: any }>();

  const queryClient = useQueryClient();
  const createMutation = useCreateLeaveRequestMutation();
  const updateMutation = useUpdateLeaveRequestMutation();
  const leaveConfigQuery = useLeaveConfigQuery();
  let leaveConfig = $derived($leaveConfigQuery.data ?? DEFAULT_LEAVE_CONFIG);

  // --- Derived context for validation/preview ---
  let balance = $state<BalanceSummary | null>(null);
  let workingDays = $state<WorkingDaysCount | null>(null);
  let calculating = $state(false);
  let overlap = $state<{ hasOverlap: boolean; leaves: any[] } | null>(null);

  // Fetch balance when employee changes
  $effect(() => {
    const empId = form.values.employeeId as string | undefined;
    if (!empId || !/^[0-9a-f-]{36}$/i.test(empId)) { balance = null; return; }
    leaveRequestsEndpoint.getBalanceSummary(empId).then(d => balance = d).catch(() => balance = null);
  });

  // Debounced working days fetch
  let timer: ReturnType<typeof setTimeout> | null = null;
  $effect(() => {
    const empId = form.values.employeeId as string | undefined;
    const start = form.values.startDate as string | undefined;
    const end = form.values.endDate as string | undefined;
    if (!empId || !start || !end) { workingDays = null; return; }
    if (timer) clearTimeout(timer);
    timer = setTimeout(async () => {
      calculating = true;
      try { workingDays = await leaveRequestsEndpoint.countWorkingDays(empId, start, end); }
      catch { workingDays = null; }
      finally { calculating = false; }
    }, 300);
  });

  // Overlap check
  $effect(() => {
    const empId = form.values.employeeId as string | undefined;
    const start = form.values.startDate as string | undefined;
    const end = form.values.endDate as string | undefined;
    const type = form.values.type as string | undefined;
    if (!empId || !start || !end || !open || request) { overlap = null; return; }
    const excluded = type === 'sick' ? 'ANNUAL,CIRCUMSTANCE,UNPAID' : undefined;
    leaveRequestsEndpoint.checkOverlap(empId, start, end, excluded).then(d => overlap = d).catch(() => overlap = null);
  });

  const displayDays = $derived(workingDays?.workingDays ?? 0);
  const isAnnual = $derived(form.values.type === 'annual');
  const isCircumstantial = $derived(form.values.type === 'circumstantial');
  const requiresAttachment = $derived(
    form.values.type === 'sick' ||
    (isCircumstantial && form.values.circumstanceType === 'CHILD_HOSPITALIZATION')
  );

  const LEAVE_OPTIONS = Object.entries(LEAVE_TYPE_LABELS).map(([value, label]) => ({ value, label }));
  const CIRCUMSTANCE_OPTIONS = CIRCUMSTANCE_TYPE_OPTIONS.map(o => ({ value: o.value, label: o.label }));

  const fields: FieldConfig[] = [
    ({ id: 'preview', type: 'workingDaysTimeline' as any, label: 'Aperçu période', dependencies: { dependsOn: ['employeeId', 'startDate', 'endDate'], compute: async (vals: any) => {
      if (!vals.employeeId || !vals.startDate || !vals.endDate) return null;
      try { return await leaveRequestsEndpoint.countWorkingDays(vals.employeeId, vals.startDate, vals.endDate); } catch { return null; }
    }, debounceMs: 300 } } as FieldConfig),
    employee('employeeId', {
      out: 'employee_id',
      label: 'Employé',
      required: true,
      validators: [validators.required("L'employé est requis")]
    }),
    select('type', {
      label: 'Type de congé',
      required: true,
      defaultValue: 'annual',
      dataSource: { type: 'static', values: LEAVE_OPTIONS },
      validators: [validators.required('Le type est requis')]
    }),
    select('circumstanceType', {
      out: 'circumstance_type',
      label: 'Type de circonstance',
      placeholder: 'Sélectionner une circonstance',
      dataSource: { type: 'static', values: CIRCUMSTANCE_OPTIONS },
      dependencies: { visibleIf: (vals: any) => vals.type === 'circumstantial' }
    }),
    date('startDate', {
      out: 'start_date',
      label: 'Date de début',
      required: true,
      validators: [validators.required('La date de début est requise')]
    }),
    date('endDate', {
      out: 'end_date',
      label: 'Date de fin',
      required: true,
      validators: [validators.required('La date de fin est requise')]
    }),
    textarea('reason', {
      label: 'Motif',
      required: true,
      placeholder: 'Précisez le motif...',
      validators: [validators.required('Le motif est requis')]
    }),
    file('attachment', {
      label: 'Justificatif',
      accept: 'application/pdf,image/*',
      dependencies: { visibleIf: () => requiresAttachment }
    })
  ];

  const form = createForm({
    id: 'leave-request-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Demandeur', fields: ['employeeId'] },
        { title: 'Type', fields: ['type', 'circumstanceType'] },
        { title: 'Période', fields: ['startDate', 'endDate', 'preview'] },
        { title: 'Motif', fields: ['reason', 'attachment'] }
      ]
    },
    validators: [
      invariant((v) => {
        if (v.startDate && v.endDate && v.endDate < v.startDate) return { valid: false, field: 'endDate' };
        return { valid: true };
      }, 'La date de fin doit être postérieure au début'),
      invariant((v) => {
        if (v.type === 'circumstantial' && !v.circumstanceType) return { valid: false, field: 'circumstanceType' };
        return { valid: true };
      }, 'Veuillez sélectionner un type de circonstance'),
      invariant((v) => {
        if (!v.startDate || !v.endDate || !workingDays) return { valid: true };
        const d = workingDays.workingDays;
        if (v.type === 'annual' && leaveConfig.maxConsecutiveDays > 0 && d > leaveConfig.maxConsecutiveDays)
          return { valid: false, field: 'endDate' };
        if (v.type === 'circumstantial' && v.circumstanceType) {
          const sl = leaveConfig.specialLeaves.find(s => s.type === v.circumstanceType);
          if (sl && sl.daysAllowed > 0 && d > sl.daysAllowed) return { valid: false, field: 'endDate' };
        }
        if (v.type === 'annual' && balance && d > balance.available) return { valid: false, field: 'endDate' };
        return { valid: true };
      }, 'La période dépasse les limites autorisées'),
      invariant((v) => {
        const need = v.type === 'sick' || (v.type === 'circumstantial' && v.circumstanceType === 'CHILD_HOSPITALIZATION');
        if (need && !v.attachment && !(request?.attachment)) return { valid: false, field: 'attachment' };
        return { valid: true };
      }, 'Le justificatif est requis')
    ],
    onSubmit: async (data, extra) => {
      const isEdit = !!request;
      const payload: any = {
        type: data.type,
        startDate: data.startDate,
        endDate: data.endDate,
        reason: data.reason?.trim(),
      };
      if (data.type === 'circumstantial' && data.circumstanceType) {
        const bt = BACKEND_CIRCUMSTANCE_TYPES[data.circumstanceType as CircumstanceType];
        if (bt) payload.circumstanceType = bt;
      }
      const fileAttachment = extra?.files?.attachment?.[0] ?? data.attachment;
      if (fileAttachment) payload.attachment = fileAttachment;

      if (isEdit) {
        await $updateMutation.mutateAsync({ requestId: request.id, ...payload });
      } else {
        await $createMutation.mutateAsync({ employeeId: String(data.employeeId), ...payload });
        await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.requests() });
      }
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });

  const entity = $derived(request ? {
    employeeId: request.employeeId,
    type: request.type,
    circumstanceType: request.circumstanceType ?? '',
    startDate: request.startDate,
    endDate: request.endDate,
    reason: request.reason ?? ''
  } : null);
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  entity={entity}
  title={request ? "Modifier la demande" : "Nouvelle demande de congé"}
  submitLabel={request ? "Mettre à jour" : "Soumettre"}
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
>
  {#snippet extras()}
    {#if overlap?.hasOverlap}
      <p class="text-[0.82rem] text-amber-600">⚠ Chevauchement avec {overlap.leaves.length} congé(s) existant(s)</p>
    {/if}
    {#if balance && isAnnual}
      <p class="text-[0.82rem] text-slate-500">Solde : <strong>{balance.available}j dispo</strong> / {balance.allocated}j alloués{#if balance.carryOver?.available} · {balance.carryOver.available}j reportés{/if}</p>
    {/if}
  {/snippet}
</FormView>
