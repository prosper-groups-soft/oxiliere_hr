// Types Configuration Congés - Code du Travail RDC

export type SpecialLeaveType = 'MARRIAGE' | 'BIRTH' | 'DEATH_SPOUSE_CHILD' | 'DEATH_ANCESTOR' | 'CHILD_MARRIAGE' | 'MOVING' | 'CHILD_HOSPITALIZATION' | 'OTHER';

export interface SpecialLeave {
	type: SpecialLeaveType;
	label: string;
	daysAllowed: number;
	description: string; // From backend (editable) or fallback to local labels
	icon?: string;
	isPaid?: boolean; // Default: true (congé payé)
}

export interface SeniorityBonus {
	enabled: boolean;
	yearsPerBonus: number; // Par défaut: 5 ans
	bonusDays: number; // Par défaut: 1 jour
	maxBonus?: number; // Maximum de jours bonus
}

export interface LeaveConfig {
	annualLeaveDays: number; // 18 ou 24 jours selon Code Travail RDC
	specialLeaves: SpecialLeave[];
	seniorityBonus: SeniorityBonus;
	// Carry over settings
	allowsCarryOver: boolean;
	maxCarryOverDays: number;
	carryOverExpirationMonth: number; // Month (1-12) when carried-over days expire
	// Options supplémentaires
	allowHalfDays: boolean;
	requireApproval: boolean;
	maxConsecutiveDays: number;
	noticePeriodDays: number; // Délai de préavis pour demande
}

// Configuration par défaut minimale - les vraies valeurs viennent du backend
// C'est juste pour éviter les erreurs avant le chargement initial
export const DEFAULT_LEAVE_CONFIG: LeaveConfig = {
	annualLeaveDays: 18,
	specialLeaves: [], // Vide - sera rempli depuis le backend
	seniorityBonus: {
		enabled: true,
		yearsPerBonus: 5,
		bonusDays: 1,
		maxBonus: 6
	},
	allowsCarryOver: false,
	maxCarryOverDays: 10,
	carryOverExpirationMonth: 3, // March
	allowHalfDays: true,
	requireApproval: true,
	maxConsecutiveDays: 30,
	noticePeriodDays: 15
};

export interface LeaveBalance {
	employeeId: string;
	year: number;
	totalDays: number;
	usedDays: number;
	remainingDays: number;
	seniorityBonusDays: number;
	specialLeavesUsed: Record<SpecialLeaveType, number>;
}
