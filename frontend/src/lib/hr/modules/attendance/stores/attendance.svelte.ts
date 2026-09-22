import { attendanceService } from '../services/attendance.service';
import { backendToWorkPolicy, workPolicyToDailyConfigs } from '../constants/attendance.helpers';
import type { AttendanceFilters, AttendanceStatus, WorkPolicy, PolicyAssignment } from '../types/types';
import type { EmploymentSchemeOut } from '../api/attendance.endpoints';


export class AttendanceStore {
	policies = $state<WorkPolicy[]>([]);
	policyAssignments = $state<PolicyAssignment[]>([]);

	// Policy search & sort (déportés dans le store pour l'en-tête)
	policySearch = $state('');
	policySortBy = $state('name');
	policySortOrder = $state<'asc' | 'desc'>('asc');
	policiesLoading = $state(false);
	policiesError = $state<string | null>(null);
	assignmentsLoading = $state(false);
	assignmentsError = $state<string | null>(null);


	filters = $state<AttendanceFilters>({
		search: '',
		orgUnit: [],
		recurrence: [],
		status: [],
		policy: [],
		dateRange: {
			from: new Date().toISOString().split('T')[0],
			to: new Date().toISOString().split('T')[0]
		}
	});

	sortBy = $state<string>('name');
	sortOrder = $state<'asc' | 'desc'>('asc');

	constructor() {
		this.loadPolicies();
	}

	async loadPolicies() {
		this.policiesLoading = true;
		this.policiesError = null;
		try {
			const results = await attendanceService.listPolicies();
			this.policies = results.map(backendToWorkPolicy);
		} catch (err) {
			this.policiesError = 'Impossible de charger les modèles de travail';
			console.warn('[AttendanceStore] Failed to load policies from API, using mocks', err);
		} finally {
			this.policiesLoading = false;
		}
	}

	async loadPoliciesWithRetry() {
		this.policiesError = null;
		await this.loadPolicies();
	}

	async loadAssignments() {
		this.assignmentsLoading = true;
		this.assignmentsError = null;
		try {
			const response = await attendanceService.listAssignments({ page: 1, page_size: 200 });
			this.policyAssignments = response.results.map(backendToPolicyAssignment);
		} catch (err) {
			this.assignmentsError = 'Impossible de charger les affectations';
			console.warn('[AttendanceStore] Failed to load assignments from API', err);
		} finally {
			this.assignmentsLoading = false;
		}
	}

	async loadAssignmentsWithRetry() {
		this.assignmentsError = null;
		await this.loadAssignments();
	}

	// --- Derived State ---

	activeFiltersCount = $derived.by(() => {
		return (this.filters.orgUnit?.length || 0) +
			(this.filters.recurrence?.length || 0) +
			(this.filters.status?.length || 0) +
			(this.filters.policy?.length || 0);
	});

	// --- Actions ---
	setSearch(query: string) {
		this.filters.search = query;
	}

	toggleFilter(category: 'orgUnit' | 'status' | 'policy' | 'recurrence', value: any) {
		const current = this.filters[category] as any[];
		if (current.includes(value)) {
			this.filters[category] = current.filter(v => v !== value) as any;
		} else {
			this.filters[category] = [...current, value] as any;
		}
	}

	resetFilters() {
		this.filters.search = '';
		this.filters.orgUnit = [];
		this.filters.recurrence = [];
		this.filters.status = [];
		this.filters.policy = [];
	}

	setSort(by: string) {
		this.sortBy = by;
	}

	toggleSortOrder() {
		this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
	}

	// Policy Actions
	async addPolicy(policy: Omit<WorkPolicy, 'id' | 'createdAt'>) {
		try {
			// Convert to backend format and create via API
			const dailyConfigs = workPolicyToDailyConfigs(policy as WorkPolicy);
			const result = await attendanceService.createPolicy({
				name: policy.name,
				description: policy.description,
				weekly_target_hours: (policy.targetHours || 40),
				daily_configs: dailyConfigs as any,
			});
			this.policies = [...this.policies, backendToWorkPolicy(result)];
		} catch (err) {
			console.error('[AttendanceStore] addPolicy error:', err);
		}
	}

	getFilteredPolicies(searchQuery: string, sortBy: string, sortOrder: 'asc' | 'desc' = 'asc') {
		const filtered = this.policies.filter(policy => {
			const search = searchQuery.toLowerCase();
			return policy.name.toLowerCase().includes(search) || policy.description?.toLowerCase().includes(search);
		});

		return filtered.sort((a, b) => {
			let comparison = 0;
			switch (sortBy) {
				case 'name':
					comparison = a.name.localeCompare(b.name);
					break;
				case 'created':
					const dateA = a.createdAt ? new Date(a.createdAt).getTime() : 0;
					const dateB = b.createdAt ? new Date(b.createdAt).getTime() : 0;
					comparison = dateA - dateB;
					break;
				case 'activeDays':
					const getActiveCount = (p: WorkPolicy) => Object.values(p.pattern).filter(day => day && !day.isOff).length;
					comparison = getActiveCount(a) - getActiveCount(b);
					break;
			}
			return sortOrder === 'asc' ? comparison : -comparison;
		});
	}

	assignPolicy(employeeId: string | number, policyId: string, startDate: string) {
		const existingIndex = this.policyAssignments.findIndex(pa => pa.employeeId === employeeId && !pa.isOverride);
		if (existingIndex !== -1) {
			this.policyAssignments[existingIndex] = {
				...this.policyAssignments[existingIndex],
				policyId,
				startDate
			};
		} else {
			this.policyAssignments.push({
				id: `pa-${employeeId}-${Date.now()}`,
				employeeId,
				policyId,
				startDate
			});
		}
		this.policyAssignments = [...this.policyAssignments];
	}

	assignOverridePolicy(employeeId: string | number, policyId: string, startDate: string, endDate?: string) {
		// Remove existing override for this employee
		this.policyAssignments = this.policyAssignments.filter(pa => !(pa.employeeId === employeeId && pa.isOverride));

		// Add new override
		this.policyAssignments.push({
			id: `pa-override-${employeeId}-${Date.now()}`,
			employeeId,
			policyId,
			startDate,
			endDate,
			isOverride: true,
			overrideStartDate: startDate,
			overrideEndDate: endDate
		});
		this.policyAssignments = [...this.policyAssignments];
	}

	async createPolicyAssignment(data: { employeeId: string; policyId: string; startDate: string; endDate?: string }) {
		try {
			const result = await attendanceService.createAssignment({
				employee_id: data.employeeId,
				policy_id: data.policyId,
				start_date: data.startDate,
				end_date: data.endDate ?? null,
			});
			const newPa: PolicyAssignment = {
				id: result.id,
				employeeId: result.employee_id,
				policyId: result.policy_id,
				startDate: result.valid_from,
				endDate: result.valid_until ?? undefined,
				isOverride: false,
			};
			this.policyAssignments = [...this.policyAssignments, newPa];
			return newPa;
		} catch (err) {
			console.error('[AttendanceStore] createPolicyAssignment error:', err);
			throw err;
		}
	}

	async deletePolicyAssignment(id: string) {
		try {
			await attendanceService.deleteAssignment(id);
			this.policyAssignments = this.policyAssignments.filter(pa => pa.id !== id);
		} catch (err) {
			console.error('[AttendanceStore] deletePolicyAssignment error:', err);
			throw err;
		}
	}

	getEffectivePolicyForEmployee(employeeId: string | number, date: string): WorkPolicy | null {
		const assignments = this.policyAssignments.filter(pa => pa.employeeId === employeeId);

		// Check for override policies first
		const overrideAssignment = assignments.find(pa => pa.isOverride &&
			date >= pa.startDate &&
			(!pa.endDate || date <= pa.endDate)
		);

		if (overrideAssignment) {
			return this.policies.find(p => p.id === overrideAssignment.policyId) || null;
		}

		// Check for base policy
		const baseAssignment = assignments.find(pa => !pa.isOverride && date >= pa.startDate);

		if (baseAssignment) {
			return this.policies.find(p => p.id === baseAssignment.policyId) || null;
		}

		return null;
	}

	async updatePolicy(id: string, data: Partial<WorkPolicy>) {
		// Call backend API to update
		try {
			const dailyConfigs = data.pattern ? workPolicyToDailyConfigs(data as WorkPolicy) : undefined;
			const result = await attendanceService.updatePolicy(id, {
				name: data.name,
				description: data.description,
				weekly_target_hours: data.targetHours ?? undefined,
				daily_configs: dailyConfigs,
			});
			const index = this.policies.findIndex(p => p.id === id);
			if (index !== -1) {
				this.policies[index] = backendToWorkPolicy(result);
			}
		} catch (err) {
			console.error('[AttendanceStore] updatePolicy error:', err);
		}
	}

	async deletePolicy(id: string) {
		const index = this.policies.findIndex(p => p.id === id);
		if (index === -1) return;

		try {
			await attendanceService.deletePolicy(id);
			this.policies = this.policies.filter(p => p.id !== id);
		} catch (err) {
			console.error('[AttendanceStore] deletePolicy error:', err);
		}
	}
}


function backendToPolicyAssignment(backend: EmploymentSchemeOut): PolicyAssignment {
	return {
		id: backend.id,
		employeeId: backend.employee_id,
		policyId: backend.policy_id,
		startDate: backend.valid_from,
		endDate: backend.valid_until ?? undefined,
		isOverride: false,
	};
}


export const attendanceStore = new AttendanceStore();
