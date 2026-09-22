import type { Vacancy, VacancyPriority, VacancyStatus } from '../types/types';
import APIEndPoint from '@/hr/utilities/http/rest';
import type { PaginatedResponse } from '@/hr/types/pagination';
import type { JobPosition } from '../types/types';


/**
 * Raw API response structure for vacancies
 * Backend returns nested position object, not just ID
 */
interface VacancyApiResponse {
  id: string;
  position_id: string;
  position: {
    id: string;
    name: string;
    level: string;
    job_family?: {
      id: string;
      name: string;
    };
    org_unit?: {
      id: string;
      name: string;
      type?: string;
    } | null;
  };
  priority: VacancyPriority;
  status: VacancyStatus;
  opened_date: string;
  target_date: string | null;
  reason: string | null;
  filled_date: string | null;
  created_at: string;
  updated_at: string;
}


/**
 * Map API response to frontend Vacancy format
 */
function mapVacancyResponse(apiData: VacancyApiResponse): Vacancy {
  return {
    id: apiData.id,
    positionId: apiData.position_id || apiData.position?.id || '',
    position: apiData.position ? {
      id: apiData.position.id,
      name: apiData.position.name,
      level: apiData.position.level,
      job_family: apiData.position.job_family || { id: '', name: '' },
      org_unit: apiData.position.org_unit || null,
      level_display: '',
      salary_min: 0,
      salary_max: 0,
      requirements: [],
      skills: []
    } : undefined,
    openedDate: apiData.opened_date,
    targetDate: apiData.target_date,
    priority: apiData.priority,
    status: apiData.status,
    reason: apiData.reason,
    filledDate: apiData.filled_date,
    createdAt: apiData.created_at,
    updatedAt: apiData.updated_at
  };
}


// Types pour les requêtes API
export interface VacancyCreateData {
  position_id: string;
  priority: VacancyPriority;
  status: VacancyStatus;
  opened_date?: string;
  target_date?: string | null;
  reason?: string;
}


export interface VacancyUpdateData {
  position_id?: string;
  priority?: VacancyPriority;
  status?: VacancyStatus;
  opened_date?: string;
  target_date?: string | null;
  reason?: string;
  filled_date?: string | null;
}


/**
 * Endpoints API pour les Vacancies (postes vacants)
 * Base path: /api/vacancies
 */
export const vacancyEndpoint = {
  /**
   * GET /api/vacancies
   * Liste toutes les vacancies (paginée)
   */
  async list(
    priority?: VacancyPriority,
    status?: VacancyStatus,
    page?: number,
    pageSize?: number,
    search?: string
  ): Promise<PaginatedResponse<Vacancy>> {
    const endpoint = new APIEndPoint('/api/vacancies', '/api/vacancies');

    // Construire les query params
    const params: Record<string, string> = {};
    if (priority) params.priority = priority;
    if (status) params.status = status;
    if (page) params.page = String(page);
    if (pageSize) params.page_size = String(pageSize);
    if (search) params.search = search;

    const response = await endpoint.list(params);

    // Handle paginated response
    const paginated = response as PaginatedResponse<VacancyApiResponse>;
    if (paginated.results) {
      return {
        count: paginated.count,
        next: paginated.next,
        previous: paginated.previous,
        results: paginated.results.map(mapVacancyResponse),
      };
    }

    // Fallback for non-paginated response
    const results = Array.isArray(response) ? response : [];
    return {
      count: results.length,
      next: null,
      previous: null,
      results: (results as VacancyApiResponse[]).map(mapVacancyResponse),
    };
  },

  /**
   * GET /api/vacancies/{id}
   * Récupère une vacancy par ID
   */
  async get(id: string): Promise<Vacancy> {
    const endpoint = new APIEndPoint(`/api/vacancies/${id}`, `/api/vacancies/${id}`);
    const response = await endpoint.retrieve() as VacancyApiResponse;
    return mapVacancyResponse(response);
  },

  /**
   * POST /api/vacancies
   * Crée une nouvelle vacancy
   */
  async create(data: VacancyCreateData): Promise<Vacancy> {
    const endpoint = new APIEndPoint('/api/vacancies', '/api/vacancies');
    const response = await endpoint.create(data) as VacancyApiResponse;
    return mapVacancyResponse(response);
  },

  /**
   * PATCH /api/vacancies/{id}
   * Met à jour une vacancy existante (partial update)
   */
  async update(id: string, data: VacancyUpdateData): Promise<Vacancy> {
    const endpoint = new APIEndPoint(`/api/vacancies/${id}`, `/api/vacancies/${id}`);
    const response = await endpoint.partial_update(data) as VacancyApiResponse;
    return mapVacancyResponse(response);
  },

  /**
   * DELETE /api/vacancies/{id}
   * Supprime une vacancy
   */
  async delete(id: string): Promise<void> {
    const endpoint = new APIEndPoint(`/api/vacancies/${id}`, `/api/vacancies/${id}`);
    await endpoint.destroy();
  },

  /**
   * POST /api/vacancies/{id}/close
   * Clôt une vacancy (marquer comme pourvue)
   */
  async close(id: string, transitionId?: string): Promise<Vacancy> {
    const endpoint = new APIEndPoint(
      `/api/vacancies/${id}/close`,
      `/api/vacancies/${id}/close`
    );
    const body = transitionId ? { transition_id: transitionId } : {};
    const response = await endpoint.create(body) as VacancyApiResponse;
    return mapVacancyResponse(response);
  }
};

      