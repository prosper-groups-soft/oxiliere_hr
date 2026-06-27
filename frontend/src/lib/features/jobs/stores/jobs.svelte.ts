import type {
	JobPosition,
	Vacancy,
	SeniorityLevelDefinition,
	Transition,
	JobFamily
} from '../types/types';
import type { 
	OrgUnit, 
	OrgUnitCreate, 
	OrgUnitUpdate 
} from '../types/org.types';
import { orgService } from '../services/org.service';


// Couleurs statiques pour les niveaux de séniorité
export const STATIC_SENIORITY_COLORS: Record<string, string> = {
	// Débutant (bleu)
	TRAINEE: 'bg-blue-50 text-blue-700 border-blue-200',
	APPRENTICE: 'bg-blue-100 text-blue-800 border-blue-300',
	JUNIOR: 'bg-blue-200 text-blue-900 border-blue-400',
	// Intermédiaire (ambre)
	INTERMEDIATE: 'bg-amber-50 text-amber-700 border-amber-200',
	// Confirmé (vert)
	SENIOR: 'bg-green-50 text-green-700 border-green-200',
	// Cadre (violet)
	LEAD: 'bg-purple-50 text-purple-700 border-purple-200',
	MANAGER: 'bg-purple-100 text-purple-800 border-purple-300',
	// Direction (rouge)
	DIRECTOR: 'bg-red-50 text-red-700 border-red-200',
	EXECUTIVE: 'bg-red-100 text-red-800 border-red-300'
};


class JobsStore {
	// Reactive states - Org Units
	orgUnits = $state<OrgUnit[]>([]);
	positions = $state<JobPosition[]>([]);
	seniorityLevels = $state<SeniorityLevelDefinition[]>([]);
	jobFamilies = $state<JobFamily[]>([]);
	vacancies = $state<Vacancy[]>([]);
	transitions = $state<Transition[]>([]);

	// Selection/UI states
	selectedOrgUnitId = $state<string | null>(null);
	searchQuery = $state('');

	constructor() {
		// Les niveaux de séniorité sont chargés dynamiquement depuis le backend
		this.seniorityLevels = [];
	}

	// Charger les niveaux de séniorité depuis le backend
	setSeniorityLevels(levels: SeniorityLevelDefinition[]) {
		this.seniorityLevels = levels;
	}

	// Charger les familles de métiers depuis le backend
	setJobFamilies(families: JobFamily[]) {
		this.jobFamilies = families;
	}

	// --- Derived states ---

	/**
	 * Returns a map of org units by parentId for tree building
	 */
	get orgUnitsByParent() {
		const map = new Map<string | null, OrgUnit[]>();
		this.orgUnits.forEach((orgUnit) => {
			const children = map.get(orgUnit.parentId) || [];
			children.push(orgUnit);
			map.set(orgUnit.parentId, children);
		});
		return map;
	}

	/**
	 * Root org units (parentId === null)
	 */
	get rootOrgUnits() {
		return this.orgUnits.filter((orgUnit) => orgUnit.parentId === null);
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

	/**
	 * Charge les unités org depuis le backend
	 * Appelé par les queries après un fetch
	 */
	setOrgUnits(orgUnits: OrgUnit[]) {
		this.orgUnits = orgUnits;
	}

	setOrgUnit(id: string | null) {
		this.selectedOrgUnitId = id;
	}

	// --- Org Unit Actions (modern naming) ---

	getOrgUnitById(id: string) {
		return this.orgUnits.find((u) => u.id === id);
	}

	getChildOrgUnits(parentId: string) {
		return this.orgUnits.filter((u) => u.parentId === parentId);
	}

	getDeleteOrgUnitGuard(orgUnit: OrgUnit): string | null {
		const childCount = this.getChildOrgUnits(orgUnit.id).length;
		if (childCount > 0) {
			return `Impossible de supprimer "${orgUnit.name}" tant qu'il contient ${childCount} sous-unité(s). Déplacez ou supprimez d'abord les sous-unités.`;
		}

		const activeEmployees = orgUnit.employeeCount ?? 0;
		if (activeEmployees > 0) {
			return `Impossible de supprimer "${orgUnit.name}" tant que ${activeEmployees} employé(s) y sont encore affecté(s). Réaffectez-les d'abord.`;
		}

		return null;
	}

	async addOrgUnit(data: OrgUnitCreate) {
		const newUnit = await orgService.createOrgUnit(data);
		this.orgUnits = [...this.orgUnits, newUnit];
		return newUnit;
	}

	async updateOrgUnit(id: string, data: OrgUnitUpdate) {
		const updatedOrgUnit = await orgService.updateOrgUnit(id, data);
		this.orgUnits = this.orgUnits.map((u) => (u.id === id ? updatedOrgUnit : u));
		return updatedOrgUnit;
	}

	async deleteOrgUnit(id: string) {
		await orgService.deleteOrgUnit(id);
		this.orgUnits = this.orgUnits.filter((u) => u.id !== id);
		if (this.selectedOrgUnitId === id) {
			this.selectedOrgUnitId = null;
		}
	}

	async transferLeadership(orgUnitId: string, newManagerId: string) {
		const updatedOrgUnit = await orgService.transferLeadership(orgUnitId, newManagerId);
		this.orgUnits = this.orgUnits.map((u) => (u.id === orgUnitId ? updatedOrgUnit : u));
		return updatedOrgUnit;
	}

	// --- Positions Actions ---

	addPosition(pos: Omit<JobPosition, 'id'>) {
		// TODO: Call backend API to create, then add to store with returned ID
		console.warn('addPosition: Backend integration needed to get ID');
		return pos as JobPosition;
	}

	updatePosition(id: string, data: Partial<Omit<JobPosition, 'id'>>) {
		this.positions = this.positions.map((p) => (p.id === id ? { ...p, ...data } : p));
	}

	deletePosition(id: string) {
		this.positions = this.positions.filter((p) => p.id !== id);
	}

	// --- Seniority Actions ---

	addSeniorityLevel(level: Omit<SeniorityLevelDefinition, 'id'>) {
		// TODO: Call backend API to create, then add to store with returned ID
		console.warn('addSeniorityLevel: Backend integration needed to get ID');
		return level as SeniorityLevelDefinition;
	}

	updateSeniorityLevel(id: string, data: Partial<Omit<SeniorityLevelDefinition, 'id'>>) {
		this.seniorityLevels = this.seniorityLevels
			.map((s) => (s.id === id ? { ...s, ...data } : s))
			.sort((a, b) => a.rank - b.rank);
	}

	deleteSeniorityLevel(id: string) {
		this.seniorityLevels = this.seniorityLevels.filter((s) => s.id !== id);
	}

	// --- Transitions Actions ---

	/**
	 * Charge toutes les transitions depuis le backend
	 * Appelé par les queries après un fetch
	 */
	setTransitions(transitions: Transition[]) {
		this.transitions = transitions;
	}

	/**
	 * Ajoute une transition au store (appelé par mutation après succès API)
	 */
	addTransition(trans: Transition) {
		// Vérifier si la transition existe déjà (éviter les doublons)
		const exists = this.transitions.some((t) => t.id === trans.id);
		if (!exists) {
			this.transitions = [trans, ...this.transitions];
		}
	}

	/**
	 * Met à jour une transition dans le store
	 */
	updateTransition(id: string, data: Partial<Transition>) {
		this.transitions = this.transitions.map((t) => (t.id === id ? { ...t, ...data } : t));
	}

	/**
	 * Supprime une transition du store
	 */
	deleteTransition(id: string) {
		this.transitions = this.transitions.filter((t) => t.id !== id);
	}

	// --- Vacancies Actions ---

	setVacancies(vacancies: Vacancy[]) {
		this.vacancies = vacancies;
	}

	addVacancy(vac: Omit<Vacancy, 'id'>) {
		// TODO: Call backend API to create, then add to store with returned ID
		console.warn('addVacancy: Backend integration needed to get ID');
		return vac as Vacancy;
	}

	updateVacancy(id: string, data: Partial<Omit<Vacancy, 'id'>>) {
		this.vacancies = this.vacancies.map((v) => (v.id === id ? { ...v, ...data } : v));
	}
	deleteVacancy(id: string) {
		this.vacancies = this.vacancies.filter((v) => v.id !== id);
	}
}


export const jobsStore = new JobsStore();
