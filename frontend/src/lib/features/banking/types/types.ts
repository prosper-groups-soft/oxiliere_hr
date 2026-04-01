export type VerificationStatus = 'verified' | 'pending' | 'rejected' | 'blocked';
export type AccountType = 'savings' | 'checking' | 'mobile_money';
export type Currency = 'USD' | 'CDF' | 'EUR';

export interface BankInstitution {
	id: string;
	name: string;
	shortName: string;
	country: string;
	logoUrl?: string;
	type: 'bank' | 'mobile_money';
	swiftCode?: string;
}

export interface BankAccount {
	id: string;
	employeeId: number;
	employeeName: string;
	institutionId: string;
	accountName: string;
	accountNumber: string;
	iban?: string;
	swift?: string;
	currency: Currency;
	type: AccountType;
	isPrimary: boolean;
	status: VerificationStatus;
	verifiedAt?: string;
	createdAt: string;
}

export interface BankingFilters {
	search: string;
	status: VerificationStatus[];
	currency: Currency[];
	institutionId: string[];
}

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
	USD: 'text-blue-600',
	CDF: 'text-emerald-600',
	EUR: 'text-amber-600'
};
