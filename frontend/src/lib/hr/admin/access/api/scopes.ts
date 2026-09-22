import APIEndPoint from '@/utilities/http/rest';


/**
 * Endpoints API pour les scopes
 * Base path: /api/access/scopes
 */

export const scopesEndpoint = {
	/**
	 * GET /api/access/scopes
	 * Liste tous les scopes disponibles
	 */
	list: async (): Promise<string[]> => {
		const endpoint = new APIEndPoint('/api/access/scopes', '/api/access/scopes');
		const response = await endpoint.list();
		return response || [];
	}
};
