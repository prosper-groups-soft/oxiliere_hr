export interface Employee {
	id: number;
	name: string;
	jobTitle: string;
	department: string;
	positionId?: string;
	departmentId?: string;
	status: string;
	location: string;
	contractType: string;
	joinDate: string;
	phone: string;
	email: string;
	avatarUrl: string;
	role: string;
	birthDate?: string;
}

export interface EmployeeFilters {
	department: string[];
	status: string[];
	location: string[];
}

export interface TimelineEvent {
	id: number | string;
	date: string;
	label: string;
	status: string;
}

export interface Document {
	id: number | string;
	name: string;
	type: string;
	size: string;
	expiry: string | null;
	status: 'valid' | 'warning' | 'expired';
	url: string | null;
}

export interface EmergencyContact {
	id: number | string;
	name: string;
	relation: string;
	phone: string;
	primary: boolean;
}

export interface Child {
	id: number | string;
	name: string;
	birthDate: string;
	gender: string;
}
