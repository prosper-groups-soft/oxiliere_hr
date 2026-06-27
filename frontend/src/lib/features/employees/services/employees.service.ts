import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { employeesEndpoint } from '../api/employees.endpoints';
import type {
  Employee,
  EmployeeCreate,
  EmployeeUpdate,
  EmployeeFullProfile,
  EmployeeFilters
} from '../types/types';


/**
 * Normalise les données employé pour le frontend
 * Convertit les champs snake_case vers camelCase si nécessaire
 */
function normalizeEmployee(employee: any): Employee {
  const fullName = employee.middle_name
    ? `${employee.last_name} ${employee.middle_name} ${employee.first_name}`
    : `${employee.last_name} ${employee.first_name}`;
  
  return {
    id: employee.id,
    name: fullName,
    jobTitle: employee.job_title || '',
    orgUnit: employee.org_unit || '',
    orgUnitType: employee.org_unit_type || '',
    positionId: employee.position_id,
    orgUnitId: employee.org_unit_id,
    status: employee.status || (employee.is_active ? 'active' : 'inactive'),
    location: employee.location || '',
    contractType: employee.contract_type || '',
    joinDate: employee.hire_date || '',
    phone: employee.phone || '',
    email: employee.email || '',
    avatarUrl: employee.avatar_url || '',
    role: employee.role || '',
    birthDate: employee.birthdate,
    // Champs bruts supplémentaires
    first_name: employee.first_name,
    last_name: employee.last_name,
    middle_name: employee.middle_name,
    matricule: employee.matricule,
    is_active: employee.is_active,
    can_connect: employee.can_connect,
    gender: employee.gender,
    nationality: employee.nationality,
    marital_status: employee.marital_status,
    description: employee.description,
    hire_date: employee.hire_date,
    termination_date: employee.termination_date,
    current_status: employee.current_status,
  };
}


/**
 * Service pour la gestion des employés
 * Utilise les endpoints dédiés dans le dossier api/
 * Aligné avec la documentation API /api/employees/*
 */
class EmployeesService {
  /**
   * GET /api/employees
   * Récupère tous les employés sans pagination (pour les sélecteurs)
   */
  async getAllForSelect(filters?: EmployeeFilters): Promise<Employee[]> {
    try {
      // Utilise une limite élevée pour récupérer tous les employés
      const response = await employeesEndpoint.list({ limit: 1000, filters });
      return (response.results || []).map(normalizeEmployee);
    } catch (error: any) {
      console.error('[EmployeesService] Error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * GET /api/employees?org_unit=XXX
   * Récupère tous les employés d'une unité organisationnelle (sans pagination)
   */
  async getEmployeesByOrgUnit(orgUnitId: string, limit: number = 1000): Promise<Employee[]> {
    try {
      // Utilise le filtre org_unit avec une grande limite
      const response = await employeesEndpoint.list({ 
        limit, 
        filters: { orgUnit: [orgUnitId] } as EmployeeFilters 
      });
      return (response.results || []).map(normalizeEmployee);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * GET /api/employees
   * Liste tous les employés avec pagination, filtres et tri
   */
  async listEmployees(
    page?: number, 
    limit?: number,
    search?: string,
    filters?: EmployeeFilters,
    sortBy?: string,
    sortOrder?: 'asc' | 'desc'
  ): Promise<{ results: Employee[]; count: number }> {
    try {
      const response = await employeesEndpoint.list({ page, limit, search, filters, sortBy, sortOrder });
      return {
        results: (response.results || []).map(normalizeEmployee),
        count: response.count || 0
      };
    } catch (error: any) {
      console.error('[EmployeesService] Error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * POST /api/employees
   * Crée un nouvel employé (onboarding)
   */
  async createEmployee(data: EmployeeCreate): Promise<Employee> {
    try {
      const employee = await employeesEndpoint.create(data);
      notification.toast.success('Employé créé avec succès');
      return normalizeEmployee(employee);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * GET /api/employees/{employee_id}
   * Récupère le profil complet d'un employé
   */
  async getEmployeeDetail(employeeId: string): Promise<EmployeeFullProfile> {
    try {
      const profile = await employeesEndpoint.retrieve(employeeId);
      return profile;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * PATCH /api/employees/{employee_id}/personal-info
   * Met à jour les informations personnelles d'un employé
   */
  async updatePersonalInfo(employeeId: string, data: EmployeeUpdate): Promise<Employee> {
    try {
      const employee = await employeesEndpoint.updatePersonalInfo(employeeId, data);
      return normalizeEmployee(employee);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * PATCH /api/employees/{employee_id}/assign-user/{user_id}
   * Lie un compte utilisateur à un employé
   */
  async assignUserAccount(employeeId: string, userId: string): Promise<void> {
    try {
      await employeesEndpoint.assignUser(employeeId, userId);
      notification.toast.success('Compte utilisateur lié avec succès');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * POST /api/employees/{employee_id}/revoke-user
   * Révoque l'accès utilisateur d'un employé
   */
  async revokeUserAccess(employeeId: string): Promise<void> {
    try {
      await employeesEndpoint.revokeUser(employeeId);
      notification.toast.success('Accès utilisateur révoqué');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * POST /api/organization/units/{org_unit_id}/employees/{employee_id}/assign
   * Affecte un employé à une unité organisationnelle
   */
  async assignToOrgUnit(employeeId: string, orgUnitId: string, positionId?: string): Promise<Employee> {
    try {
      const employee = await employeesEndpoint.assignToOrgUnit(employeeId, orgUnitId, positionId);
      notification.toast.success('Employé affecté avec succès');
      return normalizeEmployee(employee);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * POST /api/organization/employees/{employee_id}/unassign
   * Désaffecte un employé de son unité organisationnelle
   */
  async unassignFromOrgUnit(employeeId: string): Promise<void> {
    try {
      await employeesEndpoint.unassignFromOrgUnit(employeeId);
      notification.toast.success('Employé désaffecté avec succès');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * PATCH /api/employees/{employee_id}/contract-info
   * Met à jour les informations de contrat et de poste d'un employé
   */
  async updateContractInfo(employeeId: string, data: any): Promise<Employee> {
    try {
      const employee = await employeesEndpoint.updateContractInfo(employeeId, data);
      notification.toast.success('Contrat mis à jour avec succès');
      return normalizeEmployee(employee);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  // ==========================================
  // FAMILY
  // ==========================================

  async addChild(employeeId: string, data: any): Promise<any> {
    try {
      const child = await employeesEndpoint.addChild(employeeId, data);
      notification.toast.success('Enfant ajouté avec succès');
      return child;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async updateChild(childId: string, data: any): Promise<any> {
    try {
      const child = await employeesEndpoint.updateChild(childId, data);
      notification.toast.success('Enfant mis à jour avec succès');
      return child;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async removeChild(childId: string): Promise<void> {
    try {
      await employeesEndpoint.removeChild(childId);
      notification.toast.success('Enfant supprimé avec succès');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async addEmergencyContact(employeeId: string, data: any): Promise<any> {
    try {
      const contact = await employeesEndpoint.addEmergencyContact(employeeId, data);
      notification.toast.success('Contact d\'urgence ajouté avec succès');
      return contact;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async updateEmergencyContact(contactId: string, data: any): Promise<any> {
    try {
      const contact = await employeesEndpoint.updateEmergencyContact(contactId, data);
      notification.toast.success('Contact d\'urgence mis à jour avec succès');
      return contact;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async removeEmergencyContact(contactId: string): Promise<void> {
    try {
      await employeesEndpoint.removeEmergencyContact(contactId);
      notification.toast.success('Contact d\'urgence supprimé avec succès');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async addDocument(employeeId: string, data: any): Promise<any> {
    try {
      const formData = new FormData();
      if (data.file instanceof File) formData.append('file', data.file);
      
      const metadata = {
        document_type: data.document_type || 'OTHER',
        document_number: data.document_number || undefined,
        issue_date: data.issue_date || undefined,
        expiry_date: data.expiry_date || undefined
      };
      
      formData.append('data', JSON.stringify(metadata));

      const doc = await employeesEndpoint.addDocument(employeeId, formData);
      notification.toast.success('Document ajouté avec succès');
      return doc;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async updateDocument(documentId: string, data: any): Promise<any> {
    try {
      const doc = await employeesEndpoint.updateDocument(documentId, data);
      notification.toast.success('Document mis à jour avec succès');
      return doc;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async replaceDocumentFile(documentId: string, file: File): Promise<any> {
    try {
      const doc = await employeesEndpoint.replaceDocumentFile(documentId, file);
      notification.toast.success('Fichier mis à jour avec succès');
      return doc;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async removeDocument(documentId: string): Promise<void> {
    try {
      await employeesEndpoint.removeDocument(documentId);
      notification.toast.success('Document supprimé avec succès');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  // ==========================================
  // EDUCATION
  // ==========================================

  async addEducation(employeeId: string, data: any): Promise<any> {
    try {
      const education = await employeesEndpoint.addEducation(employeeId, data);
      notification.toast.success('Éducation ajoutée avec succès');
      return education;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async updateEducation(educationId: string, data: any): Promise<any> {
    try {
      const education = await employeesEndpoint.updateEducation(educationId, data);
      notification.toast.success('Éducation mise à jour avec succès');
      return education;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async removeEducation(educationId: string): Promise<void> {
    try {
      await employeesEndpoint.removeEducation(educationId);
      notification.toast.success('Éducation supprimée avec succès');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async suspendEmployee(employeeId: string, data: { reason: string; effective_date?: string }): Promise<Employee> {
    try {
      const employee = await employeesEndpoint.suspend(employeeId, data);
      notification.toast.success('Contrat suspendu avec succès');
      return normalizeEmployee(employee);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async reactivateEmployee(employeeId: string, data: { effective_date?: string; reason?: string; is_active?: boolean; can_connect?: boolean }): Promise<Employee> {
    try {
      const employee = await employeesEndpoint.reactivate(employeeId, data);
      notification.toast.success('Employé réactivé avec succès');
      return normalizeEmployee(employee);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async offboardEmployee(employeeId: string, data: { end_date: string; departure_type?: string; reason: string }): Promise<Employee> {
    try {
      const employee = await employeesEndpoint.offboard(employeeId, data);
      notification.toast.success('Départ de l\'employé enregistré avec succès');
      return normalizeEmployee(employee);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
}


export const employeesService = new EmployeesService();
