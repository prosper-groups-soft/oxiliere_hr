import type { TransitionType } from '../types/types';


export class TransitionsStore {
	// --- Reactive State (Runes) ---
	searchQuery = $state('');
	filters = $state<{
		transitionType: TransitionType[];
	}>({
		transitionType: []
	});

	// Pagination state
	page = $state(1);
	perPage = $state(8);

	// --- Derived State ---
	activeFiltersCount = $derived(
		this.filters.transitionType.length + (this.searchQuery ? 1 : 0)
	);

	// First selected transition type (for API filter)
	firstTransitionType = $derived(
		this.filters.transitionType[0] || null
	);

	// --- Actions ---
	setSearchQuery(query: string) {
		this.searchQuery = query;
		this.page = 1; // Reset to first page on search
	}

	toggleTransitionType(type: TransitionType) {
		const current = this.filters.transitionType;
		if (current.includes(type)) {
			this.filters.transitionType = current.filter((t) => t !== type);
		} else {
			this.filters.transitionType = [...current, type];
		}
		this.page = 1; // Reset to first page on filter change
	}

	setTransitionType(type: TransitionType) {
		// Single type selection - replace any existing selection
		this.filters.transitionType = [type];
		this.page = 1;
	}

	clearTransitionType() {
		this.filters.transitionType = [];
		this.page = 1;
	}

	setPage(page: number) {
		this.page = page;
	}

	setPerPage(size: number) {
		this.perPage = size;
		this.page = 1;
	}

	nextPage() {
		this.page++;
	}

	prevPage() {
		this.page = Math.max(1, this.page - 1);
	}

	resetFilters() {
		this.filters = { transitionType: [] };
		this.searchQuery = '';
		this.page = 1;
	}
}


// Singleton instance
export const transitionsStore = new TransitionsStore();
