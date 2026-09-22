import { 
  transitionEndpoint, 
  type TransitionCreateData, 
  type TransitionUpdateData 
} from '../api/transition.endpoints';
import type { Transition, TransitionType } from '../types/types';
import type { PaginatedResponse } from '@/hr/types/pagination';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';


/**
 * Service pour la gestion des transitions (mobilité employés)
 * Gère les appels API et les notifications
 */
class TransitionService {
  /**
   * Liste toutes les transitions avec filtrage optionnel (pagination support)
   */
  async listTransitions(
    employeeId?: string,
    transitionType?: TransitionType,
    page?: number,
    pageSize?: number,
    search?: string
  ): Promise<PaginatedResponse<Transition>> {
    try {
      return await transitionEndpoint.list(employeeId, transitionType, page, pageSize, search);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Récupère une transition par ID
   */
  async getTransition(id: string): Promise<Transition | null> {
    try {
      return await transitionEndpoint.getById(id);
    } catch (error: any) {
      if (error?.response?.status === 404) {
        return null;
      }
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Récupère les transitions d'un employé
   */
  async getEmployeeTransitions(employeeId: string): Promise<Transition[]> {
    try {
      return await transitionEndpoint.getByEmployee(employeeId);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Crée une nouvelle transition
   */
  async createTransition(data: TransitionCreateData): Promise<Transition> {
    try {
      const transition = await transitionEndpoint.create(data);
      notification.toast.success('Mouvement enregistré avec succès');
      return transition;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Met à jour une transition
   */
  async updateTransition(id: string, data: TransitionUpdateData): Promise<Transition> {
    try {
      const transition = await transitionEndpoint.update(id, data);
      notification.toast.success('Mouvement mis à jour');
      return transition;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Supprime une transition
   */
  async deleteTransition(id: string): Promise<void> {
    try {
      await transitionEndpoint.delete(id);
      notification.toast.success('Mouvement supprimé');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
}


export const transitionService = new TransitionService();

