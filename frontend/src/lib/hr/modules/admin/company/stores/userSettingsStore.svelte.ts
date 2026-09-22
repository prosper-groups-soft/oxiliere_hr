import type {
	User,
	UserRole,
	CreateUserInput,
	UpdateUserInput,
	UserFilters
} from '../types/user.types';

import UserEndpoints from '../api/users.endpoints';
import { accessService } from '@/hr/modules/admin/access/services/access.service';


export class UserSettingsStore {
	// --- Reactive State ---
	users = $state<User[]>([]);
	selectedUser = $state<User | null>(null);
	isEditing = $state(false);
	isLoading = $state(false);
	error = $state<string | null>(null);

	// Filters
	filters = $state<UserFilters>({
		search: '',
		role: [],
		orgUnit: [],
		isActive: null
	});

	// Pagination
	currentPage = $state(1);
	perPage = $state(8);

	// --- Derived State ---
	filteredUsers = $derived.by(() => {
		// Note: The backend now handles filtering, but we keep this for local refinement if needed
		return this.users.sort((a, b) => {
			const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0;
			const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0;
			return dateB - dateA;
		});
	});

	paginatedUsers = $derived.by(() => {
		return this.filteredUsers; // Backend already paginates, but we'll adapt depending on API response structure
	});

	totalCount = $state(0);
	totalPages = $derived(Math.ceil(this.totalCount / this.perPage) || 1);

	activeFiltersCount = $derived(
		(this.filters.role.length > 0 ? 1 : 0) +
		(this.filters.orgUnit.length > 0 ? 1 : 0) +
		(this.filters.isActive !== null ? 1 : 0)
	);

	// Unique values for filters
	orgUnits = $derived(
		[...new Set(this.users.map(u => u.orgUnit).filter(Boolean))] as string[]
	);

	// Statistics
	stats = $derived({
		total: this.totalCount,
		active: this.users.filter(u => u.isActive).length,
		inactive: this.users.filter(u => !u.isActive).length,
		byRole: {} // Will be populated dynamically if needed
	});

	// --- Actions ---
	
	async init() {
		return this.fetchUsers();
	}

	async fetchUsers() {
		this.isLoading = true;
		this.error = null;
		try {
			const params: any = {
				page: this.currentPage,
				page_size: this.perPage,
				search: this.filters.search || undefined
			};
			const response = await UserEndpoints.users.list(params);
			
			// Map backend snake_case to frontend camelCase
			this.users = (response.results || []).map((u: any) => ({
				id: u.id,
				email: u.email,
				username: u.username,
				firstName: u.first_name,
				lastName: u.last_name,
				isActive: u.is_active,
				groups: u.groups || [],
				createdAt: u.date_joined || u.created_at
			}));
			
			this.totalCount = response.count || this.users.length;
		} catch (e: any) {
			this.error = e.message || "Erreur lors du chargement des utilisateurs";
		} finally {
			this.isLoading = false;
		}
	}

	setSearch(query: string) {
		this.filters.search = query;
		this.currentPage = 1;
		this.fetchUsers();
	}

	toggleRoleFilter(role: UserRole) {
		const current = this.filters.role;
		if (current.includes(role)) {
			this.filters.role = current.filter(r => r !== role);
		} else {
			this.filters.role = [...current, role];
		}
		this.currentPage = 1;
		this.fetchUsers();
	}

	toggleOrgUnitFilter(orgUnit: string) {
		const current = this.filters.orgUnit;
		if (current.includes(orgUnit)) {
			this.filters.orgUnit = current.filter(d => d !== orgUnit);
		} else {
			this.filters.orgUnit = [...current, orgUnit];
		}
		this.currentPage = 1;
		this.fetchUsers();
	}

	setActiveFilter(isActive: boolean | null) {
		this.filters.isActive = isActive;
		this.currentPage = 1;
		this.fetchUsers();
	}

	setPage(page: number) {
		if (page >= 1 && page <= this.totalPages) {
			this.currentPage = page;
			this.fetchUsers();
		}
	}

	setPerPage(size: number) {
		this.perPage = size;
		this.currentPage = 1;
		this.fetchUsers();
	}

	async selectUser(user: User | null) {
		this.selectedUser = user;
		this.isEditing = false;
		if (user) {
			// Reload user details to get fresh info if needed
		}
	}

	async assignGroupToUser(userId: string | number, groupSlug: string) {
		try {
			await accessService.assignGroupToUser({ user_id: String(userId), group: groupSlug });
			await this.fetchUsers();
			if (this.selectedUser?.id === userId) {
				this.selectedUser.groups = [...this.selectedUser.groups, groupSlug];
			}
		} catch (e: any) {
			this.error = e.message;
		}
	}

	async revokeGroupFromUser(userId: string | number, groupSlug: string) {
		try {
			await accessService.revokeGroupFromUser({ user_id: String(userId), group: groupSlug });
			await this.fetchUsers();
			if (this.selectedUser?.id === userId) {
				this.selectedUser.groups = this.selectedUser.groups.filter(g => g !== groupSlug);
			}
		} catch (e: any) {
			this.error = e.message;
		}
	}

	// Legacy Mocks to keep Typescript happy for now
	resetFilters() {
		this.filters = { search: '', role: [], orgUnit: [], isActive: null };
		this.currentPage = 1;
		this.fetchUsers();
	}
	toggleUserActive(id: string | number) {}
	updateUser(id: string | number, data: UpdateUserInput) {}
	createUser(data: CreateUserInput) {}
	deleteUser(id: string | number) {}
}


export const userSettingsStore = new UserSettingsStore();

