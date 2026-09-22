import type { LeaveType, LeaveStatus, CircumstanceType } from "../types/types";


// Labels

export const LEAVE_TYPE_LABELS: Record<LeaveType, string> = {
	annual: 'Annuel',
	sick: 'Maladie',
	circumstantial: 'Circonstanciel',
	unpaid: 'Sans solde',
};

export const LEAVE_STATUS_LABELS: Record<LeaveStatus, string> = {
	pending: 'En attente',
	approved: 'Approuvé',
	rejected: 'Refusé',
};

/**
 * Labels des sous-types de congés circonstanciels (Code du Travail RDC).
 */
export const CIRCUMSTANCE_TYPE_LABELS: Record<CircumstanceType, string> = {
	MARRIAGE: 'Mariage de l\'employé',
	BIRTH: 'Naissance d\'un enfant',
	DEATH_SPOUSE_CHILD: 'Décès conjoint/enfant (1er degrée)',
	DEATH_ANCESTOR: 'Décès ascendant (parent) (2ème degrée)',
	CHILD_MARRIAGE: 'Mariage d\'un enfant',
	MOVING: 'Déménagement',
	CHILD_HOSPITALIZATION: 'Hospitalisation d\'un enfant',
	OTHER: 'Autre circonstance légale',
};

/**
 * Icônes Lucide pour chaque sous-type de congé circonstanciel.
 */
export const CIRCUMSTANCE_TYPE_ICONS: Record<CircumstanceType, string> = {
	MARRIAGE: 'heart',
	BIRTH: 'baby',
	DEATH_SPOUSE_CHILD: 'flower-2',
	DEATH_ANCESTOR: 'flower-2',
	CHILD_MARRIAGE: 'heart',
	MOVING: 'moving',
	CHILD_HOSPITALIZATION: 'stethoscope',
	OTHER: 'file-plus',
};


// Couleurs

export const LEAVE_TYPE_COLORS: Record<LeaveType, { bg: string; text: string; dot: string }> = {
	annual: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
	sick: { bg: 'bg-rose-50', text: 'text-rose-700', dot: 'bg-rose-500' },
	circumstantial: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
	unpaid: { bg: 'bg-slate-50', text: 'text-slate-600', dot: 'bg-slate-400' },
};

export const LEAVE_STATUS_COLORS: Record<LeaveStatus, { bg: string; text: string }> = {
	pending: { bg: 'bg-amber-50', text: 'text-amber-700' },
	approved: { bg: 'bg-emerald-50', text: 'text-emerald-700' },
	rejected: { bg: 'bg-rose-50', text: 'text-rose-700' },
};


// Mapping backend (valeurs envoyées par/au backend Django)
// Les catégories backend sont en majuscules, les statuts aussi

export const BACKEND_LEAVE_CATEGORIES: Record<LeaveType, string> = {
	annual: 'ANNUAL',
	sick: 'SICK',
	circumstantial: 'CIRCUMSTANCE',
	unpaid: 'UNPAID',
};

export const FRONTEND_LEAVE_CATEGORIES: Record<string, LeaveType> = {
	ANNUAL: 'annual',
	SICK: 'sick',
	CIRCUMSTANCE: 'circumstantial',
	UNPAID: 'unpaid',
};

export const FRONTEND_LEAVE_STATUSES: Record<string, LeaveStatus> = {
	PENDING: 'pending',
	APPROVED: 'approved',
	REJECTED: 'rejected',
	CANCELLED: 'pending',
	TAKEN: 'approved',
};

/** Mapping frontend → backend pour CircumstanceType */
export const BACKEND_CIRCUMSTANCE_TYPES: Record<CircumstanceType, string> = {
	MARRIAGE: 'MARRIAGE_EMPLOYEE',
	BIRTH: 'BIRTH_SPOUSE',
	DEATH_SPOUSE_CHILD: 'DEATH_FIRST_DEGREE',
	DEATH_ANCESTOR: 'DEATH_SECOND_DEGREE',
	CHILD_MARRIAGE: 'CHILD_MARRIAGE',
	MOVING: 'MOVING',
	CHILD_HOSPITALIZATION: 'CHILD_HOSPITALIZATION',
	OTHER: 'OTHER',
};

/** Mapping backend → frontend pour CircumstanceType */
export const FRONTEND_CIRCUMSTANCE_TYPES: Record<string, CircumstanceType> = {
	MARRIAGE_EMPLOYEE: 'MARRIAGE',
	BIRTH_SPOUSE: 'BIRTH',
	DEATH_FIRST_DEGREE: 'DEATH_SPOUSE_CHILD',
	DEATH_SECOND_DEGREE: 'DEATH_ANCESTOR',
	CHILD_MARRIAGE: 'CHILD_MARRIAGE',
	MOVING: 'MOVING',
	CHILD_HOSPITALIZATION: 'CHILD_HOSPITALIZATION',
	OTHER: 'OTHER',
};


// Options pour dropdowns

export const LEAVE_TYPE_OPTIONS: { value: LeaveType; label: string }[] =
  (Object.entries(LEAVE_TYPE_LABELS) as [LeaveType, string][]).map(
    ([value, label]) => ({ value, label })
  );

export const LEAVE_STATUS_OPTIONS: { value: LeaveStatus; label: string }[] =
  (Object.entries(LEAVE_STATUS_LABELS) as [LeaveStatus, string][]).map(
    ([value, label]) => ({ value, label })
  );

/** Options pour le sélecteur de sous-type circonstanciel */
export const CIRCUMSTANCE_TYPE_OPTIONS: { value: CircumstanceType; label: string }[] =
	(Object.entries(CIRCUMSTANCE_TYPE_LABELS) as [CircumstanceType, string][]).map(
		([value, label]) => ({ value, label })
	);

/** Légende pour le TeamPlanner (types de congés affichés) */
export const LEAVE_TYPE_LEGEND: { type: LeaveType; label: string }[] =
  (Object.entries(LEAVE_TYPE_LABELS) as [LeaveType, string][]).map(
    ([type, label]) => ({ type, label })
  );

