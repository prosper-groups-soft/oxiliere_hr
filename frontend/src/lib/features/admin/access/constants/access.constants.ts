// Scope labels mapping - raw scope → human-readable label
export const SCOPE_LABELS: Record<string, string> = {
	'access': 'Paramètre',
	'employees': 'Employés',
	'jobs': 'Postes & Organigramme',
	'leaves': 'Congés & Absences',
	'attendance': 'Présences',
	'calendar': 'Calendrier',
	'payroll': 'Paie',
	'banking': 'Banque',
	'recruitment': 'Recrutement',
	'performance': 'Performance',
};

// Groupes système critiques (ne pas supprimer, protégés)
export const SYSTEM_GROUPS = ['manager', 'admins'] as const;

// Rôles système critiques (requis pour le fonctionnement)
export const SYSTEM_ROLES = ['admin', 'employee', 'hr_manager'] as const;

// Types dérivés
export type SystemGroup = typeof SYSTEM_GROUPS[number];
export type SystemRole = typeof SYSTEM_ROLES[number];

// Action hierarchy: when granting an action, also grant its dependencies
// When revoking an action, also revoke actions that depend on it
// Format: action -> set of actions it requires
export const ACTION_HIERARCHY: Record<string, Set<string>> = {
    "r": new Set(),            // read - no dependencies
    "w": new Set(["r"]),       // write requires read
    "u": new Set(["r"]),       // update requires read
    "d": new Set(["r", "w"]),  // delete requires write and read
    "a": new Set(["r"]),       // approve requires read
};

export interface ActionDefinition {
	id: string;
	label: string;
	color: string;
	bgColor: string;
	borderColor: string;
}

export const ACTION_DEFINITIONS: ActionDefinition[] = [
	{ id: 'r', label: 'Lire', color: 'text-blue-700', bgColor: 'bg-blue-50/60', borderColor: 'border-blue-200' },
	{ id: 'w', label: 'Créer', color: 'text-emerald-700', bgColor: 'bg-emerald-50/60', borderColor: 'border-emerald-200' },
	{ id: 'u', label: 'Modifier', color: 'text-amber-700', bgColor: 'bg-amber-50/60', borderColor: 'border-amber-200' },
	{ id: 'd', label: 'Supprimer', color: 'text-rose-700', bgColor: 'bg-rose-50/60', borderColor: 'border-rose-200' },
];

// Helper to get action by id
export function getActionById(id: string): ActionDefinition | undefined {
	return ACTION_DEFINITIONS.find(a => a.id === id);
}

// Helper to get scope label
export function getScopeLabel(scope: string): string {
	return SCOPE_LABELS[scope] || scope;
}

// Actions for PermissionMatrix component (backward compatible)
export const PERMISSION_ACTIONS = ACTION_DEFINITIONS.map(a => ({
	id: a.id,
	label: a.label,
	color: a.color
}));
