/**
 * Types pour la gestion des sites de travail
 * API Endpoints: /api/work-sites
 */


// Employee summary attached to a work site
export interface WorkSiteEmployee {
  id: string;
  matricule: string;
  first_name: string;
  last_name: string;
}


// Work Site entity
export interface WorkSite {
  id: string;
  name: string;
  latitude: number;
  longitude: number;
  allowed_radius: number;
  employees: WorkSiteEmployee[];
}


// Create payload
export interface WorkSiteCreate {
  name: string;
  latitude: number;
  longitude: number;
  allowed_radius: number;
}


// Update payload (all fields optional)
export interface WorkSiteUpdate {
  name?: string;
  latitude?: number;
  longitude?: number;
  allowed_radius?: number;
}


// Form state for UI
export interface WorkSiteFormState {
  name: string;
  latitude: number | null;
  longitude: number | null;
  allowed_radius: number | null;
}


// Store state
export interface WorkSitesStoreState {
  workSites: WorkSite[];
  isLoading: boolean;
  isSaving: boolean;
  error: Error | null;
  currentPage: number;
  perPage: number;
  totalCount: number;
  showAddForm: boolean;
  formState: WorkSiteFormState;
  validationErrors: Record<string, string>;
}

