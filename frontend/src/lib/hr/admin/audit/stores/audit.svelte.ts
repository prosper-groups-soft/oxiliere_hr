import { employeeStore } from '@/hr/employees/stores/employees.svelte';
import type {
  AuditLog,
  AuditFilters,
  AuditAction,
  AuditModule,
  AuditTabId,
} from '../types/types';

// Mock data generator

const MOCK_ACTIONS: AuditAction[] = ['CREATE', 'UPDATE', 'DELETE', 'LOGIN', 'LOGOUT', 'EXPORT', 'APPROVE', 'REJECT'];
const MOCK_MODULES: AuditModule[] = ['employees', 'attendance', 'leaves', 'payroll', 'recruitment', 'banking', 'jobs'];

const MOCK_TEMPLATES: Array<{ action: AuditAction; module: AuditModule; description: string; entityLabel?: string; diff?: { before: Record<string, unknown>; after: Record<string, unknown> } }> = [
  { action: 'CREATE',  module: 'employees',   description: "Création d'un employé",         entityLabel: 'Nouveau employé',             diff: { before: {}, after: { name: 'Jean Dupont', orgUnit: 'RH', status: 'active' } } },
  { action: 'UPDATE',  module: 'employees',   description: "Modification d'un employé",      entityLabel: 'Jean Dupont',                 diff: { before: { orgUnit: 'RH' }, after: { orgUnit: 'Finance' } } },
  { action: 'DELETE',  module: 'employees',   description: "Suppression d'un employé",       entityLabel: 'Marie Curie'                  },
  { action: 'APPROVE', module: 'leaves',      description: "Approbation d'une demande",      entityLabel: 'Congé annuel — 5 jours',      diff: { before: { status: 'pending' }, after: { status: 'approved' } } },
  { action: 'REJECT',  module: 'leaves',      description: "Rejet d'une demande de congé",   entityLabel: 'Congé maladie — 3 jours',     diff: { before: { status: 'pending' }, after: { status: 'rejected' } } },
  { action: 'CREATE',  module: 'payroll',     description: "Génération d'une fiche de paie", entityLabel: 'Fiche de paie — Mars 2026'    },
  { action: 'EXPORT',  module: 'payroll',     description: "Export des bulletins PDF",        entityLabel: 'Mars 2026 — 24 bulletins'     },
  { action: 'UPDATE',  module: 'recruitment', description: "Mise à jour d'un candidat",      entityLabel: 'Alice Martin',                diff: { before: { stage: 'Applied' }, after: { stage: 'Interview' } } },
  { action: 'CREATE',  module: 'jobs',        description: "Création d'un nouveau poste",    entityLabel: 'Développeur Fullstack'        },
  { action: 'LOGIN',   module: 'auth',        description: "Connexion au système",            entityLabel: undefined                      },
  { action: 'LOGOUT',  module: 'auth',        description: "Déconnexion du système",          entityLabel: undefined                      },
  { action: 'UPDATE',  module: 'banking',     description: "Modification d'un compte bancaire", entityLabel: 'Compte CIC — Jean Dupont',  diff: { before: { iban: 'FR76...0001' }, after: { iban: 'FR76...0042' } } },
  { action: 'EXPORT',  module: 'attendance',  description: "Export du registre de présences", entityLabel: 'Semaine 13 — 2026'            },
  { action: 'UPDATE',  module: 'settings',    description: "Modification des paramètres",     entityLabel: 'Paramètres de l\'entreprise', diff: { before: { timezone: 'UTC' }, after: { timezone: 'Europe/Paris' } } },
];


function generateMockLogs(): AuditLog[] {
  const logs: AuditLog[] = [];
  const employees = employeeStore.employees.slice(0, 5);
  if (employees.length === 0) {
    // Fallback if employees not loaded yet
    const fallbackUsers = [
      { id: 1, name: 'Admin Système', avatarUrl: undefined },
      { id: 2, name: 'Sophie Bernard', avatarUrl: undefined },
      { id: 3, name: 'Marc Dupuis', avatarUrl: undefined },
    ];
    for (const user of fallbackUsers) {
      for (let i = 0; i < 5; i++) {
        const template = MOCK_TEMPLATES[(user.id * i + i) % MOCK_TEMPLATES.length];
        const date = new Date();
        date.setDate(date.getDate() - Math.floor(i / 2));
        date.setHours(Math.floor(8 + Math.random() * 10), Math.floor(Math.random() * 60));
        logs.push({
          id: `log-${user.id}-${i}`,
          timestamp: date.toISOString(),
          userId: user.id,
          userName: user.name,
          action: template.action,
          module: template.module,
          description: template.description,
          entityLabel: template.entityLabel,
          diff: template.diff,
          ipAddress: `192.168.1.${10 + user.id}`,
        });
      }
    }
    return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
  }

  let logId = 0;
  employees.forEach((emp, empIndex) => {
    const count = 8 + empIndex * 2;
    for (let i = 0; i < count; i++) {
      const template = MOCK_TEMPLATES[(empIndex + i) % MOCK_TEMPLATES.length];
      const date = new Date();
      date.setDate(date.getDate() - Math.floor(i * 0.8));
      date.setHours(Math.floor(8 + (logId % 10)), Math.floor((logId * 7) % 60));
      logs.push({
        id: `log-${logId++}`,
        timestamp: date.toISOString(),
        userId: emp.id,
        userName: emp.name,
        avatarUrl: emp.avatarUrl,
        action: template.action,
        module: template.module,
        description: template.description,
        entityLabel: template.entityLabel,
        diff: template.diff,
        ipAddress: `192.168.1.${10 + emp.id}`,
      });
    }
  });

  return logs.sort((a, b) => new Date(b.timestamp).getTime() - new Date(a.timestamp).getTime());
}


// Store

export class AuditStore {
  logs = $state<AuditLog[]>([]);

  filters = $state<AuditFilters>({
    search: '',
    modules: [],
    actions: [],
    dateRange: {
      from: '',
      to: '',
    },
  });

  activeTab = $state<AuditTabId>('logs');

  // Pagination
  currentPage = $state(1);
  perPage = $state(25);

  // Selected log for detail sheet
  selectedLog = $state<AuditLog | null>(null);

  constructor() {
    this.logs = generateMockLogs();
  }

  // Derived

  filteredLogs = $derived.by(() => {
    return this.logs.filter(log => {
      const q = this.filters.search.toLowerCase();
      const matchesSearch =
        !q ||
        log.userName.toLowerCase().includes(q) ||
        log.description.toLowerCase().includes(q) ||
        (log.entityLabel ?? '').toLowerCase().includes(q);

      const matchesModule =
        this.filters.modules.length === 0 || this.filters.modules.includes(log.module);

      const matchesAction =
        this.filters.actions.length === 0 || this.filters.actions.includes(log.action);

      const logDate = log.timestamp.split('T')[0];
      const matchesFrom = !this.filters.dateRange.from || logDate >= this.filters.dateRange.from;
      const matchesTo   = !this.filters.dateRange.to   || logDate <= this.filters.dateRange.to;

      return matchesSearch && matchesModule && matchesAction && matchesFrom && matchesTo;
    });
  });

  paginatedLogs = $derived.by(() => {
    const start = (this.currentPage - 1) * this.perPage;
    return this.filteredLogs.slice(start, start + this.perPage);
  });

  totalCount = $derived(this.filteredLogs.length);
  totalPages = $derived(Math.max(1, Math.ceil(this.filteredLogs.length / this.perPage)));

  activeFiltersCount = $derived(
    (this.filters.modules.length) +
    (this.filters.actions.length) +
    (this.filters.dateRange.from ? 1 : 0) +
    (this.filters.dateRange.to ? 1 : 0)
  );

  stats = $derived.by(() => {
    const all = this.filteredLogs;
    return {
      total: all.length,
      creates: all.filter(l => l.action === 'CREATE').length,
      updates: all.filter(l => l.action === 'UPDATE').length,
      deletes: all.filter(l => l.action === 'DELETE').length,
    };
  });

  uniqueUsers = $derived.by(() => {
    const seen = new Set<number>();
    return this.logs.filter(l => {
      if (seen.has(l.userId)) return false;
      seen.add(l.userId);
      return true;
    }).map(l => ({ id: l.userId, name: l.userName, avatarUrl: l.avatarUrl }));
  });

  // Actions

  setSearch(query: string) {
    this.filters.search = query;
    this.currentPage = 1;
  }

  toggleFilter(category: 'modules' | 'actions', value: AuditModule | AuditAction) {
    const current = this.filters[category] as string[];
    if (current.includes(value)) {
      (this.filters[category] as string[]) = current.filter(v => v !== value);
    } else {
      (this.filters[category] as string[]) = [...current, value];
    }
    this.currentPage = 1;
  }

  setDateRange(from: string, to: string) {
    this.filters.dateRange = { from, to };
    this.currentPage = 1;
  }

  resetFilters() {
    this.filters.search = '';
    this.filters.modules = [];
    this.filters.actions = [];
    this.filters.dateRange = { from: '', to: '' };
    this.currentPage = 1;
  }

  setPage(page: number) {
    this.currentPage = page;
  }

  setPerPage(n: number) {
    this.perPage = n;
    this.currentPage = 1;
  }

  nextPage() {
    if (this.currentPage < this.totalPages) this.currentPage++;
  }

  prevPage() {
    if (this.currentPage > 1) this.currentPage--;
  }

  selectLog(log: AuditLog | null) {
    this.selectedLog = log;
  }

  exportLogs() {
    const rows = this.filteredLogs.map(l => [
      new Date(l.timestamp).toLocaleString('fr-FR'),
      l.userName,
      l.action,
      l.module,
      l.description,
      l.entityLabel ?? '',
      l.ipAddress ?? '',
    ]);

    const header = ['Horodatage', 'Utilisateur', 'Action', 'Module', 'Description', 'Entité', 'IP'];
    const csv = [header, ...rows].map(r => r.map(cell => `"${String(cell).replace(/"/g, '""')}"`).join(',')).join('\n');

    const blob = new Blob(['\uFEFF' + csv], { type: 'text/csv;charset=utf-8;' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `audit-logs-${new Date().toISOString().split('T')[0]}.csv`;
    a.click();
    URL.revokeObjectURL(url);
  }
}


export const auditStore = new AuditStore();

