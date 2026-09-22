// Schemas Zod pour la validation des données de configuration des congés
import { z } from 'zod';


// Schema pour la politique de congés (LeavePolicy)
export const LeavePolicySchema = z.object({
	id: z.uuid().optional(),
	name: z.string().min(1, 'Le nom est requis'),
	country_code: z.string().length(2, 'Code pays sur 2 caractères'),
	standard_annual_days: z.number().int().min(12).max(40),
	allows_carry_over: z.boolean().default(false),
	max_carry_over_days: z.number().int().min(0).default(0),
	carry_over_expiration_month: z.number().int().min(1).max(12).default(3),
	max_consecutive_days: z.number().int().min(0).max(60).default(30),
	notice_period_days: z.number().int().min(0).max(90).default(15),
});


export type LeavePolicy = z.infer<typeof LeavePolicySchema>;


// Schema pour les règles de congés de circonstances (CircumstanceLeaveRule)
// Note: Les valeurs sont en UPPERCASE pour correspondre à l'enum Django
export const CircumstanceLeaveRuleSchema = z.object({
	id: z.uuid().optional(),
	policy_id: z.uuid().optional(),
	type: z.enum([
		'MARRIAGE_EMPLOYEE',
		'BIRTH_SPOUSE',
		'DEATH_FIRST_DEGREE',
		'DEATH_SECOND_DEGREE',
		'CHILD_MARRIAGE',
		'MOVING',
		'CHILD_HOSPITALIZATION',
		'OTHER'
	]),
	duration_days: z.number().int().min(0).max(30),
	is_paid: z.boolean().default(true),
	description: z.string().optional(),
});


export type CircumstanceLeaveRule = z.infer<typeof CircumstanceLeaveRuleSchema>;


// Schema pour les règles d'ancienneté (SeniorityRule)
export const SeniorityRuleSchema = z.object({
	id: z.uuid().optional(),
	policy_id: z.uuid().optional(),
	years_of_service: z.number().int().min(1),
	bonus_days: z.number().int().min(1),
});


export type SeniorityRule = z.infer<typeof SeniorityRuleSchema>;


// Mapping entre les types backend et les labels frontend
export const CircumstanceTypeLabels: Record<string, { label: string; description: string; icon: string }> = {
	marriage_employee: { label: 'Mariage', description: 'Mariage de l\'employé', icon: 'heart' },
	birth_spouse: { label: 'Naissance', description: 'Naissance d\'un enfant', icon: 'baby' },
	death_1st_degree: { label: 'Décès conjoint/enfant', description: 'Décès du conjoint ou d\'un enfant', icon: 'flower-2' },
	death_2nd_degree: { label: 'Décès ascendant', description: 'Décès d\'un parent ou grand-parent', icon: 'flower-2' },
	child_marriage: { label: 'Mariage enfant', description: 'Mariage d\'un enfant', icon: 'heart' },
	moving: { label: 'Déménagement', description: 'Déménagement du domicile', icon: 'moving' },
};


// Schema pour la création/mise à jour de policy
export const LeavePolicyCreateSchema = LeavePolicySchema.omit({ id: true });
export const LeavePolicyUpdateSchema = LeavePolicySchema.partial().omit({ id: true, country_code: true });


// Schema pour la création/mise à jour de règle de circonstance
export const CircumstanceRuleCreateSchema = CircumstanceLeaveRuleSchema.omit({ id: true, policy_id: true });
// Note: type is included because backend requires it even for PATCH updates
export const CircumstanceRuleUpdateSchema = CircumstanceLeaveRuleSchema.partial().omit({ id: true, policy_id: true });

// Schema pour la création/mise à jour de règle d'ancienneté
export const SeniorityRuleCreateSchema = SeniorityRuleSchema.omit({ id: true, policy_id: true });
export const SeniorityRuleUpdateSchema = SeniorityRuleSchema.partial().omit({ id: true, policy_id: true });


// Schema pour la validation frontend de LeaveConfig
export const LeaveConfigValidationSchema = z.object({
	annualLeaveDays: z.number().int().min(12, 'Minimum 12 jours').max(40, 'Maximum 40 jours'),
	allowsCarryOver: z.boolean(),
	maxCarryOverDays: z.number().int().min(0, 'Minimum 0 jours').max(30, 'Maximum 30 jours'),
	carryOverExpirationMonth: z.number().int().min(1, 'Mois entre 1 et 12').max(12, 'Mois entre 1 et 12'),
	seniorityBonus: z.object({
		enabled: z.boolean(),
		yearsPerBonus: z.number().int().min(1, 'Minimum 1 an').max(10, 'Maximum 10 ans'),
		bonusDays: z.number().int().min(1, 'Minimum 1 jour').max(10, 'Maximum 10 jours'),
		maxBonus: z.number().int().optional(),
	}),
});

export type LeaveConfigValidation = z.infer<typeof LeaveConfigValidationSchema>;

// Types exportés
export type LeavePolicyCreate = z.infer<typeof LeavePolicyCreateSchema>;
export type LeavePolicyUpdate = z.infer<typeof LeavePolicyUpdateSchema>;
export type CircumstanceRuleCreate = z.infer<typeof CircumstanceRuleCreateSchema>;
export type CircumstanceRuleUpdate = z.infer<typeof CircumstanceRuleUpdateSchema>;
export type SeniorityRuleCreate = z.infer<typeof SeniorityRuleCreateSchema>;
export type SeniorityRuleUpdate = z.infer<typeof SeniorityRuleUpdateSchema>;

