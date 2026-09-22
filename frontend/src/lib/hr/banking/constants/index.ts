import type { VerificationStatus, Currency, AccountType } from '../types/types';


export const VERIFICATION_STATUS_LABELS: Record<VerificationStatus, string> = {
	verified: 'Vérifié',
	pending: 'En attente',
	rejected: 'Rejeté',
	blocked: 'Bloqué'
};


export const VERIFICATION_STATUS_COLORS: Record<VerificationStatus, { bg: string; text: string; dot: string }> = {
	verified: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
	pending: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
	rejected: { bg: 'bg-rose-50', text: 'text-rose-700', dot: 'bg-rose-500' },
	blocked: { bg: 'bg-slate-100', text: 'text-slate-700', dot: 'bg-slate-500' }
};


export const CURRENCY_COLORS: Record<Currency, string> = {
	USD: 'bg-blue-50 border-blue-100 text-blue-700',
	CDF: 'bg-emerald-50 border-emerald-100 text-emerald-700',
	EUR: 'bg-amber-50 border-amber-100 text-amber-700',
};


export const ACCOUNT_TYPE_LABELS: Record<AccountType, string> = {
	checking: 'Courant',
	savings: 'Épargne',
	salary: 'Salaire',
	mobile_money: 'Mobile Money',
};

