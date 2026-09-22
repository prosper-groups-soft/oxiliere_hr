<script lang="ts">
  import { notification } from "@/hr/stores/notification.svelte";
  import { employeesService } from "@/hr/modules/employees/services/employees.service";
  import { payrollStore } from "../../../stores/payroll.svelte";
  import type { Advance } from "../../../types/types";
  import {
    createForm, FormView,
    number, select, cancel
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { advance = null as Advance | null, open = $bindable(false), onApproved } = $props<{ advance: Advance | null; open: boolean; onApproved?: (a: Advance) => void }>();

  // Reference salary for estimation
  let refSalary = $state(0);
  let refCurrency = $state('CDF');
  $effect(() => {
    const empId = advance?.employee?.id;
    if (!empId) { refSalary = 0; return; }
    employeesService.getEmployeeDetail(String(empId)).then((p: any) => {
      const c = p?.current_contract?.is_active ? p.current_contract : null;
      refSalary = c ? Number(c.remuneration_type === 'HOURLY' ? (c.hourly_rate ?? 0) : (c.base_salary ?? 0)) : 0;
      refCurrency = c?.currency ?? 'CDF';
    }).catch(() => refSalary = 0);
  });

  const amount = $derived(Number(advance?.amount ?? 0));

  const fields: FieldConfig[] = [
    ({ id: 'repaymentPlan', type: 'repaymentPlan' as any, label: 'Plan de remboursement', defaultValue: { percentage: 20, months: 3, startMonth: '', refSalary, amount, currency: refCurrency } } as FieldConfig),
    select('deductionBase', {
      label: 'Base de déduction',
      defaultValue: 'NET',
      dataSource: { type: 'static', values: [{ value: 'GROSS', label: 'Salaire brut' }, { value: 'NET', label: 'Salaire net' }] }
    }),
    select('taxTiming', {
      label: 'Moment de la retenue',
      defaultValue: 'AFTER_TAX',
      dataSource: { type: 'static', values: [{ value: 'BEFORE_TAX', label: 'Avant impôt' }, { value: 'AFTER_TAX', label: 'Après impôt' }] }
    }),
    number('priorityOrder', { label: 'Priorité', min: 1, defaultValue: 1 })
  ];

  const form = createForm({
    id: 'advance-approve-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'sheet', side: 'right', width: 'sm:max-w-xl' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Remboursement', fields: ['repaymentPlan'] },
        { title: 'Configuration', fields: ['deductionBase', 'taxTiming', 'priorityOrder'] }
      ]
    },
    onSubmit: async (data) => {
      if (!advance) return;
      const plan = data.repaymentPlan ?? { percentage: 20, months: 3, startMonth: '' };
      let pct = Number(plan.percentage ?? 20);
      const dur = Math.max(1, Math.ceil(amount / (refSalary * (pct / 100) || 1)));
      const startMonth = plan.startMonth ? String(plan.startMonth).slice(0, 7) + '-01' : '';
      const endMonth = startMonth ? (() => { const [y, m] = startMonth.split('-').map(Number); const d = new Date(y, m - 1 + dur, 1); return `${d.getFullYear()}-${String(d.getMonth()+1).padStart(2,'0')}-01`; })() : '';

      const configPayload: any = {
        repayment_percentage: pct,
        salary_base_for_deduction: data.deductionBase,
        tax_timing: data.taxTiming,
        deduction_window: startMonth ? 'CUSTOM_PERIOD' : 'ALL_MONTHS',
        ...(startMonth ? { deduction_start_date: startMonth, deduction_end_date: endMonth } : {}),
        priority_order: Number(data.priorityOrder),
        is_active: true
      };
      const updated = await payrollStore.approveAdvance(advance.id);
      await payrollStore.updateAdvanceConfig(advance.id, configPayload);
      notification.toast.success("Demande approuvée");
      onApproved?.(updated ?? advance);
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) notification.toast.error(e.message);
    else notification.toast.error("Veuillez corriger les erreurs");
  });

  $effect(() => {
    if (open && advance) {
      form.hydrate({
        repaymentPlan: { percentage: advance.repayment_percentage ?? 20, months: 3, startMonth: '', refSalary, amount, currency: refCurrency },
        deductionBase: (advance as any).salary_base_for_deduction ?? 'NET',
        taxTiming: (advance as any).tax_timing ?? 'AFTER_TAX',
        priorityOrder: 1
      });
    }
  });
</script>

<FormView
  {form}
  fields={fields}
  bind:open
  title="Approuver l'avance"
  submitLabel="Approuver"
  submitIcon="check-circle"
  showReset={false}
  actions={[cancel('Annuler', { icon: 'x', variant: 'secondary', handler: () => { open = false; } })]}
/>
