// Aligné avec backend PositionLevel enum

export type SeniorityLevel = 
  | 'TRAINEE' 
  | 'APPRENTICE' 
  | 'JUNIOR' 
  | 'INTERMEDIATE' 
  | 'SENIOR' 
  | 'LEAD' 
  | 'MANAGER' 
  | 'DIRECTOR' 
  | 'EXECUTIVE';


// Groupes pour l'affichage frontend
export const SENIORITY_GROUPS = {
  'DÉBUTANT': ['TRAINEE', 'APPRENTICE', 'JUNIOR'] as SeniorityLevel[],
  'INTERMÉDIAIRE': ['INTERMEDIATE'] as SeniorityLevel[],
  'CONFIRMÉ': ['SENIOR'] as SeniorityLevel[],
  'CADRE': ['LEAD', 'MANAGER'] as SeniorityLevel[],
  'DIRECTION': ['DIRECTOR', 'EXECUTIVE'] as SeniorityLevel[]
};


// Labels français pour affichage
export const SENIORITY_LABELS: Record<SeniorityLevel, string> = {
  'TRAINEE': 'Stagiaire',
  'APPRENTICE': 'Apprenti',
  'JUNIOR': 'Junior',
  'INTERMEDIATE': 'Intermédiaire',
  'SENIOR': 'Senior',
  'LEAD': 'Lead',
  'MANAGER': 'Manager',
  'DIRECTOR': 'Directeur',
  'EXECUTIVE': 'Exécutif'
};


export type NodeType = 
  | 'DEPARTMENT' 
  | 'DIVISION' 
  | 'TEAM' 
  | 'FUNCTION' 
  | 'BRANCH' 
  | 'PROJECT';


export interface SeniorityLevelDefinition {
	id: string;
	level: SeniorityLevel;  // Code technique (TRAINEE, JUNIOR, etc.)
	name: string;           // Label d'affichage
	rank: number;
	requirements: string[];
	/** Classe professionnelle RDC (1-7) — grille des catégories professionnelles */
	classe?: number | null;
	is_active?: boolean;
}


export interface Department {
	id: string;
	name: string;
	type: NodeType;
	parentId: string | null;
	managerId: string | null;
	managerName?: string;
	managerPhoto?: string;
	affointId?: string | null;
	affointName?: string;
	authorizedHeadcount: number;
	employeeCount?: number;
	totalEmployeeCount?: number;
}


export interface JobFamily {
	id: string;
	name: string;
	description?: string;
}

export interface PositionSeniority {
	id: string;
	position_id: string;
	seniority_level: SeniorityLevelDefinition;
	salary_min: number;
	salary_max: number;
	/** Échelon dans la grille (1-4) — progression intra-classe */
	echelon?: number | null;
	rank: number;
	next_level_id?: string | null;
	is_active: boolean;
}

export interface JobPosition {
	id: string;
	name: string;
	job_family: JobFamily;
	org_unit?: {
		id: string;
		name: string;
		type?: string;
	} | null;
	seniority_levels: PositionSeniority[];
	description?: string;
	requirements: string[];
	skills: {
		name: string;
		level: number; // 1-5
	}[];
}

export interface JobPositionCreate {
	name: string;
	family_name: string; 
	org_unit_id?: string | null;
	description?: string;
	seniority_levels: {
		seniority_level: SeniorityLevel;
		salary_min: number;
		salary_max: number;
		/** Échelon (1-4) optionnel */
		echelon?: number | null;
		rank: number;
		next_level_id?: string;
		is_active?: boolean;
	}[];
	requirements?: string[];
	skills?: { name: string; level: number }[];
}

export type JobPositionUpdate = Partial<{
	name: string;
	family_name: string;
	org_unit_id: string | null;
	description: string;
	seniority_levels: {
		seniority_level: SeniorityLevel;
		salary_min: number;
		salary_max: number;
		/** Échelon (1-4) optionnel */
		echelon?: number | null;
		rank: number;
		next_level_id?: string;
		is_active?: boolean;
	}[];
	requirements: string[];
	skills: { name: string; level: number }[];
}>;

export interface CareerPath {
	id: string;
	positionId: string;
	seniorityLevels: SeniorityLevel[];
	requirementsPerLevel: Record<string, string[]>;
}

export type TransitionType = 
  | 'PROMOTION' 
  | 'TRANSFER' 
  | 'HIRE' 
  | 'OFFBOARD';


export interface TransitionSeniorityLevel {
	id: string;
	level: string;
	rank: number;
	label: string;
	requirements: string[];
	is_active: boolean;
}

export interface Transition {
	id: string;
	employee_id: string;
	/** Full employee object from API (for display) */
	employee?: {
		id: string;
		matricule?: string;
		first_name?: string;
		middle_name?: string | null;
		last_name?: string;
		email?: string;
		gender?: string;
		phone?: string;
		is_active?: boolean;
	} | null;
	transition_type: string;
	transition_type_display?: string;
	date: string;
	reason?: string;
	created_at?: string;
	created_by_id?: string | null;
	/** Position IDs */
	from_position?: JobPosition | null;
	to_position?: JobPosition | null;
	/** Seniority level objects from API (snake_case as returned by backend) */
	from_seniority_level?: TransitionSeniorityLevel | null;
	to_seniority_level?: TransitionSeniorityLevel | null;
}


export type VacancyPriority = 'HIGH' | 'MEDIUM' | 'LOW';

export type VacancyStatus = 'OPEN' | 'IN_PROGRESS' | 'RECRUITMENT' | 'CANCELLED' | 'FILLED';

export interface Vacancy {
	id: string;
	positionId: string;
	position?: JobPosition;
	openedDate: string;
	targetDate?: string | null;
	priority: VacancyPriority;
	status: VacancyStatus;
	reason?: string | null;
	filledDate?: string | null;
	createdAt?: string;
	updatedAt?: string;
}



