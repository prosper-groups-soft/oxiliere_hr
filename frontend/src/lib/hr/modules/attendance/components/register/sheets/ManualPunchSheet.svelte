<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { attendanceStore } from "../../../stores/attendance.svelte";
  import {
    createForm, FormView,
    employee, date, select, validators, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { open = $bindable(false) } = $props<{ open: boolean }>();

  const STATUS_OPTIONS = [
    { value: 'PRESENT', label: 'Présent' },
    { value: 'LATE', label: 'Retard' },
    { value: 'ABSENT', label: 'Absent' }
  ];

  const punchFields: FieldConfig[] = [
    employee('employeeId', {
      out: 'employeeId',
      label: 'Employé',
      required: true,
      validators: [validators.required("L'employé est requis")]
    }),
    date('date', {
      label: 'Date',
      required: true,
      defaultValue: new Date().toISOString().split('T')[0],
      validators: [validators.required('La date est requise')]
    }),
    select('status', {
      label: 'Statut',
      required: true,
      defaultValue: 'PRESENT',
      dataSource: { type: 'static', values: STATUS_OPTIONS }
    }),
    date('checkIn', { label: 'Arrivée', defaultValue: '08:00' }),
    date('checkOut', { label: 'Départ', defaultValue: '17:00' })
  ];

  // Use text fields for time inputs — date field handles date, time via text with type time
  punchFields[3] = { ...punchFields[3], type: 'text' as any, placeholder: 'HH:MM' } as FieldConfig;
  punchFields[4] = { ...punchFields[4], type: 'text' as any, placeholder: 'HH:MM' } as FieldConfig;

  const form = createForm({
    id: 'manual-punch-form',
    fields: punchFields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-md' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Employé', fields: ['employeeId'] },
        { title: 'Date & Statut', fields: ['date', 'status'] },
        { title: 'Horaires', fields: ['checkIn', 'checkOut'] }
      ]
    },
    onSubmit: async (data) => {
      // Resolve employee display data for store
      const { employeeStore } = await import("@/hr/modules/employees/stores/employees.svelte");
      const emp = employeeStore.employees.find((e: any) => String(e.id) === String(data.employeeId));
      if (!emp) {
        notification.toast.error("Employé introuvable");
        throw new Error("Employee not found");
      }
      attendanceStore.addRecord({
        employeeId: emp.id,
        employeeName: emp.name,
        avatarUrl: emp.avatarUrl,
        orgUnit: emp.orgUnit ?? '',
        date: data.date,
        checkIn: data.checkIn ?? '08:00',
        checkOut: data.checkOut ?? '17:00',
        status: data.status as any
      });
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs du formulaire");
  });
</script>

<FormView
  {form}
  fields={punchFields}
  bind:open
  title="Pointage Manuel"
  submitLabel="Enregistrer"
  submitIcon="check"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
