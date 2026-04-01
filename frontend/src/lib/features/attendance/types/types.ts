export type AttendanceStatus = 'PRESENT' | 'LATE' | 'ABSENT' | 'LEAVE' | 'OFF' | 'PENDING';
export type DayOfWeek = 0 | 1 | 2 | 3 | 4 | 5 | 6; // 0 = Sunday, 1 = Monday, etc.

export interface AttendanceRecord {
	id: string;
	employeeId: number;
	employeeName: string;
	avatarUrl?: string;
	department: string;
	date: string; // ISO format
	checkIn: string | null; // HH:mm
	checkOut: string | null; // HH:mm
	status: AttendanceStatus;
	workDuration: number; // in minutes
	overtime: number; // in minutes
	isLocked: boolean;
	anomalies: string[];
}

export interface Shift {
	id: string;
	name: string;
	startTime: string; // HH:mm
	endTime: string; // HH:mm
	breakDuration: number; // in minutes
	color: string;
}

export interface AttendanceFilters {
	search: string;
	department: string[];
	status: AttendanceStatus[];
	dateRange: {
		from: string;
		to: string;
	};
	policy: string[];
}

export interface AttendanceStats {
	presentCount: number;
	lateCount: number;
	absentCount: number;
	totalOvertime: number;
	attendanceRate: number;
}

export interface ShiftAssignment {
	id: string;
	employeeId: number;
	shiftId: string;
	date: string; // ISO format
}

export interface WorkPeriod {
	id: string;
	startTime: string; // HH:mm
	endTime: string; // HH:mm
	type: 'work' | 'break';
	name?: string; // ex: "morning", "lunch break", "afternoon"
}

export interface DayPattern {
	isOff: boolean;
	periods: WorkPeriod[]; // List of time of work/break
}

export interface WorkPolicy {
	id?: string;
	name: string;
	description?: string;
	pattern: Record<DayOfWeek, DayPattern>; // day index -> DayPattern
	targetHours?: number;
	createdAt?: string;
}

export interface PolicyAssignment {
	id: string;
	employeeId: number;
	policyId: string;
	startDate: string;
	endDate?: string;
	isOverride?: boolean;
	overrideStartDate?: string;
	overrideEndDate?: string;
}

export type AttendanceTabId = 'register' | 'config' | 'policies';
