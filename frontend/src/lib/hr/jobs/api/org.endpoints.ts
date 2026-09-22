import APIEndPoint from '@/utilities/http/rest';
import type { PaginatedResponse } from '@/utilities/common/types';
import type { 
  OrgUnitCreate, 
  OrgUnitUpdate, 
  OrgUnit,
  OrgTreeNode 
} from '../types/org.types';
import type { JobPosition } from '../types/types';


/**
 * Endpoints API pour la structure organisationnelle
 * Base path: /api/organization
 */
export const orgEndpoint = {
  /**
   * GET /api/organization/units
   * Liste toutes les unités organisationnelles (départements, équipes, etc.)
   */
  list: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
  }): Promise<PaginatedResponse<OrgUnit>> => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.search) queryParams.set('search', params.search);

    const queryString = queryParams.toString();
    const url = queryString ? `/api/organization/units?${queryString}` : '/api/organization/units';

    const endpoint = new APIEndPoint(url, url);
    return await endpoint.list();
  },

  /**
   * GET /api/organization/tree
   * Récupère l'arbre hiérarchique complet de l'organisation
   */
  getTree: async (): Promise<OrgTreeNode[]> => {
    const endpoint = new APIEndPoint('/api/organization/tree', '/api/organization/tree');
    return await endpoint.list();
  },

  /**
   * POST /api/organization/units
   * Crée une nouvelle unité organisationnelle
   */
  create: async (data: OrgUnitCreate): Promise<OrgUnit> => {
    const endpoint = new APIEndPoint('/api/organization/units', '/api/organization/units');
    // Convertir camelCase vers snake_case pour le backend
    const backendData = {
      name: data.name,
      type: data.type,
      parent_id: data.parentId,
      manager_id: data.managerId,
      affoint_id: data.affointId,
      authorized_headcount: data.authorizedHeadcount,
    };
    return await endpoint.create(backendData);
  },

  /**
   * GET /api/organization/units/{unit_id}
   * Récupère le détail d'une unité
   */
  retrieve: async (unitId: string): Promise<OrgUnit> => {
    const endpoint = new APIEndPoint(
      `/api/organization/units/${unitId}`,
      `/api/organization/units/${unitId}`
    );
    return await endpoint.retrieve();
  },

  /**
   * PATCH /api/organization/units/{unit_id}
   * Met à jour une unité existante
   */
  update: async (unitId: string, data: OrgUnitUpdate): Promise<OrgUnit> => {
    const endpoint = new APIEndPoint(
      `/api/organization/units/${unitId}`,
      `/api/organization/units/${unitId}`
    );
    // Convertir camelCase vers snake_case pour le backend
    const backendData: Record<string, any> = {};
    if (data.name !== undefined) backendData.name = data.name;
    if (data.type !== undefined) backendData.type = data.type;
    if (data.parentId !== undefined) backendData.parent_id = data.parentId;
    if (data.managerId !== undefined) backendData.manager_id = data.managerId;
    if (data.affointId !== undefined) backendData.affoint_id = data.affointId;
    if (data.authorizedHeadcount !== undefined) backendData.authorized_headcount = data.authorizedHeadcount;
    return await endpoint.partial_update(backendData);
  },

  /**
   * PATCH /api/organization/units/{unit_id}/transfer-leadership/{new_manager_id}
   * Transfère la direction d'une unité à un nouvel employé
   */
  transferLeadership: async (unitId: string, newManagerId: string): Promise<OrgUnit> => {
    const endpoint = new APIEndPoint(
      `/api/organization/units/${unitId}/transfer-leadership/${newManagerId}`,
      `/api/organization/units/${unitId}/transfer-leadership/${newManagerId}`
    );
    return await endpoint.partial_update({});
  },

  /**
   * DELETE /api/organization/units/{unit_id}
   * Supprime une unité (les enfants sont réassignés au parent)
   */
  delete: async (unitId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/organization/units/${unitId}`,
      `/api/organization/units/${unitId}`
    );
    return await endpoint.destroy();
  },

  /**
   * GET /api/organization/units/{unit_id}/positions
   * Récupère toutes les positions d'une unité organisationnelle
   */
  getPositions: async (unitId: string, pageSize: number = 100): Promise<PaginatedResponse<JobPosition>> => {
    const endpoint = new APIEndPoint(
      `/api/organization/units/${unitId}/positions?page=1&page_size=${pageSize}`,
      `/api/organization/units/${unitId}/positions?page=1&page_size=${pageSize}`
    );
    return await endpoint.list();
  }
};

