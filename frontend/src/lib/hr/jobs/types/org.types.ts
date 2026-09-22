/**
 * Types pour la structure organisationnelle (Org Chart)
 * Lié au backend Django - modèle Department avec hiérarchie
 */

import type { Department } from './types';


/**
 * Objet employé simplifié pour l'org chart
 */
export interface OrgChartEmployee {
  id: string;
  first_name: string;
  last_name: string;
  middle_name?: string | null;
  photo?: string | null;
}

/**
 * Représente une unité organisationnelle dans l'org chart
 * Une unité peut être un département, une équipe, ou toute autre entité
 */
export interface OrgUnit extends Department {
  // Les champs sont hérités de Department
  // Ajout de métadonnées calculées côté serveur
  level: number; // Niveau dans la hiérarchie (0 = root)
  path: string[]; // Chemin des IDs parents
  employeeCount?: number; // Nombre d'employés dans cette unité
  subUnitCount?: number; // Nombre de sous-unités
  // Objets manager et adjoint (inclus dans l'arbre)
  manager?: OrgChartEmployee | null;
  affoint?: OrgChartEmployee | null;
}


/**
 * Nœud de l'arbre organisationnel retourné par le backend
 */
export interface OrgTreeNode {
  id: string;
  name: string;
  type: string; // Type de l'unité (Département, Équipe, etc.)
  employee_count?: number;
  authorized_headcount?: number;
  // Objets manager et adjoint (inclus par le backend)
  manager?: OrgChartEmployee | null;
  affoint?: OrgChartEmployee | null;
  sub_units: OrgTreeNode[];
}


/**
 * Format plat pour faciliter la manipulation frontend
 */
export interface FlatOrgUnit extends OrgUnit {
  childrenIds: string[]; // IDs des enfants directs
  ancestorIds: string[]; // IDs de tous les ancêtres
}


/**
 * Données pour créer une unité
 * Correspond à OrgUnitType dans le backend
 */
export interface OrgUnitCreate {
  name: string;
  type: 'DEPARTMENT' | 'DIVISION' | 'TEAM' | 'FUNCTION' | 'BRANCH' | 'PROJECT';
  parentId: string | null;
  managerId: string | null;
  affointId: string | null;
  authorizedHeadcount: number;
}


/**
 * Données pour mettre à jour une unité
 */
export interface OrgUnitUpdate {
  name?: string;
  type?: 'DEPARTMENT' | 'DIVISION' | 'TEAM' | 'FUNCTION' | 'BRANCH' | 'PROJECT';
  parentId?: string | null;
  managerId?: string | null;
  affointId?: string | null;
  authorizedHeadcount?: number;
}


/**
 * Réponse de l'API pour l'arbre complet
 */
export interface OrgTreeResponse {
  tree: OrgTreeNode[];
  flat: OrgUnit[];
}


/**
 * Filtres pour la liste des unités
 */
export interface OrgUnitFilters {
  type?: ('DEPARTMENT' | 'DIVISION' | 'TEAM' | 'FUNCTION' | 'BRANCH' | 'PROJECT')[];
  hasManager?: boolean;
  search?: string;
}

