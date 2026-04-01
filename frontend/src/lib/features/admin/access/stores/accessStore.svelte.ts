import type { 
	Role, 
	Group, 
	RoleGrant, 
	GroupCreate, 
	RoleGrantCreate 
} from '../types/access.types';
import AccessEndpoints from '../api/access.endpoints';


export class AccessStore {
	// --- State ---
	roles = $state<Role[]>([]);
	groups = $state<Group[]>([]);
	roleGrants = $state<RoleGrant[]>([]);
	scopes = $state<string[]>([]);
	
	isLoading = $state(false);
	error = $state<string | null>(null);

	// --- Actions ---
	
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
			this.error = e.message || "Erreur lors du chargement des accès";
		} finally {
			this.isLoading = false;
		}
	}

	async fetchScopes() {
		const response = await AccessEndpoints.scopes.list();
		this.scopes = response || [];
	}

	async fetchRoles() {
		const response = await AccessEndpoints.roles.list();
		this.roles = response.results || [];
	}

	async fetchGroups() {
		const response = await AccessEndpoints.groups.list();
		this.groups = response.results || [];
	}

	async fetchRoleGrants() {
		const response = await AccessEndpoints.roleGrants.list();
		this.roleGrants = response.results || [];
	}

	async createGroup(data: GroupCreate) {
		this.isLoading = true;
		try {
			const newGroup = await AccessEndpoints.groups.create(data);
			await this.fetchGroups();
			return newGroup;
		} catch (e: any) {
			this.error = e.message;
			throw e;
		} finally {
			this.isLoading = false;
		}
	}

	async updateGroup(slug: string, data: Partial<GroupCreate>) {
		this.isLoading = true;
		this.error = null;
		try {
			// PUT: slug first for URL mapping (:slug), data becomes body
			const response = await AccessEndpoints.groups.update(slug, data);
			await this.fetchGroups();
			return response;
		} catch (e: any) {
			this.error = e.message;
			throw e;
		} finally {
			this.isLoading = false;
		}
	}

	async deleteGroup(slug: string) {
		this.isLoading = true;
		this.error = null;
		try {
			// DELETE: slug first for URL mapping (:slug)
			await AccessEndpoints.groups.destroy(slug);
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
			const rg = await AccessEndpoints.roleGrants.create(data);
			await this.fetchRoleGrants();
			return rg;
		} catch (e: any) {
			this.error = e.message;
			throw e;
		}
	}

	async updateRoleGrant(id: number, actions: string[]) {
		this.error = null;
		try {
			await AccessEndpoints.roleGrants.update([id], { actions });
			await this.fetchRoleGrants();
		} catch (e: any) {
			this.error = e.message;
			throw e;
		}
	}

	async deleteRoleGrant(id: number) {
		this.error = null;
		try {
			await AccessEndpoints.roleGrants.destroy([id]);
			await this.fetchRoleGrants();
		} catch (e: any) {
			this.error = e.message;
			throw e;
		}
	}

	async syncGroup(slug: string) {
		this.error = null;
		try {
			const response = await AccessEndpoints.syncGroup(slug).create();
			return response;
		} catch (e: any) {
			this.error = e.message;
			throw e;
		}
	}

	// Helper to get RoleGrants for a specific role
	getGrantsForRole(roleSlug: string): RoleGrant[] {
		return this.roleGrants?.filter(rg => rg.role.slug === roleSlug) || [];
	}
}


export const accessStore = new AccessStore();
