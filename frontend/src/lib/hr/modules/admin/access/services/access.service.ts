import {
	groupsEndpoint,
	rolesEndpoint,
	roleGrantsEndpoint,
	usersEndpoint,
	systemUsersEndpoint,
	grantsEndpoint,
	scopesEndpoint
} from '../api';
import type {
	Role,
	Group,
	GroupCreate,
	RoleGrant,
	RoleGrantCreate,
	Grant,
	UserGroupAssignment,
	UserRoleAssignment,
	UserGrantOverride,
	GroupMember
} from '../types/access.types';


/**
 * Service pour gérer les accès et permissions
 * Utilise les endpoints dédiés dans le dossier api/
 * Aligné avec la documentation API /api/access/*
 */
class AccessService {
	// SCOPES
	
	/**
	 * GET /api/access/scopes
	 * Liste tous les scopes disponibles
	 */
	async listScopes(): Promise<string[]> {
		return await scopesEndpoint.list();
	}

	// ============================================================
	// ROLES
	// ============================================================
	
	/**
	 * GET /api/access/roles
	 * Liste tous les rôles
	 */
	async listRoles(): Promise<Role[]> {
		return await rolesEndpoint.list();
	}

	/**
	 * POST /api/access/roles/{role_slug}/restore-defaults
	 * Rétablit les permissions par défaut d'un rôle
	 */
	async restoreRoleDefaults(roleSlug: string): Promise<void> {
		await rolesEndpoint.restoreDefaults(roleSlug);
	}

	// ============================================================
	// GROUPS
	// ============================================================
	
	/**
	 * GET /api/access/groups
	 * Liste tous les groupes
	 */
	async listGroups(): Promise<Group[]> {
		return await groupsEndpoint.list();
	}

	/**
	 * GET /api/access/groups/{group_slug}
	 * Récupère un groupe par son slug
	 */
	async getGroup(groupSlug: string): Promise<Group> {
		return await groupsEndpoint.get(groupSlug);
	}

	/**
	 * POST /api/access/groups
	 * Crée un nouveau groupe
	 */
	async createGroup(data: GroupCreate): Promise<Group> {
		return await groupsEndpoint.create(data);
	}

	/**
	 * PUT /api/access/groups/{group_slug}
	 * Met à jour un groupe existant
	 */
	async updateGroup(groupSlug: string, data: Partial<GroupCreate>): Promise<Group> {
		return await groupsEndpoint.update(groupSlug, data);
	}

	/**
	 * DELETE /api/access/groups/{group_slug}
	 * Supprime un groupe
	 */
	async deleteGroup(groupSlug: string): Promise<void> {
		await groupsEndpoint.delete(groupSlug);
	}

	/**
	 * GET /api/access/groups/{group_slug}/members
	 * Récupère les membres d'un groupe
	 */
	async getGroupMembers(groupSlug: string): Promise<GroupMember[]> {
		return await groupsEndpoint.getMembers(groupSlug);
	}

	// ============================================================
	// USER ASSIGNMENTS
	// ============================================================
	
	/**
	 * POST /api/access/users/assign-role
	 * Assigne un rôle à un utilisateur
	 */
	async assignRoleToUser(data: UserRoleAssignment): Promise<void> {
		await usersEndpoint.assignRole(data);
	}

	/**
	 * POST /api/access/users/revoke-role
	 * Révoque un rôle d'un utilisateur
	 */
	async revokeRoleFromUser(data: UserRoleAssignment): Promise<void> {
		await usersEndpoint.revokeRole(data);
	}

	/**
	 * POST /api/access/users/override-grant
	 * Crée une permission override pour un utilisateur
	 */
	async overrideGrantForUser(data: UserGrantOverride): Promise<Grant> {
		return await usersEndpoint.overrideGrant(data);
	}

	/**
	 * POST /api/access/users/assign-group
	 * Assigne un groupe à un utilisateur
	 */
	async assignGroupToUser(data: UserGroupAssignment): Promise<void> {
		await usersEndpoint.assignGroup(data);
	}

	/**
	 * Assigne un groupe à un utilisateur par son email
	 * Recherche l'utilisateur par email puis assigne le groupe
	 */
	async assignGroupToUserByEmail(email: string, groupSlug: string): Promise<void> {
		const users = await systemUsersEndpoint.findByEmail(email);
		if (!users || users.length === 0) {
			throw new Error('Aucun utilisateur trouvé avec cet email.');
		}
		const userId = users[0].user.id;
		await usersEndpoint.assignGroup({ user_id: userId, group: groupSlug });
	}

	/**
	 * POST /api/access/users/revoke-group
	 * Révoque un groupe d'un utilisateur
	 */
	async revokeGroupFromUser(data: UserGroupAssignment): Promise<void> {
		await usersEndpoint.revokeGroup(data);
	}

	/**
	 * GET /api/access/users/{user_id}/grants
	 * Récupère les grants d'un utilisateur
	 */
	async getUserGrants(userId: string): Promise<Grant[]> {
		return await usersEndpoint.getGrants(userId);
	}

	/**
	 * GET /api/access/users/{user_id}/groups
	 * Récupère les groupes d'un utilisateur
	 */
	async getUserGroups(userId: string): Promise<Group[]> {
		return await usersEndpoint.getGroups(userId);
	}

	/**
	 * GET /api/users
	 * Liste tous les utilisateurs système avec leurs groupes assignés
	 */
	async listUsers(params?: { search?: string; page?: number; page_size?: number }): Promise<{ count: number; results: any[] }> {
		return await systemUsersEndpoint.list(params);
	}

	// ============================================================
	// GRANTS
	// ============================================================
	
	/**
	 * PUT /api/access/grants/{grant_id}
	 * Met à jour un grant
	 */
	async updateGrant(grantId: number, actions: string[]): Promise<Grant> {
		return await grantsEndpoint.update(grantId, actions);
	}

	// ============================================================
	// ROLE GRANTS
	// ============================================================
	
	/**
	 * GET /api/access/role-grants
	 * Liste tous les role grants
	 */
	async listRoleGrants(): Promise<RoleGrant[]> {
		return await roleGrantsEndpoint.list();
	}

	/**
	 * POST /api/access/role-grants
	 * Crée un role grant
	 */
	async createRoleGrant(data: RoleGrantCreate): Promise<RoleGrant> {
		return await roleGrantsEndpoint.create(data);
	}

	/**
	 * PUT /api/access/role-grants/{grant_id}
	 * Met à jour un role grant
	 */
	async updateRoleGrant(grantId: number, actions: string[]): Promise<RoleGrant> {
		return await roleGrantsEndpoint.update(grantId, actions);
	}

	/**
	 * DELETE /api/access/role-grants/{grant_id}
	 * Supprime un role grant
	 */
	async deleteRoleGrant(grantId: number): Promise<void> {
		await roleGrantsEndpoint.delete(grantId);
	}
}


export const accessService = new AccessService();

