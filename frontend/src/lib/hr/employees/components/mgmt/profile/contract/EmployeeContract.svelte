<script lang="ts">
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';
  import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
  import type { EmployeeFullProfile } from '@/hr/employees/types/types';
  import { cn } from '@/utilities/common/css';
  import { CONTRACT_TYPES, REMUNERATION_TYPES, SALARY_BASE_TYPES } from '@/hr/employees/constants/contract';
  import ContractPayElementList from '@/hr/employees/components/shared/ContractPayElementList.svelte';
  import { useContractPayElementsQuery, useCreateContractPayElementMutation, usePatchContractPayElementMutation, useDeleteContractPayElementMutation, usePayrollAdjustmentsQuery } from '@/hr/payroll/queries/payrollHooks';
  import type { ContractPayElementInput } from '@/hr/payroll/types/types';


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


<div class="space-y-6">
  <!-- Poste et Unité organisationnelle -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="briefcase" size={18} />
        Poste
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div class="text-sm font-medium text-slate-500">Poste</div>
          <p class="text-sm text-slate-900 mt-1">{employee.job_title || '-'}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Niveau de séniorité</div>
          <p class="text-sm text-slate-900 mt-1">{employee.seniority_level || '-'}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Unité organisationnelle</div>
          <p class="text-sm text-slate-900 mt-1">{employee.org_unit || '-'}</p>
        </div>
      </div>
    </CardContent>
  </Card>

  <!-- Type de contrat -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="file-text" size={18} />
        Type de contrat
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div class="text-sm font-medium text-slate-500">Type de contrat</div>
          <p class="text-sm text-slate-900 mt-1">
            {contract ? contractTypeLabels[contract.contract_type] || contract.contract_type : '-'}
          </p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Statut du contrat</div>
          <div class="flex items-center gap-2 mt-1">
            <div class={cn(
              "h-2 w-2 rounded-full",
              contract?.is_active ? "bg-emerald-500" : "bg-slate-400"
            )}></div>
            <span class="text-sm text-slate-700">
              {contract?.is_active ? 'Actif' : 'Inactif'}
            </span>
          </div>
        </div>
      </div>
    </CardContent>
  </Card>

  <!-- Rémunération -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="banknote" size={18} />
        Rémunération
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div class="text-sm font-medium text-slate-500">Type de rémunération</div>
          <p class="text-sm text-slate-900 mt-1">
            {contract ? remunerationTypeLabels[contract.remuneration_type] || contract.remuneration_type : '-'}
          </p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Salaire</div>
          <p class="text-sm text-slate-900 mt-1">
            {formattedSalary()} {contract?.currency || ''}
          </p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Base de calcul</div>
          <p class="text-sm text-slate-900 mt-1">
            {contract ? salaryBaseTypeLabels[contract.salary_base_type] || contract.salary_base_type : '-'}
          </p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Devise</div>
          <p class="text-sm text-slate-900 -1">
            {contract?.currency || '-'}
          </p>
        </div>
      </div>

      {#if contract?.contractual_clauses}
        <div class="pt-3 border-t border-slate-100">
          <div class="text-sm font-medium text-slate-500 mb-1">Clauses particulières</div>
          <p class="text-[0.82rem] text-slate-600 whitespace-pre-line">{contract.contractual_clauses}</p>
        </div>
      {/if}
    </CardContent>
  </Card>

  <!-- Dates -->
  <Card class="shadow-none py-4">
    <CardHeader>
      <CardTitle class="flex items-center gap-2 text-[0.98rem]">
        <AppIcon name="calendar" size={18} />
        Dates
      </CardTitle>
    </CardHeader>
    <CardContent class="space-y-4">
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <div class="text-sm font-medium text-slate-500">Date de début du contrat</div>
          <p class="text-sm text-slate-900 mt-1">{formattedContractStartDate()}</p>
        </div>
        <div>
          <div class="text-sm font-medium text-slate-500">Date de fin du contrat</div>
          <p class="text-sm text-slate-900 mt-1">{formattedContractEndDate()}</p>
        </div>
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

