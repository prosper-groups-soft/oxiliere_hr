import type { 
	TimelineEvent, 
	EmployeeFullProfile, 
	EmployeeTransition,
	EmployeePositionHistory
} from '../types/types';
import { employeesService } from '../services/employees.service';
import { transitionsService } from '../services/transitions.service';
import { REVERSE_STATUS_MAPPING } from '../constants/mappings';

export class TimelineEventStore {
	#events = $state<TimelineEvent[]>([]);
	#loading = $state<boolean>(false);
	#error = $state<string | null>(null);

	get events() {
		return this.#events;
	}

	get isLoading() {
		return this.#loading;
	}

	async fetchTimeline(employeeId: string | number) {
		this.#loading = true;
		this.#error = null;

		try {
			// 1. Fetch employee detail (contains status_history)
			// and 2. Fetch transitions
			const [profile, transitions] = await Promise.all([
				employeesService.getEmployeeDetail(employeeId.toString()),
				transitionsService.getEmployeeTransitions(employeeId)
			]);

			this.#events = this.#mergeAndSortEvents(profile, transitions);
		} catch (err: any) {
			this.#error = err.message || "Erreur lors du chargement de la timeline";
			this.#events = [];
		} finally {
			this.#loading = false;
		}
	}

	#mergeAndSortEvents(profile: EmployeeFullProfile, transitions: EmployeeTransition[]): TimelineEvent[] {
		const timelineEvents: TimelineEvent[] = [];

		// Add status history events
		if (profile.status_history) {
			profile.status_history.forEach((sh) => {
				const statusLabel = REVERSE_STATUS_MAPPING[sh.status as keyof typeof REVERSE_STATUS_MAPPING] || sh.status;
				timelineEvents.push({
					id: `status-${sh.id}`,
					date: sh.start_date,
					created_at: sh.created_at,
					label: 'Statut administratif',
					status: statusLabel,
					type: 'status',
					description: sh.reason
				});
			});
		}

		// Add career/position history events
		if (profile.position_history) {
			profile.position_history.forEach((ph: EmployeePositionHistory) => {
				timelineEvents.push({
					id: `position-${ph.id}`,
					date: ph.start_date,
					created_at: ph.created_at,
					label: 'Mouvement de carrière',
					status: ph.position_name,
					type: 'transition', // We use 'transition' type for better styling
					description: ph.description || `Affectation au poste de ${ph.position_name}`,
					metadata: {
						transition_type: 'TRANSFER', // Map to a generic transition type for styling
						to: ph.position_name,
						seniority: ph.seniority_label,
						org_unit: ph.org_unit_name
					}
				});
			});
		}

		// Add transition events
		transitions.forEach((tr) => {
			const label = tr.transition_type_display || tr.transition_type;
			let status = '';
			let metadata: TimelineEvent['metadata'] = {
				transition_type: tr.transition_type
			};

			if (tr.transition_type === 'PROMOTION' || tr.transition_type === 'TRANSFER' || tr.transition_type === 'HIRE') {
				status = tr.to_position?.name || tr.transition_type;
				Object.assign(metadata, {
					from: tr.from_position?.name,
					to: tr.to_position?.name,
					reason: tr.reason
				});
			} else if (tr.transition_type === 'OFFBOARD') {
				status = 'Départ';
				Object.assign(metadata, { reason: tr.reason });
			}

			timelineEvents.push({
				id: `transition-${tr.id}`,
				date: tr.date,
				created_at: tr.created_at,
				label: label,
				status: status,
				type: 'transition',
				description: tr.reason,
				metadata
			});
		});

		// Sort by created_at descending (precise datetime with microseconds)
		return timelineEvents.sort((a, b) => {
			const aTime = a.created_at ? new Date(a.created_at).getTime() : new Date(a.date).getTime();
			const bTime = b.created_at ? new Date(b.created_at).getTime() : new Date(b.date).getTime();
			return bTime - aTime;
		});
	}

	getTimelineEvents(): TimelineEvent[] {
		return this.#events;
	}
}


export const timelineEventStore = new TimelineEventStore();

