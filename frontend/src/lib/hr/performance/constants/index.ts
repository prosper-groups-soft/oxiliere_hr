import type { ReviewStatus, CampaignStatus } from '../types/types';


export const CAMPAIGN_STATUS_LABELS: Record<CampaignStatus, string> = {
	DRAFT: 'Brouillon',
	ACTIVE: 'Active',
	CLOSED: 'Clôturée',
};

export const CAMPAIGN_STATUS_COLORS: Record<CampaignStatus, { bg: string; text: string; dot: string }> = {
	DRAFT: { bg: 'bg-slate-50', text: 'text-slate-700', dot: 'bg-slate-500' },
	ACTIVE: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
	CLOSED: { bg: 'bg-rose-50', text: 'text-rose-700', dot: 'bg-rose-500' },
};

export const CAMPAIGN_TYPE_LABELS: Record<string, string> = {
	ANNUAL: 'Annuelle',
	SEMESTRIAL: 'Semestrielle',
	TRIMESTRIAL: 'Trimestrielle',
	PROBATION: "Période d'essai",
};

export const CAMPAIGN_TYPE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
	ANNUAL: { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-200' },
	SEMESTRIAL: { bg: 'bg-sky-50', text: 'text-sky-600', border: 'border-sky-200' },
	TRIMESTRIAL: { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-200' },
	PROBATION: { bg: 'bg-violet-50', text: 'text-violet-600', border: 'border-violet-200' },
};

export const REVIEW_STATUS_LABELS: Record<ReviewStatus, string> = {
	EMPLOYEE_DRAFT: 'Auto-évaluation',
	MANAGER_DRAFT: 'Évaluation évaluateur',
	SUBMITTED: 'Soumise',
	CALIBRATED: 'Calibrée',
	ACKNOWLEDGED: 'Approuvée',
};

export const REVIEW_STATUS_COLORS: Record<ReviewStatus, { bg: string; text: string; dot: string }> = {
	EMPLOYEE_DRAFT: { bg: 'bg-slate-50', text: 'text-slate-600', dot: 'bg-slate-400' },
	MANAGER_DRAFT: { bg: 'bg-purple-50', text: 'text-purple-700', dot: 'bg-purple-500' },
	SUBMITTED: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
	CALIBRATED: { bg: 'bg-indigo-50', text: 'text-indigo-700', dot: 'bg-indigo-500' },
	ACKNOWLEDGED: { bg: 'bg-slate-100', text: 'text-slate-600', dot: 'bg-slate-400' },
};

export const GOAL_TYPE_LABELS: Record<string, string> = {
	OBJECTIVE: 'Objectif qualitatif',
	KPI: 'KPI',
};

export const SKILL_CATEGORY_LABELS: Record<string, string> = {
	TECHNICAL: 'Technique',
	BEHAVIORAL: 'Comportementale',
	LEADERSHIP: 'Leadership',
};


/**
 * Actions disponibles depuis chaque statut.
 * key = statut actuel, value = tableau des actions possibles
 */
export const REVIEW_STATUS_ACTIONS: Record<ReviewStatus, { action: string; label: string; icon?: string }[]> = {
	EMPLOYEE_DRAFT: [
		{ action: 'submit-employee', label: "Soumettre à l'évaluateur", icon: 'send' },
	],
	MANAGER_DRAFT: [
		{ action: 'submit-manager', label: 'Soumettre la notation', icon: 'check-circle' },
	],
	SUBMITTED: [
		{ action: 'acknowledge', label: 'Valider les résultats', icon: 'eye' },
		{ action: 'dispute', label: 'Contester', icon: 'alert-circle' },
	],
	CALIBRATED: [
		{ action: 'acknowledge', label: 'Valider les résultats', icon: 'eye' },
		{ action: 'dispute', label: 'Contester', icon: 'alert-circle' },
	],
	ACKNOWLEDGED: [],
};

