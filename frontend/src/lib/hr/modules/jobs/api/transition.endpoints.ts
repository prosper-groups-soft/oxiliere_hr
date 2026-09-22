import APIEndPoint from '@/hr/utilities/http/rest';
import type { PaginatedResponse } from '@/hr/types/pagination';
import type { 
  Transition, 
  TransitionType, 
  JobPosition 
} from '../types/types';


/**
 * Raw API response structure for transitions
 * Backend returns nested objects for positions and employee, not just IDs
 */
interface TransitionApiResponse {
  id: string;
  employee_id: string;
  employee?: {
    id: string;
    matricule?: string;
    first_name?: string;
    middle_name?: string | null;
    last_name?: string;
    email?: string;
    gender?: string;
    phone?: string;
    is_active?: boolean;
  } | null;
  transition_type: string;
  transition_type_display: string;
  from_position: JobPosition | null;
  from_seniority_level?: {
    id: string;
    level: string;
    rank: number;
    label: string;
    requirements: string[];
    is_active: boolean;
  } | null;
  to_position: JobPosition | null;
  to_seniority_level?: {
    id: string;
    level: string;
    rank: number;
    label: string;
    requirements: string[];
    is_active: boolean;
  } | null;
  date: string;
  reason?: string;
  created_at?: string;
  created_by_id?: string | null;
}

/**
 * Map API response to frontend Transition format
 * Since backend returns snake_case and we use snake_case in types, just pass through
 */
function mapTransitionResponse(apiData: TransitionApiResponse): Transition {
  return apiData as Transition;
}


// Types pour les requêtes API
export interface TransitionCreateData {
  employee_id: string;
  transition_type: TransitionType;
  from_position_id?: string | null;
  from_seniority_level_id?: string | null;
  to_position_id?: string | null;
  to_seniority_level_id?: string | null;
  date?: string;
  reason?: string;
}


export interface TransitionUpdateData {
  transition_type?: TransitionType;
  from_position_id?: string | null;
  from_seniority_level_id?: string | null;
  to_position_id?: string | null;
  to_seniority_level_id?: string | null;
  date?: string;
  reason?: string;
}


/**
 * Endpoints API pour les Transitions (mobilité employés)
 * Base path: /api/transitions
 */
export const transitionEndpoint = {
  /**
   * GET /api/transitions
   * Liste toutes les transitions (paginée)
   */
  async list(
    employeeId?: string,
    transitionType?: TransitionType,
    page?: number,
    pageSize?: number,
    search?: string
  ): Promise<PaginatedResponse<Transition>> {
    const endpoint = new APIEndPoint('/api/transitions', '/api/transitions');

    // Construire les query params
    const params: Record<string, string> = {};
    if (employeeId) params.employee_id = employeeId;
    if (transitionType) params.transition_type = transitionType;
    if (page) params.page = String(page);
    if (pageSize) params.page_size = String(pageSize);
    if (search) params.search = search;

    const response = await endpoint.list(params);

    // Handle paginated response
    const paginated = response as PaginatedResponse<TransitionApiResponse>;
    if (paginated.results) {
      return {
        count: paginated.count,
        next: paginated.next,
        previous: paginated.previous,
        results: paginated.results.map(mapTransitionResponse),
      };
    }

    // Fallback for non-paginated response
    const results = Array.isArray(response) ? response : [];
    return {
      count: results.length,
      next: null,
      previous: null,
      results: (results as TransitionApiResponse[]).map(mapTransitionResponse),
    };
  },

  /**
   * GET /api/transitions/{id}
   * Récupère une transition par ID
   */
  async getById(id: string): Promise<Transition> {
    const endpoint = new APIEndPoint(`/api/transitions/${id}`, `/api/transitions/${id}`);
    const response = await endpoint.retrieve() as TransitionApiResponse;
    return mapTransitionResponse(response);
  },

  /**
   * GET /api/transitions/employee/{employee_id}
   * Récupère les transitions d'un employé
   */
  async getByEmployee(employeeId: string): Promise<Transition[]> {
    const endpoint = new APIEndPoint(`/api/transitions/employee/${employeeId}`, `/api/transitions/employee/${employeeId}`);
    const response = await endpoint.list() as TransitionApiResponse[];
    return response.map(mapTransitionResponse);
  },

  /**
   * POST /api/transitions
   * Crée une nouvelle transition
   */
  async create(data: TransitionCreateData): Promise<Transition> {
    const endpoint = new APIEndPoint('/api/transitions', '/api/transitions');
    const response = await endpoint.create(data);
    // Backend retourne [201, data]
    return response[1] || response;
  },

  /**
   * PATCH /api/transitions/{id}
   * Met à jour une transition
   */
  async update(id: string, data: TransitionUpdateData): Promise<Transition> {
    const endpoint = new APIEndPoint(`/api/transitions/${id}`, `/api/transitions/${id}`);
    return await endpoint.partial_update(data);
  },

  /**
   * DELETE /api/transitions/{id}
   * Supprime une transition
   */
  async delete(id: string): Promise<void> {
    const endpoint = new APIEndPoint(`/api/transitions/${id}`, `/api/transitions/${id}`);
    await endpoint.destroy();
  }
};

