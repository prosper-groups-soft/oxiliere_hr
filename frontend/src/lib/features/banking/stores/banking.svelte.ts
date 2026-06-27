import type { BankAccount, BankInstitution, BankingFilters } from '../types/types';
import { DEFAULT_PAGE_SIZE } from '@/constants/ui/pagination';


export class BankingStore {
	// --- UI State (filters only — data is managed by TanStack Query) ---
	filters = $state<BankingFilters>({
		search: '',
		status: [],
		currency: [],
		institutionId: []
	});

	institutionFilters = $state({
		search: '',
		type: [] as ('bank' | 'mobile_money')[],
		isActive: null as boolean | null
	});

	// --- Data (populated from TanStack Query results) ---
	accounts = $state<BankAccount[]>([]);
	institutions = $state<BankInstitution[]>([]);

	// --- Pagination (server-side) ---
	currentPage = $state(1);
	accountsPerPage = $state(DEFAULT_PAGE_SIZE);
	serverTotalCount = $state(0);
	serverTotalPages = $state(1);

	// --- Sorting (server-side) ---
	sortBy = $state('created_at');
	sortOrder = $state<'asc' | 'desc'>('desc');

	// --- Derived ---
	activeFiltersCount = $derived(
		(this.filters.search ? 1 : 0) + this.filters.status.length + this.filters.currency.length + this.filters.institutionId.length
	);

	activeInstitutionFiltersCount = $derived(this.institutionFilters.type.length + (this.institutionFilters.isActive !== null ? 1 : 0));

	// Les données sont filtrées et triées par le backend
	filteredAccounts = $derived(this.accounts);

	totalCount = $derived(this.serverTotalCount);
	totalPages = $derived(this.serverTotalPages);

	// --- Data sync helpers (called by page components) ---
	updateAccounts(accounts: BankAccount[]) {
		this.accounts = accounts;
	}

	updateInstitutions(institutions: BankInstitution[]) {
		this.institutions = institutions;
	}

	setServerAccounts(accounts: BankAccount[], count: number, pages: number) {
		this.accounts = accounts;
		this.serverTotalCount = count;
		this.serverTotalPages = pages;
	}

	// --- Pagination actions ---
	setPage(page: number) {
		if (page >= 1 && page <= this.totalPages) {
			this.currentPage = page;
		}
	}

	setAccountsPerPage(val: number) {
		this.accountsPerPage = val;
		this.currentPage = 1;
	}

	nextPage() {
		if (this.currentPage < this.totalPages) this.currentPage++;
	}

	prevPage() {
		if (this.currentPage > 1) this.currentPage--;
	}

	// --- Sort actions ---
	setSort(criterion: string) {
		this.sortBy = criterion;
		this.currentPage = 1;
	}

	toggleSortOrder() {
		this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
		this.currentPage = 1;
	}

	// --- Filter actions ---
	getInstitutionById(id: string): BankInstitution | undefined {
		return this.institutions.find(i => i.id === id);
	}

	toggleFilter(category: keyof BankingFilters, value: string) {
		const current = this.filters[category] as string[];
		if (current.includes(value)) {
			this.filters[category] = current.filter((v) => v !== value) as any;
		} else {
			this.filters[category] = [...current, value] as any;
		}
		this.currentPage = 1;
	}

	toggleInstitutionType(type: 'bank' | 'mobile_money') {
		if (this.institutionFilters.type.includes(type)) {
			this.institutionFilters.type = this.institutionFilters.type.filter(t => t !== type);
		} else {
			this.institutionFilters.type = [...this.institutionFilters.type, type];
		}
	}

	resetFilters() {
		this.filters = {
			search: '',
			status: [],
			currency: [],
			institutionId: []
		};
		this.currentPage = 1;
		this.sortBy = 'created_at';
		this.sortOrder = 'desc';
	}

	resetInstitutionFilters() {
		this.institutionFilters = {
			search: '',
			type: [],
			isActive: null
		};
	}
}


export const bankingStore = new BankingStore();
