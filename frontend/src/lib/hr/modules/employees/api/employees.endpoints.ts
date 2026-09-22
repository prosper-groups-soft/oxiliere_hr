import APIEndPoint from '@/hr/utilities/http/rest';
import type { PaginatedResponse } from '@/hr/types/pagination';
import type {
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  EmployeeFullProfile,
  EmployeeFilters
} from '../types/types';


/**
 * Endpoints API pour la gestion des employés
 * Base path: /api/employees
 */
export const employeesEndpoint = {
  /**
   * GET /api/employees
   * Liste tous les employés avec pagination par curseur
   */
  list: async (params?: { 
    page?: number; 
    limit?: number;
    search?: string;
    filters?: EmployeeFilters;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }): Promise<PaginatedResponse<Employee>> => {
    	const queryParams = new URLSearchParams();
    	if (params?.page) queryParams.set('page', params.page.toString());
    	if (params?.limit) queryParams.set('page_size', params.limit.toString());
    	if (params?.search) queryParams.set('search', params.search);
    
    // Add filter params (only if they have values)
    if (params?.filters) {
      if (params.filters.gender) queryParams.set('gender', params.filters.gender);
      if (params.filters.marital_status) queryParams.set('marital_status', params.filters.marital_status);
      if (params.filters.is_active !== undefined) queryParams.set('active_only', params.filters.is_active.toString());
      if (params.filters.has_scheme !== undefined) queryParams.set('has_scheme', params.filters.has_scheme.toString());
      if (params.filters.has_active_contract !== undefined) queryParams.set('has_active_contract', params.filters.has_active_contract.toString());
      const orgUnitValue = params.filters.orgUnit || params.filters.orgUnit;
      if (orgUnitValue && (Array.isArray(orgUnitValue) ? orgUnitValue.length > 0 : orgUnitValue)) {
        queryParams.set('org_unit', Array.isArray(orgUnitValue) ? orgUnitValue.join(',') : orgUnitValue);
      }
      
      const statusValue = params.filters.status;
      if (statusValue && (Array.isArray(statusValue) ? statusValue.length > 0 : statusValue)) {
        queryParams.set('status', Array.isArray(statusValue) ? statusValue.join(',') : statusValue);
      }
      
      const locValue = params.filters.location;
      if (locValue && (Array.isArray(locValue) ? locValue.length > 0 : locValue)) {
        queryParams.set('location', Array.isArray(locValue) ? locValue.join(',') : locValue);
      }
      
      const contractTypeValue = params.filters.contractType;
      if (contractTypeValue && (Array.isArray(contractTypeValue) ? contractTypeValue.length > 0 : contractTypeValue)) {
        queryParams.set('contract_type', Array.isArray(contractTypeValue) ? contractTypeValue.join(',') : contractTypeValue);
      }
    }
    
    // Add sorting parameter
    if (params?.sortBy) {
      const orderPrefix = params.sortOrder === 'desc' ? '-' : '';
      const orderingMap: Record<string, string> = {
        'name': 'name',
        'joinDate': 'hire_date',
        'status': 'status'
      };
      const backendSort = orderingMap[params.sortBy];
      if (backendSort) {
        queryParams.set('ordering', `${orderPrefix}${backendSort}`);
      }
    }
    
    const queryString = queryParams.toString();
    const url = queryString ? `/api/employees?${queryString}` : '/api/employees';
    
    const endpoint = new APIEndPoint(url, url);
    return await endpoint.list();
  },

  /**
   * POST /api/employees
   * Crée un nouvel employé (onboarding)
   */
  create: async (data: EmployeeCreate): Promise<Employee> => {
    const endpoint = new APIEndPoint('/api/employees', '/api/employees');
    return await endpoint.create(data);
  },

  /**
   * GET /api/employees/{employee_id}
   * Récupère le profil complet d'un employé
   */
  retrieve: async (employeeId: string): Promise<EmployeeFullProfile> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}`,
      `/api/employees/${employeeId}`
    );
    return await endpoint.retrieve();
  },

  /**
   * PATCH /api/employees/{employee_id}/personal-info
   * Met à jour les informations personnelles d'un employé
   */
  updatePersonalInfo: async (employeeId: string, data: EmployeeUpdate): Promise<Employee> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/personal-info`,
      `/api/employees/${employeeId}/personal-info`
    );
    return await endpoint.partial_update(data);
  },

  /**
   * PATCH /api/employees/{employee_id}/assign-user/{user_id}
   * Lie un compte utilisateur à un employé
   */
  assignUser: async (employeeId: string, userId: string): Promise<{ message: string; employee: string; user_id: string }> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/assign-user/${userId}`,
      `/api/employees/${employeeId}/assign-user/${userId}`
    );
    return await endpoint.partial_update({});
  },

  /**
   * POST /api/employees/{employee_id}/revoke-user
   * Révoque l'accès utilisateur d'un employé
   */
  revokeUser: async (employeeId: string): Promise<{ message: string }> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/revoke-user`,
      `/api/employees/${employeeId}/revoke-user`
    );
    return await endpoint.create({});
  },

  /**
   * POST /api/organization/units/{org_unit_id}/employees/{employee_id}/assign
   * Affecte un employé à une unité organisationnelle
   */
  assignToOrgUnit: async (employeeId: string, orgUnitId: string, positionId?: string): Promise<Employee> => {
    const endpoint = new APIEndPoint(
      `/api/organization/units/${orgUnitId}/employees/${employeeId}/assign`,
      `/api/organization/units/${orgUnitId}/employees/${employeeId}/assign`
    );
    // Only include position_id in body if it's defined
    const body = positionId ? { position_id: positionId } : {};
    return await endpoint.create(body);
  },

  /**
   * POST /api/organization/employees/{employee_id}/unassign
   * Désaffecte un employé de son unité organisationnelle
   */
  unassignFromOrgUnit: async (employeeId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/organization/employees/${employeeId}/unassign`,
      `/api/organization/employees/${employeeId}/unassign`
    );
    return await endpoint.create({});
  },

  /**
   * PATCH /api/employees/{employee_id}/contract-info
   * Met à jour les informations de contrat et de poste d'un employé
   */
  updateContractInfo: async (employeeId: string, data: any): Promise<Employee> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/contract-info`,
      `/api/employees/${employeeId}/contract-info`
    );
    return await endpoint.partial_update(data);
  },

  // ==========================================
  // FAMILY ENDPOINTS
  // ==========================================

  addChild: async (employeeId: string, data: any): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/family/children`, 
      `/api/employees/${employeeId}/family/children`
    );
    return await endpoint.create(data);
  },

  updateChild: async (childId: string, data: any): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/employees/family/children/${childId}`, 
      `/api/employees/family/children/${childId}`
    );
    return await endpoint.partial_update(data);
  },

  removeChild: async (childId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/employees/family/children/${childId}`,  
      `/api/employees/family/children/${childId}`
    );
    return await endpoint.destroy();
  },

  addEmergencyContact: async (employeeId: string, data: any): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/emergency-contacts`, 
      `/api/employees/${employeeId}/emergency-contacts`
    );
    return await endpoint.create(data);
  },

  updateEmergencyContact: async (contactId: string, data: any): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/employees/emergency-contacts/${contactId}`, 
      `/api/employees/emergency-contacts/${contactId}`
    );
    return await endpoint.partial_update(data);
  },

  removeEmergencyContact: async (contactId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/employees/emergency-contacts/${contactId}`, 
      `/api/employees/emergency-contacts/${contactId}`
    );
    return await endpoint.destroy();
  },

  addDocument: async (employeeId: string, formData: FormData): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/documents`, 
      `/api/employees/${employeeId}/documents`
    );
    return await endpoint.create(formData);
  },

  updateDocument: async (documentId: string, data: any): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/employees/documents/${documentId}`, 
      `/api/employees/documents/${documentId}`
    );
    return await endpoint.partial_update(data);
  },

  removeDocument: async (documentId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/employees/documents/${documentId}`, 
      `/api/employees/documents/${documentId}`
    );
    return await endpoint.destroy();
  },

  replaceDocumentFile: async (documentId: string, file: File): Promise<any> => {
    const formData = new FormData();
    formData.append('file', file);
    const endpoint = new APIEndPoint(
      `/api/employees/documents/${documentId}/upload`, 
      `/api/employees/documents/${documentId}/upload`
    );
    return await endpoint.create(formData);
  },

  // ==========================================
  // EDUCATION ENDPOINTS
  // ==========================================

  addEducation: async (employeeId: string, data: any): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/education`, 
      `/api/employees/${employeeId}/education`
    );
    return await endpoint.create(data);
  },

  updateEducation: async (educationId: string, data: any): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/employees/education/${educationId}`, 
      `/api/employees/education/${educationId}`
    );
    return await endpoint.partial_update(data);
  },

  removeEducation: async (educationId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/employees/education/${educationId}`,  
      `/api/employees/education/${educationId}`
    );
    return await endpoint.destroy();
  },

  suspend: async (employeeId: string, data: { reason: string; effective_date?: string }): Promise<Employee> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/lifecycle/suspend`,
      `/api/employees/${employeeId}/lifecycle/suspend`
    );
    return await endpoint.create(data);
  },

  reactivate: async (employeeId: string, data: { effective_date?: string; reason?: string; is_active?: boolean; can_connect?: boolean }): Promise<Employee> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/lifecycle/reactivate`,
      `/api/employees/${employeeId}/lifecycle/reactivate`
    );
    return await endpoint.create(data);
  },

  offboard: async (employeeId: string, data: { end_date: string; departure_type?: string; reason: string }): Promise<Employee> => {
    const endpoint = new APIEndPoint(
      `/api/employees/${employeeId}/lifecycle/offboard`,
      `/api/employees/${employeeId}/lifecycle/offboard`
    );
    return await endpoint.create(data);
  }
};

