import type { ReviewStatus } from '../types/types';


export const REVIEW_STATUS_LABELS: Record<ReviewStatus, string> = {
	DRAFT: 'Brouillon',
	SUBMITTED: 'Soumis',
	ACKNOWLEDGED: 'Approuvé'
};


export const REVIEW_STATUS_COLORS: Record<ReviewStatus, { bg: string; text: string; dot: string }> = {
	DRAFT: { bg: 'bg-slate-50', text: 'text-slate-700', dot: 'bg-slate-500' },
	SUBMITTED: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
	ACKNOWLEDGED: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' }
};


export const GOAL_TYPE_LABELS: Record<string, string> = {
	OBJECTIVE: 'Objectif',
	KPI: 'KPI'
};
