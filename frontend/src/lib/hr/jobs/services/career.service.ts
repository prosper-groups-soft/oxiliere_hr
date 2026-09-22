import { careerEndpoint } from '../api/career.endpoints';
import type { 
  CareerHistory, 
  EmployeeMove, 
  InitialAssignment 
} from '../types/job.types';
import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';


export const careerService = {
  /**
   * Récupère l'historique de carrière d'un employé
   */
  async getHistory(employeeId: string): Promise<CareerHistory[]> {
    console.log('[CareerService] Fetching history for employee:', employeeId);
    try {
      return await careerEndpoint.getHistory(employeeId);
    } catch (error: any) {
      console.error('[CareerService] Error fetching history:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Assignation initiale pour un nouvel employé (onboarding)
   */
  async onboard(employeeId: string, data: InitialAssignment): Promise<CareerHistory> {
    console.log('[CareerService] Onboarding employee:', employeeId, data);
    try {
      const result = await careerEndpoint.onboard(employeeId, data);
      notification.toast.success('Assignation initiale enregistrée');
      return result;
    } catch (error: any) {
      console.error('[CareerService] Error onboarding:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Promotion, transfert ou mutation
   */
  async move(employeeId: string, data: EmployeeMove): Promise<CareerHistory> {
    console.log('[CareerService] Processing move for employee:', employeeId, data);
    try {
      const result = await careerEndpoint.move(employeeId, data);
      notification.toast.success('Mouvement enregistré avec succès');
      return result;
    } catch (error: any) {
      console.error('[CareerService] Error processing move:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
};

