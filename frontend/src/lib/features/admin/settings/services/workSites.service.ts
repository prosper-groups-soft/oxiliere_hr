import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { workSitesEndpoint } from '../api/workSites.endpoints';
import type {
  WorkSite,
  WorkSiteCreate,
  WorkSiteUpdate
} from '../types/workSites.types';


/**
 * Normalise les données du site en convertissant les strings en nombres
 * L'API retourne parfois latitude/longitude comme strings
 */
function normalizeWorkSite(site: any): WorkSite {
  return {
    ...site,
    latitude: typeof site.latitude === 'string' ? parseFloat(site.latitude) : site.latitude,
    longitude: typeof site.longitude === 'string' ? parseFloat(site.longitude) : site.longitude,
    allowed_radius: typeof site.allowed_radius === 'string' ? parseInt(site.allowed_radius) : site.allowed_radius,
  };
}


/**
 * Service pour la gestion des sites de travail
 * Utilise les endpoints dédiés dans le dossier api/
 * Aligné avec la documentation API /api/work-sites/*
 */
class WorkSitesService {
  /**
   * GET /api/work-sites
   * Liste tous les sites de travail avec pagination classique
   */
  async listWorkSites(page?: number, limit?: number): Promise<{ results: WorkSite[]; count: number }> {
    try {
      const response = await workSitesEndpoint.list({ page, limit });
      return {
        results: (response.results || []).map(normalizeWorkSite),
        count: response.count || 0
      };
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * POST /api/work-sites
   * Crée un nouveau site de travail
   */
  async createWorkSite(data: WorkSiteCreate): Promise<WorkSite> {
    try {
      const site = await workSitesEndpoint.create(data);
      notification.toast.success('Site de travail créé avec succès');
      return normalizeWorkSite(site);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * PATCH /api/work-sites/{site_id}
   * Met à jour un site de travail existant
   */
  async updateWorkSite(siteId: string, data: WorkSiteUpdate): Promise<WorkSite> {
    try {
      const site = await workSitesEndpoint.update(siteId, data);
      notification.toast.success('Site de travail mis à jour');
      return normalizeWorkSite(site);
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * DELETE /api/work-sites/{site_id}
   * Supprime un site de travail
   */
  async deleteWorkSite(siteId: string): Promise<void> {
    try {
      await workSitesEndpoint.delete(siteId);
      notification.toast.success('Site de travail supprimé');
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
}


export const workSitesService = new WorkSitesService();

