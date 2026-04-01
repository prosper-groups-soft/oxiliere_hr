import type {
	Department,
	JobPosition,
	Vacancy,
	SeniorityLevelDefinition,
	Transition,
	SeniorityLevel
} from '../types/types';

const USE_JOBS_MOCK_DATA = false;

// Shared constants for defaults (Localized for RDC)
export const DEFAULT_SENIORITY_LEVELS: SeniorityLevelDefinition[] = [
	{ id: 's1', name: 'DÉBUTANT', rank: 1, requirements: ['Diplôme de graduat minimum'] },
	{
		id: 's2',
		name: 'INTERMÉDIAIRE',
		rank: 2,
		requirements: ["2+ ans d'expérience", 'Maîtrise des outils de base']
	},
	{
		id: 's3',
		name: 'CONFIRMÉ',
		rank: 3,
		requirements: ["5+ ans d'expérience", 'Autonomie complète']
	},
	{
		id: 's4',
		name: 'CADRE',
		rank: 4,
		requirements: ["10+ ans d'expérience", 'Expérience en management']
	},
	{
		id: 's5',
		name: 'DIRECTION',
		rank: 5,
		requirements: ["15+ ans d'expérience", 'Vision stratégique']
	}
];

export const STATIC_SENIORITY_COLORS: Record<string, string> = {
	DÉBUTANT: 'bg-blue-50 text-blue-700 border-blue-200',
	INTERMÉDIAIRE: 'bg-amber-50 text-amber-700 border-amber-200',
	CONFIRMÉ: 'bg-green-50 text-green-700 border-green-200',
	CADRE: 'bg-purple-50 text-purple-700 border-purple-200',
	DIRECTION: 'bg-red-50 text-red-700 border-red-200'
};

class JobsStore {
	// Reactive states
	departments = $state<Department[]>([]);
	positions = $state<JobPosition[]>([]);
	seniorityLevels = $state<SeniorityLevelDefinition[]>([]);
	vacancies = $state<Vacancy[]>([]);
	transitions = $state<Transition[]>([]);

	// Selection/UI states
	selectedDeptId = $state<string | null>(null);
	searchQuery = $state('');

	constructor() {
		// Initialize with defaults if not provided (or mock)
		const useMockData = USE_JOBS_MOCK_DATA;
		if (useMockData) {
			this.initializeMockData();
		} else {
			this.seniorityLevels = [...DEFAULT_SENIORITY_LEVELS];
		}
	}

	/**
	 * Mock data initialization for development
	 */
	private initializeMockData() {
		this.departments = [
			{
				id: '1',
				name: 'Direction Générale',
				type: 'DEPARTMENT',
				parentId: null,
				managerId: 'm1',
				managerName: 'Jean Dupont',
				affointId: null,
				authorizedHeadcount: 5
			},
			{
				id: '2',
				name: 'Technique',
				type: 'DEPARTMENT',
				parentId: '1',
				managerId: 'm2',
				managerName: 'Alice Martin',
				affointId: 'm6',
				authorizedHeadcount: 25
			},
			{
				id: '3',
				name: 'Produit',
				type: 'DEPARTMENT',
				parentId: '1',
				managerId: 'm3',
				managerName: 'Bob Smith',
				affointId: null,
				authorizedHeadcount: 12
			},
			{
				id: '4',
				name: 'Frontend',
				type: 'TEAM',
				parentId: '2',
				managerId: 'm4',
				managerName: 'Charlie Brown',
				affointId: null,
				authorizedHeadcount: 10
			},
			{
				id: '5',
				name: 'Backend',
				type: 'TEAM',
				parentId: '2',
				managerId: 'm5',
				managerName: 'Diana Prince',
				affointId: null,
				authorizedHeadcount: 15
			}
		];

		this.positions = [
			{
				id: 'p1',
				title: 'Senior Frontend Dev',
				departmentId: '4',
				seniority: 'CONFIRMÉ',
				salaryRange: { min: 45000, max: 65000, currency: 'EUR' },
				requirements: ['Vue.js', 'TypeScript', 'Svelte 5'],
				skills: [
					{ name: 'Javascript', level: 5 },
					{ name: 'UI/UX', level: 4 }
				]
			},
			{
				id: 'p2',
				title: 'Junior Frontend Dev',
				departmentId: '4',
				seniority: 'DÉBUTANT',
				salaryRange: { min: 35000, max: 42000, currency: 'EUR' },
				requirements: ['Javascript', 'CSS'],
				skills: [{ name: 'Javascript', level: 3 }]
			}
		];

		this.seniorityLevels = [...DEFAULT_SENIORITY_LEVELS];

		this.vacancies = [
			{
				id: 'v1',
				positionId: 'p2',
				openedDate: '2026-02-01',
				priority: 'HIGH',
				status: 'OPEN'
			}
		];

		this.transitions = [
			{
				id: 't1',
				employeeId: 'e1',
				type: 'PROMOTION',
				date: '2026-01-15',
				fromPositionId: 'p2',
				toPositionId: 'p1',
				fromDepartmentId: '4',
				toDepartmentId: '4',
				reason: 'Excellente performance annuelle'
			},
			{
				id: 't2',
				employeeId: 'e2',
				type: 'TRANSFER',
				date: '2026-02-10',
				fromPositionId: 'p1',
				toPositionId: 'p1',
				fromDepartmentId: '5',
				toDepartmentId: '4',
				reason: 'Renforcement équipe frontend'
			}
		];
	}

	// --- Derived states ---

	/**
	 * Returns a map of departments by parentId for tree building
	 */
	get departmentsByParent() {
		const map = new Map<string | null, Department[]>();
		this.departments.forEach((dept) => {
			const children = map.get(dept.parentId) || [];
			children.push(dept);
			map.set(dept.parentId, children);
		});
		return map;
	}

	/**
	 * Root departments (parentId === null)
	 */
	get rootDepartments() {
		return this.departments.filter((d) => d.parentId === null);
	}

	/**
	 * Helper to get seniority labels dynamically
	 */
	get seniorityLabels(): Record<string, string> {
		const labels: Record<string, string> = {};
		this.seniorityLevels.forEach((lvl) => {
			// Capitalize first letter of name for the label if not already nice
			labels[lvl.name] = lvl.name.charAt(0).toUpperCase() + lvl.name.slice(1).toLowerCase();
		});
		return labels;
	}

	getSeniorityColor(levelName: string): string {
		return STATIC_SENIORITY_COLORS[levelName] || 'bg-slate-50 text-slate-700 border-slate-200';
	}

	// --- Actions ---

	setDept(id: string | null) {
		this.selectedDeptId = id;
	}

	getDepartmentById(id: string) {
		return this.departments.find((d) => d.id === id);
	}

	getChildDepartments(parentId: string) {
		return this.departments.filter((d) => d.parentId === parentId);
	}

	addDepartment(dept: Omit<Department, 'id'>) {
		const newDept: Department = {
			...dept,
			id: crypto.randomUUID()
		};
		this.departments = [...this.departments, newDept];
		return newDept;
	}

	updateDepartment(id: string, data: Partial<Omit<Department, 'id'>>) {
		this.departments = this.departments.map((d) => (d.id === id ? { ...d, ...data } : d));
	}

	deleteDepartment(id: string) {
		// Re-parent children to the deleted dept's parent
		const dept = this.getDepartmentById(id);
		if (dept) {
			this.departments = this.departments
				.filter((d) => d.id !== id)
				.map((d) => (d.parentId === id ? { ...d, parentId: dept.parentId } : d));
		}
	}

	// --- Positions Actions ---

	addPosition(pos: Omit<JobPosition, 'id'>) {
		const newPos: JobPosition = {
			...pos,
			id: crypto.randomUUID()
		};
		this.positions = [...this.positions, newPos];
		return newPos;
	}

	updatePosition(id: string, data: Partial<Omit<JobPosition, 'id'>>) {
		this.positions = this.positions.map((p) => (p.id === id ? { ...p, ...data } : p));
	}

	deletePosition(id: string) {
		this.positions = this.positions.filter((p) => p.id !== id);
	}

	// --- Seniority Actions ---

	addSeniorityLevel(level: Omit<SeniorityLevelDefinition, 'id'>) {
		const newLevel: SeniorityLevelDefinition = {
			...level,
			id: crypto.randomUUID()
		};
		this.seniorityLevels = [...this.seniorityLevels, newLevel].sort((a, b) => a.rank - b.rank);
		return newLevel;
	}

	updateSeniorityLevel(id: string, data: Partial<Omit<SeniorityLevelDefinition, 'id'>>) {
		this.seniorityLevels = this.seniorityLevels
			.map((s) => (s.id === id ? { ...s, ...data } : s))
			.sort((a, b) => a.rank - b.rank);
	}

	deleteSeniorityLevel(id: string) {
		this.seniorityLevels = this.seniorityLevels.filter((s) => s.id !== id);
	}

	restoreDefaultSeniorityLevels() {
		this.seniorityLevels = [...DEFAULT_SENIORITY_LEVELS];
	}

	// --- Transitions Actions ---

	addTransition(trans: Omit<Transition, 'id'>) {
		const newTrans: Transition = {
			...trans,
			id: crypto.randomUUID()
		};
		this.transitions = [...this.transitions, newTrans];
		return newTrans;
	}

	updateTransition(id: string, data: Partial<Omit<Transition, 'id'>>) {
		this.transitions = this.transitions.map((t) => (t.id === id ? { ...t, ...data } : t));
	}

	deleteTransition(id: string) {
		this.transitions = this.transitions.filter((t) => t.id !== id);
	}

	// --- Vacancies Actions ---

	addVacancy(vac: Omit<Vacancy, 'id'>) {
		const newVac: Vacancy = {
			...vac,
			id: crypto.randomUUID()
		};
		this.vacancies = [...this.vacancies, newVac];
		return newVac;
	}

	updateVacancy(id: string, data: Partial<Omit<Vacancy, 'id'>>) {
		this.vacancies = this.vacancies.map((v) => (v.id === id ? { ...v, ...data } : v));
	}

	deleteVacancy(id: string) {
		this.vacancies = this.vacancies.filter((v) => v.id !== id);
	}
}

export const jobsStore = new JobsStore();
