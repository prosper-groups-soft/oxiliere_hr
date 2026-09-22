<script lang="ts">
  import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import type { EmployeeFullProfile } from '@/hr/modules/employees/types/types';
  import { cn } from '@/hr/utilities/common/css';
  import { CONTRACT_TYPES, REMUNERATION_TYPES, SALARY_BASE_TYPES } from '@/hr/modules/employees/constants/contract';
  import ContractPayElementList from '@/hr/modules/employees/components/shared/ContractPayElementList.svelte';
  import { useContractPayElementsQuery, useCreateContractPayElementMutation, usePatchContractPayElementMutation, useDeleteContractPayElementMutation, usePayrollAdjustmentsQuery } from '@/hr/modules/payroll/queries/payrollHooks';
  import type { ContractPayElementInput } from '@/hr/modules/payroll/types/types';


  let { employee } = $props<{ employee: EmployeeFullProfile }>();

  const contract = $derived(employee.current_contract);

  // S10 — éléments de paie du contrat (TanStack Query)
  const contractId = $derived(contract?.id ?? '');
  const payElementsQuery = $derived(
    useContractPayElementsQuery(() => contractId)
  );
  const adjustmentsQuery = usePayrollAdjustmentsQuery();

  const payElements = $derived(
    $payElementsQuery.data?.elements ?? employee.contract_adjustments ?? []
  );

  const createMutation = useCreateContractPayElementMutation();
  const patchMutation = usePatchContractPayElementMutation();
  const deleteMutation = useDeleteContractPayElementMutation();

  const catalog = $derived($adjustmentsQuery.data ?? []);

  /** Payload envoyé au parent (correspond à ContractAdjustmentCreateIn backend) */
  async function handleAdd(payload: ContractPayElementInput) {
    if (!contractId) return;
    await $createMutation.mutateAsync({ contractId, data: payload });
  }

  async function handleToggle(el: any, active: boolean) {
    if (!contractId) return;
    await $patchMutation.mutateAsync({ contractId, elementId: el.id, data: { is_active: active } });
  }

  async function handleDelete(el: any, _index?: number) {
    if (!contractId) return;
    await $deleteMutation.mutateAsync({ contractId, elementId: el.id });
  }

  const formattedSalary = $derived(() => {
    if (!contract) return '-';
    const salary = contract.remuneration_type === 'HOURLY' ? contract.hourly_rate : contract.base_salary;
    if (!salary) return '-';
    return new Intl.NumberFormat('fr-FR').format(salary);
  });

  const formattedContractStartDate = $derived(() => {
    if (!contract?.start_date) return '-';
    return new Date(contract.start_date).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  });

  const formattedContractEndDate = $derived(() => {
    if (!contract?.end_date) return '-';
    return new Date(contract.end_date).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'long',
      year: 'numeric'
    });
  });

  const contractTypeLabels: Record<string, string> = Object.fromEntries(CONTRACT_TYPES.map(t => [t.value, t.label]));
  const remunerationTypeLabels: Record<string, string> = Object.fromEntries(REMUNERATION_TYPES.map(t => [t.value, t.label]));
  const salaryBaseTypeLabels: Record<string, string> = Object.fromEntries(SALARY_BASE_TYPES.map(t => [t.value, t.label]));
</script>


{#snippet Field(label: string, value: string)}
  <div class="space-y-1">
    <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400">{label}</div>
    <p class="text-[0.86rem] font-medium text-slate-900 leading-snug wrap-break-word">{value}</p>
  </div>
{/snippet}


<div class="space-y-4">
  <!-- Poste et Unité organisationnelle -->
  <Card class="rounded-xl border-slate-200 bg-white shadow-fine overflow-hidden">
    <CardHeader class="pb-3 border-b border-slate-50">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-indigo-50 border border-indigo-100 flex items-center justify-center shrink-0">
          <AppIcon name="briefcase" size={16} class="text-indigo-600" />
        </span>
        Poste
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {@render Field("Poste", employee.job_title || '-')}
        {@render Field("Niveau de séniorité", employee.seniority_level || '-')}
        {@render Field("Unité organisationnelle", employee.org_unit || '-')}
      </div>
    </CardContent>
  </Card>

  <!-- Type de contrat -->
  <Card class="rounded-xl border-slate-200 bg-white shadow-fine overflow-hidden">
    <CardHeader class="pb-3 border-b border-slate-50">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-violet-50 border border-violet-100 flex items-center justify-center shrink-0">
          <AppIcon name="file-text" size={16} class="text-violet-600" />
        </span>
        Type de contrat
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {@render Field("Type de contrat", contract ? contractTypeLabels[contract.contract_type] || contract.contract_type : '-')}
        <div class="space-y-1">
          <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400">Statut du contrat</div>
          <div class="inline-flex items-center gap-2 px-2.5 py-1 rounded-full border text-[0.84rem] font-medium {contract?.is_active ? 'bg-emerald-50 border-emerald-200 text-emerald-700' : 'bg-slate-50 border-slate-200 text-slate-600'}">
            <span class={cn("h-2 w-2 rounded-full", contract?.is_active ? "bg-emerald-500" : "bg-slate-400")}></span>
            {contract?.is_active ? 'Actif' : 'Inactif'}
          </div>
        </div>
        <div class="hidden lg:block"></div>
      </div>
    </CardContent>
  </Card>

  <!-- Rémunération -->
  <Card class="rounded-xl border-slate-200 bg-white shadow-fine overflow-hidden">
    <CardHeader class="pb-3 border-b border-slate-50">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-emerald-50 border border-emerald-100 flex items-center justify-center shrink-0">
          <AppIcon name="banknote" size={16} class="text-emerald-600" />
        </span>
        Rémunération
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-4 space-y-5">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {@render Field("Type de rémunération", contract ? remunerationTypeLabels[contract.remuneration_type] || contract.remuneration_type : '-')}
        <div class="space-y-1">
          <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400">Salaire</div>
          <p class="text-[0.86rem] font-medium text-slate-900 leading-snug wrap-break-word">{formattedSalary()} {#if contract?.currency}<span class="text-slate-500 font-normal">{contract.currency}</span>{/if}</p>
        </div>
        {@render Field("Base de calcul", contract ? salaryBaseTypeLabels[contract.salary_base_type] || contract.salary_base_type : '-')}
        {@render Field("Devise", contract?.currency || '-')}
      </div>

      {#if contract?.contractual_clauses}
        <div class="rounded-lg bg-slate-50/70 border border-slate-100 p-4">
          <div class="text-[0.78rem] font-bold uppercase tracking-widest text-slate-400 mb-2">Clauses particulières</div>
          <p class="text-[0.86rem] text-slate-700 leading-relaxed whitespace-pre-line">{contract.contractual_clauses}</p>
        </div>
      {/if}
    </CardContent>
  </Card>

  <!-- Dates -->
  <Card class="rounded-xl border-slate-200 bg-white shadow-fine overflow-hidden">
    <CardHeader class="pb-3 border-b border-slate-50">
      <CardTitle class="flex items-center gap-2.5 text-[0.92rem] font-bold tracking-tight">
        <span class="h-8 w-8 rounded-lg bg-sky-50 border border-sky-100 flex items-center justify-center shrink-0">
          <AppIcon name="calendar" size={16} class="text-sky-600" />
        </span>
        Dates
      </CardTitle>
    </CardHeader>
    <CardContent class="pt-4">
      <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-5">
        {@render Field("Date de début du contrat", formattedContractStartDate())}
        {@render Field("Date de fin du contrat", formattedContractEndDate())}
        <div class="hidden lg:block"></div>
      </div>
    </CardContent>
  </Card>

  <!-- Éléments de paie du contrat -->
  <ContractPayElementList
    {contractId}
    elements={payElements}
    {catalog}
    isLoading={$payElementsQuery.isLoading}
    catalogLoading={$adjustmentsQuery.isLoading}
    catalogError={$adjustmentsQuery.isError}
    onAdd={handleAdd}
    onToggle={handleToggle}
    onDelete={handleDelete}
  />
</div>

