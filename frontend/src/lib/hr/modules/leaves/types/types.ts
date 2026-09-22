export type LeaveType = 'annual' | 'sick' | 'circumstantial' | 'unpaid';
export type LeaveStatus = 'pending' | 'approved' | 'rejected';


/**
 * Sous-types de congés circonstanciels (Code du Travail RDC).
 * Correspond au backend CircumstanceType.
 */
export type CircumstanceType =
	| 'MARRIAGE'
	| 'BIRTH'
	| 'DEATH_SPOUSE_CHILD'
	| 'DEATH_ANCESTOR'
	| 'CHILD_MARRIAGE'
	| 'MOVING'
	| 'CHILD_HOSPITALIZATION'
	| 'OTHER';


export interface LeaveRequest {
	id: string;
	employeeId: string;
	employeeName: string;
	firstName?: string;
	lastName?: string;
	middleName?: string;
	avatarUrl?: string;
	jobTitle?: string;
	orgUnit: string;
	type: LeaveType;
	status: LeaveStatus;
	startDate: string; // ISO date
	endDate: string;   // ISO date
	days: number;
	reason?: string;
	circumstanceType?: string;
	attachment?: string;
	approver?: string;
	createdAt: string; // ISO date
	respondedAt?: string;
}


export interface LeaveBalance {
	employeeId: number;
	type: LeaveType;
	allocated: number;
	taken: number;
	remaining: number;
	expiringDays?: number;
	expiryDate?: string; // ISO date
}


export interface SeniorityRule {
	minYears: number;
	maxYears?: number;
	extraDays: number;
}


export interface LeavePolicy {
	id: string;
	name: string;
	type: LeaveType;
	daysPerYear: number;
	seniorityRules: SeniorityRule[];
	carryOverDays: number;
	requiresApproval: boolean;
	requiresJustification: boolean;
	description?: string;
}


export interface LeavesFilters {
	search: string;
	orgUnit: string[];
	type: LeaveType[];
	status: LeaveStatus[];
}


/**
 * Detailed breakdown of a single day in a leave preview period.
 */
export interface DayDetail {
	date: string;           // ISO date YYYY-MM-DD
	dayName: string;        // e.g. 'LUNDI'
	isWorking: boolean;
	reason: 'working' | 'public_holiday' | 'company_closure' | 'non_working_day' | 'no_scheme';
	eventType?: string;     // CalendarEventType or null
	eventName?: string;     // Name of the holiday/closure
	startTime?: string;     // HH:MM
	endTime?: string;       // HH:MM
}

/**
 * Breakdown of excluded days by reason.
 */
export interface ExcludedDays {
	publicHolidays: string[];
	closures: string[];
	nonWorkingPolicyDays: string[];
	totalExcluded: number;
}

/**
 * Response from GET /api/leaves/working-days-count
 */
export interface WorkingDaysCount {
	workingDays: number;
	calendarDays: number;
	excluded: ExcludedDays;
	dayDetails: DayDetail[];
}

