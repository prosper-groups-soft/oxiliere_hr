import type { CampaignStatus, CampaignType } from '../types/types';


/**
 * Store des campagnes — UI state uniquement.
 * Les données (campagnes, totalCount, totalPages) sont gérées
 * par le cache TanStack Query.
 *
 * Stocké en mémoire et persistant entre les navigations.
 */
class CampaignStore {
	// ── État réactif ──────────────────────────────
	searchQuery = $state('');
	statusFilter = $state<CampaignStatus | ''>('');
	typeFilter = $state<CampaignType | ''>('');
	currentPage = $state(1);
	perPage = $state(10);
	isLoading = $state(false);
	error = $state<string | null>(null);

	// Métadonnées de pagination (synchronisées depuis la query TanStack)
	serverTotalCount = $state(0);
	serverTotalPages = $state(1);

	// ── Dérivés ────────────────────────────────────

	activeFiltersCount = $derived(
		(this.searchQuery ? 1 : 0) +
		(this.statusFilter ? 1 : 0) +
		(this.typeFilter ? 1 : 0)
	);

	/**
	 * Objet filters enrichi de la recherche, pour FilterChips.
	 * Les clés sont les noms de filtres, les valeurs sont des tableaux
	 * (un filtre = une seule valeur sélectionnable pour les campagnes).
	 */
	filtersWithSearch = $derived.by(() => {
		const f: Record<string, string[]> = {};
		if (this.statusFilter) f.status = [this.statusFilter];
		if (this.typeFilter) f.campaign_type = [this.typeFilter];
		if (this.searchQuery) f.search = [this.searchQuery];
		return f;
	});

	// ── Métadonnées (synchro query → store) ──────

	setMetadata(total: number, pages: number) {
		this.serverTotalCount = total;
		this.serverTotalPages = pages;
	}

	setLoading(loading: boolean) {
		this.isLoading = loading;
	}

	setError(err: string | null) {
		this.error = err;
	}

	// ── Actions ────────────────────────────────────

	setSearchQuery(query: string) {
		this.searchQuery = query;
		this.currentPage = 1;
	}

	setStatusFilter(status: CampaignStatus | '') {
		this.statusFilter = status;
		this.currentPage = 1;
	}

	setTypeFilter(type: CampaignType | '') {
		this.typeFilter = type;
		this.currentPage = 1;
	}

	resetFilters() {
		this.searchQuery = '';
		this.statusFilter = '';
		this.typeFilter = '';
		this.currentPage = 1;
	}

	setPage(page: number) {
		if (page >= 1 && page <= this.serverTotalPages) {
			this.currentPage = page;
		}
	}

	setPerPage(val: number) {
		this.perPage = val;
		this.currentPage = 1;
	}

	nextPage() {
		if (this.currentPage < this.serverTotalPages) this.currentPage++;
	}

	prevPage() {
		if (this.currentPage > 1) this.currentPage--;
	}
}


export const campaignStore = new CampaignStore();

