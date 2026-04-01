import type { JobPosition, SeniorityLevel } from '../types/types';
import { jobsStore } from './jobs.svelte';

export class PositionsStore {
	// --- Reactive State (Runes) ---
	searchQuery = $state('');
	sortBy = $state('name');
	sortOrder = $state<'asc' | 'desc'>('asc');
	filters = $state<{
		department: string[];
		seniority: SeniorityLevel[];
	}>({
		department: [],
		seniority: []
	});
	// --- Derived State ---

	/**
	 * Main processing pipeline: Filters -> Sorts (Dynamic Direction)
	 */
	filteredPositions = $derived.by(() => {
		// 1. Filtering Logic
		let result = jobsStore.positions.filter((pos) => {
			const searchLower = this.searchQuery.toLowerCase();
			const matchesSearch = pos.title.toLowerCase().includes(searchLower);

			const matchesDept =
				this.filters.department.length === 0 || this.filters.department.includes(pos.departmentId);
			const matchesSeniority =
				this.filters.seniority.length === 0 || this.filters.seniority.includes(pos.seniority);

			return matchesSearch && matchesDept && matchesSeniority;
		});

		// 2. Sorting Logic with Directional multiplier
		return [...result].sort((a, b) => {
			let comparison = 0;

			if (this.sortBy === 'name') {
				comparison = a.title.localeCompare(b.title);
			} else if (this.sortBy === 'department') {
				const deptA = jobsStore.getDepartmentById(a.departmentId)?.name || '';
				const deptB = jobsStore.getDepartmentById(b.departmentId)?.name || '';
				comparison = deptA.localeCompare(deptB);
			} else if (this.sortBy === 'seniority') {
				const levelA = jobsStore.seniorityLevels.find((l) => l.name === a.seniority);
				const levelB = jobsStore.seniorityLevels.find((l) => l.name === b.seniority);
				comparison = (levelA?.rank || 0) - (levelB?.rank || 0);
			}

			// If desc, multiply result by -1 to flip order
			return this.sortOrder === 'asc' ? comparison : -comparison;
		});
	});

	totalCount = $derived(this.filteredPositions.length);
	activeFiltersCount = $derived(
		this.filters.department.length + this.filters.seniority.length + (this.searchQuery ? 1 : 0)
	);

	// --- Actions ---

	/**
	 * Toggles the sort direction between 'asc' and 'desc'
	 */
	toggleSortOrder() {
		this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
	}

	setSort(criterion: string) {
		this.sortBy = criterion;
	}

	setSearchQuery(query: string) {
		this.searchQuery = query;
	}

	toggleFilter(category: keyof typeof this.filters, value: string | SeniorityLevel) {
		const current = this.filters[category];
		if (current.includes(value as any)) {
			this.filters[category] = current.filter((v) => v !== value) as any;
		} else {
			this.filters[category] = [...current, value as any];
		}
	}

	resetFilters() {
		this.filters = { department: [], seniority: [] };
		this.searchQuery = '';
		this.sortBy = 'name';
		this.sortOrder = 'asc';
	}
}

export const positionsStore = new PositionsStore();
