import APIEndPoint from '@/utilities/http/rest';
import type { Grant } from '../types/access.types';

/**
 * Endpoints API pour la gestion des grants
 * Base path: /api/access/grants
 */

export const grantsEndpoint = {
	/**
	 * PUT /api/access/grants/{grant_id}
	 * Met à jour un grant
	 */
	update: async (grantId: number, actions: string[]): Promise<Grant> => {
		const endpoint = new APIEndPoint(
			`/api/access/grants/${grantId}`,
			`/api/access/grants/${grantId}`
		);
		return await endpoint.update({ actions });
	}
};
