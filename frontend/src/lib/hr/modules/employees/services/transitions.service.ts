import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { transitionsEndpoint } from '../api/transitions.endpoints';
import type { EmployeeTransition } from '../types/types';


/**
 * Service pour la gestion des transitions de carrière
 */
class TransitionsService {
  /**
   * Récupère l'historique des transitions d'un employé
   */
  async getEmployeeTransitions(employeeId: string | number): Promise<EmployeeTransition[]> {
    try {
      return await transitionsEndpoint.listByEmployee(employeeId);
    } catch (error: any) {
      console.error('[TransitionsService] Error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
}


export const transitionsService = new TransitionsService();

