<script lang="ts">
  import { notification } from '@/hr/stores/notification.svelte';
  import { usePositionsQuery } from "@/hr/modules/employees/queries/onboardingQueries";
  import { CONTRACT_TYPES, REMUNERATION_TYPES, type ContractType, type RemunerationType, type SalaryBaseType, type Currency } from "@/hr/modules/employees/constants/contract";
  import { payrollConfigStore } from "@/hr/modules/payroll/stores/configuration/payrollConfigStore.svelte";
  import {
    createForm, FormView,
    select, number, date, text, textarea, switchField,
    validators
  } from "@/hr/forms/index.js";
  import type { FieldConfig } from "@/hr/forms/core/types.js";

  let { employee, onSave } = $props<{ employee: any; onSave: (data: any) => void }>();

  const positionsQuery = usePositionsQuery();
  let positionOptions = $derived(($positionsQuery.data ?? []).map((p: any) => ({ value: p.id, label: p.name })));

  $effect(() => { if (!payrollConfigStore.configuration) payrollConfigStore.syncConfiguration(); });

  const workHoursPerMonth = $derived(payrollConfigStore.configuration?.work_hours_per_month ?? Math.round((payrollConfigStore.configuration?.work_hours_per_week ?? 45) * 52 / 12));

  const fields: FieldConfig[] = [
    select('position_id', {
      label: 'Poste',
      required: true,
      placeholder: 'Sélectionner un poste...',
      validators: [validators.required('Le poste est requis')]
    }),
    select('seniority_level_id', {
      label: 'Niveau de séniorité',
      required: true,
      placeholder: 'Sélectionner...',
      validators: [validators.required('Le niveau est requis')],
      dependencies: { dependsOn: 'position_id', compute: () => '' }
    }),
    select('contract_type', {
      label: 'Type de contrat',
      required: true,
      defaultValue: 'CDI',
      dataSource: { type: 'static', values: CONTRACT_TYPES.map(t => ({ value: t.value, label: t.label })) }
    }),
    select('remuneration_type', {
      label: 'Type de rémunération',
      required: true,
      defaultValue: 'FIXED',
      dataSource: { type: 'static', values: REMUNERATION_TYPES.map(t => ({ value: t.value, label: t.label })) }
    }),
    number('salary', {
      label: 'Salaire',
      required: true,
      min: 0,
      validators: [validators.required('Le salaire est requis'), validators.min(1, 'Le salaire doit être > 0')]
    }),
    select('salary_base_type', {
      label: 'Base de calcul',
      required: true,
      defaultValue: 'NET',
      dataSource: { type: 'static', values: [{ value: 'BASE', label: 'Base' }, { value: 'NET', label: 'Net' }] }
    }),
    select('currency', {
      label: 'Devise',
      required: true,
      defaultValue: 'CDF',
      dataSource: { type: 'static', values: [{ value: 'CDF', label: 'FC' }, { value: 'USD', label: 'USD' }, { value: 'EUR', label: 'EUR' }] }
    }),
    date('hire_date', { label: 'Date de début', required: true, validators: [validators.required('La date de début est requise')] }),
    date('end_date', { label: 'Date de fin' }),
    textarea('contractual_clauses', { label: 'Clauses particulières', placeholder: 'Clause de non-concurrence, période d\'essai...' }),
    switchField('is_active', { label: 'Contrat actif', defaultValue: true })
  ];

  const form = createForm({
    id: 'employee-contract-form',
    fields,
    validationTiming: 'onBlur',
    host: { type: 'inline', variant: 'plain' },
    layout: {
      type: 'section',
      sections: [
        { title: 'Poste et Unité', fields: ['position_id', 'seniority_level_id'] },
        { title: 'Type et Rémunération', fields: ['contract_type', 'remuneration_type', 'salary', 'salary_base_type', 'currency'] },
        { title: 'Dates du contrat', fields: ['hire_date', 'end_date'] },
        { title: 'Métamodèle', fields: ['contractual_clauses'] },
        { title: 'Statut', fields: ['is_active'] }
      ]
    },
    onSubmit: async (data) => {
      const payload = {
        ...data,
        end_date: data.end_date?.trim() ? data.end_date : null,
        base_salary: data.remuneration_type === 'FIXED' ? data.salary : null,
        hourly_rate: data.remuneration_type === 'HOURLY' ? data.salary : null
      };
      onSave(payload);
    }
  });

  form.on('error', (e: unknown) => {
    if (e instanceof Error) return;
    notification.toast.error("Veuillez corriger les erreurs");
  });

  // Hydrate
  $effect(() => {
    if (employee) {
      const c = employee.current_contract;
      form.hydrate({
        position_id: employee.position_id ?? '',
        seniority_level_id: employee.seniority_level_id ?? '',
        contract_type: c?.contract_type ?? 'CDI',
        remuneration_type: c?.remuneration_type ?? 'FIXED',
        salary: c?.remuneration_type === 'HOURLY' ? parseFloat(String(c?.hourly_rate ?? 0)) : parseFloat(String(c?.base_salary ?? 0)),
        salary_base_type: c?.salary_base_type ?? 'NET',
        currency: c?.currency ?? 'CDF',
        hire_date: (c?.start_date ?? employee.hire_date ?? '').split('T')[0],
        end_date: (c?.end_date ?? employee.termination_date ?? '').split('T')[0],
        contractual_clauses: c?.contractual_clauses ?? '',
        is_active: c?.is_active ?? true
      });
    }
  });

  // Dynamic datasources: positions + seniority cascade
  $effect(() => {
    form.setConfig({ fields: fields.map(f => f.id === 'position_id' ? { ...f, dataSource: { type: 'static', values: positionOptions } } : f) as any });
  });
  $effect(() => {
    const posId = form.values.position_id as string | undefined;
    const pos = ($positionsQuery.data ?? []).find((p: any) => p.id === posId);
    const opts = (pos?.seniority_levels ?? []).map((s: any) => ({
      value: s.seniority_level?.id ?? s.id,
      label: `${s.seniority_level?.label ?? s.label} (${s.seniority_level?.level ?? s.level})`
    }));
    form.setConfig({ fields: fields.map(f => f.id === 'seniority_level_id' ? { ...f, dataSource: { type: 'static', values: opts } } : f) as any });
  });

  export function submit() { form.submit(); }
</script>

<FormView {form} fields={fields} showSubmit={false} showReset={false} />

{#if form.values.remuneration_type === 'HOURLY' && Number(form.values.salary) > 0}
  <p class="text-[0.82rem] text-slate-500 mt-2">≈ {(Number(form.values.salary) * workHoursPerMonth).toLocaleString('fr-FR')} {form.values.currency}/mois ({workHoursPerMonth}h/mois)</p>
{/if}
