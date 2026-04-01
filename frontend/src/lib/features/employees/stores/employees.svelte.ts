import type { Employee, EmployeeFilters } from '../types/types';

// Mock Data
const MOCK_EMPLOYEES: Employee[] = [
	{
		id: 1,
		name: 'Alice Dupont',
		jobTitle: 'Senior Frontend Engineer',
		department: 'Engineering',
		status: 'Actif',
		location: 'Paris HQ',
		contractType: 'Permanent',
		joinDate: '2021-03-15',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 2,
		name: 'Bob Martin',
		jobTitle: 'Product Manager',
		department: 'Product',
		status: 'Actif',
		location: 'Remote',
		contractType: 'Permanent',
		joinDate: '2022-06-01',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 3,
		name: 'Charlie Durand',
		jobTitle: 'Sales Representative',
		department: 'Sales',
		status: 'En intégration',
		location: 'Lyon Office',
		contractType: 'Fixed-term',
		joinDate: '2024-02-10',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 4,
		name: 'David Leroy',
		jobTitle: 'Marketing Specialist',
		department: 'Marketing',
		status: 'Actif',
		location: 'Paris HQ',
		contractType: 'Permanent',
		joinDate: '2023-11-20',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 5,
		name: 'Eve Moreau',
		jobTitle: 'HR Coordinator',
		department: 'Human Resources',
		status: 'Suspendu',
		location: 'Bordeaux Hub',
		contractType: 'Permanent',
		joinDate: '2022-09-12',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 6,
		name: 'Frank Petit',
		jobTitle: 'Financial Analyst',
		department: 'Finance',
		status: 'Terminé',
		location: 'Paris HQ',
		contractType: 'Freelance',
		joinDate: '2020-05-15',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 7,
		name: 'Grace Thomas',
		jobTitle: 'Backend Developer',
		department: 'Engineering',
		status: 'Actif',
		location: 'Remote',
		contractType: 'Permanent',
		joinDate: '2023-01-10',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 8,
		name: 'Hugo Richard',
		jobTitle: 'UX Designer',
		department: 'Product',
		status: 'Actif',
		location: 'Lyon Office',
		contractType: 'Apprenticeship',
		joinDate: '2024-01-05',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 9,
		name: 'Ivy Bernard',
		jobTitle: 'DevOps Engineer',
		department: 'Engineering',
		status: 'Actif',
		location: 'Paris HQ',
		contractType: 'Permanent',
		joinDate: '2021-12-01',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 10,
		name: 'Jack Simon',
		jobTitle: 'Account Manager',
		department: 'Sales',
		status: 'Actif',
		location: 'Bordeaux Hub',
		contractType: 'Permanent',
		joinDate: '2022-04-18',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 11,
		name: 'Kelly Rose',
		jobTitle: 'Content Writer',
		department: 'Marketing',
		status: 'Actif',
		location: 'Remote',
		contractType: 'Internship',
		joinDate: '2024-01-15',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	},
	{
		id: 12,
		name: 'Leo Michel',
		jobTitle: 'Tech Lead',
		department: 'Engineering',
		status: 'Actif',
		location: 'Lyon Office',
		contractType: 'Permanent',
		joinDate: '2019-10-25',
		phone: '0895105540',
		email: 'kibangula.prosper@oxiliere.com',
		avatarUrl: '',
		role: 'Software Engineer'
	}
];

export class EmployeeStore {
	// --- Reactive State (Runes) ---
	employees = $state(MOCK_EMPLOYEES);
	searchQuery = $state('');
	sortBy = $state('name');
	sortOrder = $state<'asc' | 'desc'>('asc'); // New: Handles sort direction
	filters = $state<EmployeeFilters>({
		department: [],
		status: [],
		location: []
	});
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
	 * Main processing pipeline: Filters -> Sorts (Dynamic Direction)
	 */
	filteredEmployees = $derived.by(() => {
		// 1. Filtering Logic
		let result = MOCK_EMPLOYEES.filter((emp) => {
			const searchLower = this.searchQuery.toLowerCase();
			const matchesSearch =
				emp.name.toLowerCase().includes(searchLower) ||
				emp.jobTitle.toLowerCase().includes(searchLower) ||
				emp.contractType.toLowerCase().includes(searchLower);

			const matchesDept =
				this.filters.department.length === 0 || this.filters.department.includes(emp.department);
			const matchesStatus =
				this.filters.status.length === 0 || this.filters.status.includes(emp.status);
			const matchesLoc =
				this.filters.location.length === 0 || this.filters.location.includes(emp.location);

			return matchesSearch && matchesDept && matchesStatus && matchesLoc;
		});

		// 2. Sorting Logic with Directional multiplier
		return [...result].sort((a, b) => {
			let comparison = 0;

			if (this.sortBy === 'name') {
				comparison = a.name.localeCompare(b.name);
			} else if (this.sortBy === 'joinDate') {
				comparison = new Date(a.joinDate).getTime() - new Date(b.joinDate).getTime();
			} else if (this.sortBy === 'status') {
				comparison = a.status.localeCompare(b.status);
			}

			// If desc, multiply result by -1 to flip order
			return this.sortOrder === 'asc' ? comparison : -comparison;
		});
	});

	paginatedEmployees = $derived.by(() => {
		return this.filteredEmployees.slice(
			(this.currentPage - 1) * this.perPage,
			this.currentPage * this.perPage
		);
	});

	totalCount = $derived(this.filteredEmployees.length);
	totalPages = $derived(Math.ceil(this.totalCount / this.perPage) || 1);
	activeFiltersCount = $derived(
		this.filters.department.length + this.filters.status.length + this.filters.location.length
	);

	// --- Actions ---

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
		const current = this.filters[category];
		if (current.includes(value)) {
			this.filters[category] = current.filter((v) => v !== value);
		} else {
			this.filters[category] = [...current, value];
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
		this.filters = { department: [], status: [], location: [] };
		this.searchQuery = '';
		this.sortBy = 'name';
		this.sortOrder = 'asc'; // Reset to default ascending
		this.currentPage = 1;
	}

	getById(id: string | number): Employee | undefined {
		const numId = typeof id === 'string' ? parseInt(id, 10) : id;
		return this.employees.find((emp) => emp.id === numId);
	}

	updateEmployee(id: string | number, data: Partial<Omit<Employee, 'id'>>) {
		const numId = typeof id === 'string' ? parseInt(id, 10) : id;
		const index = this.employees.findIndex((emp) => emp.id === numId);
		if (index !== -1) {
			this.employees[index] = { ...this.employees[index], ...data };
			// Trigger reactivity by reassigning the array
			this.employees = [...this.employees];
		}
	}
}

export const employeeStore = new EmployeeStore();
