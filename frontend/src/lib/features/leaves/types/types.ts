export type LeaveType = 'annual' | 'sick' | 'circumstantial' | 'unpaid';
export type LeaveStatus = 'pending' | 'approved' | 'rejected';

export interface LeaveRequest {
	id: string;
	employeeId: number;
	employeeName: string;
	avatarUrl?: string;
	department: string;
	type: LeaveType;
	status: LeaveStatus;
	startDate: string; // ISO date
	endDate: string;   // ISO date
	days: number;
	reason?: string;
	approver?: string;
	createdAt: string; // ISO date
	respondedAt?: string;
}

export interface LeaveBalance {
	employeeId: number;
	type: LeaveType;
	allocated: number;
	taken: number;
	remaining: number;
	expiringDays?: number;
	expiryDate?: string; // ISO date
}

export interface SeniorityRule {
	minYears: number;
	maxYears?: number;
	extraDays: number;
}

export interface LeavePolicy {
	id: string;
	name: string;
	type: LeaveType;
	daysPerYear: number;
	seniorityRules: SeniorityRule[];
	carryOverDays: number;
	requiresApproval: boolean;
	requiresJustification: boolean;
	description?: string;
}

export interface LeavesFilters {
	search: string;
	department: string[];
	type: LeaveType[];
	status: LeaveStatus[];
}

export const LEAVE_TYPE_LABELS: Record<LeaveType, string> = {
	annual: 'Annuel',
	sick: 'Maladie',
	circumstantial: 'Circonstanciel',
	unpaid: 'Sans solde',
};

export const LEAVE_TYPE_COLORS: Record<LeaveType, { bg: string; text: string; dot: string }> = {
	annual: { bg: 'bg-blue-50', text: 'text-blue-700', dot: 'bg-blue-500' },
	sick: { bg: 'bg-rose-50', text: 'text-rose-700', dot: 'bg-rose-500' },
	circumstantial: { bg: 'bg-amber-50', text: 'text-amber-700', dot: 'bg-amber-500' },
	unpaid: { bg: 'bg-slate-50', text: 'text-slate-600', dot: 'bg-slate-400' },
};

export const LEAVE_STATUS_LABELS: Record<LeaveStatus, string> = {
	pending: 'En attente',
	approved: 'Approuvé',
	rejected: 'Refusé',
};

export const LEAVE_STATUS_COLORS: Record<LeaveStatus, { bg: string; text: string }> = {
	pending: { bg: 'bg-amber-50', text: 'text-amber-700' },
	approved: { bg: 'bg-emerald-50', text: 'text-emerald-700' },
	rejected: { bg: 'bg-rose-50', text: 'text-rose-700' },
};

