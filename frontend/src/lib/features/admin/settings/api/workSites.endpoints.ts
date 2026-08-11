import APIEndPoint from '@/utilities/http/rest';
import type { PaginatedResponse } from '@/utilities/common/types';
import type { WorkSite, WorkSiteCreate, WorkSiteUpdate } from '../types/workSites.types';


/**
 * Endpoints API pour la gestion des sites de travail
 * Base path: /api/work-sites
 */
export const workSitesEndpoint = {
  /**
   * GET /api/work-sites
   * Liste tous les sites de travail avec pagination par curseur
   */
  list: async (params?: { page?: number; limit?: number }): Promise<PaginatedResponse<WorkSite>> => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    
    const queryString = queryParams.toString();
    const url = queryString ? `/api/work-sites?${queryString}` : '/api/work-sites';
    
    const endpoint = new APIEndPoint(url, url);
    return await endpoint.list();
  },

  /**
   * POST /api/work-sites
   * Crée un nouveau site de travail
   */
  create: async (data: WorkSiteCreate): Promise<WorkSite> => {
    const endpoint = new APIEndPoint('/api/work-sites', '/api/work-sites');
    return await endpoint.create(data);
  },

  /**
   * PATCH /api/work-sites/{site_id}
   * Met à jour un site de travail existant
   */
  update: async (siteId: string, data: WorkSiteUpdate): Promise<WorkSite> => {
    const endpoint = new APIEndPoint(
      `/api/work-sites/${siteId}`,
      `/api/work-sites/${siteId}`
    );
    return await endpoint.partial_update(data);
  },

  /**
   * DELETE /api/work-sites/{site_id}
   * Supprime un site de travail
   */
  delete: async (siteId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/work-sites/${siteId}`,
      `/api/work-sites/${siteId}`
    );
    await endpoint.destroy();
  }
};
