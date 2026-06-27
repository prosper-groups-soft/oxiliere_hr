import type { LeaveRequest, LeavesFilters } from '../types/types';


/**
 * Store — UI state + métadonnées de pagination.
 * Les données (requests) sont gérées par TanStack Query.
 */
class LeavesStore {
	// --- UI State (filtres, tri, pagination) ---
	filters = $state<LeavesFilters>({
		search: '',
		orgUnit: [],
		type: [],
		status: [],
	});

	sortBy = $state<string>('createdAt');
	sortOrder = $state<'asc' | 'desc'>('desc');

	currentPage = $state(1);
	perPage = $state(10);

	// Infos de pagination (synchronisées depuis TanStack Query)
	totalCount = $state(0);

	// --- Derived ---

	get totalPages(): number {
		return Math.ceil(this.totalCount / this.perPage) || 1;
	}

	get activeFiltersCount(): number {
		let count = this.filters.orgUnit.length + this.filters.type.length + this.filters.status.length;
		if (this.filters.search) count += 1;
		return count;
	}

	/** Extract unique org units from request data */
	getOrgUnits(requests: LeaveRequest[]): string[] {
		return [...new Set(requests.map(r => r.orgUnit))];
	}


	// --- Actions ---

	setTotal(count: number) {
		this.totalCount = count;
	}

	setSearch(query: string) {
		this.filters.search = query;
		this.currentPage = 1;
	}

	toggleFilter(category: 'orgUnit' | 'type' | 'status', value: any) {
		const current = this.filters[category] as any[];
		if (current.includes(value)) {
			this.filters[category] = current.filter(v => v !== value) as any;
		} else {
			this.filters[category] = [...current, value] as any;
		}
		this.currentPage = 1;
	}

	resetFilters() {
		this.filters.search = '';
		this.filters.orgUnit = [];
		this.filters.type = [];
		this.filters.status = [];
		this.currentPage = 1;
	}

	setSort(field: string) {
		this.sortBy = field;
	}

	toggleSortOrder() {
		this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
	}

	setPage(page: number) {
		if (page >= 1 && page <= this.totalPages) {
			this.currentPage = page;
		}
	}

	setPerPage(count: number) {
		this.perPage = count;
		this.currentPage = 1;
	}

	nextPage() {
		if (this.currentPage < this.totalPages) this.currentPage++;
	}

	prevPage() {
		if (this.currentPage > 1) this.currentPage--;
	}
}


export const leavesStore = new LeavesStore();
