import APIEndPoint from '@/utilities/http/rest';
import type { PaginatedResponse } from '@/types/pagination';
import type {
	PayrollConfigResponse,
	TaxBracketResponse,
	SocialContributionResponse,
	PayrollConfigUpdate,
	TaxBracketCreate,
	TaxBracketUpdate,
	SocialContributionCreate,
	SocialContributionUpdate
} from '../schemas/tax.schemas';
import type { LegalAllowance, OvertimeRule } from '../types/tax.types';

/**
 * Endpoints API pour la configuration fiscale et sociale
 * Base path: /api/payroll/configuration
 */


export const payrollConfigEndpoint = {
	/**
	 * GET /api/payroll/configuration/
	 * Récupère la configuration globale de paie
	 */
	retrieve: async (): Promise<PayrollConfigResponse> => {
		const endpoint = new APIEndPoint('/api/payroll/configuration/', '/api/payroll/configuration/');
		return await endpoint.retrieve();
	},

	/**
	 * PATCH /api/payroll/configuration/
	 * Met à jour la configuration globale
	 */
	update: async (data: PayrollConfigUpdate): Promise<PayrollConfigResponse> => {
		const endpoint = new APIEndPoint('/api/payroll/configuration/', '/api/payroll/configuration/');
		return await endpoint.partial_update(data);
	}
};


export const taxBracketsEndpoint = {
	/**
	 * GET /api/payroll/configuration/tax-brackets/
	 * Liste tous les barèmes IPR - Retourne un tableau directement
	 */
	list: async (): Promise<TaxBracketResponse[]> => {
		const endpoint = new APIEndPoint(
			'/api/payroll/configuration/tax-brackets/',
			'/api/payroll/configuration/tax-brackets/'
		);
		const response = await endpoint.list();
		// API returns array directly, not paginated response
		return Array.isArray(response) ? response : response.results || [];
	},

	/**
	 * POST /api/payroll/configuration/tax-brackets/
	 * Crée un nouveau barème IPR
	 */
	create: async (data: TaxBracketCreate): Promise<TaxBracketResponse> => {
		const endpoint = new APIEndPoint(
			'/api/payroll/configuration/tax-brackets/',
			'/api/payroll/configuration/tax-brackets/'
		);
		return await endpoint.create(data);
	},

	/**
	 * PATCH /api/payroll/configuration/tax-brackets/{bracket_id}
	 * Met à jour un barème IPR
	 */
	update: async (bracketId: string, data: TaxBracketUpdate): Promise<TaxBracketResponse> => {
		const endpoint = new APIEndPoint(
			`/api/payroll/configuration/tax-brackets/${bracketId}`,
			`/api/payroll/configuration/tax-brackets/${bracketId}`
		);
		return await endpoint.partial_update(data);
	}
};


export const socialContributionsEndpoint = {
	/**
	 * GET /api/payroll/configuration/contributions/
	 * Liste tous les taux de cotisations sociales
	 */
	list: async (): Promise<PaginatedResponse<SocialContributionResponse>> => {
		const endpoint = new APIEndPoint(
			'/api/payroll/configuration/contributions/',
			'/api/payroll/configuration/contributions/'
		);
		return await endpoint.list();
	},

	/**
	 * POST /api/payroll/configuration/contributions/
	 * Crée un nouveau taux de cotisation
	 */
	create: async (data: SocialContributionCreate): Promise<SocialContributionResponse> => {
		const endpoint = new APIEndPoint(
			'/api/payroll/configuration/contributions/',
			'/api/payroll/configuration/contributions/'
		);
		return await endpoint.create(data);
	},

	/**
	 * PATCH /api/payroll/configuration/social-rates/{rate_id}
	 * Met à jour un taux de cotisation
	 */
	update: async (rateId: string, data: SocialContributionUpdate): Promise<SocialContributionResponse> => {
		const endpoint = new APIEndPoint(
			`/api/payroll/configuration/social-rates/${rateId}`,
			`/api/payroll/configuration/social-rates/${rateId}`
		);
		return await endpoint.partial_update(data);
	}
};


export const payrollInitEndpoint = {
	/**
	 * POST /api/payroll/configuration/init/
	 * Initialise les valeurs par défaut de la paie
	 */
	initializeDefaults: async (): Promise<{ status: string; summary: Record<string, number> }> => {
		const endpoint = new APIEndPoint(
			'/api/payroll/configuration/init/',
			'/api/payroll/configuration/init/'
		);
		return await endpoint.create();
	}
};


export const legalAllowancesEndpoint = {
	/**
	 * GET /api/payroll/configuration/allowances/
	 * Liste toutes les allocations légales (FAMILLE, LOGEMENT...)
	 */
	list: async (): Promise<LegalAllowance[]> => {
		const endpoint = new APIEndPoint(
			'/api/payroll/configuration/allowances/',
			'/api/payroll/configuration/allowances/'
		);
		const response = await endpoint.list();
		return Array.isArray(response) ? response : response.results || [];
	},

	/**
	 * PATCH /api/payroll/configuration/allowances/{allowance_id}
	 * Met à jour une allocation légale
	 */
	update: async (allowanceId: string, data: Partial<LegalAllowance>): Promise<LegalAllowance> => {
		const endpoint = new APIEndPoint(
			`/api/payroll/configuration/allowances/${allowanceId}`,
			`/api/payroll/configuration/allowances/${allowanceId}`
		);
		return await endpoint.partial_update(data);
	}
};


export const overtimeRulesEndpoint = {
	/**
	 * GET /api/payroll/configuration/overtime/
	 * Liste toutes les règles d'heures supplémentaires
	 */
	list: async (): Promise<OvertimeRule[]> => {
		const endpoint = new APIEndPoint(
			'/api/payroll/configuration/overtime/',
			'/api/payroll/configuration/overtime/'
		);
		const response = await endpoint.list();
		return Array.isArray(response) ? response : response.results || [];
	},

	/**
	 * PATCH /api/payroll/configuration/overtime/{rule_id}
	 * Met à jour une règle d'heures supplémentaires
	 */
	update: async (ruleId: string, data: Partial<OvertimeRule>): Promise<OvertimeRule> => {
		const endpoint = new APIEndPoint(
			`/api/payroll/configuration/overtime/${ruleId}`,
			`/api/payroll/configuration/overtime/${ruleId}`
		);
		const response = await endpoint.partial_update(data);
		return response as OvertimeRule;
	}
};

