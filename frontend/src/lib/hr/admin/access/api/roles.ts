import APIEndPoint from '@/utilities/http/rest';
import type { 
	Role, 
	RoleGrant, 
	RoleGrantCreate 
} from '../types/access.types';


/**
 * Endpoints API pour la gestion des rôles et role grants
 * Base paths: /api/access/roles, /api/access/role-grants
 */

export const rolesEndpoint = {
	/**
	 * GET /api/access/roles
	 * Liste tous les rôles
	 */
	list: async (): Promise<Role[]> => {
		const endpoint = new APIEndPoint('/api/access/roles', '/api/access/roles');
		return await endpoint.list();
	},

	/**
	 * POST /api/access/roles/{role_slug}/restore-defaults
	 * Rétablit les permissions par défaut d'un rôle
	 */
	restoreDefaults: async (roleSlug: string): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/access/roles/${roleSlug}/restore-defaults`,
			`/api/access/roles/${roleSlug}/restore-defaults`
		);
		await endpoint.create({});
	}
};


export const roleGrantsEndpoint = {
	/**
	 * GET /api/access/role-grants
	 * Liste tous les role grants
	 */
	list: async (): Promise<RoleGrant[]> => {
		const endpoint = new APIEndPoint('/api/access/role-grants', '/api/access/role-grants');
		return await endpoint.list();
	},

	/**
	 * POST /api/access/role-grants
	 * Crée un role grant
	 */
	create: async (data: RoleGrantCreate): Promise<RoleGrant> => {
		const endpoint = new APIEndPoint('/api/access/role-grants', '/api/access/role-grants');
		return await endpoint.create(data);
	},

	/**
	 * PUT /api/access/role-grants/{grant_id}
	 * Met à jour un role grant
	 */
	update: async (grantId: number, actions: string[]): Promise<RoleGrant> => {
		const endpoint = new APIEndPoint(
			`/api/access/role-grants/${grantId}`,
			`/api/access/role-grants/${grantId}`
		);
		return await endpoint.update({ actions });
	},

	/**
	 * DELETE /api/access/role-grants/{grant_id}
	 * Supprime un role grant
	 */
	delete: async (grantId: number): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/access/role-grants/${grantId}/`,
			`/api/access/role-grants/${grantId}/`
		);
		await endpoint.destroy();
	}
};

