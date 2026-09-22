import type { VacancyPriority, VacancyStatus } from '../types/types';


export const VACANCY_PRIORITY_OPTIONS: Array<{
	value: VacancyPriority;
	label: string;
	icon: string;
	color: string;
	badgeClass: string;
}> = [
	{
		value: 'HIGH',
		label: 'Urgente',
		icon: 'triangle-alert',
		color: 'text-red-500',
		badgeClass: 'bg-red-50 text-red-600 border-red-100'
	},
	{
		value: 'MEDIUM',
		label: 'Normale',
		icon: 'info',
		color: 'text-amber-500',
		badgeClass: 'bg-amber-50 text-amber-600 border-amber-100'
	},
	{
		value: 'LOW',
		label: 'Faible',
		icon: 'circle-check',
		color: 'text-green-500',
		badgeClass: 'bg-emerald-50 text-emerald-600 border-emerald-100'
	}
];


export const VACANCY_STATUS_OPTIONS: Array<{
	value: VacancyStatus;
	label: string;
	icon: string;
	color: string;
	badgeClass: string;
}> = [
	{
		value: 'OPEN',
		label: 'Ouverte',
		icon: 'pin',
		color: 'text-blue-500',
		badgeClass: 'bg-blue-50 text-blue-600 border-blue-100'
	},
	{
		value: 'IN_PROGRESS',
		label: 'En cours',
		icon: 'rotate-cw',
		color: 'text-amber-600',
		badgeClass: 'bg-amber-50 text-amber-600 border-amber-100'
	},
	{
		value: 'RECRUITMENT',
		label: 'Réc. Externe',
		icon: 'users',
		color: 'text-purple-600',
		badgeClass: 'bg-purple-50 text-purple-600 border-purple-100'
	},
	{
		value: 'CANCELLED',
		label: 'Annulée',
		icon: 'circle-x',
		color: 'text-slate-500',
		badgeClass: 'bg-slate-50 text-slate-500 border-slate-100'
	},
	{
		value: 'FILLED',
		label: 'Pourvue',
		icon: 'check',
		color: 'text-green-600',
		badgeClass: 'bg-emerald-50 text-emerald-600 border-emerald-100'
	}
];


export const PRIORITY_CONFIG: Record<VacancyPriority, { label: string; icon: string; color: string; badgeClass: string }> = {
	'HIGH': { label: 'Urgente', icon: 'triangle-alert', color: 'text-red-500', badgeClass: 'bg-red-50 text-red-600 border-red-100' },
	'MEDIUM': { label: 'Normale', icon: 'info', color: 'text-amber-500', badgeClass: 'bg-amber-50 text-amber-600 border-amber-100' },
	'LOW': { label: 'Faible', icon: 'circle-check', color: 'text-green-500', badgeClass: 'bg-emerald-50 text-emerald-600 border-emerald-100' }
};


export const STATUS_CONFIG: Record<VacancyStatus, { label: string; icon: string; color: string; badgeClass: string }> = {
	'OPEN': { label: 'Ouverte', icon: 'pin', color: 'text-blue-500', badgeClass: 'bg-blue-50 text-blue-600 border-blue-100' },
	'IN_PROGRESS': { label: 'En cours', icon: 'rotate-cw', color: 'text-amber-600', badgeClass: 'bg-amber-50 text-amber-600 border-amber-100' },
	'RECRUITMENT': { label: 'Réc. Externe', icon: 'users', color: 'text-purple-600', badgeClass: 'bg-purple-50 text-purple-600 border-purple-100' },
	'CANCELLED': { label: 'Annulée', icon: 'circle-x', color: 'text-slate-500', badgeClass: 'bg-slate-50 text-slate-500 border-slate-100' },
	'FILLED': { label: 'Pourvue', icon: 'check', color: 'text-green-600', badgeClass: 'bg-emerald-50 text-emerald-600 border-emerald-100' }
};


/**
 * Helper function to get priority config (similar to getTransitionConfig pattern)
 */
export function getPriorityConfig(priority: VacancyPriority) {
	return PRIORITY_CONFIG[priority] ?? PRIORITY_CONFIG.MEDIUM;
}


/**
 * Helper function to get status config (similar to getTransitionConfig pattern)
 */
export function getStatusConfig(status: VacancyStatus) {
	return STATUS_CONFIG[status] ?? STATUS_CONFIG.OPEN;
}
