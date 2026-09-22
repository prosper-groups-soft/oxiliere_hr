import type { AttendanceStatus, AttendanceTabId, DayOfWeek } from '../constants/attendance.constants';
export type { AttendanceStatus, AttendanceTabId, DayOfWeek };

// Constantes — import local + re-export
import { 
	STATUS_LABELS, STATUS_COLORS, STATUS_PILL,
	STATUS_OPTIONS, TAB_LABELS, TAB_OPTIONS,
	BACKEND_WEEKDAYS, FRONTEND_WEEKDAYS
} from '../constants/attendance.constants';
export {
	STATUS_LABELS,
	STATUS_COLORS,
	STATUS_PILL,
	STATUS_OPTIONS,
	TAB_LABELS,
	TAB_OPTIONS,
	BACKEND_WEEKDAYS,
	FRONTEND_WEEKDAYS,
};


export interface AttendanceRecord {
	id: string;
	employeeId: string | number;
	employeeName: string;
	firstName?: string;
	lastName?: string;
	jobTitle?: string;
	avatarUrl?: string;
	orgUnit: string;
	orgUnitId?: string;
	date: string; // ISO format
	checkIn: string | null; // HH:mm
	checkOut: string | null; // HH:mm
	checkInAt?: string | null; // ISO datetime
	checkOutAt?: string | null; // ISO datetime
	checkInPunchId?: string | null; // UUID for inline editing
	checkOutPunchId?: string | null;
	isManualEntry?: boolean;
	expectedIn?: string; // HH:mm
	expectedOut?: string; // HH:mm
	expectedBreakDuration?: number; // minutes

	isWorkingDay: boolean;
	scheduleName?: string;
	scheduleSource?: string; // "policy" | "override" | "holiday" | "none"

	remarks?: string;
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
	orgUnit: string[];
	recurrence: string[];
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
	employeeId: string | number;
	shiftId: string;
	date: string; // ISO format
}

export interface WorkPeriod {
	id: string;
	startTime: string; // HH:mm
	endTime: string; // HH:mm
	type: 'work' | 'break';
	name?: string;
}

export interface DayPattern {
	isOff: boolean;
	periods: WorkPeriod[];
}

export interface WorkPolicy {
	id?: string;
	name: string;
	description?: string;
	pattern: Record<DayOfWeek, DayPattern>;
	targetHours?: number;
	createdAt?: string;
}

export interface PolicyAssignment {
	id: string;
	employeeId: string | number;
	policyId: string;
	startDate: string;
	endDate?: string;
	isOverride?: boolean;
	overrideStartDate?: string;
	overrideEndDate?: string;
	recurrence?: string;
	recurrenceCount?: number | null;
}

