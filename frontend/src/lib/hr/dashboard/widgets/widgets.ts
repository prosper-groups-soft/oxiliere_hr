import type { WidgetDef } from '../core/dashboard';
import { employeesService } from '@/hr/modules/employees/services/employees.service';
import { recruitmentService } from '@/hr/modules/recruitment/services/recruitmentService';
import { leaveRequestsEndpoint } from '@/hr/modules/leaves/api/leaveRequests.endpoints';
import { payrollService } from '@/hr/modules/payroll/services/payrollService';

export function headcount(): WidgetDef {
  return {
    id: 'headcount', metric: 'headcount', source: () => ({ queryKey: ['dashboard', 'headcount'], queryFn: () => employeesService.listEmployees(1, 1, '', {} as any, 'name', 'asc') }),
    mapData: (d: any) => ({ value: String(d.count ?? 0), label: 'Total Employés', sublabel: 'Effectif total', icon: 'users', color: 'text-slate-600' }),
    visibleIf: (r) => r === 'admin' || r === 'hr'
  };
}

export function leavesPending(): WidgetDef {
  return {
    id: 'leavesPending', metric: 'leavesPending', source: () => ({ queryKey: ['dashboard', 'leavesPending'], queryFn: () => leaveRequestsEndpoint.listRequests({ status: ['pending'] } as any) }),
    mapData: (d: any) => ({ value: String(d.count ?? d.length ?? 0), label: 'Congés en attente', sublabel: 'À valider', icon: 'calendar', color: 'text-amber-600' }),
    visibleIf: (r) => r === 'admin' || r === 'hr'
  };
}

export function recruitmentOpen(): WidgetDef {
  return {
    id: 'recruitmentOpen', metric: 'recruitmentOpen', source: () => ({ queryKey: ['dashboard', 'recruitmentOpen'], queryFn: () => recruitmentService.listJobOffers(1, 1, undefined, true, '', 'OPEN', [], 'name', 'asc') }),
    mapData: (d: any) => ({ value: String(d.count ?? 0), label: 'Recrutements', sublabel: 'Postes ouverts', icon: 'briefcase', color: 'text-indigo-600' }),
    visibleIf: (r) => r === 'admin' || r === 'hr'
  };
}

export function payrollMass(): WidgetDef {
  return {
    id: 'payrollMass', metric: 'payrollMass', source: () => ({ queryKey: ['dashboard', 'payrollMass'], queryFn: () => payrollService.listPayslips({} as any) }),
    mapData: (d: any) => ({ value: `${Math.round((d.totalNet ?? 0) / 1000)}k $`, label: 'Masse Salariale', sublabel: 'Mois en cours', icon: 'trending-up', color: 'text-emerald-600' }),
    visibleIf: (r) => r === 'admin'
  };
}

export function myLeaves(): WidgetDef {
  return {
    id: 'myLeaves', metric: 'myLeaves', source: () => ({ queryKey: ['dashboard', 'myLeaves'], queryFn: () => leaveRequestsEndpoint.listRequests({} as any) }),
    mapData: (d: any) => ({ value: String(d.count ?? 0), label: 'Mes congés', sublabel: 'Demandes', icon: 'calendar', color: 'text-blue-600' }),
    visibleIf: (r) => r === 'employee'
  };
}

export function myPayslip(): WidgetDef {
  return {
    id: 'myPayslip', metric: 'myPayslip', source: () => ({ queryKey: ['dashboard', 'myPayslip'], queryFn: () => payrollService.listPayslips({} as any) }),
    mapData: (d: any) => ({ value: String(d.count ?? 0), label: 'Mes bulletins', sublabel: 'Disponibles', icon: 'file-text', color: 'text-slate-600' }),
    visibleIf: (r) => r === 'employee'
  };
}
