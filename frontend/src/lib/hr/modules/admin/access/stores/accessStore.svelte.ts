import type { Role, Group, RoleGrant, GroupCreate, RoleGrantCreate } from '../types/access.types';
import { accessService } from '../services/access.service';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { accessQueryKeys } from '../queries/accessQueries.svelte';
import type { QueryClient } from '@tanstack/svelte-query';


/**
 * Internal helper that verify if a role is locked.
 */
function isLockedRoleInternal(slug: string): boolean {
	return slug === 'admin';
}


export class AccessStore {
	// --- State ---
	roles = $state<Role[]>([]);
	groups = $state<Group[]>([]);
	roleGrants = $state<RoleGrant[]>([]);
	scopes = $state<string[]>([]);
	
	isLoading = $state(false);
	error = $state<string | null>(null);
	activeTabId = $state('users');
	selectedRole = $state<Role | null>(null);

	// Group mgmt UI (shared with PageTitle actions)
	groupsSearchQuery = $state('');
	isGroupSheetOpen = $state(false);
	selectedGroup = $state<Group | null>(null);
	
	private queryClient: QueryClient | null = null;

	// --- Actions ---

	openGroupSheet(group: Group | null = null) {
		this.selectedGroup = group;
		this.isGroupSheetOpen = true;
	}
	
	setQueryClient(client: QueryClient) {
		this.queryClient = client;
	}
	
	async init() {
		this.isLoading = true;
		try {
			await Promise.all([
				this.fetchScopes(),
				this.fetchRoles(),
				this.fetchGroups(),
				this.fetchRoleGrants()
			]);
		} catch (e: any) {
			this.error = getFriendlyErrorMessage(e);
		} finally {
			this.isLoading = false;
		}
	}

	async fetchScopes() {
		this.scopes = await accessService.listScopes();
	}

	async fetchRoles() {
		const response = await accessService.listRoles();
		this.roles = response || [];
	}

	async fetchGroups() {
		const response = await accessService.listGroups();
		this.groups = response || [];
	}

	async fetchRoleGrants() {
		const response = await accessService.listRoleGrants();
		this.roleGrants = response || [];
	}

	async createGroup(data: GroupCreate) {
		this.isLoading = true;
		try {
			const newGroup = await accessService.createGroup(data);
			await this.fetchGroups();
			return newGroup;
		} catch (e: any) {
			this.error = getFriendlyErrorMessage(e);
			throw e;
		} finally {
			this.isLoading = false;
		}
	}

	async updateGroup(slug: string, data: Partial<GroupCreate>) {
		this.isLoading = true;
		this.error = null;
		try {
			const response = await accessService.updateGroup(slug, data);
			await this.fetchGroups();
			return response;
		} catch (e: any) {
			this.error = getFriendlyErrorMessage(e);
			throw e;
		} finally {
			this.isLoading = false;
		}
	}

	async deleteGroup(slug: string) {
		this.isLoading = true;
		this.error = null;
		try {
			await accessService.deleteGroup(slug);
			await this.fetchGroups();
		} catch (e: any) {
			this.error = e.message;
			throw e;
		} finally {
			this.isLoading = false;
		}
	}

	async createRoleGrant(data: RoleGrantCreate) {
		this.error = null;
		try {
			const rg = await accessService.createRoleGrant(data);
			await this.fetchRoleGrants();
			if (this.queryClient) {
				this.queryClient.invalidateQueries({ queryKey: accessQueryKeys.roleGrants() });
			}
			return rg;
		} catch (e: any) {
			this.error = getFriendlyErrorMessage(e);
			throw e;
		}
	}

	async updateRoleGrant(id: number, actions: string[]) {
		this.error = null;
		try {
			const rg = this.roleGrants.find(item => item.id === id);
			if (rg && isLockedRoleInternal(rg.role.slug)) {
				throw new Error("Modification interdite pour ce rôle système.");
			}
			await accessService.updateRoleGrant(id, actions);
			await this.fetchRoleGrants();
			if (this.queryClient) {
				this.queryClient.invalidateQueries({ queryKey: accessQueryKeys.roleGrants() });
			}
		} catch (e: any) {
			this.error = getFriendlyErrorMessage(e);
			throw e;
		}
	}

	async deleteRoleGrant(id: number) {
		this.error = null;
		try {
			const rg = this.roleGrants.find(item => item.id === id);
			if (rg && isLockedRoleInternal(rg.role.slug)) {
				throw new Error("Suppression interdite pour ce rôle système.");
			}
			await accessService.deleteRoleGrant(id);
			await this.fetchRoleGrants();
			if (this.queryClient) {
				this.queryClient.invalidateQueries({ queryKey: accessQueryKeys.roleGrants() });
			}
		} catch (e: any) {
			this.error = getFriendlyErrorMessage(e);
			throw e;
		}
	}

	async restoreRoleDefaults(roleSlug: string) {
		this.isLoading = true;
		this.error = null;
		try {
			if (isLockedRoleInternal(roleSlug)) {
				throw new Error("Restauration interdite pour ce rôle système.");
			}
			await accessService.restoreRoleDefaults(roleSlug);
			await this.fetchRoleGrants();
			if (this.queryClient) {
				this.queryClient.invalidateQueries({ queryKey: accessQueryKeys.roleGrants() });
			}
		} catch (e: any) {
			this.error = e.message;
			throw e;
		} finally {
			this.isLoading = false;
		}
	}

	// Helper to get RoleGrants for a specific role
	getGrantsForRole(roleSlug: string): RoleGrant[] {
		return this.roleGrants?.filter(rg => rg.role.slug === roleSlug) || [];
	}
}


// Export instance (named and default)
export const accessStore = new AccessStore();
export default accessStore;

