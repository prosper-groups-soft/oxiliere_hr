import { employeeStore } from '@/features/employees/stores/employees.svelte';
import type { 
  AttendanceRecord, 
  AttendanceFilters, 
  AttendanceStatus, 
  Shift, 
  AttendanceStats,
  ShiftAssignment,
  WorkPolicy,
  PolicyAssignment,
  DayPattern,
  WorkPeriod,
  AttendanceTabId
} from '../types/types';


// Mock Shifts
const MOCK_SHIFTS: Shift[] = [
	{ id: 'shift-1', name: 'Matin', startTime: '08:00', endTime: '16:00', breakDuration: 60, color: '#3b82f6' },
	{ id: 'shift-2', name: 'Après-midi', startTime: '14:00', endTime: '22:00', breakDuration: 60, color: '#10b981' },
	{ id: 'shift-3', name: 'Nuit', startTime: '22:00', endTime: '06:00', breakDuration: 60, color: '#6366f1' }
];


// Generate Mock Attendance Records for the current date
const generateMockRecords = (): AttendanceRecord[] => {
	const records: AttendanceRecord[] = [];
	const offsets = [-1, 0, 1]; // Yesterday, Today, Tomorrow

	offsets.forEach(offset => {
		const d = new Date();
		d.setDate(d.getDate() + offset);
		const dateStr = d.toISOString().split('T')[0];

		employeeStore.employees.forEach((emp, index) => {
			const statuses: AttendanceStatus[] = ['PRESENT', 'PRESENT', 'LATE', 'PRESENT', 'ABSENT', 'PRESENT'];
			// Slightly vary status based on date and index
			const statusIndex = (index + Math.abs(offset)) % statuses.length;
			const status = statuses[statusIndex];
			
			let checkIn = null;
			let checkOut = null;
			let workDuration = 0;
			let overtime = 0;
			let anomalies: string[] = [];

			if (status === 'PRESENT' || status === 'LATE') {
				checkIn = status === 'LATE' ? '08:45' : '08:00';
				checkOut = '17:00';
				workDuration = 480; // 8 hours
				if (status === 'LATE') anomalies.push('Retard détecté');
			} else if (status === 'ABSENT') {
				anomalies.push('Absence non justifiée', 'Absence non justifiée');
			}

			records.push({
				id: `att-${emp.id}-${dateStr}`,
				employeeId: emp.id,
				employeeName: emp.name,
				avatarUrl: emp.avatarUrl,
				department: emp.department,
				date: dateStr,
				checkIn,
				checkOut,
				status,
				workDuration,
				overtime,
				isLocked: false,
				anomalies
			});
		});
	});

	return records;
};

export class AttendanceStore {
	records = $state<AttendanceRecord[]>([]);
	shifts = $state<Shift[]>(MOCK_SHIFTS);
	assignments = $state<ShiftAssignment[]>([]);
	policies = $state<WorkPolicy[]>([]);
	policyAssignments = $state<PolicyAssignment[]>([]);
	
	
	filters = $state<AttendanceFilters>({
		search: '',
		department: [],
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
		this.records = generateMockRecords();
		
		// Mock Policies
		this.policies = [
			{
				id: 'pol-1',
				name: 'Bureau Standard',
				description: '8h00 - 17h00, Lundi au Vendredi',
        createdAt: '2024-02-20T14:30:00Z',
				pattern: {
					1: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					2: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					3: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					4: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					5: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					6: { isOff: true, periods: [] },
					0: { isOff: true, periods: [] }
				}
			},
			{
				id: 'pol-2',
				name: 'Demi-journée Samedi',
				description: 'Lundi-Vendredi 8h-18h, Samedi 8h-12h',
        createdAt: '2024-01-15T10:00:00Z',
				pattern: {
					1: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					2: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					3: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					4: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					5: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' },
						{ id: '2', startTime: '12:00', endTime: '14:00', type: 'break', name: 'Pause déjeuner' },
						{ id: '3', startTime: '14:00', endTime: '18:00', type: 'work', name: 'Après-midi' }
					]},
					6: { isOff: false, periods: [
						{ id: '1', startTime: '08:00', endTime: '12:00', type: 'work', name: 'Matin' }
					]},
					0: { isOff: true, periods: [] }
				}
			}
		];

		// Initial assignments mock
		const today = new Date();
		employeeStore.employees.forEach(emp => {
			for (let i = 0; i < 7; i++) {
				const d = new Date(today);
				d.setDate(today.getDate() + i);
				const dateStr = d.toISOString().split('T')[0];
				this.assignments.push({
					id: `as-${emp.id}-${dateStr}`,
					employeeId: emp.id,
					shiftId: MOCK_SHIFTS[i % 3].id,
					date: dateStr
				});
			}

			// Assign default policy to some employees
			if (emp.id % 2 === 0) {
				this.policyAssignments.push({
					id: `pa-${emp.id}`,
					employeeId: emp.id,
					policyId: 'pol-1',
					startDate: '2024-01-01'
				});
			}
		});
	}

	// --- Derived State ---
	filteredRecords = $derived.by(() => {
		return this.records.filter(record => {
			const matchesSearch = record.employeeName.toLowerCase().includes(this.filters.search.toLowerCase());
			const matchesDept = this.filters.department.length === 0 || this.filters.department.includes(record.department);
			const matchesStatus = this.filters.status.length === 0 || this.filters.status.includes(record.status);
			const matchesDate = record.date === this.filters.dateRange.from;
			return matchesSearch && matchesDept && matchesStatus && matchesDate;
		});
	});

	currentPeriodRecords = $derived.by(() => {
		return this.records.filter((record) => record.date === this.filters.dateRange.from);
	});

	stats = $derived.by((): AttendanceStats => {
		const recs = this.filteredRecords;
		const total = recs.length || 1;
		return {
			presentCount: recs.filter(r => r.status === 'PRESENT' || r.status === 'LATE').length,
			lateCount: recs.filter(r => r.status === 'LATE').length,
			absentCount: recs.filter(r => r.status === 'ABSENT').length,
			totalOvertime: recs.reduce((acc, r) => acc + r.overtime, 0),
			attendanceRate: Math.round((recs.filter(r => r.status === 'PRESENT' || r.status === 'LATE').length / total) * 100)
		};
	});

	activeFiltersCount = $derived.by(() => {
		return (this.filters.department?.length || 0) + 
			     (this.filters.status?.length || 0) + 
			     (this.filters.policy?.length || 0);
	});

	isCurrentPeriodLocked = $derived.by(() => {
		return this.currentPeriodRecords.length > 0 && this.currentPeriodRecords.every((record) => record.isLocked);
	});

	// --- Actions ---
	setSearch(query: string) {
		this.filters.search = query;
	}

	toggleFilter(category: 'department' | 'status' | 'policy', value: any) {
		const current = this.filters[category] as any[];
		if (current.includes(value)) {
			this.filters[category] = current.filter(v => v !== value) as any;
		} else {
			this.filters[category] = [...current, value] as any;
		}
	}

  resetFilters() {
    this.filters.search = '';
    this.filters.department = [];
    this.filters.status = [];
    this.filters.policy = [];
  }

  setSort(by: string) {
    this.sortBy = by;
  }

  toggleSortOrder() {
    this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
  }

  updateRecord(id: string, data: Partial<AttendanceRecord>) {
    const index = this.records.findIndex(r => r.id === id);
    if (index !== -1) {
      this.records[index] = { ...this.records[index], ...data };
      this.records = [...this.records];
    }
  }

	assignShift(employeeId: number, date: string, shiftId: string) {
		const existingIndex = this.assignments.findIndex(a => a.employeeId === employeeId && a.date === date);
		if (existingIndex !== -1) {
			this.assignments[existingIndex].shiftId = shiftId;
		} else {
			this.assignments.push({
				id: `as-${employeeId}-${date}`,
				employeeId,
				date,
				shiftId
			});
		}
		this.assignments = [...this.assignments];
	}

	removeAssignment(id: string) {
		this.assignments = this.assignments.filter(a => a.id !== id);
	}

	// Policy Actions
  addPolicy(policy: Omit<WorkPolicy, 'id' | 'createdAt'>) {
    const newPolicy: WorkPolicy = {
      ...policy,
      id: `pol-${Date.now()}`,
      createdAt: new Date().toISOString()
    };
    this.policies = [...this.policies, newPolicy];
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

	assignPolicy(employeeId: number, policyId: string, startDate: string) {
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

	assignOverridePolicy(employeeId: number, policyId: string, startDate: string, endDate?: string) {
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

	getEffectivePolicyForEmployee(employeeId: number, date: string): WorkPolicy | null {
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

	addRecord(record: Omit<AttendanceRecord, 'id' | 'isLocked' | 'anomalies' | 'workDuration' | 'overtime'>) {
		const id = `att-${record.employeeId}-${record.date}`;
		const existingIndex = this.records.findIndex(r => r.id === id);
		
		const newRecord: AttendanceRecord = {
			...record,
			id,
			isLocked: false,
			anomalies: [],
			workDuration: 0,
			overtime: 0
		};

		if (existingIndex !== -1) {
			this.records[existingIndex] = { ...this.records[existingIndex], ...newRecord };
		} else {
			this.records.push(newRecord);
		}
		this.records = [...this.records];
	}

	lockPeriod() {
		const visibleRecordIds = new Set(this.currentPeriodRecords.map((record) => record.id));
		this.records = this.records.map((record) =>
			visibleRecordIds.has(record.id) ? { ...record, isLocked: true } : record
		);
	}

	unlockPeriod() {
		const visibleRecordIds = new Set(this.currentPeriodRecords.map((record) => record.id));
		this.records = this.records.map((record) =>
			visibleRecordIds.has(record.id) ? { ...record, isLocked: false } : record
		);
	}

  togglePeriodLock() {
    const visibleIds = new Set(this.currentPeriodRecords.map(r => r.id));
    const nextLockedState = !this.isCurrentPeriodLocked;
    this.records = this.records.map(r => visibleIds.has(r.id) ? { ...r, isLocked: nextLockedState } : r);
  }

  updatePolicy(id: string, data: Partial<WorkPolicy>) {
    const index = this.policies.findIndex(p => p.id === id);
    if (index !== -1) {
      this.policies[index] = { ...this.policies[index], ...data };
    }
  }
}


export const attendanceStore = new AttendanceStore();
