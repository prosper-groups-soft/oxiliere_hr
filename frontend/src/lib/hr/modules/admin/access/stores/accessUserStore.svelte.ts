import type { 
	SystemUser, 
	Group, 
	Grant, 
	PaginatedSystemUsersResponse,
	ApiUserCreate,
	ApiUserUpdate
} from '../types/access.types';
import { usersEndpoint } from '../api/users';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { accessStore } from './accessStore.svelte';


export class AccessUserStore {
	// UI STATE
	
	// Pagination
	currentPage = $state(1);
	perPage = $state(8);
	
	// Filters
	searchQuery = $state('');
	selectedGroups = $state<string[]>([]);
	selectedRoles = $state<string[]>([]);
	isActiveFilter = $state<boolean | null>(null);
	
	// Selection
	selectedUser = $state<SystemUser | null>(null);
	
	// Cache for user groups in list view (userId -> Group[])
	userGroupsCache = $state<Map<string, Group[]>>(new Map());

	// DATA received from components (TanStack Query results)
	// Components call setUsersData(), setUserGroups(), setUserGrants() to update
	
	// Query filters - computed from UI state (passed to component queries)
	queryFilters = $derived({
		search: this.searchQuery || undefined,
		page: this.currentPage,
		page_size: this.perPage,
		groups: this.selectedGroups.length > 0 ? this.selectedGroups : undefined,
		roles: this.selectedRoles.length > 0 ? this.selectedRoles : undefined,
		is_active: this.isActiveFilter !== null ? this.isActiveFilter : undefined
	});

	// DATA STATE (set by components using TanStack Query)
	// These are synced via $effect blocks at the end of the class
	users = $state<SystemUser[]>([]);
	totalCount = $state(0);
	isLoading = $state(false);
	isFetching = $state(false);
	queryError = $state<Error | null>(null);
	hasLoaded = $state(false);
	
	selectedUserGroups = $state<Group[]>([]);
	selectedUserGrants = $state<Grant[]>([]);

	// Mutations (set by components, called via callbacks)
	toggleActiveMutation?: { mutateAsync: (vars: { tenantUserId: string; userId: string; isActive: boolean }) => Promise<SystemUser> };
	deleteMutation?: { mutateAsync: (userId: string) => Promise<void> };
	createMutation?: { mutateAsync: (data: ApiUserCreate) => Promise<SystemUser> };
	updateMutation?: { mutateAsync: (vars: { tenantUserId: string; userId: string; data: ApiUserUpdate }) => Promise<SystemUser> };

	// DERIVED DATA
	totalPages = $derived(Math.ceil(this.totalCount / this.perPage));
	error = $derived(this.queryError ? String(this.queryError) : null);
	hasEverSeenUsers = $derived(this.users.length > 0 || this.hasLoaded);

	// --- Computed ---
	activeFiltersCount = $derived(
		(this.searchQuery ? 1 : 0) +
		this.selectedGroups.length +
		this.selectedRoles.length +
		(this.isActiveFilter !== null ? 1 : 0)
	);

	paginatedUsers = $derived(this.users);

	// View state for UI transitions
	viewState: 'initial-loading' | 'content' | 'empty' = $derived(
		!this.hasLoaded && this.isLoading ? 'initial-loading' :
		this.users.length > 0 ? 'content' :
		'empty'
	);

	// True when reloading data
	// True when reloading data (background refetch)
	isReloading = $derived(this.hasLoaded && this.isFetching);

	// Safety checks for last admin/owner
	adminCount = $derived(this.users.filter((u: SystemUser) => u.is_admin && u.is_active !== false).length);
	ownerCount = $derived(this.users.filter((u: SystemUser) => u.is_owner && u.is_active !== false).length);

	// ACTIONS - Filter management
	
	setSearch(query: string) {
		this.searchQuery = query;
		this.currentPage = 1;
		this.selectedUser = null;
	}

	setPage(page: number) {
		if (page < 1 || page > this.totalPages) return;
		this.currentPage = page;
		this.selectedUser = null;
	}

	setPerPage(size: number) {
		this.perPage = size;
		this.currentPage = 1;
		this.selectedUser = null;
	}

	toggleGroupFilter(groupSlug: string) {
		if (this.selectedGroups.includes(groupSlug)) {
			this.selectedGroups = this.selectedGroups.filter(g => g !== groupSlug);
		} else {
			this.selectedGroups = [...this.selectedGroups, groupSlug];
		}
		this.currentPage = 1;
		this.selectedUser = null;
	}

	toggleRoleFilter(roleSlug: string) {
		if (this.selectedRoles.includes(roleSlug)) {
			this.selectedRoles = this.selectedRoles.filter(r => r !== roleSlug);
		} else {
			this.selectedRoles = [...this.selectedRoles, roleSlug];
		}
		this.currentPage = 1;
		this.selectedUser = null;
	}

	setActiveFilter(isActive: boolean | null) {
		this.isActiveFilter = isActive;
		this.currentPage = 1;
		this.selectedUser = null;
	}

	resetFilters() {
		this.searchQuery = '';
		this.selectedGroups = [];
		this.selectedRoles = [];
		this.isActiveFilter = null;
		this.currentPage = 1;
		this.selectedUser = null;
	}

	// ACTIONS - User mutations via TanStack Query

	// USER MUTATIONS

	async toggleUserActive(tenantUserId: string) {
		const user = this.users.find((u: SystemUser) => u.id === tenantUserId);
		if (!user) return;
		
		const newStatus = !user.is_active;
		
		// GUARD: Prevent disabling last admin or owner
		if (!newStatus && user.is_active) {
			if (user.is_admin && this.adminCount <= 1) {
				notification.toast.error('Impossible de désactiver le dernier administrateur');
				throw new Error('Cannot disable last admin');
			}
			if (user.is_owner && this.ownerCount <= 1) {
				notification.toast.error('Impossible de désactiver le dernier propriétaire');
				throw new Error('Cannot disable last owner');
			}
		}
		
		try {
			if (!this.toggleActiveMutation) {
				throw new Error('toggleActiveMutation not set');
			}
			await this.toggleActiveMutation.mutateAsync({
				tenantUserId: user.id,
				userId: user.user.id,
				isActive: newStatus
			});

			
			notification.toast.success(`Utilisateur ${newStatus ? 'activé' : 'désactivé'}`);
			// Le cache s'invalide automatiquement
		} catch (e: any) {
			notification.toast.error(getFriendlyErrorMessage(e));
			throw e;
		}
	}

	async deleteUser(tenantUserId: string) {
		const user = this.users.find((u: SystemUser) => u.id === tenantUserId);
		if (!user) return;
		
		// GUARD: Prevent deleting last admin or owner
		if (user.is_admin && this.adminCount <= 1) {
			notification.toast.error('Impossible de supprimer le dernier administrateur');
			throw new Error('Cannot delete last admin');
		}
		if (user.is_owner && this.ownerCount <= 1) {
			notification.toast.error('Impossible de supprimer le dernier propriétaire');
			throw new Error('Cannot delete last owner');
		}
		
		try {
			if (!this.deleteMutation) {
				throw new Error('deleteMutation not set');
			}
			await this.deleteMutation.mutateAsync(user.user.id);
			if (this.selectedUser?.id === tenantUserId) {
				this.selectedUser = null;
			}
			notification.toast.success('Utilisateur supprimé');
			// Le cache s'invalide automatiquement
		} catch (e: any) {
			notification.toast.error(getFriendlyErrorMessage(e));
			throw e;
		}
	}

	async createUser(data: {
		email: string;
		first_name: string;
		last_name: string;
		password: string;
		is_active?: boolean;
		is_admin?: boolean;
		is_owner?: boolean;
		groups?: string[];
	}) {
		try {
			// La mutation gère la création et invalidation du cache
			if (!this.createMutation) {
				throw new Error('createMutation not set');
			}
			const newUser = await this.createMutation.mutateAsync(data as ApiUserCreate);
			
			// Assign admin/owner roles if needed (via endpoint direct)
			if (data.is_admin) {
				await usersEndpoint.assignRole({ user_id: newUser.user.id, role: 'admin', scope: '' });
			}
			if (data.is_owner) {
				await usersEndpoint.assignRole({ user_id: newUser.user.id, role: 'owner', scope: '' });
			}
			
			notification.toast.success('Utilisateur créé avec succès');
			return newUser;
		} catch (e: any) {
			notification.toast.error(getFriendlyErrorMessage(e));
			throw e;
		}
	}

	async updateUser(tenantUserId: string, data: {
		email?: string;
		first_name?: string;
		last_name?: string;
		is_active?: boolean;
		is_admin?: boolean;
		is_owner?: boolean;
		groups?: string[];
	}) {
		const user = this.users.find((u: SystemUser) => u.id === tenantUserId);
		if (!user) {
			notification.toast.error('Utilisateur introuvable');
			return;
		}
		
		// GUARD: Prevent removing last admin
		if (data.is_admin === false && user.is_admin && this.adminCount <= 1) {
			notification.toast.error('Impossible de retirer les droits administrateur au dernier administrateur');
			throw new Error('Cannot remove last admin');
		}
		
		// GUARD: Prevent removing last owner
		if (data.is_owner === false && user.is_owner && this.ownerCount <= 1) {
			notification.toast.error('Impossible de retirer les droits propriétaire au dernier propriétaire');
			throw new Error('Cannot remove last owner');
		}
		
		try {
			if (!this.updateMutation) {
				throw new Error('updateMutation not set');
			}
			const updated = await this.updateMutation.mutateAsync({
				tenantUserId: user.id,
				userId: user.user.id,
				data
			});
			
			// Mise à jour du selectedUser si nécessaire
			if (this.selectedUser?.id === tenantUserId) {
				const merged: SystemUser = {
					...user,
					user: { ...user.user, ...updated.user },
					is_active: updated.is_active ?? user.is_active,
				};
				this.selectedUser = merged;
			}
			
			return updated;
		} catch (e: any) {
			throw e;
		}
	}

	// SELECTION (simplifiée avec TanStack Query)
	
	selectUser(user: SystemUser | null) {
		this.selectedUser = user;
	}

	async fetchAndCacheUserGroups(userId: string): Promise<Group[]> {
		// Return cached if available
		if (this.userGroupsCache.has(userId)) {
			return this.userGroupsCache.get(userId)!;
		}
		
		try {
			const groups = await usersEndpoint.getGroups(userId);
			// Update cache
			this.userGroupsCache = new Map(this.userGroupsCache).set(userId, groups);
			return groups;
		} catch (e: any) {
			console.error('Failed to fetch user groups for list:', e);
			notification.toast.error(getFriendlyErrorMessage(e));
			return [];
		}
	}

	clearUserGroupsCache() {
		this.userGroupsCache = new Map();
	}

	// ROLE MANAGEMENT

	async assignRole(userId: string, roleSlug: string) {
		// Ensure scopes are loaded
		if (accessStore.scopes.length === 0) {
			await accessStore.fetchScopes();
		}
		
		try {
			// Assign role for all scopes
			const scopes = accessStore.scopes;
			if (scopes.length === 0) {
				throw new Error('Aucun scope disponible');
			}
			
			// Create assignments for all scopes
			const assignments = scopes.map(scope => 
				usersEndpoint.assignRole({ user_id: userId, role: roleSlug, scope })
			);
			await Promise.all(assignments);
			
			// Trigger grants query refetch (via selection update)
			// Les grants se rechargent automatiquement via la query
			notification.toast.success(`Rôle assigné avec succès`);
		} catch (e: any) {
			notification.toast.error(getFriendlyErrorMessage(e));
			throw e;
		}
	}

	async revokeRole(userId: string, roleSlug: string) {
		// GUARD: Prevent revoking admin role from last admin
		if (roleSlug === 'admin') {
			const user = this.users.find((u: SystemUser) => u.user.id === userId);
			if (user?.is_admin && this.adminCount <= 1) {
				notification.toast.error('Impossible de retirer le rôle administrateur au dernier administrateur');
				throw new Error('Cannot revoke admin role from last admin');
			}
		}
		
		// GUARD: Prevent revoking owner role from last owner
		if (roleSlug === 'owner') {
			const user = this.users.find((u: SystemUser) => u.user.id === userId);
			if (user?.is_owner && this.ownerCount <= 1) {
				notification.toast.error('Impossible de retirer le rôle propriétaire au dernier propriétaire');
				throw new Error('Cannot revoke owner role from last owner');
			}
		}
		
		// Ensure scopes are loaded
		if (accessStore.scopes.length === 0) {
			await accessStore.fetchScopes();
		}
		
		try {
			// Revoke role for all scopes
			const scopes = accessStore.scopes;
			if (scopes.length === 0) {
				throw new Error('Aucun scope disponible');
			}
			
			// Create revocations for all scopes
			const revocations = scopes.map(scope => 
				usersEndpoint.revokeRole({ user_id: userId, role: roleSlug, scope })
			);
			await Promise.all(revocations);
			
			// Trigger grants query refetch
			// Les grants se rechargent automatiquement via la query
			notification.toast.success(`Rôle retiré avec succès`);
		} catch (e: any) {
			notification.toast.error(getFriendlyErrorMessage(e));
			throw e;
		}
	}

	// DATA SETTERS (called by components with TanStack Query results)
	
	setUsersData(data: PaginatedSystemUsersResponse | undefined, isLoading: boolean, isFetching: boolean, error: Error | null, hasLoaded: boolean) {
		this.isLoading = isLoading;
		this.isFetching = isFetching;
		this.queryError = error;
		this.hasLoaded = hasLoaded;
		if (data) {
			this.users = data.results ?? [];
			this.totalCount = data.count ?? 0;
		}
	}

	setUserGroups(groups: Group[] | undefined) {
		this.selectedUserGroups = groups ?? [];
	}

	setUserGrants(grants: Grant[] | undefined) {
		this.selectedUserGrants = grants ?? [];
	}

	// Mutations setters (components pass their mutation objects)
	setMutations(mutations: {
		toggleActive?: { mutateAsync: (vars: { tenantUserId: string; userId: string; isActive: boolean }) => Promise<SystemUser> };
		delete?: { mutateAsync: (userId: string) => Promise<void> };
		create?: { mutateAsync: (data: ApiUserCreate) => Promise<SystemUser> };
		update?: { mutateAsync: (vars: { tenantUserId: string; userId: string; data: ApiUserUpdate }) => Promise<SystemUser> };
	}) {
		this.toggleActiveMutation = mutations.toggleActive;
		this.deleteMutation = mutations.delete;
		this.createMutation = mutations.create;
		this.updateMutation = mutations.update;
	}
}


// Singleton instance
export const accessUserStore = new AccessUserStore();

