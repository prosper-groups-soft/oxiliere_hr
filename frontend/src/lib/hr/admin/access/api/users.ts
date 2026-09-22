import APIEndPoint from '@/utilities/http/rest';
import type { 
	UserGroupAssignment, 
	UserRoleAssignment, 
	UserGrantOverride, 
	Grant, 
	Group,
	SystemUser,
	PaginatedSystemUsersResponse,
	ApiUserCreate,
	ApiUserUpdate
} from '../types/access.types';


/**
 * Endpoints API pour la gestion des utilisateurs système
 * Base path: /api/users
 */
export const systemUsersEndpoint = {
	/**
	 * GET /api/users
	 * Liste tous les utilisateurs système avec pagination
	 */
	list: async (params?: { search?: string; page?: number; page_size?: number; groups?: string[]; is_active?: boolean }): Promise<PaginatedSystemUsersResponse> => {
		const endpoint = new APIEndPoint('/api/users', '/api/users');
		return await endpoint.list(params);
	},

	/**
	 * POST /api/users
	 * Crée un nouvel utilisateur
	 */
	create: async (data: ApiUserCreate): Promise<SystemUser> => {
		const endpoint = new APIEndPoint('/api/users', '/api/users');
		return await endpoint.create(data);
	},

	/**
	 * GET /api/users/{user_id}
	 * Récupère un utilisateur par son ID
	 */
	get: async (userId: string): Promise<SystemUser> => {
		const endpoint = new APIEndPoint(`/api/users/${userId}`, `/api/users/${userId}`);
		return await endpoint.retrieve();
	},

	/**
	 * PATCH /api/users/{user_id}
	 * Met à jour un utilisateur
	 */
	update: async (userId: string, data: ApiUserUpdate): Promise<SystemUser> => {
		const endpoint = new APIEndPoint(`/api/users/${userId}`, `/api/users/${userId}`);
		return await endpoint.update(data);
	},

	/**
	 * DELETE /api/users/{user_id}
	 * Supprime un utilisateur
	 */
	delete: async (userId: string): Promise<void> => {
		const endpoint = new APIEndPoint(`/api/users/${userId}`, `/api/users/${userId}`);
		await endpoint.destroy(userId);
	},

	/**
	 * PUT /api/users/{user_id}/set-admin
	 * Définit le statut admin d'un utilisateur
	 */
	setAdmin: async (userId: string, isAdmin: boolean): Promise<SystemUser> => {
		const endpoint = new APIEndPoint(`/api/users/${userId}/set-admin`, `/api/users/${userId}/set-admin`);
		return await endpoint.update({ is_admin: isAdmin });
	},

	/**
	 * PUT /api/users/{user_id}/set-owner
	 * Définit le statut owner d'un utilisateur
	 */
	setOwner: async (userId: string, isOwner: boolean): Promise<SystemUser> => {
		const endpoint = new APIEndPoint(`/api/users/${userId}/set-owner`, `/api/users/${userId}/set-owner`);
		return await endpoint.update({ is_owner: isOwner });
	},

	/**
	 * Recherche un utilisateur par email
	 */
	findByEmail: async (email: string): Promise<SystemUser[]> => {
		const endpoint = new APIEndPoint('/api/users', '/api/users');
		return await endpoint.list({ email });
	}
};


/**
 * Endpoints API pour la gestion des utilisateurs et leurs permissions
 * Base path: /api/access/users
 */
export const usersEndpoint = {
	/**
	 * POST /api/access/users/assign-role
	 * Assigne un rôle à un utilisateur
	 */
	assignRole: async (data: UserRoleAssignment): Promise<void> => {
		const endpoint = new APIEndPoint(
			'/api/access/users/assign-role',
			'/api/access/users/assign-role'
		);
		await endpoint.create(data);
	},

	/**
	 * POST /api/access/users/revoke-role
	 * Révoque un rôle d'un utilisateur
	 */
	revokeRole: async (data: UserRoleAssignment): Promise<void> => {
		const endpoint = new APIEndPoint(
			'/api/access/users/revoke-role',
			'/api/access/users/revoke-role'
		);
		await endpoint.create(data);
	},

	/**
	 * POST /api/access/users/override-grant
	 * Crée une permission override pour un utilisateur
	 */
	overrideGrant: async (data: UserGrantOverride): Promise<Grant> => {
		const endpoint = new APIEndPoint(
			'/api/access/users/override-grant',
			'/api/access/users/override-grant'
		);
		return await endpoint.create(data);
	},

	/**
	 * POST /api/access/users/assign-group
	 * Assigne un groupe à un utilisateur
	 */
	assignGroup: async (data: UserGroupAssignment): Promise<void> => {
		const endpoint = new APIEndPoint(
			'/api/access/users/assign-group',
			'/api/access/users/assign-group'
		);
		await endpoint.create(data);
	},

	/**
	 * POST /api/access/users/revoke-group
	 * Révoque un groupe d'un utilisateur
	 */
	revokeGroup: async (data: UserGroupAssignment): Promise<void> => {
		const endpoint = new APIEndPoint(
			'/api/access/users/revoke-group',
			'/api/access/users/revoke-group'
		);
		await endpoint.create(data);
	},

	/**
	 * GET /api/access/users/{user_id}/grants
	 * Récupère les grants d'un utilisateur
	 */
	getGrants: async (userId: string): Promise<Grant[]> => {
		const endpoint = new APIEndPoint(
			`/api/access/users/${userId}/grants`,
			`/api/access/users/${userId}/grants`
		);
		return await endpoint.list();
	},

	/**
	 * GET /api/access/users/{user_id}/groups
	 * Récupère les groupes d'un utilisateur
	 */
	getGroups: async (userId: string): Promise<Group[]> => {
		const endpoint = new APIEndPoint(
			`/api/access/users/${userId}/groups`,
			`/api/access/users/${userId}/groups`
		);
		return await endpoint.list();
	}
};

