
export interface EmployeeContractSalaryInfo {
	id: string | number;
	contract_type?: string;
	remuneration_type?: string;
	base_salary?: number;
	salary_base_type?: string; // 'GROSS' | 'NET'
	hourly_rate?: number | null;
	currency?: string;
	start_date?: string;
	end_date?: string | null;
}

export interface Employee {
	id: string | number;
	name: string;
	jobTitle: string;
	orgUnit?: string; // Nom de l'unité org (anciennement unité)
	orgUnitType?: string; // Type de l'unité org (e.g., 'DEPARTMENT', 'TEAM')
	positionId?: string;
	orgUnitId?: string; // ID de l'unité org (anciennement orgUnitId)
	status: string;
	location: string;
	contractType: string;
	joinDate: string;
	phone: string;
	email: string;
	avatarUrl: string;
	role: string;
	birthDate?: string;
	// Contrat courant (source unique, enrichie côté backend — pas de cascade)
	currentContract?: EmployeeContractSalaryInfo | null;
	// Éléments de paie S10 assignés au contrat courant
	contractPayElements?: ContractPayElementItem[];
	// Champs bruts API (snake_case)
	first_name?: string;
	last_name?: string;
	middle_name?: string;
	matricule?: string;
	is_active?: boolean;
	can_connect?: boolean;
	gender?: string;
	nationality?: string;
	marital_status?: string;
	description?: string;
	hire_date?: string;
	termination_date?: string | null;
	profile_photo?: string | null;
	current_status?: EmployeeStatusHistory | null;
}

export interface EmployeeFilters {
	orgUnit?: string[];
	status?: string[];
	location?: string[];
	contractType?: string[];
	gender?: string;
	marital_status?: string;
	is_active?: boolean;
	has_scheme?: boolean;
	has_active_contract?: boolean;
}

export interface EmployeeAddress {
	id: string;
	number?: string;
	street?: string;
	municipality?: string;
	city?: string;
	province?: string;
	country?: string;
	country_code?: string;
	is_current?: boolean;
	move_in_date?: string;
	move_out_date?: string | null;
}

export interface EmployeeChild {
	id: string;
	first_name: string;
	middle_name?: string;
	last_name: string;
	gender?: string;
	birthdate?: string;
	is_dependent?: boolean;
}

export interface EmployeeEducation {
	id: string;
	institute: string;
	degree: string;
	major?: string;
	start_year?: number;
	end_year?: number;
	location?: string;
}

export interface EmployeeEmergencyContact {
	id: string;
	first_name: string;
	middle_name?: string;
	last_name: string;
	phone?: string;
	relation?: string;
	priority?: number;
	is_primary?: boolean;
}

export interface EmployeeDocument {
	id: string;
	document_type: string;
	document_number?: string;
	issue_date?: string;
	expiry_date?: string | null;
	file?: string | null;
	is_verified?: boolean;
}

export interface EmployeeStatusHistory {
	id: string;
	status: string;
	start_date: string;
	end_date?: string | null;
	reason?: string;
	created_at?: string;
}

export interface EmployeePositionHistory {
	id: string;
	position_name: string;
	seniority_label?: string;
	org_unit_name?: string;
	start_date: string;
	end_date?: string | null;
	is_current: boolean;
	description?: string;
	created_at?: string;
}

export interface EmployeeTransition {
	id: string;
	employee_id: string;
	transition_type: string;
	transition_type_display?: string;
	from_position?: { id: string; name: string };
	from_seniority_level?: { id: string; label: string };
	to_position?: { id: string; name: string };
	to_seniority_level?: { id: string; label: string };
	date: string;
	reason?: string;
	created_at?: string;
}

export interface EmployeeContract {
	id: string;
	remuneration_type: string;
	contract_type: string;
	base_salary?: number;
	salary_base_type: string;
	hourly_rate?: number;
	currency: string;
	start_date: string;
	end_date?: string | null;
	is_active: boolean;
	/** Clauses particulières du contrat */
	contractual_clauses?: string;
	/** Éléments de paie assignés à ce contrat (S10) */
	pay_elements?: ContractPayElementItem[];
	created_at: string;
	updated_at: string;
}

/** Élément de paie d'un contrat (S10) — miroir du backend ContractAdjustment */
export interface ContractPayElementItem {
	id: string;
	catalog_code?: string | null;
	label: string;
	value_type: string;
	amount: number | null;
	custom_amount: number | null;
	custom_percentage: number | null;
	is_active: boolean;
	is_taxable: boolean;
	recurrence: string;
	start_period: string;
	end_period: string | null;
}

export interface EmployeeFullProfile {
	id: string;
	matricule: string;
	first_name: string;
	middle_name?: string;
	last_name: string;
	email: string;
	phone?: string;
	gender?: string;
	birthdate?: string;
	nationality?: string;
	marital_status?: string;
	description?: string;
	hire_date?: string;
	termination_date?: string | null;
	is_active: boolean;
	can_connect?: boolean;
	profile_photo?: string | null;
	work_site?: string | null;
	work_site_id?: string | null;
	job_title?: string | null;
	seniority_level?: string | null;
	seniority_level_id?: string | null;
	org_unit?: string | null;
	org_unit_id?: string | null;
	org_unit_type?: string | null;
	// Relations
	addresses: EmployeeAddress[];
	children: EmployeeChild[];
	educations: EmployeeEducation[];
	emergency_contacts: EmployeeEmergencyContact[];
	documents: EmployeeDocument[];
	status_history: EmployeeStatusHistory[];
	position_history: EmployeePositionHistory[];
	current_address?: EmployeeAddress | null;
	current_status?: EmployeeStatusHistory | null;
	current_contract?: EmployeeContract | null;
	/** Éléments de paie du contrat courant (S10) */
	contract_adjustments?: ContractPayElementItem[];
	user?: {
		id: string;
		email: string;
		first_name: string;
		last_name: string;
		is_active: boolean;
		photo?: string | null;
	} | null;
}

export interface EmployeeCreate {
	first_name: string;
	middle_name?: string;
	last_name: string;
	email: string;
	phone?: string;
	gender?: string;
	birthdate?: string;
	nationality?: string;
	marital_status?: string;
	work_site?: string;
	hire_date?: string;
	description?: string;
	create_account?: boolean;
	group_slug?: string;
	initial_status?: 'ACTIVE' | 'PROBATION' | 'PENDING';
}

export interface EmployeeUpdate {
	first_name?: string;
	middle_name?: string;
	last_name?: string;
	email?: string;
	phone?: string;
	gender?: string;
	birthdate?: string;
	nationality?: string;
	marital_status?: string;
	description?: string;
	work_site?: string;
	address?: OnboardingAddressData;
}

export interface TimelineEvent {
	id: number | string;
	date: string;
	created_at?: string;
	label: string;
	status: string;
	type: 'status' | 'transition';
	description?: string;
	metadata?: {
		from?: string;
		to?: string;
		reason?: string;
		transition_type?: string;
		seniority?: string;
		org_unit?: string;
		org_unit_type?: string;
	};
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
	priority?: number;
}

export interface Child {
	id: number | string;
	name: string;
	birthDate: string;
	gender?: 'MALE' | 'FEMALE' | 'NOT_SPECIFIED';
	isDependent?: boolean;
}


// ============================================
// ONBOARDING TYPES
// ============================================

export interface OnboardingIdentityData {
	profile_photo?: File | null;
	first_name: string;
	middle_name?: string;
	last_name: string;
	email: string;
	phone?: string;
	birthdate?: string;
	gender?: 'MALE' | 'FEMALE' | 'NOT_SPECIFIED';
	nationality?: string;
	marital_status?: 'SINGLE' | 'MARRIED' | 'DIVORCED' | 'WIDOWED';
	work_site?: string;
	address?: OnboardingAddressData;
}

export interface OnboardingAddressData {
	number?: string;
	street?: string;
	municipality?: string;
	city?: string;
	province?: string;
	country_code?: string;
}

export interface OnboardingAccountData {
	create_account: boolean;
	group_slug?: string;
}

export interface OnboardingContractData {
	position_id: string;
	seniority_level_id: string;
	contract_type: 'CDI' | 'CDD' | 'INTERNSHIP' | 'PROBATION' | 'FREELANCE';
	salary: number;
	hire_date: string;
	remuneration_type: 'FIXED' | 'HOURLY';
	salary_base_type: 'GROSS' | 'NET';
	currency: 'CDF' | 'USD' | 'EUR';
	end_date?: string;
	is_active?: boolean;
	initial_status?: 'ACTIVE' | 'PROBATION' | 'PENDING';
	// Métamodèle (Règle 5)
	contractual_clauses?: string;
	// S10 — éléments de paie sélectionnés pendant l'onboarding
	contract_adjustments?: ContractPayElementItem[];
}

export interface OnboardingDocumentItem {
	id: string;
	file: File;
	document_type: "NATIONAL_ID" | "VOTER_CARD" | "PASSPORT" | "DRIVING_LICENSE" | "DIPLOMA" | "RESIDENCE_PERMIT" | "PHOTO" | "CRIMINAL_RECORD" | "OTHER";
	document_number?: string;
	issue_date?: string;
	expiry_date?: string;
}

export interface OnboardingFamilyData {
	emergency_contacts: EmergencyContact[];
	children: Child[];
}

export interface OnboardingEducationItem {
	degree: string;
	institute: string;
	major?: string;
	start_year?: number;
	end_year?: number;
	location?: string;
}

export interface OnboardingEducationData {
	educations: OnboardingEducationItem[];
}

export interface OnboardingSubmitData {
	identity: OnboardingIdentityData;
	account?: OnboardingAccountData;
	contract: OnboardingContractData;
	documents: OnboardingDocumentItem[];
	family: OnboardingFamilyData;
	education: OnboardingEducationData;
}

export interface EmployeeContractCreate {
	position_id: string;
	seniority_level_id: string;
	contract_type: string;
	base_salary: number;
	remuneration_type: string;
	salary_base_type: string;
	start_date: string;
	end_date?: string | null;
	currency: string;
	is_active: boolean;
	/** Clauses particulières */
	contractual_clauses?: string;
}

export interface OnboardingResult {
	success: boolean;
	employee?: Employee;
	errors?: Record<string, string[]>;
}

