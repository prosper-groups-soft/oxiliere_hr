import APIEndPoint from '@/utilities/http/rest';
import type { PaginatedResponse } from '@/utilities/common/types';
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


/**
 * Endpoints API pour la configuration des congés
 * Base path: /api/leaves/config
 */
export const leavePoliciesEndpoint = {
	/**
	 * GET /api/leaves/config/policies
	 * Liste toutes les politiques de congés
	 */
	list: async (): Promise<PaginatedResponse<LeavePolicy>> => {
		const endpoint = new APIEndPoint('/api/leaves/config/policies', '/api/leaves/config/policies');
		return await endpoint.list();
	},

	/**
	 * POST /api/leaves/config/policies
	 * Crée une nouvelle politique de congés
	 */
	create: async (data: LeavePolicyCreate): Promise<LeavePolicy> => {
		const endpoint = new APIEndPoint('/api/leaves/config/policies', '/api/leaves/config/policies');
		return await endpoint.create(data);
	},

	/**
	 * PATCH /api/leaves/config/policies/{policy_id}
	 * Met à jour une politique existante
	 */
	update: async (policyId: string, data: LeavePolicyUpdate): Promise<LeavePolicy> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/policies/${policyId}`,
			`/api/leaves/config/policies/${policyId}`
		);
		return await endpoint.partial_update(data);
	}
};


export const circumstanceRulesEndpoint = {
	/**
	 * GET /api/leaves/config/policies/{policy_id}/circumstance-rules
	 * Liste les règles de congés de circonstance pour une politique
	 */
	list: async (policyId: string): Promise<PaginatedResponse<CircumstanceLeaveRule>> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/policies/${policyId}/circumstance-rules`,
			`/api/leaves/config/policies/${policyId}/circumstance-rules`
		);
		return await endpoint.list();
	},

	/**
	 * POST /api/leaves/config/policies/{policy_id}/circumstance-rules
	 * Crée une nouvelle règle de congé de circonstance
	 */
	create: async (policyId: string, data: CircumstanceRuleCreate): Promise<CircumstanceLeaveRule> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/policies/${policyId}/circumstance-rules`,
			`/api/leaves/config/policies/${policyId}/circumstance-rules`
		);
		return await endpoint.create(data);
	},

	/**
	 * PATCH /api/leaves/config/circumstance-rules/{rule_id}
	 * Met à jour une règle de congé de circonstance
	 */
	update: async (ruleId: string, data: CircumstanceRuleUpdate): Promise<CircumstanceLeaveRule> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/circumstance-rules/${ruleId}`,
			`/api/leaves/config/circumstance-rules/${ruleId}`
		);
		return await endpoint.partial_update(data);
	},

	/**
	 * DELETE /api/leaves/config/circumstance-rules/{rule_id}
	 * Supprime une règle de congé de circonstance
	 */
	delete: async (ruleId: string): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/circumstance-rules/${ruleId}`,
			`/api/leaves/config/circumstance-rules/${ruleId}`
		);
		await endpoint.destroy();
	}
};


export const seniorityRulesEndpoint = {
	/**
	 * GET /api/leaves/config/policies/{policy_id}/seniority-rules
	 * Liste les règles d'ancienneté pour une politique
	 */
	list: async (policyId: string): Promise<PaginatedResponse<SeniorityRule>> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/policies/${policyId}/seniority-rules`,
			`/api/leaves/config/policies/${policyId}/seniority-rules`
		);
		return await endpoint.list();
	},

	/**
	 * POST /api/leaves/config/policies/{policy_id}/seniority-rules
	 * Crée une nouvelle règle d'ancienneté
	 */
	create: async (policyId: string, data: SeniorityRuleCreate): Promise<SeniorityRule> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/policies/${policyId}/seniority-rules`,
			`/api/leaves/config/policies/${policyId}/seniority-rules`
		);
		return await endpoint.create(data);
	},

	/**
	 * PATCH /api/leaves/config/seniority-rules/{rule_id}
	 * Met à jour une règle d'ancienneté
	 */
	update: async (ruleId: string, data: SeniorityRuleUpdate): Promise<SeniorityRule> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/seniority-rules/${ruleId}`,
			`/api/leaves/config/seniority-rules/${ruleId}`
		);
		return await endpoint.partial_update(data);
	},

	/**
	 * DELETE /api/leaves/config/seniority-rules/{rule_id}
	 * Supprime une règle d'ancienneté
	 */
	delete: async (ruleId: string): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/leaves/config/seniority-rules/${ruleId}`,
			`/api/leaves/config/seniority-rules/${ruleId}`
		);
		await endpoint.destroy();
	}
};


export const leaveConfigEndpoint = {
	/**
	 * POST /api/leaves/config/init-defaults
	 * Initialise les valeurs par défaut des congés
	 */
	initializeDefaults: async (): Promise<void> => {
		const endpoint = new APIEndPoint(
			'/api/leaves/config/init-defaults',
			'/api/leaves/config/init-defaults'
		);
		await endpoint.create();
	}
};

