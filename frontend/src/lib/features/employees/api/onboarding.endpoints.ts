import APIEndPoint from '@/utilities/http/rest';
import type {
	Employee,
	EmployeeCreate,
	EmployeeContractCreate,
	EmergencyContact,
	Child
} from '../types/types';


/**
 * Endpoints API pour l'onboarding des employés
 * Base path: /api/employees
 */
export const onboardingEndpoint = {
	/**
	 * POST /api/employees/
	 * Crée un nouvel employé (Phase 1: Identity + Account)
	 * Retourne l'employé créé avec son matricule
	 */
	async createEmployee(data: EmployeeCreate): Promise<Employee> {
		const endpoint = new APIEndPoint('/api/employees/', '/api/employees/');
		const response = await endpoint.create(data);
		// Backend returns {201: EmployeeOut}, extract the employee data
		return response[1] || response;
	},

	/**
	 * POST /api/employees/{id}/contracts
	 * Crée un contrat pour l'employé (Phase 2a)
	 */
	async createContract(
		employeeId: string,
		data: EmployeeContractCreate
	): Promise<{ id: string; employee_id: string; position_id: string }> {
		const endpoint = new APIEndPoint(
			`/api/employees/${employeeId}/contracts`,
			`/api/employees/${employeeId}/contracts`
		);
		return await endpoint.create(data);
	},

	/**
	 * POST /api/employees/{id}/upload-photo
	 * Upload la photo de profil (Phase 2b)
	 * Multipart form data
	 */
	async uploadProfilePhoto(
		employeeId: string,
		file: File
	): Promise<{ photo_url: string }> {
		const formData = new FormData();
		formData.append('file', file);

		const endpoint = new APIEndPoint(
			`/api/employees/${employeeId}/upload-photo`,
			`/api/employees/${employeeId}/upload-photo`
		);
		return await endpoint.create(formData);
	},

	/**
	 * POST /api/employees/{id}/documents
	 * Upload un document (Phase 2c)
	 * Multipart form data avec métadonnées
	 */
	async uploadDocument(
		employeeId: string,
		file: File,
		metadata: {
			document_type: string;
			document_number?: string;
			issue_date?: string;
			expiry_date?: string;
		}
	): Promise<{ id: string; file_url: string }> {
		const formData = new FormData();
		formData.append('file', file);
		formData.append('data', JSON.stringify(metadata));

		const endpoint = new APIEndPoint(
			`/api/employees/${employeeId}/documents`,
			`/api/employees/${employeeId}/documents`
		);
		return await endpoint.create(formData);
	},

	/**
	 * POST /api/employees/{id}/emergency-contacts
	 * Ajoute un contact d'urgence (Phase 2d)
	 */
	async addEmergencyContact(
		employeeId: string,
		data: {
			first_name?: string;
			middle_name?: string;
			last_name: string;
			phone?: string;
			relation?: string;
			priority?: number;
			is_primary?: boolean;
		}
	): Promise<EmergencyContact> {
		const endpoint = new APIEndPoint(
			`/api/employees/${employeeId}/emergency-contacts`,
			`/api/employees/${employeeId}/emergency-contacts`
		);
		return await endpoint.create(data);
	},

	/**
	 * POST /api/employees/{id}/family/children
	 * Ajoute un enfant (Phase 2d)
	 */
	async addChild(
		employeeId: string,
		data: {
			first_name?: string;
			middle_name?: string;
			last_name: string;
			gender?: string;
			birthdate?: string;
			is_dependent?: boolean;
		}
	): Promise<Child> {
		const endpoint = new APIEndPoint(
			`/api/employees/${employeeId}/family/children`,
			`/api/employees/${employeeId}/family/children`
		);
		return await endpoint.create(data);
	},

	/**
	 * GET /api/jobs/positions
	 * Récupère la liste des positions disponibles pour l'onboarding
	 */
	async getPositions(): Promise<
		Array<{
			id: string;
			name: string;
			org_unit: {
				id: string;
				name: string;
				type: string;
			};
			job_family?: {
				id: string;
				name: string;
				description?: string;
			};
			description?: string;
			requirements?: string[];
			skills?: any[];
			seniority_levels?: any[];
		}>
	> {
		const endpoint = new APIEndPoint(
			'/api/jobs/positions', 
			'/api/jobs/positions'
		);
		const response = await endpoint.list();
		return Array.isArray(response) ? response : (response.results || []);
	},

	/**
	 * GET /api/jobs/positions/{id}/seniority-levels
	 * Récupère les niveaux de séniorité pour une position
	 */
	async getPositionSeniorityLevels(
		positionId: string
	): Promise<
		Array<{
			id: string;
			level: string;
			label: string;
			rank: number;
		}>
	> {
		const endpoint = new APIEndPoint(
			`/api/jobs/positions/${positionId}/seniority-levels`,
			`/api/jobs/positions/${positionId}/seniority-levels`
		);
		return await endpoint.list();
	},

	/**
	 * POST /api/employees/{id}/address
	 * Ajoute une adresse pour l'employé (Phase 2f)
	 */
	async addEmployeeAddress(
		employeeId: string,
		data: {
			number?: string;
			street?: string;
			municipality?: string;
			city?: string;
			province?: string;
			country?: string;
			country_code?: string;
		}
	): Promise<{ id: string; message: string }> {
		const endpoint = new APIEndPoint(
			`/api/employees/${employeeId}/address`,
			`/api/employees/${employeeId}/address`
		);
		return await endpoint.create(data);
	},

	/**
	 * DELETE /api/employees/{id}
	 * Supprime un employé (rollback onboarding)
	 */
	async deleteEmployee(employeeId: string): Promise<void> {
		const endpoint = new APIEndPoint(
			`/api/employees/${employeeId}`,
			`/api/employees/${employeeId}`
		);
		await endpoint.destroy();
	},

	/**
	 * POST /api/employees/{id}/education
	 * Ajoute une éducation pour l'employé (Phase 2g)
	 */
	async addEducation(
		employeeId: string,
		data: {
			degree: string;
			institute: string;
			major?: string;
			location?: string;
			start_year?: number;
			end_year?: number;
		}
	): Promise<{ id: string; message: string }> {
		const endpoint = new APIEndPoint(
			`/api/employees/${employeeId}/education`,
			`/api/employees/${employeeId}/education`
		);
		return await endpoint.create(data);
	}
};

