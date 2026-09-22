import type { VacancyPriority, VacancyStatus } from "../types/types";


interface VacancyFilters {
	priority: VacancyPriority | null;
	status: VacancyStatus | null;
}


class VacanciesStore {
	// Search state
	searchQuery = $state("");

	// Filter state (single selection like transitions)
	filters = $state<VacancyFilters>({
		priority: null,
		status: null
	});

	// Pagination state
	page = $state(1);
	perPage = $state(8);

	// Derived values
	activeFiltersCount = $derived(
		(this.searchQuery ? 1 : 0) +
		(this.filters.priority ? 1 : 0) +
		(this.filters.status ? 1 : 0)
	);

	// Check if any filter is active (including search)
	hasActiveFilters = $derived(
		this.searchQuery !== "" ||
		this.filters.priority !== null ||
		this.filters.status !== null
	);

	setSearchQuery(query: string) {
		this.searchQuery = query;
		this.page = 1; // Reset to first page on search change
	}

	setPriority(priority: VacancyPriority | null) {
		this.filters.priority = priority;
		this.page = 1;
	}

	setStatus(status: VacancyStatus | null) {
		this.filters.status = status;
		this.page = 1;
	}

	clearPriority() {
		this.filters.priority = null;
		this.page = 1;
	}

	clearStatus() {
		this.filters.status = null;
		this.page = 1;
	}

	clearSearch() {
		this.searchQuery = "";
		this.page = 1;
	}

	resetFilters() {
		this.filters = { priority: null, status: null };
		this.searchQuery = "";
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
		if (this.page > 1) {
			this.page--;
		}
	}
}


export const vacanciesStore = new VacanciesStore();
