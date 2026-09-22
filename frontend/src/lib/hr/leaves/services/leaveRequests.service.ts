import { leaveRequestsEndpoint, mapToFrontend } from '../api/leaveRequests.endpoints';
import type { LeaveRequest } from '../types/types';
import { BACKEND_LEAVE_CATEGORIES, FRONTEND_LEAVE_STATUSES } from '../constants/leaves';


/**
 * Maps frontend LeaveType keys to backend category values for filter params
 */
function toBackendFilterCategory(frontendType: string): string | null {
  return BACKEND_LEAVE_CATEGORIES[frontendType as keyof typeof BACKEND_LEAVE_CATEGORIES] || null;
}


/**
 * Maps frontend LeaveStatus keys to backend status values for filter params
 */
function toBackendFilterStatus(frontendStatus: string): string | null {
  for (const [backend, frontend] of Object.entries(FRONTEND_LEAVE_STATUSES)) {
    if (frontend === frontendStatus) return backend;
  }
  return null;
}


/**
 * Service for leave requests CRUD with server-side pagination, filtering, and sorting.
 * Follows the same pattern as employees.service.ts.
 */
class LeaveRequestsService {
  /**
   * GET /api/leaves/requests
   * Lists leave requests with server-side pagination, search, filters, and sorting.
   */
  async listRequests(
    page?: number,
    limit?: number,
    search?: string,
    filters?: { type?: string[]; status?: string[]; orgUnit?: string[] },
    sortBy?: string,
    sortOrder?: 'asc' | 'desc'
  ): Promise<{ results: LeaveRequest[]; count: number }> {
    // Build category filter (comma-separated backend values)
    let categoryParam: string | undefined;
    if (filters?.type?.length) {
      const backendTypes = filters.type
        .map(t => toBackendFilterCategory(t))
        .filter(Boolean) as string[];
      if (backendTypes.length) categoryParam = backendTypes.join(',');
    }

    // Build status filter (comma-separated backend values)
    let statusParam: string | undefined;
    if (filters?.status?.length) {
      const backendStatuses = filters.status
        .map(s => toBackendFilterStatus(s))
        .filter(Boolean) as string[];
      if (backendStatuses.length) statusParam = backendStatuses.join(',');
    }

    // Build org unit filter (comma-separated)
    let orgUnitParam: string | undefined;
    if (filters?.orgUnit?.length) {
      orgUnitParam = filters.orgUnit.join(',');
    }

    const response = await leaveRequestsEndpoint.list({
      page,
      limit,
      search,
      category: categoryParam,
      status: statusParam,
      org_unit: orgUnitParam,
      sortBy,
      sortOrder,
    });

    return {
      results: (response.results || []).map(mapToFrontend),
      count: response.count || 0,
    };
  }
}


export const leaveRequestsService = new LeaveRequestsService();
