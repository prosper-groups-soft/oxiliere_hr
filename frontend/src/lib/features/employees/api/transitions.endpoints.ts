import APIEndPoint from '@/utilities/http/rest';
import type { EmployeeTransition } from '../types/types';


/**
 * Endpoints API pour les transitions de carrière
 * Base path: /api/transitions
 */
export const transitionsEndpoint = {
  /**
   * GET /api/transitions/employee/{employee_id}
   * Récupère toutes les transitions pour un employé spécifique
   */
  listByEmployee: async (employeeId: string | number): Promise<EmployeeTransition[]> => {
    const url = `/api/transitions/employee/${employeeId}`;
    const endpoint = new APIEndPoint(url, url);
    return await endpoint.list() as unknown as EmployeeTransition[];
  }
};

