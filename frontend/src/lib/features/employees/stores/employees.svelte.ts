import type { Employee, EmployeeFilters, EmployeeFullProfile } from '../types/types';
import { employeesEndpoint } from '../api/employees.endpoints';


export class EmployeeStore {
	// --- Reactive State (Runes) ---
	// Données chargées depuis le backend (via queries)
	employees = $state<Employee[]>([]);
	isLoading = $state(false);
	error = $state<string | null>(null);
	current = $state<EmployeeFullProfile | null>(null);
	
	// Métadonnées de pagination du serveur
	serverTotalCount = $state(0);
	serverTotalPages = $state(1);
	
	// Filtres UI (côté client pour affichage)
	searchQuery = $state('');
	sortBy = $state('name');
	sortOrder = $state<'asc' | 'desc'>('asc');
	filters = $state<EmployeeFilters>({
		orgUnit: [],
		status: [],
		location: [],
		contractType: []
	});
	
	// Pagination côté client (pour la vue)
	currentPage = $state(1);
	perPage = $state(8);
	viewMode = $state<'list' | 'grid'>('list');

	constructor() {
		if (typeof window !== 'undefined') {
			const savedViewMode = localStorage.getItem('employeeViewMode');
			if (savedViewMode === 'list' || savedViewMode === 'grid') {
				this.viewMode = savedViewMode;
			}
		}
	}

	// --- Derived State ---

	/**
	 * Les données sont filtrées et triées par le backend.
	 * On retourne directement les données reçues du serveur.
	 */
	filteredEmployees = $derived.by(() => {
		// Le backend s'occupe déjà du filtrage et du tri
		// On retourne les données telles quelles
		return this.employees;
	});

	paginatedEmployees = $derived.by(() => {
		// Le backend pagine déjà, on retourne les données telles quelles
		return this.filteredEmployees;
	});

	totalCount = $derived(this.serverTotalCount);
	totalPages = $derived(this.serverTotalPages);
	activeFiltersCount = $derived(
		((this.filters.orgUnit as string[] | undefined)?.length || 0) + 
		((this.filters.status as string[] | undefined)?.length || 0) + 
		((this.filters.location as string[] | undefined)?.length || 0) +
		((this.filters.contractType as string[] | undefined)?.length || 0)
	);

	// --- Actions ---

	/**
	 * Met à jour les données depuis le serveur
	 * Appelé par les queries après un fetch
	 */
	setEmployees(data: Employee[], total?: number, pages?: number) {
		this.employees = data;
		if (total !== undefined) {
			this.serverTotalCount = total;
		}
		if (pages !== undefined) {
			this.serverTotalPages = pages;
		}
	}

	setLoading(loading: boolean) {
		this.isLoading = loading;
	}

	setError(err: string | null) {
		this.error = err;
	}
	
	setCurrent(employee: EmployeeFullProfile | null) {
        this.current = employee;
    }

	getById(id: string | number): Employee | undefined {
        // Si c'est une chaîne qui ressemble à un UUID, on ne parse surtout pas en Int
        if (typeof id === 'string' && id.includes('-')) {
            return this.employees.find((emp) => emp.id === id);
        }
        
        // Pour les IDs numériques classiques
        const lookFor = typeof id === 'string' ? parseInt(id, 10) : id;
        return this.employees.find((emp) => emp.id === lookFor);
    }

	async getFullProfileById(id: string): Promise<EmployeeFullProfile | null> {
		try {
			const fullProfile = await employeesEndpoint.retrieve(id);
			this.current = fullProfile;
			return fullProfile;
		} catch (error) {
			console.error('Error fetching full profile:', error);
			return null;
		}
	}

	/**
	 * Ajoute un employé à la liste (après création)
	 */
	addEmployee(employee: Employee) {
		this.employees = [employee, ...this.employees];
	}

	/**
	 * Met à jour un employé dans la liste
	 */
	updateEmployee(id: string | number, data: Partial<Employee>) {
		const numId = typeof id === 'string' ? parseInt(id, 10) : id;
		const index = this.employees.findIndex((emp) => emp.id === numId);
		if (index !== -1) {
			this.employees[index] = { ...this.employees[index], ...data };
			// Trigger reactivity by reassigning the array
			this.employees = [...this.employees];
		}
	}

	/**
	 * Supprime un employé de la liste
	 */
	removeEmployee(id: string | number) {
		const numId = typeof id === 'string' ? parseInt(id, 10) : id;
		this.employees = this.employees.filter((emp) => emp.id !== numId);
	}

	/**
	 * Toggles the sort direction between 'asc' and 'desc'
	 */
	toggleSortOrder() {
		this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
		this.currentPage = 1;
	}

	setViewMode(mode: 'list' | 'grid') {
		this.viewMode = mode;
		if (typeof window !== 'undefined') {
			localStorage.setItem('employeeViewMode', mode);
		}
	}

	toggleViewMode() {
		const nextMode = this.viewMode === 'list' ? 'grid' : 'list';
		this.setViewMode(nextMode);
	}

	setSort(criterion: string) {
		this.sortBy = criterion;
		this.currentPage = 1;
	}

	setSearchQuery(query: string) {
		this.searchQuery = query;
		this.currentPage = 1;
	}

	toggleFilter(category: keyof EmployeeFilters, value: string) {
		// Only handle array-type filters (orgUnit, status, location)
		if (category === 'gender' || category === 'marital_status' || category === 'is_active') {
			return; // Skip non-array filters for now
		}
		
		const current = (this.filters[category] as string[]) || [];
		if (current.includes(value)) {
			(this.filters as Record<string, string[]>)[category] = current.filter((v) => v !== value);
		} else {
			(this.filters as Record<string, string[]>)[category] = [...current, value];
		}
		this.currentPage = 1;
	}

	setPage(page: number) {
		if (page >= 1 && page <= this.totalPages) {
			this.currentPage = page;
		}
	}

	setPerPage(val: number) {
		this.perPage = val;
		this.currentPage = 1;
	}

	nextPage() {
		if (this.currentPage < this.totalPages) this.currentPage++;
	}

	prevPage() {
		if (this.currentPage > 1) this.currentPage--;
	}

	resetFilters() {
		this.filters = { orgUnit: [], status: [], location: [], contractType: [] };
		this.searchQuery = '';
		this.sortBy = 'name';
		this.sortOrder = 'asc';
		this.currentPage = 1;
	}
}


export const employeeStore = new EmployeeStore();

