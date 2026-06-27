import APIEndPoint from '@/utilities/http/rest';
import type { 
  JobPosition,
  JobPositionCreate,
  JobPositionUpdate,
  SeniorityLevel
} from '../types/types';


// Type pour la réponse brute du backend (utilise 'label' au lieu de 'name')
interface SeniorityLevelBackendResponse {
  id: string;
  level: SeniorityLevel;
  label: string;
  rank: number;
  requirements: string[];
  is_active?: boolean;
}


/**
 * Endpoints API pour le Job Repository
 * Base path: /api/jobs
 */
export const jobEndpoint = {
  /**
   * GET /api/jobs/families
   * Liste toutes les familles de métiers (non-paginated)
   */
  async listFamilies(): Promise<Array<{ id: string; name: string; description: string }>> {
    const endpoint = new APIEndPoint('/api/jobs/families', '/api/jobs/families');
    const response = await endpoint.list();
    // Backend now returns plain array, not paginated
    return Array.isArray(response) ? response : (response.results || []);
  },

  /**
   * POST /api/jobs/families
   * Crée une nouvelle famille de métiers
   */
  async createFamily(data: { name: string; description?: string }): Promise<{ id: string; name: string; description: string }> {
    const endpoint = new APIEndPoint('/api/jobs/families', '/api/jobs/families');
    const response = await endpoint.create(data);
    return response[1] || response;
  },

  /**
   * PATCH /api/jobs/families/{id}
   * Met à jour une famille de métiers
   */
  async updateFamily(id: string, data: Partial<{ name: string; description: string }>): Promise<{ id: string; name: string; description: string }> {
    const endpoint = new APIEndPoint(`/api/jobs/families/${id}`, `/api/jobs/families/${id}`);
    return await endpoint.partial_update(data);
  },

  /**
   * DELETE /api/jobs/families/{id}
   * Supprime une famille de métiers
   */
  async deleteFamily(id: string): Promise<void> {
    const endpoint = new APIEndPoint(`/api/jobs/families/${id}`, `/api/jobs/families/${id}`);
    await endpoint.destroy();
  },

  /**
   * POST /api/jobs/positions
   * Crée une nouvelle position
   */
  async createPosition(data: JobPositionCreate): Promise<JobPosition> {
    const endpoint = new APIEndPoint('/api/jobs/positions', '/api/jobs/positions');
    const response = await endpoint.create(data);
    // Backend returns {201: PositionOut}, extract the position data
    return response[1] || response;
  },

  /**
   * GET /api/jobs/families/{familyId}/career-path
   * Parcours de carrière pour une famille
   */
  async getCareerPath(familyId: string): Promise<JobPosition[]> {
    const endpoint = new APIEndPoint(
      `/api/jobs/families/${familyId}/career-path`,
      `/api/jobs/families/${familyId}/career-path`
    );
    return await endpoint.list();
  },

  /**
   * GET /api/jobs/positions/level/{level}
   * Positions par niveau de séniorité
   */
  async listBySeniority(level: string): Promise<JobPosition[]> {
    const endpoint = new APIEndPoint(
      `/api/jobs/positions/level/${level}`,
      `/api/jobs/positions/level/${level}`
    );
    return await endpoint.list();
  },

  /**
   * GET /api/jobs/catalog
   * Catalogue complet des métiers
   */
  async getCatalog(): Promise<Record<string, string[]>> {
    const endpoint = new APIEndPoint('/api/jobs/catalog', '/api/jobs/catalog');
    return await endpoint.list();
  },

  /**
   * GET /api/jobs/seniority-levels
   * Niveaux de séniorité avec prérequis
   */
  async getSeniorityLevels(): Promise<SeniorityLevelBackendResponse[]> {
    const endpoint = new APIEndPoint('/api/jobs/seniority-levels', '/api/jobs/seniority-levels');
    return await endpoint.list();
  },

  /**
   * GET /api/jobs/positions
   * Liste toutes les positions (non-paginated)
   */
  async getPositions(): Promise<JobPosition[]> {
    const endpoint = new APIEndPoint('/api/jobs/positions', '/api/jobs/positions');
    const response = await endpoint.list();
    // Backend now returns plain array
    return Array.isArray(response) ? response : (response.results || []);
  },

  /**
   * PATCH /api/jobs/positions/{id}
   * Met à jour une position (partial update)
   */
  async updatePosition(id: string, data: JobPositionUpdate): Promise<JobPosition> {
    const endpoint = new APIEndPoint(
      `/api/jobs/positions/${id}`,
      `/api/jobs/positions/${id}`
    );
    return await endpoint.partial_update(data);
  },

  /**
   * DELETE /api/jobs/positions/{id}
   * Supprime une position
   */
  async deletePosition(id: string): Promise<void> {
    const endpoint = new APIEndPoint(
      `/api/jobs/positions/${id}`,
      `/api/jobs/positions/${id}`
    );
    return await endpoint.destroy();
  },

  /**
   * POST /api/jobs/seniority-levels
   * Crée un nouveau niveau de séniorité
   */
  async createSeniorityLevel(data: Omit<SeniorityLevelBackendResponse, 'id'>): Promise<SeniorityLevelBackendResponse> {
    const endpoint = new APIEndPoint('/api/jobs/seniority-levels', '/api/jobs/seniority-levels');
    return await endpoint.create(data);
  },

  /**
   * PATCH /api/jobs/seniority-levels/{id}
   * Met à jour partiellement un niveau de séniorité
   */
  async updateSeniorityLevel(id: string, data: Partial<Omit<SeniorityLevelBackendResponse, 'id'>>): Promise<SeniorityLevelBackendResponse> {
    const endpoint = new APIEndPoint(
      `/api/jobs/seniority-levels/${id}`,
      `/api/jobs/seniority-levels/${id}`
    );
    return await endpoint.partial_update(data);
  },

  /**
   * DELETE /api/jobs/seniority-levels/{id}
   * Supprime un niveau de séniorité
   */
  async deleteSeniorityLevel(id: string): Promise<void> {
    const endpoint = new APIEndPoint(
      `/api/jobs/seniority-levels/${id}`,
      `/api/jobs/seniority-levels/${id}`
    );
    return await endpoint.destroy();
  },

  /**
   * POST /api/jobs/seniority-levels/reset
   * Réinitialise tous les niveaux de séniorité aux valeurs par défaut
   */
  async resetSeniorityLevels(): Promise<SeniorityLevelBackendResponse[]> {
    const endpoint = new APIEndPoint(
      '/api/jobs/seniority-levels/reset',
      '/api/jobs/seniority-levels/reset'
    );
    return await endpoint.create({});
  }
};

