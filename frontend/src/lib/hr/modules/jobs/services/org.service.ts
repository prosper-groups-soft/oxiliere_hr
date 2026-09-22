import { orgEndpoint } from '../api/org.endpoints';
import type { 
  OrgUnit, 
  OrgTreeNode, 
  OrgUnitCreate, 
  OrgUnitUpdate 
} from '../types/org.types';
import type { JobPosition } from '../types/types';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { formatEmployeeName } from '@/hr/utilities/common/employee.utils';


/**
 * Normalise une unité organisationnelle du backend (snake_case → camelCase)
 */
function normalizeOrgUnit(unit: any, level: number = 0, path: string[] = []): OrgUnit {
  // Le manager peut être une string (arbre) ou un objet Employee (détail)
  const managerName = typeof unit.manager === 'string' 
    ? unit.manager 
    : (unit.manager?.first_name && unit.manager?.last_name 
      ? formatEmployeeName(unit.manager)
      : unit.manager_name);
  
  const affointName = typeof unit.affoint === 'string'
    ? unit.affoint
    : (unit.affoint?.first_name && unit.affoint?.last_name
      ? formatEmployeeName(unit.affoint)
      : unit.affoint_name);

  return {
    id: unit.id,
    name: unit.name,
    type: unit.type || unit.get_type_display || 'DEPARTMENT',
    parentId: unit.parent_id || null,
    managerId: unit.manager_id || unit.manager?.id || null,
    managerName: managerName,
    managerPhoto: unit.manager_photo || unit.manager?.photo || null,
    affointId: unit.affoint_id || unit.affoint?.id || null,
    affointName: affointName,
    authorizedHeadcount: unit.authorized_headcount || unit.headcount || 0,
    employeeCount: unit.employee_count || 0,
    level,
    path,
  };
}


/**
 * Convertit l'arbre hiérarchique en liste plate de départements
 */
function flattenTree(nodes: OrgTreeNode[], parentId: string | null = null, level: number = 0, parentPath: string[] = []): OrgUnit[] {
  const result: OrgUnit[] = [];

  for (const node of nodes) {
    const path = [...parentPath, node.id];
    const orgUnit: OrgUnit = {
      id: node.id,
      name: node.name,
      type: (node.type as 'DEPARTMENT' | 'DIVISION' | 'TEAM' | 'FUNCTION' | 'BRANCH' | 'PROJECT') || 'DEPARTMENT',
      parentId,
      managerId: node.manager?.id || null,
      managerName: node.manager ? formatEmployeeName(node.manager) : undefined,
      affointId: node.affoint?.id || null,
      affointName: node.affoint ? formatEmployeeName(node.affoint) : undefined,
      manager: node.manager || null,
      affoint: node.affoint || null,
      authorizedHeadcount: node.authorized_headcount || 0,
      employeeCount: node.employee_count || 0,
      level,
      path,
    };
    result.push(orgUnit);

    // Récursivement ajouter les enfants
    if (node.sub_units && node.sub_units.length > 0) {
      result.push(...flattenTree(node.sub_units, node.id, level + 1, path));
    }
  }

  return result;
}


/**
 * Service pour la gestion de la structure organisationnelle
 */
class OrgService {
  /**
   * GET /api/organization/tree
   * Récupère l'arbre hiérarchique et le convertit en liste plate
   */
  async getOrgTree(): Promise<{ tree: OrgTreeNode[]; orgUnits: OrgUnit[] }> {
    try {
      const tree = await orgEndpoint.getTree();
      const orgUnits = flattenTree(tree);
      return { tree, orgUnits };
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * @deprecated Utiliser getOrgTree()
   */
  async getOrgUnitTree(): Promise<{ tree: OrgTreeNode[]; orgUnits: OrgUnit[] }> {
    const result = await this.getOrgTree();
    return { tree: result.tree, orgUnits: result.orgUnits };
  }

  /**
   * GET /api/organization/units
   * Liste toutes les unités org (paginé)
   */
  async listOrgUnits(
    page?: number,
    limit?: number,
    search?: string
  ): Promise<{ results: OrgUnit[]; count: number }> {
    try {
      const response = await orgEndpoint.list({ page, limit, search });
      return {
        results: (response.results || []).map((u) => normalizeOrgUnit(u)),
        count: response.count || 0,
      };
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * POST /api/organization/units
   * Crée une nouvelle unité org
   */
  async createOrgUnit(data: OrgUnitCreate): Promise<OrgUnit> {
    try {
      const response = await orgEndpoint.create(data);
      const orgUnit = normalizeOrgUnit(response);
      return orgUnit;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * PATCH /api/organization/units/{id}
   * Met à jour une unité org
   */
  async updateOrgUnit(unitId: string, data: OrgUnitUpdate): Promise<OrgUnit> {
    try {
      const response = await orgEndpoint.update(unitId, data);
      const orgUnit = normalizeOrgUnit(response);
      return orgUnit;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * PATCH /api/organization/units/{id}/transfer-leadership/{manager_id}
   * Change le manager d'une unité org
   */
  async transferLeadership(orgUnitId: string, newManagerId: string): Promise<OrgUnit> {
    try {
      const response = await orgEndpoint.transferLeadership(orgUnitId, newManagerId);
      const orgUnit = normalizeOrgUnit(response);
      return orgUnit;
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * DELETE /api/organization/units/{id}
   * Supprime une unité org
   */
  async deleteOrgUnit(unitId: string): Promise<void> {
    try {
      await orgEndpoint.delete(unitId);
    } catch (error: any) {
      const detail = error?.response?.data?.detail;
      const message = typeof detail === 'string' && detail.trim()
        ? detail
        : getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * GET /api/organization/units/{id}/positions
   * Récupère toutes les positions d'une unité org avec une limite élevée
   */
  async getPositionsByOrgUnit(unitId: string, pageSize: number = 100): Promise<JobPosition[]> {
    try {
      const response = await orgEndpoint.getPositions(unitId, pageSize);
      return response.results || [];
    } catch (error: any) {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
}


export const orgService = new OrgService();
