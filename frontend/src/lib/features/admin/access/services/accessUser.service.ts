import { systemUsersEndpoint, usersEndpoint } from '../api/users';
import { accountEndpoint } from '../api/account';
import type {
	SystemUser,
	PaginatedSystemUsersResponse,
	ApiUserCreate,
	ApiUserUpdate,
	Group,
	Grant
} from '../types/access.types';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { notification } from '@/stores/notification.svelte';


/**
 * Service pour la gestion des utilisateurs système
 * Utilise les endpoints systemUsersEndpoint
 * Gère les messages d'erreur utilisateur-friendly
 */
class AccessUserService {
	// LIST & FETCH

	/**
	 * Liste tous les utilisateurs avec pagination et recherche
	 */
	async listUsers(params?: {
		search?: string;
		page?: number;
		page_size?: number;
		groups?: string[];
		roles?: string[];
		is_active?: boolean;
	}): Promise<PaginatedSystemUsersResponse> {
		try {
			// Use accountEndpoint for listing (supports search, is_active, and groups filters)
			return await accountEndpoint.list(params);
		} catch (error: any) {
			notification.toast.error(getFriendlyErrorMessage(error));
			throw error;
		}
	}

	/**
	 * Récupère un utilisateur par son ID
	 */
	async getUser(userId: string): Promise<SystemUser> {
		try {
			return await systemUsersEndpoint.get(userId);
		} catch (error: any) {
			notification.toast.error(getFriendlyErrorMessage(error));
			throw error;
		}
	}

	// CREATE

	/**
	 * Crée un nouvel utilisateur
	 */
	async createUser(data: ApiUserCreate): Promise<SystemUser> {
		try {
			const user = await systemUsersEndpoint.create(data);
			notification.toast.success('Utilisateur créé avec succès');
			return user;
		} catch (error: any) {
			notification.toast.error(getFriendlyErrorMessage(error));
			throw error;
		}
	}

	// UPDATE

	/**
	 * Met à jour un utilisateur existant
	 * Fait jusqu'à 3 appels :
	 * - PATCH /api/account/{userId} pour le profil (first_name, last_name, email, is_active, groups)
	 * - PUT /api/users/{tenantUserId}/set-admin pour is_admin (avec guard last-admin)
	 * - PUT /api/users/{tenantUserId}/set-owner pour is_owner (avec guard last-owner)
	 * 
	 * @param tenantUserId - L'ID du TenantUser (user.id) pour /api/users
	 * @param userId - L'ID du User (user.user.id) pour /api/account
	 */
	async updateUser(tenantUserId: string, userId: string, data: ApiUserUpdate): Promise<SystemUser> {
		try {
			// Split data into profile fields
			const profileData: {
				first_name?: string;
				last_name?: string;
				email?: string;
				is_active?: boolean;
				groups?: string[];
			} = {};

			// Profile fields go to /api/account (utilise userId - User ID)
			if (data.first_name !== undefined) profileData.first_name = data.first_name;
			if (data.last_name !== undefined) profileData.last_name = data.last_name;
			if (data.email !== undefined) profileData.email = data.email;
			if (data.is_active !== undefined) profileData.is_active = data.is_active;
			if (data.groups !== undefined) profileData.groups = data.groups;

			// Call profile endpoint if needed
			if (Object.keys(profileData).length > 0) {
				await accountEndpoint.update(userId, profileData);
			}

			// Call permission endpoints (with last-admin/last-owner guards)
			// Use specific endpoints /set-admin and /set-owner instead of generic /update
			if (data.is_admin !== undefined) {
				await systemUsersEndpoint.setAdmin(tenantUserId, data.is_admin);
			}
			if (data.is_owner !== undefined) {
				await systemUsersEndpoint.setOwner(tenantUserId, data.is_owner);
			}

			// Re-fetch to get consistent SystemUser format (utilise tenantUserId)
			const updatedUser = await systemUsersEndpoint.get(tenantUserId);

			notification.toast.success('Utilisateur mis à jour');
			return updatedUser;
		} catch (error: any) {
			notification.toast.error(getFriendlyErrorMessage(error));
			throw error;
		}
	}

	/**
	 * Active ou désactive un utilisateur
	 * Note: is_active est un champ User (pas TenantUser), donc on utilise /api/account
	 * 
	 * @param tenantUserId - L'ID du TenantUser (user.id) pour re-fetch
	 * @param userId - L'ID du User (user.user.id) pour /api/account
	 */
	async toggleUserActive(tenantUserId: string, userId: string, isActive: boolean): Promise<SystemUser> {
		try {
			await accountEndpoint.update(userId, { is_active: isActive });
			// Re-fetch to get consistent SystemUser format (utilise tenantUserId)
			const user = await systemUsersEndpoint.get(tenantUserId);
			notification.toast.success(`Utilisateur ${isActive ? 'activé' : 'désactivé'}`);
			return user;
		} catch (error: any) {
			notification.toast.error(getFriendlyErrorMessage(error));
			throw error;
		}
	}

	// DELETE

	/**
	 * Supprime un utilisateur
	 */
	async deleteUser(userId: string): Promise<void> {
		try {
			await systemUsersEndpoint.delete(userId);
			notification.toast.success('Utilisateur supprimé');
		} catch (error: any) {
			notification.toast.error(getFriendlyErrorMessage(error));
			throw error;
		}
	}

	// USER DETAILS (Groups & Grants)

	/**
	 * Récupère les groupes d'un utilisateur
	 */
	async getUserGroups(userId: string): Promise<Group[]> {
		try {
			return await usersEndpoint.getGroups(userId);
		} catch (error: any) {
			notification.toast.error(getFriendlyErrorMessage(error));
			throw error;
		}
	}

	/**
	 * Récupère les grants (permissions) d'un utilisateur
	 */
	async getUserGrants(userId: string): Promise<Grant[]> {
		try {
			return await usersEndpoint.getGrants(userId);
		} catch (error: any) {
			notification.toast.error(getFriendlyErrorMessage(error));
			throw error;
		}
	}

	// ERROR HANDLING

}


export const accessUserService = new AccessUserService();

