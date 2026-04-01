// Types Configuration Congés - Code du Travail RDC

export type SpecialLeaveType = 'MARRIAGE' | 'BIRTH' | 'DEATH_SPOUSE_CHILD' | 'DEATH_ANCESTOR' | 'SICK_CHILD';

export interface SpecialLeave {
	type: SpecialLeaveType;
	label: string;
	daysAllowed: number;
	description: string;
	icon?: string;
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
	// Options supplémentaires
	allowHalfDays: boolean;
	requireApproval: boolean;
	maxConsecutiveDays: number;
	noticePeriodDays: number; // Délai de préavis pour demande
}

// Configuration par défaut selon le Code du Travail RDC
export const DEFAULT_LEAVE_CONFIG: LeaveConfig = {
	annualLeaveDays: 18,
	specialLeaves: [
		{
			type: 'MARRIAGE',
			label: 'Mariage',
			daysAllowed: 2,
			description: 'Mariage de l\'employé',
			icon: 'heart'
		},
		{
			type: 'BIRTH',
			label: 'Naissance',
			daysAllowed: 2,
			description: 'Naissance d\'un enfant',
			icon: 'baby'
		},
		{
			type: 'DEATH_SPOUSE_CHILD',
			label: 'Décès conjoint/enfant',
			daysAllowed: 4,
			description: 'Décès du conjoint ou d\'un enfant',
			icon: 'flower-2'
		},
		{
			type: 'DEATH_ANCESTOR',
			label: 'Décès ascendant',
			daysAllowed: 3,
			description: 'Décès d\'un parent ou grand-parent',
			icon: 'flower-2'
		},
		{
			type: 'SICK_CHILD',
			label: 'Enfant malade',
			daysAllowed: 3,
			description: 'Soins à un enfant malade (par an)',
			icon: 'stethoscope'
		}
	],
	seniorityBonus: {
		enabled: true,
		yearsPerBonus: 5,
		bonusDays: 1,
		maxBonus: 6
	},
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
