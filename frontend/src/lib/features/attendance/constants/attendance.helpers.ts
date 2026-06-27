import type { WorkPolicy, WorkPeriod, DayPattern, PolicyAssignment } from '../types/types';
import type { ShiftPolicyOut, EmploymentSchemeOut } from '../api/attendance.endpoints';
import {
	BACKEND_WEEKDAYS,
	FRONTEND_WEEKDAYS,
	type DayOfWeek,
} from './attendance.constants';

/**
 * Convertit une politique backend (ShiftPolicyOut) → format frontend (WorkPolicy)
 */
export function backendToWorkPolicy(backend: ShiftPolicyOut): WorkPolicy {
	const pattern: Record<number, DayPattern> = {};
	for (let d = 0; d <= 6; d++) {
		pattern[d] = { isOff: true, periods: [] };
	}

	for (const detail of backend.details) {
		const dayIndex = BACKEND_WEEKDAYS[detail.weekday];
		if (dayIndex === undefined) continue;

		if (!detail.is_working_day) {
			pattern[dayIndex] = { isOff: true, periods: [] };
			continue;
		}

		// Map periods directly from the backend if available
		if (detail.periods && detail.periods.length > 0) {
			const periods: WorkPeriod[] = detail.periods.map((p, i) => ({
				id: String(i + 1),
				startTime: p.start_time,
				endTime: p.end_time,
				type: p.period_type === 'BREAK' ? 'break' : 'work',
				name: p.name || (p.period_type === 'BREAK' ? 'Pause' : 'Travail'),
			}));
			pattern[dayIndex] = { isOff: false, periods };
		} else {
			// Fallback: reconstruct from aggregate fields (backward compatibility)
			const periods: WorkPeriod[] = [];
			let pid = 1;

			if (detail.start_time && detail.break_start_time) {
				periods.push({ id: String(pid++), startTime: detail.start_time, endTime: detail.break_start_time, type: 'work', name: 'Matin' });
				const breakEnd = calcBreakEnd(detail.break_start_time, detail.break_duration);
				periods.push({ id: String(pid++), startTime: detail.break_start_time, endTime: breakEnd, type: 'break', name: 'Pause déjeuner' });
			}

			if (detail.end_time) {
				const breakEnd = calcBreakEnd(detail.break_start_time, detail.break_duration);
				periods.push({ id: String(pid++), startTime: breakEnd, endTime: detail.end_time, type: 'work', name: 'Après-midi' });
			}

			// Fallback: just start → end
			if (!detail.break_start_time && detail.start_time && detail.end_time) {
				periods.length = 0;
				periods.push({ id: '1', startTime: detail.start_time, endTime: detail.end_time, type: 'work', name: 'Travail' });
			}

			pattern[dayIndex] = { isOff: false, periods };
		}
	}

	return {
		id: backend.id,
		name: backend.name,
		description: backend.description || '',
		pattern,
		targetHours: backend.weekly_target_hours,
		createdAt: backend.created_at,
	};
}

/**
 * Convertit une affectation backend (EmploymentSchemeOut) → format frontend (PolicyAssignment)
 */
export function backendToPolicyAssignment(backend: EmploymentSchemeOut): PolicyAssignment {
	return {
		id: backend.id,
		employeeId: backend.employee_id,
		policyId: backend.policy_id,
		startDate: backend.valid_from,
		endDate: backend.valid_until ?? undefined,
		isOverride: false,
		recurrence: backend.recurrence,
	};
}

/**
 * Convertit une politique frontend (WorkPolicy) → format backend daily_configs
 */
export function workPolicyToDailyConfigs(policy: WorkPolicy): Record<string, any> {
	const configs: Record<string, any> = {};

	for (let d = 0; d <= 6; d++) {
		const dayPattern = policy.pattern[d as DayOfWeek];
		const weekdayKey = FRONTEND_WEEKDAYS[d as number];
		if (!weekdayKey) continue;

		if (!dayPattern || dayPattern.isOff || dayPattern.periods.length === 0) {
			configs[weekdayKey] = { work: false };
			continue;
		}

		// Emit full periods array for the backend
		const periods = dayPattern.periods.map((p: WorkPeriod) => ({
			name: p.name || '',
			period_type: p.type === 'break' ? 'BREAK' : 'WORK',
			start_time: p.startTime,
			end_time: p.endTime,
		}));

		configs[weekdayKey] = { work: true, periods };
	}

	return configs;
}

function calcBreakEnd(breakStart: string | null, breakDuration: string | null): string {
	if (!breakStart || !breakDuration) return '14:00';
	const [h, m] = breakStart.split(':').map(Number);
	const totalMinutes = h * 60 + m + parseISODurationToMinutes(breakDuration);
	const rh = Math.floor(totalMinutes / 60);
	const rm = Math.round(totalMinutes % 60);
	return `${String(rh).padStart(2, '0')}:${String(rm).padStart(2, '0')}`;
}

function parseISODurationToMinutes(duration: string): number {
	// e.g. "P0DT02H00M00S" → 120 minutes
	const daysMatch = duration.match(/(\d+)D/);
	const hoursMatch = duration.match(/(\d+)H/);
	const minutesMatch = duration.match(/(\d+)M(?!S)/); // minutes before 'S'
	const secondsMatch = duration.match(/(\d+)S/);
	const days = daysMatch ? parseInt(daysMatch[1]) : 0;
	const hours = hoursMatch ? parseInt(hoursMatch[1]) : 0;
	const minutes = minutesMatch ? parseInt(minutesMatch[1]) : 0;
	const seconds = secondsMatch ? parseInt(secondsMatch[1]) : 0;
	return days * 24 * 60 + hours * 60 + minutes + seconds / 60;
}

/**
 * Parse ISO 8601 duration to hours.
 * e.g. "P1DT16H00M00S" → 40
 */
export function parseISODurationToHours(duration: string): number {
	return Math.round(parseISODurationToMinutes(duration) / 60);
}

function breakDurationToMinutes(startTime: string, endTime: string): number {
	const [h1, m1] = startTime.split(':').map(Number);
	const [h2, m2] = endTime.split(':').map(Number);
	return ((h2 * 60 + m2) - (h1 * 60 + m1));
}

/**
 * Template par défaut pour la création d'un nouveau modèle de travail.
 * 5 jours ouvrés (Lun-Ven) avec 3 périodes (Matin, Pause, Après-midi),
 * et Samedi/Dimanche en repos.
 */
export const DEFAULT_POLICY_TEMPLATE = {
  name: "",
  description: "",
  targetHours: 40,
  pattern: {
    0: { isOff: true, periods: [] },
    1: { isOff: false, periods: [
      { id: "1", startTime: "08:00", endTime: "12:00", type: "work" as const, name: "Matin" },
      { id: "2", startTime: "12:00", endTime: "14:00", type: "break" as const, name: "Pause déjeuner" },
      { id: "3", startTime: "14:00", endTime: "17:00", type: "work" as const, name: "Après-midi" }
    ]},
    2: { isOff: false, periods: [
      { id: "1", startTime: "08:00", endTime: "12:00", type: "work" as const, name: "Matin" },
      { id: "2", startTime: "12:00", endTime: "14:00", type: "break" as const, name: "Pause déjeuner" },
      { id: "3", startTime: "14:00", endTime: "17:00", type: "work" as const, name: "Après-midi" }
    ]},
    3: { isOff: false, periods: [
      { id: "1", startTime: "08:00", endTime: "12:00", type: "work" as const, name: "Matin" },
      { id: "2", startTime: "12:00", endTime: "14:00", type: "break" as const, name: "Pause déjeuner" },
      { id: "3", startTime: "14:00", endTime: "17:00", type: "work" as const, name: "Après-midi" }
    ]},
    4: { isOff: false, periods: [
      { id: "1", startTime: "08:00", endTime: "12:00", type: "work" as const, name: "Matin" },
      { id: "2", startTime: "12:00", endTime: "14:00", type: "break" as const, name: "Pause déjeuner" },
      { id: "3", startTime: "14:00", endTime: "17:00", type: "work" as const, name: "Après-midi" }
    ]},
    5: { isOff: false, periods: [
      { id: "1", startTime: "08:00", endTime: "12:00", type: "work" as const, name: "Matin" },
      { id: "2", startTime: "12:00", endTime: "14:00", type: "break" as const, name: "Pause déjeuner" },
      { id: "3", startTime: "14:00", endTime: "17:00", type: "work" as const, name: "Après-midi" }
    ]},
    6: { isOff: true, periods: [] },
  } satisfies Record<number, { isOff: boolean; periods: { id: string; startTime: string; endTime: string; type: 'work' | 'break'; name: string }[] }>,
};
