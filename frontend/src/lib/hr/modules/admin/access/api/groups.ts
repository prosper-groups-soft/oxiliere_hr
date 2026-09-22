import APIEndPoint from '@/hr/utilities/http/rest';
import type { 
	Group, 
	GroupCreate, 
	GroupMember 
} from '../types/access.types';

/**
 * Endpoints API pour la gestion des groupes
 * Base path: /api/access/groups
 */

export const groupsEndpoint = {
	/**
	 * GET /api/access/groups
	 * Liste tous les groupes
	 */
	list: async (): Promise<Group[]> => {
		const endpoint = new APIEndPoint('/api/access/groups', '/api/access/groups');
		return await endpoint.list();
	},

	/**
	 * GET /api/access/groups/{group_slug}
	 * Récupère un groupe par son slug
	 */
	get: async (groupSlug: string): Promise<Group> => {
		const endpoint = new APIEndPoint(
			`/api/access/groups/${groupSlug}`,
			`/api/access/groups/${groupSlug}`
		);
		return await endpoint.retrieve();
	},

	/**
	 * POST /api/access/groups
	 * Crée un nouveau groupe
	 */
	create: async (data: GroupCreate): Promise<Group> => {
		const endpoint = new APIEndPoint('/api/access/groups', '/api/access/groups');
		return await endpoint.create(data);
	},

	/**
	 * PUT /api/access/groups/{group_slug}
	 * Met à jour un groupe existant
	 */
	update: async (groupSlug: string, data: Partial<GroupCreate>): Promise<Group> => {
		const endpoint = new APIEndPoint(
			`/api/access/groups/${groupSlug}`,
			`/api/access/groups/${groupSlug}`
		);
		return await endpoint.update(data);
	},

	/**
	 * DELETE /api/access/groups/{group_slug}
	 * Supprime un groupe
	 */
	delete: async (groupSlug: string): Promise<void> => {
		const endpoint = new APIEndPoint(
			`/api/access/groups/${groupSlug}`,
			`/api/access/groups/${groupSlug}`
		);
		await endpoint.destroy();
	},

	/**
	 * GET /api/access/groups/{group_slug}/members
	 * Récupère les membres d'un groupe
	 */
	getMembers: async (groupSlug: string): Promise<GroupMember[]> => {
		const endpoint = new APIEndPoint(
			`/api/access/groups/${groupSlug}/members`,
			`/api/access/groups/${groupSlug}/members`
		);
		return await endpoint.list();
	}
};

