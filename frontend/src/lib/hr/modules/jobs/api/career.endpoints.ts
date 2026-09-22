import APIEndPoint from '@/hr/utilities/http/rest';
import type { 
  CareerHistory, 
  EmployeeMove, 
  InitialAssignment 
} from '../types/job.types';


/**
 * Endpoints API pour la gestion de carrière
 * Base path: /api/career
 */
export const careerEndpoint = {
  /**
   * GET /api/career/{employeeId}/history
   * Historique de carrière d'un employé
   */
  async getHistory(employeeId: string): Promise<CareerHistory[]> {
    const endpoint = new APIEndPoint(
      `/api/career/${employeeId}/history`,
      `/api/career/${employeeId}/history`
    );
    return await endpoint.list();
  },

  /**
   * POST /api/career/{employeeId}/onboard
   * Assignation initiale pour un nouvel employé
   */
  async onboard(employeeId: string, data: InitialAssignment): Promise<CareerHistory> {
    const endpoint = new APIEndPoint(
      `/api/career/${employeeId}/onboard`,
      `/api/career/${employeeId}/onboard`
    );
    // Convertir camelCase vers snake_case pour le backend
    const backendData = {
      position_id: data.position_id,
      org_unit_id: data.org_unit_id,
      start_date: data.start_date,
    };
    return await endpoint.create(backendData);
  },

  /**
   * POST /api/career/{employeeId}/promote
   * Promotion, transfert ou mutation
   */
  async move(employeeId: string, data: EmployeeMove): Promise<CareerHistory> {
    const endpoint = new APIEndPoint(
      `/api/career/${employeeId}/promote`,
      `/api/career/${employeeId}/promote`
    );
    // Convertir camelCase vers snake_case pour le backend
    const backendData = {
      new_position_id: data.new_position_id,
      new_org_unit_id: data.new_org_unit_id,
      effective_date: data.effective_date,
      description: data.description,
    };
    return await endpoint.create(backendData);
  }
};

