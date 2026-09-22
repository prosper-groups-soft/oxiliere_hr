import { createQuery } from '@tanstack/svelte-query';
import { payrollQueryOptions } from '@/hr/modules/payroll/queries/payroll';
import type { Payslip } from '@/hr/modules/payroll/types/types';


/**
 * Queries « bulletins par employé » — extraites de EmployeePayslipsSection.svelte
 * pour respecter le dossier `queries/` du module employees.
 *
 * Utilise `payrollQueryOptions.employeePayslips` / `payslipDetail` côté payroll
 * (filtre serveur `contract__employee_id`, tri `-created_at`).
 */

export function useEmployeePayslipsQuery(
  employeeId: () => string,
  opts: { page?: number; pageSize?: number; ordering?: string } = { page: 1, pageSize: 50, ordering: '-created_at' }
) {
  return createQuery({
    get queryKey() {
      return payrollQueryOptions.employeePayslips(employeeId(), opts).queryKey;
    },
    queryFn: () => payrollQueryOptions.employeePayslips(employeeId(), opts).queryFn(),
    staleTime: 1000 * 60 * 2,
    gcTime: 1000 * 60 * 10,
    refetchOnWindowFocus: true,
    get enabled() {
      return !!employeeId();
    }
  });
}

export function usePayslipDetailQuery(
  payslipId: () => string | null,
  getInitial?: () => Payslip | null
) {
  return createQuery({
    get queryKey() {
      return payrollQueryOptions.payslipDetail(payslipId() ?? '').queryKey;
    },
    queryFn: () => payrollQueryOptions.payslipDetail(payslipId() ?? '').queryFn(),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
    get enabled() {
      return !!payslipId();
    },
    //  cache local → sheet instantané, backend reste vérité (refetch si stale)
    get initialData() {
      return (getInitial?.() as any) ?? undefined;
    },
    get initialDataUpdatedAt() {
      return getInitial?.() ? Date.now() - 1000 * 60 : 0;
    }
  });
}

