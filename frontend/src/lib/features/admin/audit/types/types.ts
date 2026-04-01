export type AuditAction =
  | 'CREATE'
  | 'UPDATE'
  | 'DELETE'
  | 'LOGIN'
  | 'LOGOUT'
  | 'EXPORT'
  | 'APPROVE'
  | 'REJECT';


export type AuditModule =
  | 'employees'
  | 'attendance'
  | 'leaves'
  | 'payroll'
  | 'recruitment'
  | 'banking'
  | 'jobs'
  | 'calendar'
  | 'settings'
  | 'auth';


export interface AuditDiff {
  before: Record<string, unknown>;
  after: Record<string, unknown>;
}


export interface AuditLog {
  id: string;
  timestamp: string;     // ISO datetime
  userId: number;
  userName: string;
  avatarUrl?: string;
  action: AuditAction;
  module: AuditModule;
  entityId?: string;
  entityLabel?: string;  // e.g. "Jean Dupont", "Fiche de paie #42"
  description: string;   // Human-readable sentence
  diff?: AuditDiff;
  ipAddress?: string;
}


export interface AuditFilters {
  search: string;
  modules: AuditModule[];
  actions: AuditAction[];
  dateRange: {
    from: string; // ISO date
    to: string;   // ISO date
  };
}

export type AuditTabId = 'logs';

// Labels 

export const ACTION_LABELS: Record<AuditAction, string> = {
  CREATE:  'Création',
  UPDATE:  'Modification',
  DELETE:  'Suppression',
  LOGIN:   'Connexion',
  LOGOUT:  'Déconnexion',
  EXPORT:  'Export',
  APPROVE: 'Approbation',
  REJECT:  'Rejet',
};


export const MODULE_LABELS: Record<AuditModule, string> = {
  employees:   'Employés',
  attendance:  'Présences',
  leaves:      'Congés',
  payroll:     'Paie',
  recruitment: 'Recrutement',
  banking:     'Banque',
  jobs:        'Postes',
  calendar:    'Calendrier',
  settings:    'Paramètres',
  auth:        'Authentification',
};


// Colors 

export const ACTION_COLORS: Record<AuditAction, { bg: string; text: string; dot: string }> = {
  CREATE:  { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
  UPDATE:  { bg: 'bg-blue-50',    text: 'text-blue-700',    dot: 'bg-blue-500'    },
  DELETE:  { bg: 'bg-rose-50',    text: 'text-rose-700',    dot: 'bg-rose-500'    },
  LOGIN:   { bg: 'bg-slate-100',  text: 'text-slate-600',   dot: 'bg-slate-400'   },
  LOGOUT:  { bg: 'bg-slate-100',  text: 'text-slate-600',   dot: 'bg-slate-400'   },
  EXPORT:  { bg: 'bg-violet-50',  text: 'text-violet-700',  dot: 'bg-violet-500'  },
  APPROVE: { bg: 'bg-green-50',   text: 'text-green-700',   dot: 'bg-green-500'   },
  REJECT:  { bg: 'bg-amber-50',   text: 'text-amber-700',   dot: 'bg-amber-500'   },
};


export const MODULE_COLORS: Record<AuditModule, { bg: string; text: string }> = {
  employees:   { bg: 'bg-sky-50',      text: 'text-sky-700'      },
  attendance:  { bg: 'bg-teal-50',     text: 'text-teal-700'     },
  leaves:      { bg: 'bg-indigo-50',   text: 'text-indigo-700'   },
  payroll:     { bg: 'bg-orange-50',   text: 'text-orange-700'   },
  recruitment: { bg: 'bg-purple-50',   text: 'text-purple-700'   },
  banking:     { bg: 'bg-emerald-50',  text: 'text-emerald-700'  },
  jobs:        { bg: 'bg-cyan-50',     text: 'text-cyan-700'     },
  calendar:    { bg: 'bg-pink-50',     text: 'text-pink-700'     },
  settings:    { bg: 'bg-slate-100',   text: 'text-slate-600'    },
  auth:        { bg: 'bg-yellow-50',   text: 'text-yellow-700'   },
};

