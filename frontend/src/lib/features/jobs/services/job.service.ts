import { jobEndpoint } from '../api/job.endpoints';
import type { 
  JobPosition, 
  JobPositionCreate, 
  JobPositionUpdate,
  SeniorityLevelDefinition,
  ProfessionalCategory 
} from '../types/types';
import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';


export const jobService = {
  /**
   * Liste toutes les familles de métiers
   */
  async getJobFamilies(): Promise<Array<{ id: string; name: string; description: string }>> {
    try {
      return await jobEndpoint.listFamilies();
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Crée une nouvelle famille de métiers
   */
  async createJobFamily(data: { name: string; description?: string }): Promise<{ id: string; name: string; description: string }> {
    try {
      return await jobEndpoint.createFamily(data);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Met à jour une famille de métiers
   */
  async updateJobFamily(id: string, data: Partial<{ name: string; description: string }>): Promise<{ id: string; name: string; description: string }> {
    try {
      return await jobEndpoint.updateFamily(id, data);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Supprime une famille de métiers
   */
  async deleteJobFamily(id: string): Promise<void> {
    try {
      await jobEndpoint.deleteFamily(id);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Crée une nouvelle position
   */
  async createPosition(data: JobPositionCreate): Promise<JobPosition> {
    console.log('[JobService] Creating position:', data);
    try {
      // Map frontend 'name' to backend 'name' (same now)
      return await jobEndpoint.createPosition(data);
    } catch (error: any) {
      console.error('[JobService] Error creating position:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Parcours de carrière pour une famille
   */
  async getCareerPath(familyId: string): Promise<JobPosition[]> {
    try {
      return await jobEndpoint.getCareerPath(familyId);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Positions par niveau de séniorité
   */
  async listBySeniority(level: string): Promise<JobPosition[]> {
    try {
      return await jobEndpoint.listBySeniority(level);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Catalogue complet des métiers
   */
  async getCatalog(): Promise<Record<string, string[]>> {
    try {
      return await jobEndpoint.getCatalog();
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Niveaux de séniorité avec prérequis
   */
  async getSeniorityLevels(): Promise<SeniorityLevelDefinition[]> {
    try {
      const data = await jobEndpoint.getSeniorityLevels();
      // Mapper 'label' (backend) vers 'name' (frontend)
      return data.map(item => ({
        ...item,
        name: item.label
      }));
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Liste toutes les positions
   */
  async getPositions(): Promise<JobPosition[]> {
    try {
      return await jobEndpoint.getPositions();
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Met à jour une position
   */
  async updatePosition(id: string, data: JobPositionUpdate): Promise<JobPosition> {
    try {
      return await jobEndpoint.updatePosition(id, data);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Supprime une position
   */
  async deletePosition(id: string): Promise<void> {
    try {
      await jobEndpoint.deletePosition(id);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Crée un nouveau niveau de séniorité
   */
  async createSeniorityLevel(data: Omit<SeniorityLevelDefinition, 'id'>): Promise<SeniorityLevelDefinition> {
    try {
      // Mapper 'name' (frontend) vers 'label' (backend)
      const backendData = {
        level: data.level,
        label: data.name,
        rank: data.rank,
        requirements: data.requirements,
        is_active: true
      };
      const response = await jobEndpoint.createSeniorityLevel(backendData);
      // Mapper la réponse
      return {
        ...response,
        name: response.label
      };
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Met à jour un niveau de séniorité (envoie uniquement les champs modifiés)
   */
  async updateSeniorityLevel(
    id: string, 
    data: Partial<Omit<SeniorityLevelDefinition, 'id'>>, 
    originalLevel?: SeniorityLevelDefinition
  ): Promise<SeniorityLevelDefinition> {
    try {
      // Si on a les données originales, on compare et n'envoie que les changements
      const changedData: any = {};
      
      if (originalLevel) {
        // Comparer chaque champ et n'ajouter que ceux qui ont changé
        if (data.name !== undefined && data.name !== originalLevel.name) {
          changedData.label = data.name;
        }
        if (data.rank !== undefined && data.rank !== originalLevel.rank) {
          changedData.rank = data.rank;
        }
        if (data.requirements !== undefined && 
            JSON.stringify(data.requirements) !== JSON.stringify(originalLevel.requirements)) {
          changedData.requirements = data.requirements;
        }
        if (data.level !== undefined && data.level !== originalLevel.level) {
          changedData.level = data.level;
        }
      } else {
        // Fallback: envoyer tous les champs si on n'a pas l'original
        if (data.name !== undefined) changedData.label = data.name;
        if (data.rank !== undefined) changedData.rank = data.rank;
        if (data.requirements !== undefined) changedData.requirements = data.requirements;
        if (data.level !== undefined) changedData.level = data.level;
      }
      
      // Si aucun changement, retourner simplement le niveau original
      if (Object.keys(changedData).length === 0) {
        return originalLevel || data as SeniorityLevelDefinition;
      }
      
      const response = await jobEndpoint.updateSeniorityLevel(id, changedData);
      // Mapper la réponse
      return {
        ...response,
        name: response.label
      };
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Supprime un niveau de séniorité
   */
  async deleteSeniorityLevel(id: string): Promise<void> {
    try {
      await jobEndpoint.deleteSeniorityLevel(id);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Réinitialise tous les niveaux de séniorité aux valeurs par défaut
   */
  async resetSeniorityLevels(): Promise<SeniorityLevelDefinition[]> {
    try {
      const response = await jobEndpoint.resetSeniorityLevels();
      // Mapper la réponse
      return response.map(level => ({
        ...level,
        name: level.label
      }));
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Grille des catégories professionnelles (7 classes × 4 échelons)
   */
  async getProfessionalCategories(): Promise<ProfessionalCategory[]> {
    try {
      return await jobEndpoint.listProfessionalCategories();
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Modifie une classe/échelon de la grille
   */
  async updateProfessionalCategory(id: string, data: Partial<ProfessionalCategory>): Promise<ProfessionalCategory> {
    try {
      return await jobEndpoint.updateProfessionalCategory(id, data);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  },

  /**
   * Réinitialise la grille depuis la fixture légale
   */
  async resetProfessionalCategories(): Promise<{ status: string; reset_count: number }> {
    try {
      return await jobEndpoint.resetProfessionalCategories();
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
};

