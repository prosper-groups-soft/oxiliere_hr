// Attendance — Status
// ------------------------------------------

export type AttendanceStatus = 'PRESENT' | 'LATE' | 'ABSENT' | 'LEAVE' | 'OFF' | 'PENDING' | 'HOLIDAY' | 'PARTIAL' | 'EXCUSED' | 'ON_LEAVE';

export const STATUS_LABELS: Record<AttendanceStatus, string> = {
	PRESENT: 'Présent',
	LATE: 'En retard',
	ABSENT: 'Absent',
	LEAVE: 'En congé',
	OFF: 'Repos',
	PENDING: 'En attente',
	HOLIDAY: 'Férié',
	PARTIAL: 'Partiel',
	EXCUSED: 'Excusé',
	ON_LEAVE: 'En congé',
};

export const STATUS_COLORS: Record<AttendanceStatus, string> = {
	PRESENT: 'bg-emerald-100 text-emerald-700 border-emerald-200',
	LATE: 'bg-amber-100 text-amber-700 border-amber-200',
	ABSENT: 'bg-red-100 text-red-700 border-red-200',
	LEAVE: 'bg-blue-100 text-blue-700 border-blue-200',
	OFF: 'bg-slate-100 text-slate-500 border-slate-200',
	PENDING: 'bg-gray-100 text-gray-700 border-gray-200',
	HOLIDAY: 'bg-purple-100 text-purple-700 border-purple-200',
	PARTIAL: 'bg-orange-100 text-orange-700 border-orange-200',
	EXCUSED: 'bg-teal-100 text-teal-700 border-teal-200',
	ON_LEAVE: 'bg-blue-100 text-blue-700 border-blue-200',
};

/** Dot + label colours used in the register row status indicator. */
export const STATUS_DOT_CONFIG: Record<AttendanceStatus, { label: string; color: string; textColor: string }> = {
	PRESENT: { label: 'Présent', color: 'bg-emerald-500', textColor: 'text-emerald-600' },
	LATE: { label: 'Retard', color: 'bg-amber-500', textColor: 'text-amber-600' },
	ABSENT: { label: 'Absent', color: 'bg-rose-500', textColor: 'text-rose-600' },
	LEAVE: { label: 'Congé', color: 'bg-blue-500', textColor: 'text-blue-600' },
	OFF: { label: 'Repos', color: 'bg-slate-400', textColor: 'text-slate-500' },
	PENDING: { label: 'En attente', color: 'bg-gray-400', textColor: 'text-gray-500' },
	HOLIDAY: { label: 'Férié', color: 'bg-purple-500', textColor: 'text-purple-600' },
	PARTIAL: { label: 'Partiel', color: 'bg-orange-500', textColor: 'text-orange-600' },
	EXCUSED: { label: 'Excusé', color: 'bg-teal-500', textColor: 'text-teal-600' },
	ON_LEAVE: { label: 'Congé', color: 'bg-blue-500', textColor: 'text-blue-600' },
};

export const STATUS_PILL: Record<AttendanceStatus, string> = {
	PRESENT: 'bg-emerald-100 text-emerald-600',
	LATE: 'bg-amber-100 text-amber-600',
	ABSENT: 'bg-red-100 text-red-600',
	LEAVE: 'bg-blue-100 text-blue-600',
	OFF: 'bg-slate-100 text-slate-400',
	PENDING: 'bg-gray-100 text-gray-600',
	HOLIDAY: 'bg-purple-100 text-purple-600',
	PARTIAL: 'bg-orange-100 text-orange-600',
	EXCUSED: 'bg-teal-100 text-teal-600',
	ON_LEAVE: 'bg-blue-100 text-blue-600',
};

export const STATUS_OPTIONS: { value: AttendanceStatus; label: string }[] = (
	Object.entries(STATUS_LABELS) as [AttendanceStatus, string][]
).map(([value, label]) => ({ value, label }));

/** Status options for the register filter dropdown (excludes PENDING). */
export const FILTER_STATUS_OPTIONS: { value: AttendanceStatus; label: string }[] = [
	{ value: 'PRESENT', label: 'Présent' },
	{ value: 'LATE', label: 'Retard' },
	{ value: 'ABSENT', label: 'Absent' },
	{ value: 'LEAVE', label: 'Congé' },
	{ value: 'OFF', label: 'Repos' },
	{ value: 'HOLIDAY', label: 'Férié' },
	{ value: 'PARTIAL', label: 'Partiel' },
	{ value: 'EXCUSED', label: 'Excusé' },
];


// Attendance — Tabs
// ------------------------------------------

export type AttendanceTabId = 'register' | 'config' | 'policies';

export const TAB_LABELS: Record<AttendanceTabId, string> = {
	register: 'Registre',
	config: 'Configuration',
	policies: 'Politiques',
};

export const TAB_OPTIONS: { value: AttendanceTabId; label: string }[] = (
	Object.entries(TAB_LABELS) as [AttendanceTabId, string][]
).map(([value, label]) => ({ value, label }));


// Weekday helpers
// ------------------------------------------

export type DayOfWeek = 0 | 1 | 2 | 3 | 4 | 5 | 6; // 0 = Sunday, 1 = Monday, etc.

export const BACKEND_WEEKDAYS: Record<string, number> = {
	'MONDAY': 1,
	'TUESDAY': 2,
	'WEDNESDAY': 3,
	'THURSDAY': 4,
	'FRIDAY': 5,
	'SATURDAY': 6,
	'SUNDAY': 0,
};

export const FRONTEND_WEEKDAYS: Record<number, string> = {
	1: 'MONDAY',
	2: 'TUESDAY',
	3: 'WEDNESDAY',
	4: 'THURSDAY',
	5: 'FRIDAY',
	6: 'SATURDAY',
	0: 'SUNDAY',
};

export interface DayLabel {
	label: string;
	index: DayOfWeek;
	short: string;
}

export const DAYS: DayLabel[] = [
	{ label: 'Lundi', index: 1, short: 'Lun' },
	{ label: 'Mardi', index: 2, short: 'Mar' },
	{ label: 'Mercredi', index: 3, short: 'Mer' },
	{ label: 'Jeudi', index: 4, short: 'Jeu' },
	{ label: 'Vendredi', index: 5, short: 'Ven' },
	{ label: 'Samedi', index: 6, short: 'Sam' },
	{ label: 'Dimanche', index: 0, short: 'Dim' },
];

export const PERIOD_TYPES: { value: 'work' | 'break'; label: string }[] = [
	{ value: 'work', label: 'Travail' },
	{ value: 'break', label: 'Pause' },
];


// Attendance — Recurrence labels
// ------------------------------------------

export const RECURRENCE_LABELS: Record<string, string> = {
	NONE: 'Aucune',
	WEEKLY: 'Hebdo',
	BIWEEKLY: 'Bi-hebdo',
	MONTHLY: 'Mensuel',
	QUARTERLY: 'Trimestriel',
};


// Recurrence modes used in override sheets (lowercase keys)
export type RecurrenceMode = 'none' | 'weekly' | 'biweekly' | 'monthly' | 'quarterly';

export const RECURRENCE_MODE_LABELS: Record<RecurrenceMode, string> = {
	none: 'Aucune',
	weekly: 'Hebdo',
	biweekly: 'Bi-hebdo',
	monthly: 'Mensuel',
	quarterly: 'Trimestriel',
};
