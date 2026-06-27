import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import {
	leavePoliciesEndpoint,
	circumstanceRulesEndpoint,
	seniorityRulesEndpoint,
	leaveConfigEndpoint
} from '../api/leave.endpoints';
import type {
	LeavePolicy,
	LeavePolicyCreate,
	LeavePolicyUpdate,
	CircumstanceLeaveRule,
	CircumstanceRuleCreate,
	CircumstanceRuleUpdate,
	SeniorityRule,
	SeniorityRuleCreate,
	SeniorityRuleUpdate
} from '../schemas/leave.schemas';
import { CircumstanceTypeLabels } from '../schemas/leave.schemas';


/**
 * Service pour la gestion de la configuration des congés
 * Utilise les endpoints dédiés dans le dossier api/
 * Aligné avec la documentation API /api/leaves/config/*
 */
class LeaveSettingsService {
	// LEAVE POLICIES

	/**
	 * GET /api/leaves/config/policies
	 * Liste toutes les politiques de congés
	 */
	async listPolicies(): Promise<LeavePolicy[]> {
		try {
			const response = await leavePoliciesEndpoint.list();
			// API returns paginated response { results: [...], count: n }
			return response.results || response;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	/**
	 * POST /api/leaves/config/policies
	 * Crée une nouvelle politique de congés
	 */
	async createPolicy(data: LeavePolicyCreate): Promise<LeavePolicy> {
		try {
			const policy = await leavePoliciesEndpoint.create(data);
			notification.toast.success('Politique de congés créée avec succès');
			return policy;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	/**
	 * PATCH /api/leaves/config/policies/{policy_id}
	 * Met à jour une politique existante
	 */
	async updatePolicy(policyId: string, data: LeavePolicyUpdate, silent = false): Promise<LeavePolicy> {
		try {
			const policy = await leavePoliciesEndpoint.update(policyId, data);
			if (!silent) notification.toast.success('Politique de congés mise à jour');
			return policy;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	// SENIORITY RULES

	/**
	 * GET /api/leaves/config/policies/{policy_id}/seniority-rules
	 * Liste les règles d'ancienneté pour une politique
	 */
	async listSeniorityRules(policyId: string): Promise<SeniorityRule[]> {
		try {
			const response = await seniorityRulesEndpoint.list(policyId);
			return response.results || response;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	/**
	 * POST /api/leaves/config/policies/{policy_id}/seniority-rules
	 * Crée une nouvelle règle d'ancienneté
	 */
	async createSeniorityRule(policyId: string, data: SeniorityRuleCreate): Promise<SeniorityRule> {
		try {
			const rule = await seniorityRulesEndpoint.create(policyId, data);
			notification.toast.success('Règle d\'ancienneté créée');
			return rule;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	/**
	 * PATCH /api/leaves/config/seniority-rules/{rule_id}
	 * Met à jour une règle d'ancienneté
	 */
	async updateSeniorityRule(ruleId: string, data: SeniorityRuleUpdate, silent = false): Promise<SeniorityRule> {
		try {
			const rule = await seniorityRulesEndpoint.update(ruleId, data);
			if (!silent) notification.toast.success('Règle d\'ancienneté mise à jour');
			return rule;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	/**
	 * DELETE /api/leaves/config/seniority-rules/{rule_id}
	 * Supprime une règle d'ancienneté
	 */
	async deleteSeniorityRule(ruleId: string): Promise<void> {
		try {
			await seniorityRulesEndpoint.delete(ruleId);
			notification.toast.success('Règle d\'ancienneté supprimée');
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	// CIRCUMSTANCE RULES

	/**
	 * GET /api/leaves/config/policies/{policy_id}/circumstance-rules
	 * Liste les règles de congés de circonstance pour une politique
	 */
	async listCircumstanceRules(policyId: string): Promise<CircumstanceLeaveRule[]> {
		try {
			const response = await circumstanceRulesEndpoint.list(policyId);
			// API returns paginated response { results: [...], count: n }
			return response.results || response;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	/**
	 * POST /api/leaves/config/policies/{policy_id}/circumstance-rules
	 * Crée une nouvelle règle de congé de circonstance
	 */
	async createCircumstanceRule(policyId: string, data: CircumstanceRuleCreate): Promise<CircumstanceLeaveRule> {
		try {
			const rule = await circumstanceRulesEndpoint.create(policyId, data);
			notification.toast.success('Règle de congé créée avec succès');
			return rule;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	/**
	 * PATCH /api/leaves/config/circumstance-rules/{rule_id}
	 * Met à jour une règle de congé de circonstance
	 */
	async updateCircumstanceRule(ruleId: string, data: CircumstanceRuleUpdate, silent = false): Promise<CircumstanceLeaveRule> {
		try {
			const rule = await circumstanceRulesEndpoint.update(ruleId, data);
			if (!silent) notification.toast.success('Règle de congé mise à jour');
			return rule;
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	/**
	 * DELETE /api/leaves/config/circumstance-rules/{rule_id}
	 * Supprime une règle de congé de circonstance
	 */
	async deleteCircumstanceRule(ruleId: string): Promise<void> {
		try {
			await circumstanceRulesEndpoint.delete(ruleId);
			notification.toast.success('Règle de congé supprimée');
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	// INITIALIZATION

	/**
	 * POST /api/leaves/config/init-defaults
	 * Initialise les valeurs par défaut des congés
	 */
	async initializeDefaults(): Promise<void> {
		try {
			await leaveConfigEndpoint.initializeDefaults();
			notification.toast.success('Configuration par défaut initialisée');
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(message);
			throw error;
		}
	}

	// HELPERS

	/**
	 * Convertit les règles backend vers le format frontend
	 */
	convertRulesToFrontend(rules: CircumstanceLeaveRule[]): Array<{
		type: string;
		label: string;
		daysAllowed: number;
		description: string;
		icon: string;
		id?: string;
	}> {
		return rules.map(rule => {
			const labels = CircumstanceTypeLabels[rule.type] || {
				label: rule.type,
				description: '',
				icon: 'calendar'
			};
			return {
				id: rule.id,
				type: rule.type,
				label: labels.label,
				daysAllowed: rule.duration_days,
				description: labels.description,
				icon: labels.icon
			};
		});
	}
}


export const leaveSettingsService = new LeaveSettingsService();
