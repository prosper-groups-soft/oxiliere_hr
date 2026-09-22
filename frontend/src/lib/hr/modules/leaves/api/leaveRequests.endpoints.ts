import APIEndPoint from '@/hr/utilities/http/rest';
import type { LeaveRequest, LeaveType, WorkingDaysCount } from '../types/types';
import { 
  BACKEND_LEAVE_CATEGORIES, 
  FRONTEND_LEAVE_CATEGORIES,
  FRONTEND_LEAVE_STATUSES,
} from '../constants/leaves';


/** Maps frontend LeaveType to backend LeaveCategory */
export function toBackendCategory(type: LeaveType): string {
  return BACKEND_LEAVE_CATEGORIES[type];
}

/** Maps backend LeaveCategory to frontend LeaveType */
export function toFrontendCategory(cat: string): LeaveType {
  return FRONTEND_LEAVE_CATEGORIES[cat] || 'annual';
}


/** Maps backend LeaveStatus to frontend LeaveStatus */
export function toFrontendStatus(status: string): 'pending' | 'approved' | 'rejected' {
  const s = FRONTEND_LEAVE_STATUSES[status];
  return s || 'pending';
}


/** Raw response shape from the backend for a leave request */
export interface LeaveRequestBackendResponse {
  id: string;
  employee: string; // employee UUID
  employee_name: string;
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  job_title?: string;
  org_unit?: string;
  avatar_url?: string;
  category: string;
  circumstance_type?: string;
  start_date: string;
  end_date: string;
  requested_days: number;
  status: string;
  attachment?: string;
  comment?: string;
}


/** A single day of leave in the team planner Gantt view */
export interface TeamPlannerDay {
  date: string;
  type: string;
  status: string;
}


/** Employee with their expanded leave days for the team planner */
export interface TeamPlannerEmployee {
  employee_id: string;
  employee_name: string;
  org_unit?: string;
  avatar_url?: string;
  days: TeamPlannerDay[];
}

/** Maps backend response to frontend LeaveRequest */
function mapToFrontend(raw: LeaveRequestBackendResponse): LeaveRequest {
  // Parse comment: backend appends status lines like "[APPROUVÉ] Par ... le ..."
  // The first non-prefix part is the original reason, any [PREFIX] lines are for the approver column
  const APPROVAL_PREFIXES = ['[APPROUVÉ]', '[REJETÉ]', '[ANNULÉ]', '[ARCHIVÉ]', '[CONVERTI]', '[DOC]'];
  let reason = '';
  let approver = '';
  
  if (raw.comment) {
    const lines = raw.comment.split('\n').filter(Boolean);
    const approvalLines: string[] = [];
    const reasonLines: string[] = [];
    
    for (const line of lines) {
      const trimmed = line.trim();
      if (APPROVAL_PREFIXES.some(p => trimmed.startsWith(p))) {
        approvalLines.push(trimmed);
      } else {
        reasonLines.push(trimmed);
      }
    }
    
    reason = reasonLines.join(' ');
    approver = approvalLines.join(' | ');
  }

  return {
    id: raw.id,
    employeeId: raw.employee,
    employeeName: raw.employee_name || 'N/A',
    firstName: raw.first_name,
    lastName: raw.last_name,
    middleName: raw.middle_name,
    avatarUrl: raw.avatar_url,
    jobTitle: raw.job_title,
    orgUnit: raw.org_unit || '',
    type: toFrontendCategory(raw.category),
    circumstanceType: raw.circumstance_type,
    status: toFrontendStatus(raw.status),
    startDate: raw.start_date,
    endDate: raw.end_date,
    days: raw.requested_days,
    reason,
    approver,
    attachment: raw.attachment,
    createdAt: new Date().toISOString().split('T')[0],
  };
}


/** Maps backend snake_case response to frontend camelCase WorkingDaysCount */
function mapWorkingDaysCount(raw: any): WorkingDaysCount {
  return {
    workingDays: raw.working_days,
    calendarDays: raw.calendar_days,
    excluded: {
      publicHolidays: raw.excluded?.public_holidays ?? [],
      closures: raw.excluded?.closures ?? [],
      nonWorkingPolicyDays: raw.excluded?.non_working_policy_days ?? [],
      totalExcluded: raw.excluded?.total_excluded ?? 0,
    },
    dayDetails: (raw.day_details ?? []).map((d: any) => ({
      date: d.date,
      dayName: d.day_name,
      isWorking: d.is_working,
      reason: d.reason,
      eventType: d.event_type ?? undefined,
      eventName: d.event_name ?? undefined,
      startTime: d.start_time ?? undefined,
      endTime: d.end_time ?? undefined,
    })),
  };
}


/** Shape of the balance summary from GET /api/leaves/balances/summary/{id} */
interface BalanceSummaryRaw {
  allocated: number;
  deducted: number;
  available: number;
  carry_over?: {
    total: number;
    used: number;
    available: number;
    expires_at: string;
  };
  total_available: number;
}

/** Enriched frontend balance with carry-over details */
export interface BalanceSummary {
  allocated: number;
  deducted: number;
  available: number;
  totalAvailable: number;
  carryOver?: {
    total: number;
    used: number;
    available: number;
    expiresAt: string;
  };
}

/** Maps backend balance summary to frontend enriched BalanceSummary */
function mapBalanceSummary(raw: BalanceSummaryRaw): BalanceSummary {
  return {
    allocated: raw.allocated,
    deducted: raw.deducted,
    available: raw.available,
    totalAvailable: raw.total_available,
    carryOver: raw.carry_over
      ? {
          total: raw.carry_over.total,
          used: raw.carry_over.used,
          available: raw.carry_over.available,
          expiresAt: raw.carry_over.expires_at,
        }
      : undefined,
  };
}


/**
 * Endpoints API pour les demandes de congé
 * Base path: /api/leaves
 */
export const leaveRequestsEndpoint = {
  /**
   * POST /api/leaves/requests/employee/{employee_id}
   * Crée une demande de congé pour un employé spécifique (RH)
   */
  createForEmployee: async (
    employeeId: string,
    data: {
      category: string;
      circumstance_type?: string;
      start_date: string;
      end_date: string;
      comment?: string;
      attachment?: File;
    }
  ): Promise<LeaveRequestBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/leaves/requests/employee/${employeeId}`,
      `/api/leaves/requests/employee/${employeeId}`
    );
    // Le backend a un paramètre File optionnel → nécessite multipart/form-data
    // Django Ninja attend le corps du schéma dans un champ JSON 'data'
    const formData = new FormData();
    const bodyPayload: Record<string, any> = {
      category: data.category,
      start_date: data.start_date,
      end_date: data.end_date,
    };
    if (data.comment) bodyPayload.comment = data.comment;
    if (data.circumstance_type) bodyPayload.circumstance_type = data.circumstance_type;
    formData.append('data', JSON.stringify(bodyPayload));
    if (data.attachment) formData.append('attachment', data.attachment);
    const response = await endpoint.create(formData);
    // Backend returns [201, data] for creation
    return response[1] || response;
  },

  /**
   * POST /api/leaves/requests/{request_id}/approve
   * Approuve une demande de congé
   */
  approve: async (requestId: string): Promise<LeaveRequestBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/leaves/requests/${requestId}/approve`,
      `/api/leaves/requests/${requestId}/approve`
    );
    const response = await endpoint.create({});
    return response[1] || response;
  },

  /**
   * POST /api/leaves/requests/{request_id}/reject
   * Rejette une demande de congé
   */
  reject: async (requestId: string, reason?: string): Promise<LeaveRequestBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/leaves/requests/${requestId}/reject`,
      `/api/leaves/requests/${requestId}/reject`
    );
    const response = await endpoint.create({ reason: reason || null });
    return response[1] || response;
  },
  list: async (params?: {
    page?: number;
    limit?: number;
    search?: string;
    category?: string;
    status?: string;
    org_unit?: string;
    sortBy?: string;
    sortOrder?: 'asc' | 'desc';
  }): Promise<{ results: LeaveRequestBackendResponse[]; count: number }> => {
    const queryParams = new URLSearchParams();
    if (params?.page) queryParams.set('page', params.page.toString());
    if (params?.limit) queryParams.set('limit', params.limit.toString());
    if (params?.search) queryParams.set('search', params.search);
    if (params?.category) queryParams.set('category', params.category);
    if (params?.status) queryParams.set('status', params.status);
    if (params?.org_unit) queryParams.set('org_unit', params.org_unit);

    // Map sorting
    if (params?.sortBy) {
      const orderPrefix = params.sortOrder === 'desc' ? '-' : '';
      const orderingMap: Record<string, string> = {
        createdAt: 'created_at',
        startDate: 'start_date',
        name: 'employee_name',
        days: 'requested_days',
      };
      const backendOrder = orderingMap[params.sortBy];
      if (backendOrder) {
        queryParams.set('ordering', `${orderPrefix}${backendOrder}`);
      }
    }

    const queryString = queryParams.toString();
    const url = queryString ? `/api/leaves/requests?${queryString}` : '/api/leaves/requests';

    const endpoint = new APIEndPoint(url, url);
    return await endpoint.list();
  },

  /**
   * GET /api/leaves/team-planner?year=&month=
   * Toutes les demandes non rejetées pour un mois donné (vue équipe)
   */
  getTeamPlanner: async (year: number, month: number): Promise<TeamPlannerEmployee[]> => {
    const endpoint = new APIEndPoint('/api/leaves/team-planner', '/api/leaves/team-planner');
    return await endpoint.list({ year, month });
  },

  /**
   * GET /api/leaves/requests/pending-count
   * Retourne le nombre de demandes de congé en attente
   */
  getPendingCount: async (): Promise<{ count: number }> => {
    const endpoint = new APIEndPoint('/api/leaves/requests/pending-count', '/api/leaves/requests/pending-count');
    return await endpoint.list();
  },

  /**
   * GET /api/leaves/requests/{request_id}
   * Détail d'une demande de congé
   */
  getById: async (requestId: string): Promise<LeaveRequestBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/leaves/requests/${requestId}`,
      `/api/leaves/requests/${requestId}`
    );
    return await endpoint.retrieve();
  },

  /**
   * GET /api/leaves/working-days-count
   * Calcule le détail des jours ouvrés pour une période et un employé
   */
  countWorkingDays: async (
    employeeId: string,
    startDate: string,
    endDate: string
  ): Promise<WorkingDaysCount> => {
    const endpoint = new APIEndPoint(
      '/api/leaves/working-days-count',
      '/api/leaves/working-days-count'
    );
    const params = {
      employee_id: employeeId,
      start_date: startDate,
      end_date: endDate,
    };
    const response = await endpoint.list(params);
    return mapWorkingDaysCount(response);
  },

  /**
   * GET /api/leaves/balances/summary/{employee_id}
   * Récupère le solde de congés réel d'un employé depuis la DB
   */
  getBalanceSummary: async (
    employeeId: string,
    year?: number
  ): Promise<BalanceSummary> => {
    const base = `/api/leaves/balances/summary/${employeeId}`;
    const endpoint = new APIEndPoint(base, base);
    const response = await endpoint.list(year ? { year } : {});
    return mapBalanceSummary(response);
  },

  /**
   * GET /api/leaves/overlap-check
   * Détecte les congés qui chevauchent une période donnée.
   * excluded_categories: comma-separated list of categories to exclude from the check.
   *   Exemple: 'ANNUAL,CIRCUMSTANCE,UNPAID' pour ne vérifier que les chevauchements SICK.
   */
  checkOverlap: async (
    employeeId: string,
    startDate: string,
    endDate: string,
    excludedCategories?: string,
  ): Promise<{ hasOverlap: boolean; leaves: Array<{ id: string; category: string; start_date: string; end_date: string; requested_days: number; status: string }> }> => {
    const endpoint = new APIEndPoint('/api/leaves/overlap-check', '/api/leaves/overlap-check');
    const params: Record<string, string> = {
      employee_id: employeeId,
      start_date: startDate,
      end_date: endDate,
    };
    if (excludedCategories) {
      params.excluded_categories = excludedCategories;
    }
    return await endpoint.list(params);
  },
  /**
   * PATCH /api/leaves/requests/{request_id}
   * Modifie une demande de congé en attente
   */
  update: async (
    requestId: string,
    data: {
      category?: string;
      circumstance_type?: string;
      start_date?: string;
      end_date?: string;
      comment?: string;
      attachment?: File;
    }
  ): Promise<LeaveRequestBackendResponse> => {
    const endpoint = new APIEndPoint(
      `/api/leaves/requests/${requestId}/hr-update`,
      `/api/leaves/requests/${requestId}/hr-update`
    );
    // Backend gère multipart/form-data si attachment présent
    const formData = new FormData();
    const bodyPayload: Record<string, any> = {};
    if (data.category) bodyPayload.category = data.category;
    if (data.circumstance_type) bodyPayload.circumstance_type = data.circumstance_type;
    if (data.start_date) bodyPayload.start_date = data.start_date;
    if (data.end_date) bodyPayload.end_date = data.end_date;
    if (data.comment !== undefined) bodyPayload.comment = data.comment;
    formData.append('data', JSON.stringify(bodyPayload));
    if (data.attachment) formData.append('attachment', data.attachment);
    const response = await endpoint.partial_update(formData);
    return response[1] || response;
  },
}


export { mapToFrontend };

