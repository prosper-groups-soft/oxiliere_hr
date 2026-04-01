import type {
	LeaveRequest, LeaveBalance, LeavePolicy, LeaveType, LeaveStatus, LeavesFilters
} from '../types/types';
import { employeeStore } from '@/features/employees/stores/employees.svelte';


// Mock Data Generators 

function generateMockBalances(): LeaveBalance[] {
	const employees = employeeStore.employees;
	const balances: LeaveBalance[] = [];

	for (const emp of employees) {
		balances.push(
			{ employeeId: emp.id, type: 'annual', allocated: 22, taken: 8, remaining: 14, expiringDays: 4, expiryDate: '2026-03-31' },
			{ employeeId: emp.id, type: 'sick', allocated: 12, taken: 2, remaining: 10 },
			{ employeeId: emp.id, type: 'circumstantial', allocated: 5, taken: 1, remaining: 4 },
			{ employeeId: emp.id, type: 'unpaid', allocated: 0, taken: 0, remaining: 0 },
		);
	}
	return balances;
}

function generateMockRequests(): LeaveRequest[] {
	const employees = employeeStore.employees;
	if (employees.length === 0) return [];

	const types: LeaveType[] = ['annual', 'sick', 'circumstantial', 'unpaid'];
	const statuses: LeaveStatus[] = ['pending', 'approved', 'rejected'];
	const reasons = [
		'Vacances en famille',
		'Rendez-vous médical',
		'Mariage d\'un proche',
		'Déménagement',
		'Convenance personnelle',
		'Grippe saisonnière',
		'Examen universitaire',
		'Événement familial',
	];

	return [
		{
			id: 'lr-001', employeeId: employees[0]?.id, employeeName: employees[0]?.name ?? 'Employé 1',
			department: employees[0]?.department ?? 'Ingénierie', type: 'annual', status: 'pending',
			startDate: '2026-04-07', endDate: '2026-04-11', days: 5, reason: reasons[0],
			createdAt: '2026-03-15',
		},
		{
			id: 'lr-002', employeeId: employees[1]?.id, employeeName: employees[1]?.name ?? 'Employé 2',
			department: employees[1]?.department ?? 'Produit', type: 'sick', status: 'approved',
			startDate: '2026-03-10', endDate: '2026-03-11', days: 2, reason: reasons[5],
			approver: 'Marie Dupont', createdAt: '2026-03-09', respondedAt: '2026-03-09',
		},
		{
			id: 'lr-003', employeeId: employees[2]?.id, employeeName: employees[2]?.name ?? 'Employé 3',
			department: employees[2]?.department ?? 'Vente', type: 'circumstantial', status: 'approved',
			startDate: '2026-03-20', endDate: '2026-03-21', days: 2, reason: reasons[2],
			approver: 'Jean Martin', createdAt: '2026-03-14', respondedAt: '2026-03-15',
		},
		{
			id: 'lr-004', employeeId: employees[3]?.id ?? 4, employeeName: employees[3]?.name ?? 'Employé 4',
			department: employees[3]?.department ?? 'Ingénierie', type: 'annual', status: 'rejected',
			startDate: '2026-04-14', endDate: '2026-04-18', days: 5, reason: reasons[4],
			approver: 'Sophie Bernard', createdAt: '2026-03-12', respondedAt: '2026-03-13',
		},
		{
			id: 'lr-005', employeeId: employees[0]?.id, employeeName: employees[0]?.name ?? 'Employé 1',
			department: employees[0]?.department ?? 'Ingénierie', type: 'annual', status: 'approved',
			startDate: '2026-02-17', endDate: '2026-02-19', days: 3, reason: reasons[3],
			approver: 'Marie Dupont', createdAt: '2026-02-10', respondedAt: '2026-02-11',
		},
		{
			id: 'lr-006', employeeId: employees[4]?.id ?? 5, employeeName: employees[4]?.name ?? 'Employé 5',
			department: employees[4]?.department ?? 'Produit', type: 'sick', status: 'pending',
			startDate: '2026-03-24', endDate: '2026-03-25', days: 2, reason: reasons[1],
			createdAt: '2026-03-20',
		},
		{
			id: 'lr-007', employeeId: employees[5]?.id ?? 6, employeeName: employees[5]?.name ?? 'Employé 6',
			department: employees[5]?.department ?? 'Vente', type: 'unpaid', status: 'pending',
			startDate: '2026-04-21', endDate: '2026-04-25', days: 5, reason: reasons[6],
			createdAt: '2026-03-18',
		},
		{
			id: 'lr-008', employeeId: employees[1]?.id, employeeName: employees[1]?.name ?? 'Employé 2',
			department: employees[1]?.department ?? 'Produit', type: 'annual', status: 'approved',
			startDate: '2026-05-05', endDate: '2026-05-09', days: 5, reason: reasons[7],
			approver: 'Marie Dupont', createdAt: '2026-03-01', respondedAt: '2026-03-02',
		},
		{
			id: 'lr-009', employeeId: employees[2]?.id, employeeName: employees[2]?.name ?? 'Employé 3',
			department: employees[2]?.department ?? 'Vente', type: 'circumstantial', status: 'pending',
			startDate: '2026-04-02', endDate: '2026-04-02', days: 1, reason: reasons[7],
			createdAt: '2026-03-19',
		},
		{
			id: 'lr-010', employeeId: employees[6]?.id ?? 7, employeeName: employees[6]?.name ?? 'Employé 7',
			department: employees[6]?.department ?? 'Ingénierie', type: 'annual', status: 'approved',
			startDate: '2026-03-31', endDate: '2026-04-04', days: 5, reason: reasons[0],
			approver: 'Jean Martin', createdAt: '2026-03-10', respondedAt: '2026-03-11',
		},
		{
			id: 'lr-011', employeeId: employees[7]?.id ?? 8, employeeName: employees[7]?.name ?? 'Employé 8',
			department: employees[7]?.department ?? 'Produit', type: 'sick', status: 'approved',
			startDate: '2026-03-17', endDate: '2026-03-18', days: 2, reason: reasons[5],
			approver: 'Sophie Bernard', createdAt: '2026-03-16', respondedAt: '2026-03-16',
		},
		{
			id: 'lr-012', employeeId: employees[3]?.id ?? 4, employeeName: employees[3]?.name ?? 'Employé 4',
			department: employees[3]?.department ?? 'Ingénierie', type: 'annual', status: 'pending',
			startDate: '2026-05-12', endDate: '2026-05-16', days: 5, reason: reasons[4],
			createdAt: '2026-03-20',
		},
	];
}

function generateMockPolicies(): LeavePolicy[] {
	return [
		{
			id: 'lp-001', name: 'Congé annuel', type: 'annual', daysPerYear: 22,
			seniorityRules: [
				{ minYears: 5, maxYears: 10, extraDays: 2 },
				{ minYears: 10, maxYears: 15, extraDays: 4 },
				{ minYears: 15, extraDays: 6 },
			],
			carryOverDays: 5, requiresApproval: true, requiresJustification: false,
			description: 'Congé annuel payé selon la législation en vigueur.',
		},
		{
			id: 'lp-002', name: 'Congé maladie', type: 'sick', daysPerYear: 12,
			seniorityRules: [], carryOverDays: 0,
			requiresApproval: false, requiresJustification: true,
			description: 'Congé pour raison médicale. Justificatif requis au-delà de 2 jours.',
		},
		{
			id: 'lp-003', name: 'Congé circonstanciel', type: 'circumstantial', daysPerYear: 5,
			seniorityRules: [], carryOverDays: 0,
			requiresApproval: true, requiresJustification: true,
			description: 'Mariage, naissance, décès d\'un proche, déménagement.',
		},
	];
}


// Store 

class LeavesStore {
	requests = $state<LeaveRequest[]>([]);
	balances = $state<LeaveBalance[]>([]);
	policies = $state<LeavePolicy[]>([]);

	filters = $state<LeavesFilters>({
		search: '',
		department: [],
		type: [],
		status: [],
	});

	sortBy = $state<string>('createdAt');
	sortOrder = $state<'asc' | 'desc'>('desc');

	currentPage = $state(1);
	perPage = $state(10);

	constructor() {
		this.requests = generateMockRequests();
		this.balances = generateMockBalances();
		this.policies = generateMockPolicies();
	}


	// Derived 

	get pendingCount(): number {
		return this.requests.filter(r => r.status === 'pending').length;
	}

	get activeFiltersCount(): number {
		return this.filters.department.length + this.filters.type.length + this.filters.status.length;
	}

	get filteredRequests(): LeaveRequest[] {
		let results = [...this.requests];

		// Search
		if (this.filters.search) {
			const q = this.filters.search.toLowerCase();
			results = results.filter(r =>
				r.employeeName.toLowerCase().includes(q) ||
				r.department.toLowerCase().includes(q)
			);
		}

		// Department filter
		if (this.filters.department.length > 0) {
			results = results.filter(r => this.filters.department.includes(r.department));
		}

		// Type filter
		if (this.filters.type.length > 0) {
			results = results.filter(r => this.filters.type.includes(r.type));
		}

		// Status filter
		if (this.filters.status.length > 0) {
			results = results.filter(r => this.filters.status.includes(r.status));
		}

		// Sort
		results.sort((a, b) => {
			let cmp = 0;
			switch (this.sortBy) {
				case 'name': cmp = a.employeeName.localeCompare(b.employeeName); break;
				case 'department': cmp = a.department.localeCompare(b.department); break;
				case 'createdAt': cmp = new Date(a.createdAt).getTime() - new Date(b.createdAt).getTime(); break;
				case 'startDate': cmp = new Date(a.startDate).getTime() - new Date(b.startDate).getTime(); break;
				case 'days': cmp = a.days - b.days; break;
				default: cmp = 0;
			}
			return this.sortOrder === 'asc' ? cmp : -cmp;
		});

		return results;
	}

	get totalCount(): number {
		return this.filteredRequests.length;
	}

	get totalPages(): number {
		return Math.ceil(this.totalCount / this.perPage) || 1;
	}

	get paginatedRequests(): LeaveRequest[] {
		const start = (this.currentPage - 1) * this.perPage;
		const end = start + this.perPage;
		return this.filteredRequests.slice(start, end);
	}

	/**
	 * Get balances for a specific employee (default: first employee for demo)
	 */
	getBalancesForEmployee(employeeId?: number): LeaveBalance[] {
		const id = employeeId ?? this.balances[0]?.employeeId;
		return this.balances.filter(b => b.employeeId === id);
	}

	/**
	 * Get all unique departments from requests
	 */
	get departments(): string[] {
		return [...new Set(this.requests.map(r => r.department))];
	}


	// Actions

	setSearch(query: string) {
		this.filters.search = query;
		this.currentPage = 1;
	}

	toggleFilter(category: 'department' | 'type' | 'status', value: any) {
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
		this.filters.department = [];
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

	approveRequest(id: string, approver: string = 'Marie Dupont') {
		const req = this.requests.find(r => r.id === id);
		if (req && req.status === 'pending') {
			req.status = 'approved';
			req.approver = approver;
			req.respondedAt = new Date().toISOString().split('T')[0];
		}
	}

	rejectRequest(id: string, approver: string = 'Marie Dupont') {
		const req = this.requests.find(r => r.id === id);
		if (req && req.status === 'pending') {
			req.status = 'rejected';
			req.approver = approver;
			req.respondedAt = new Date().toISOString().split('T')[0];
		}
	}

	addRequest(data: Omit<LeaveRequest, 'id' | 'createdAt' | 'status'>) {
		const newReq: LeaveRequest = {
			...data,
			id: `lr-${Date.now()}`,
			status: 'pending',
			createdAt: new Date().toISOString().split('T')[0],
		};
		this.requests = [newReq, ...this.requests];
	}
}


export const leavesStore = new LeavesStore();
