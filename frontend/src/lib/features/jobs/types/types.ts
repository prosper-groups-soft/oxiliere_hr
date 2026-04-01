export type SeniorityLevel = 'DÉBUTANT' | 'INTERMÉDIAIRE' | 'CONFIRMÉ' | 'CADRE' | 'DIRECTION';

export type NodeType = 'DEPARTMENT' | 'TEAM' | 'FUNCTION';

export interface SeniorityLevelDefinition {
	id: string;
	name: string;
	rank: number;
	requirements: string[];
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
}

export interface JobPosition {
	id: string;
	title: string;
	departmentId: string;
	seniority: SeniorityLevel;
	salaryRange: {
		min: number;
		max: number;
		currency: string;
	};
	requirements: string[];
	skills: {
		name: string;
		level: number; // 1-5
	}[];
}

export interface CareerPath {
	id: string;
	positionId: string;
	seniorityLevels: SeniorityLevel[];
	requirementsPerLevel: Record<string, string[]>;
}

export type TransitionType = 'PROMOTION' | 'TRANSFER' | 'HIRE' | 'OFFBOARD';

export interface Transition {
	id: string;
	employeeId: string;
	type: TransitionType;
	date: string;
	fromPositionId?: string;
	toPositionId: string;
	fromDepartmentId?: string;
	toDepartmentId: string;
	reason?: string;
}

export interface Vacancy {
	id: string;
	positionId: string;
	openedDate: string;
	priority: 'LOW' | 'MEDIUM' | 'HIGH';
	status: 'OPEN' | 'IN_PROGRESS' | 'CANCELLED';
}

export interface Certification {
	id: string;
	name: string;
	issuedDate: string;
	expiryDate: string | null;
	status: 'VALID' | 'EXPIRING' | 'EXPIRED';
}
