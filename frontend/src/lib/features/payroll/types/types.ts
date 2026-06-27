export type Currency = 'USD' | 'CDF';

export type PayrollStep = 'preparation' | 'calculation' | 'review' | 'approval' | 'payment';

export type PayrollStatus = 'draft' | 'calculated' | 'reviewed' | 'approved' | 'paid';
export type PayslipStatus = 'draft' | 'calculated' | 'paid';
export type AdvanceStatus = 'pending' | 'approved' | 'rejected' | 'completed';


export interface PayrollRun {
	id: string;
	period: string;
	status: PayrollStatus;
	totalGross: number;
	totalNet: number;
	totalContributions: number;
	totalTaxes: number;
	totalAllocations: number;
	employeeCount: number;
	createdAt: string;
	calculatedAt?: string;
	approvedAt?: string;
	paidAt?: string;
}


export interface PayslipLine {
	label: string;
	amount: number;
	formula?: string;
	type: 'earning' | 'deduction';
}


export interface Payslip {
	id: string;
	employeeId: number;
	employeeName: string;
	orgUnit: string;
	period: string;
	baseSalary: number;
	lines: PayslipLine[];
	grossPay: number;
	netPay: number;
	status: PayslipStatus;
	paidAt?: string;
}


export interface Advance {
	id: string;
	employeeId: number;
	employeeName: string;
	amount: number;
	remainingAmount: number;
	monthlyDeduction: number;
	requestDate: string;
	approvedDate?: string;
	completedDate?: string;
	status: AdvanceStatus;
	reason: string;
	riskLevel: 'low' | 'medium' | 'high';
}


export interface PayrollFilters {
	search: string;
	status: PayrollStatus[];
	orgUnit: string[];
	period: string;
}

export interface ExcludedEmployee {
	employeeName: string;
	reason: string;
	orgUnit: string;
}


export const PAYROLL_STATUS_LABELS: Record<PayrollStatus, string> = {
	draft: 'Brouillon',
	calculated: 'Calculé',
	reviewed: 'Révisé',
	approved: 'Approuvé',
	paid: 'Payé'
};


export const PAYROLL_STATUS_COLORS: Record<PayrollStatus, { bg: string; text: string; dot: string }> = {
	draft: { bg: 'bg-slate-100', text: 'text-slate-700', dot: 'bg-slate-500' },
	calculated: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
	reviewed: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
	approved: { bg: 'bg-emerald-50', text: 'text-emerald-700', dot: 'bg-emerald-500' },
	paid: { bg: 'bg-purple-50', text: 'text-purple-700', dot: 'bg-purple-500' }
};


export const ADVANCE_STATUS_LABELS: Record<AdvanceStatus, string> = {
	pending: 'En attente',
	approved: 'Approuvé',
	rejected: 'Rejeté',
	completed: 'Terminé'
};


export const ADVANCE_STATUS_COLORS: Record<AdvanceStatus, { bg: string; text: string }> = {
	pending: { bg: 'bg-amber-100', text: 'text-amber-700' },
	approved: { bg: 'bg-emerald-100', text: 'text-emerald-700' },
	rejected: { bg: 'bg-rose-100', text: 'text-rose-700' },
	completed: { bg: 'bg-slate-100', text: 'text-slate-700' }
};


export const ADVANCE_RISK_LABELS: Record<Advance['riskLevel'], string> = {
	low: 'Faible',
	medium: 'Moyen',
	high: 'Élevé'
};


export const ORG_UNITS = ['IT', 'RH', 'Finance', 'Commercial', 'Production', 'Administration'];

export const PAYROLL_STEPS: PayrollStep[] = ['preparation', 'calculation', 'review', 'approval', 'payment'];


export const PAYROLL_STEP_LABELS: Record<PayrollStep, string> = {
	preparation: 'Préparation',
	calculation: 'Calcul',
	review: 'Révision',
	approval: 'Approbation',
	payment: 'Paiement'
};


export const PAYROLL_STEP_DESCRIPTIONS: Record<PayrollStep, string> = {
	preparation: 'Sélectionnez la période et les employés à inclure dans cette paie',
	calculation: 'Visualisez les calculs et formules appliquées à chaque employé',
	review: 'Contrôlez et modifiez les fiches de paie avant validation',
	approval: 'Confirmez les montants et approuvez la paie',
	payment: 'Finalisez le paiement et générez les justificatifs'
};

