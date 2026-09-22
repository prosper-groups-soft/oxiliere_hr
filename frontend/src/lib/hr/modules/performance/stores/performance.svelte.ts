import type { ReviewStatus } from '../types/types';


/**
 * Store des performances — UI state uniquement.
 * Toutes les données (reviews, totalCount, totalPages) sont gérées
 * par le cache TanStack Query.
 * Stocké en mémoire et persistant entre les navigations.
 */
class PerformanceStore {
	filters = $state<{ search: string; status: ReviewStatus | '' }>({
		search: '',
		status: '',
	});

	currentPage = $state(1);
	perPage = $state(10);

	get activeFiltersCount(): number {
		let count = 0;
		if (this.filters.search) count += 1;
		if (this.filters.status) count += 1;
		return count;
	}

	setSearch(query: string) {
		this.filters.search = query;
		this.currentPage = 1;
	}

	setStatusFilter(status: ReviewStatus | '') {
		this.filters.status = status;
		this.currentPage = 1;
	}

	resetFilters() {
		this.filters = { search: '', status: '' };
		this.currentPage = 1;
	}

	setPage(page: number) {
		if (page >= 1) this.currentPage = page;
	}

	setPerPage(count: number) {
		this.perPage = count;
		this.currentPage = 1;
	}

	nextPage() {
		this.currentPage++;
	}

	prevPage() {
		if (this.currentPage > 1) this.currentPage--;
	}
}


export const performanceStore = new PerformanceStore();

