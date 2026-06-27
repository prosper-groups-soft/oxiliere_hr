import type { 
	SeniorityLevel 
} from '../types/types';
import { jobsStore } from './jobs.svelte';


export class PositionsStore {
	// --- Reactive State (Runes) ---
	searchQuery = $state('');
	sortBy = $state('name');
	sortOrder = $state<'asc' | 'desc'>('asc');
	filters = $state<{
		orgUnit: string[];
		seniority: SeniorityLevel[];
	}>({
		orgUnit: [],
		seniority: []
	});
	// --- Derived State ---

	/**
	 * Main processing pipeline: Filters -> Sorts (Dynamic Direction)
	 */
	filteredPositions = $derived.by(() => {
		// 1. Filtering Logic - using backend field names
		let result = jobsStore.positions.filter((pos) => {
			const searchLower = this.searchQuery.toLowerCase();
			const matchesSearch = !this.searchQuery ||
				pos.name.toLowerCase().includes(searchLower) ||
				pos.job_family?.name?.toLowerCase().includes(searchLower) ||
				pos.org_unit?.name?.toLowerCase().includes(searchLower) ||
				pos.skills?.some(s => s.name.toLowerCase().includes(searchLower)) ||
				pos.requirements?.some(r => r.toLowerCase().includes(searchLower)) ||
				// Search in seniority levels
				pos.seniority_levels?.some(sl => 
					sl.seniority_level.level.toLowerCase().includes(searchLower) ||
					sl.seniority_level.name?.toLowerCase().includes(searchLower)
				);

			const matchesOrgUnit =
				this.filters.orgUnit.length === 0 || this.filters.orgUnit.includes(pos.org_unit?.id || '');
			
			// Updated seniority filtering - check if position has any of the selected seniority levels
			const matchesSeniority =
				this.filters.seniority.length === 0 || 
				(pos.seniority_levels && pos.seniority_levels.length > 0
					? this.filters.seniority.some(selectedLevel =>
						pos.seniority_levels!.some(sl => sl.seniority_level.level === selectedLevel)
					)
					: this.filters.seniority.includes((pos as any).level as SeniorityLevel) // Fallback for old data
				);

			return matchesSearch && matchesOrgUnit && matchesSeniority;
		});

		// 2. Sorting Logic with Directional multiplier
		return [...result].sort((a, b) => {
			let comparison = 0;

			if (this.sortBy === 'name') {
				comparison = a.name.localeCompare(b.name);
			} else if (this.sortBy === 'orgUnit') {
				const orgUnitA = jobsStore.getOrgUnitById(a.org_unit?.id || '')?.name || '';
				const orgUnitB = jobsStore.getOrgUnitById(b.org_unit?.id || '')?.name || '';
				comparison = orgUnitA.localeCompare(orgUnitB);
			} else if (this.sortBy === 'seniority') {
				// For multi-level positions, use the minimum rank (most junior level)
				const getMinRank = (pos: any) => {
					if (pos.seniority_levels && pos.seniority_levels.length > 0) {
						return Math.min(...pos.seniority_levels.map((sl: any) => sl.rank || 0));
					}
					// Fallback for old data
					const level = jobsStore.seniorityLevels.find((l) => l.level === pos.level);
					return level?.rank || 0;
				};
				comparison = getMinRank(a) - getMinRank(b);
			}

			// If desc, multiply result by -1 to flip order
			return this.sortOrder === 'asc' ? comparison : -comparison;
		});
	});

	totalCount = $derived(this.filteredPositions.length);
	activeFiltersCount = $derived(
		this.filters.orgUnit.length + this.filters.seniority.length + (this.searchQuery ? 1 : 0)
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
		this.filters = { orgUnit: [], seniority: [] };
		this.searchQuery = '';
		this.sortBy = 'name';
		this.sortOrder = 'asc';
	}
}


export const positionsStore = new PositionsStore();

