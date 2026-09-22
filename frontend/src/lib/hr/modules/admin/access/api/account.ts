import APIEndPoint from '@/hr/utilities/http/rest';
import type { 
	SystemUser,
	PaginatedSystemUsersResponse
} from '../types/access.types';


/**
 * Endpoints API pour la gestion du profil utilisateur (account)
 * Base path: /api/account
 * Ce contrôleur permet de mettre à jour les champs User (first_name, last_name, email)
 * contrairement à /api/users qui gère les champs TenantUser (is_admin, is_owner)
 */
export const accountEndpoint = {
	/**
	 * GET /api/account
	 * Liste tous les utilisateurs avec recherche et pagination
	 */
	list: async (params?: { 
		search?: string; 
		page?: number; 
		page_size?: number;
		is_active?: boolean;
		groups?: string[];
		roles?: string[];
	}): Promise<PaginatedSystemUsersResponse> => {
		const endpoint = new APIEndPoint('/api/account', '/api/account');
		return await endpoint.list(params);
	},


	/**
	 * PATCH /api/account/{user_id}
	 * Met à jour le profil utilisateur (first_name, last_name, email, is_active, groups)
	 */
	update: async (userId: string, data: {
		first_name?: string;
		last_name?: string;
		email?: string;
		is_active?: boolean;
		groups?: string[];
	}): Promise<SystemUser> => {
		const endpoint = new APIEndPoint(`/api/account/${userId}`, `/api/account/${userId}`);
		// Use partial_update (PATCH) instead of update (PUT) - backend only accepts PATCH
		return await endpoint.partial_update(data);
	},
};

