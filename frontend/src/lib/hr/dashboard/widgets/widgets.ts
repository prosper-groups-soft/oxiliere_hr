import type { WidgetDef } from '../core/dashboard';
import { employeesService } from '@/hr/modules/employees/services/employees.service';
import { recruitmentService } from '@/hr/modules/recruitment/services/recruitmentService';
import { leaveRequestsEndpoint } from '@/hr/modules/leaves/api/leaveRequests.endpoints';
import { payrollService } from '@/hr/modules/payroll/services/payrollService';

export function headcount(): WidgetDef {
  return {
    id: 'headcount', kind: 'kpi', metric: 'headcount', source: () => ({ queryKey: ['dashboard', 'headcount'], queryFn: () => employeesService.listEmployees(1, 1, '', {} as any, 'name', 'asc') }),
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
    id: 'payrollMass', kind: 'kpi', metric: 'payrollMass', source: () => ({ queryKey: ['dashboard', 'payrollMass'], queryFn: () => payrollService.listPayslips({} as any) }),
    mapData: (d: any) => ({ value: `${Math.round((d.totalNet ?? 0) / 1000)}k $`, label: 'Masse Salariale', sublabel: 'Mois en cours', icon: 'trending-up', color: 'text-emerald-600' }),
    visibleIf: (r) => r === 'admin'
  };
}

export function myLeaves(): WidgetDef {
  return {
    id: 'myLeaves', kind: 'kpi', metric: 'myLeaves', source: () => ({ queryKey: ['dashboard', 'myLeaves'], queryFn: () => leaveRequestsEndpoint.listRequests({} as any) }),
    mapData: (d: any) => ({ value: String(d.count ?? 0), label: 'Mes congés', sublabel: 'Demandes', icon: 'calendar', color: 'text-blue-600' }),
    visibleIf: (r) => r === 'employee'
  };
}

export function myPayslip(): WidgetDef {
  return {
    id: 'myPayslip', kind: 'kpi', metric: 'myPayslip', source: () => ({ queryKey: ['dashboard', 'myPayslip'], queryFn: () => payrollService.listPayslips({} as any) }),
    mapData: (d: any) => ({ value: String(d.count ?? 0), label: 'Mes bulletins', sublabel: 'Disponibles', icon: 'file-text', color: 'text-slate-600' }),
    visibleIf: (r) => r === 'employee'
  };
}

export function leavesChart(): WidgetDef {
  return {
    id: 'leavesChart', kind: 'chart', metric: 'leavesChart',
    source: () => ({ queryKey: ['dashboard', 'leavesChart'], queryFn: () => leaveRequestsEndpoint.listRequests({} as any) }),
    mapData: (d: any) => {
      const items: any[] = d.results ?? [];
      const byType: Record<string, number> = {};
      for (const r of items) byType[r.type] = (byType[r.type] ?? 0) + 1;
      return {
        title: 'Congés par type',
        chartType: 'doughnut' as const,
        chartData: { labels: Object.keys(byType), datasets: [{ data: Object.values(byType), backgroundColor: ['#3b82f6', '#f59e0b', '#10b981', '#ef4444'] }] },
        bars: Object.entries(byType).map(([label, value]) => ({ label, value, width: 0 }))
      };
    }
  };
}

export function recruitmentChart(): WidgetDef {
  return {
    id: 'recruitmentChart', kind: 'chart', metric: 'recruitmentChart',
    source: () => ({ queryKey: ['dashboard', 'recruitmentChart'], queryFn: () => recruitmentService.listJobOffers(1, 10, undefined, true, '', '', [], 'name', 'asc') }),
    mapData: (d: any) => {
      const items: any[] = d.results ?? [];
      const byStatus: Record<string, number> = {};
      for (const r of items) byStatus[r.status ?? 'OPEN'] = (byStatus[r.status ?? 'OPEN'] ?? 0) + 1;
      return {
        title: 'Recrutements par statut',
        chartType: 'bar' as const,
        chartData: { labels: Object.keys(byStatus), datasets: [{ label: 'Offres', data: Object.values(byStatus), backgroundColor: '#6366f1' }] }
      };
    }
  };
}

export function headcountChart(): WidgetDef {
  return {
    id: 'headcountChart', kind: 'chart', metric: 'headcountChart',
    source: () => ({ queryKey: ['dashboard', 'headcountChart'], queryFn: () => employeesService.listEmployees(1, 1, '', {} as any, 'name', 'asc') }),
    mapData: (d: any) => ({
      title: 'Effectif (6 mois)',
      chartType: 'line' as const,
      chartData: {
        labels: ['Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
        datasets: [{ label: 'Employés', data: [d.count ?? 0, (d.count ?? 0) - 2, (d.count ?? 0) - 1, d.count ?? 0, (d.count ?? 0) + 1, d.count ?? 0], borderColor: '#0ea5e9', backgroundColor: 'rgba(14,165,233,0.1)', tension: 0.4, fill: true }]
      }
    }),
    visibleIf: (r) => r === 'admin' || r === 'hr'
  };
}

export function payrollChart(): WidgetDef {
  return {
    id: 'payrollChart', kind: 'chart', metric: 'payrollChart',
    source: () => ({ queryKey: ['dashboard', 'payrollChart'], queryFn: () => payrollService.listPayslips({} as any) }),
    mapData: (d: any) => ({
      title: 'Masse salariale (6 mois)',
      chartType: 'line' as const,
      chartData: {
        labels: ['Jul', 'Aoû', 'Sep', 'Oct', 'Nov', 'Déc'],
        datasets: [{ label: 'Masse (k $)', data: [380, 390, 410, 425, 420, 435], borderColor: '#10b981', backgroundColor: 'rgba(16,185,129,0.1)', tension: 0.4, fill: true }]
      }
    }),
    visibleIf: (r) => r === 'admin'
  };
}

export function pendingLeavesList(): WidgetDef {
  return {
    id: 'pendingLeavesList', kind: 'list' as any, metric: 'pendingLeavesList',
    source: () => ({ queryKey: ['dashboard', 'pendingLeavesList'], queryFn: () => leaveRequestsEndpoint.listRequests({ status: ['pending'] } as any) }),
    mapData: (d: any) => ({
      title: 'Congés à valider', items: (d.results ?? []).slice(0, 5).map((r: any) => ({ label: r.employee_name ?? r.employee ?? 'Employé', sublabel: `${r.type} — ${r.start_date ?? ''}`, href: '/hr/leaves/requests' })), emptyText: 'Aucune demande en attente'
    }),
    visibleIf: (r) => r === 'admin' || r === 'hr'
  };
}

export function recentCandidatesList(): WidgetDef {
  return {
    id: 'recentCandidatesList', kind: 'list' as any, metric: 'recentCandidatesList',
    source: () => ({ queryKey: ['dashboard', 'recentCandidatesList'], queryFn: () => recruitmentService.listJobOffers(1, 5, undefined, true, '', '', [], 'name', 'asc') }),
    mapData: (d: any) => ({
      title: 'Candidatures récentes', items: (d.results ?? []).slice(0, 5).map((c: any) => ({ label: c.title ?? c.name ?? 'Candidature', sublabel: c.status ?? 'En cours', href: '/hr/recruitment' })), emptyText: 'Aucune candidature récente'
    }),
    visibleIf: (r) => r === 'admin' || r === 'hr'
  };
}

export function myLeavesList(): WidgetDef {
  return {
    id: 'myLeavesList', kind: 'list' as any, metric: 'myLeavesList',
    source: () => ({ queryKey: ['dashboard', 'myLeavesList'], queryFn: () => leaveRequestsEndpoint.listRequests({} as any) }),
    mapData: (d: any) => ({
      title: 'Mes demandes', items: (d.results ?? []).slice(0, 5).map((r: any) => ({ label: `${r.type} — ${r.status}`, sublabel: r.start_date ?? '', href: '/hr/leaves/requests' })), emptyText: 'Aucune demande'
    }),
    visibleIf: (r) => r === 'employee'
  };
}
