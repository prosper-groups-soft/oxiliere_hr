import APIEndPoint from '@/utilities/http/rest';


export interface ShiftPolicyOut {
  id: string;
  name: string;
  description: string;
  weekly_target_hours: number; // hours
  details: ShiftDetailOut[];
  created_at?: string;
  updated_at?: string;
}

export interface ShiftPeriodOut {
  id: string;
  name: string;
  period_type: string; // "WORK" | "BREAK"
  start_time: string;  // HH:mm
  end_time: string;    // HH:mm
}

export interface ShiftDetailOut {
  weekday: string; // e.g. "MONDAY", "TUESDAY", etc.
  start_time: string | null; // HH:mm (derived from periods)
  end_time: string | null;
  break_start_time: string | null;
  break_duration: string | null; // ISO 8601 duration e.g. "P0DT02H00M00S"
  is_working_day: boolean;
  flexible_hours: boolean;
  periods: ShiftPeriodOut[];
}

export interface ShiftPeriodIn {
  name: string;
  period_type: "WORK" | "BREAK";
  start_time: string; // HH:mm
  end_time: string;   // HH:mm
}

export interface DayConfigIn {
  work: boolean;
  periods?: ShiftPeriodIn[];
}

export interface ShiftPolicyCreateIn {
  name: string;
  description?: string;
  weekly_target_hours: number; // in seconds
  daily_configs: Record<string, DayConfigIn>;
}

export interface ShiftPolicyUpdateIn {
  name?: string;
  description?: string;
  weekly_target_hours?: number;
  daily_configs?: Record<string, DayConfigIn>;
}

export interface PaginatedResponse<T> {
  results: T[];
  count: number;
  next: string | null;
  previous: string | null;
}


export interface EmploymentSchemeOut {
  id: string;
  employee_id: string;
  employee_name: string;
  first_name?: string;
  last_name?: string;
  middle_name?: string;
  profile_photo?: string | null;
  policy_id: string;
  policy_name: string;
  valid_from: string;
  valid_until: string | null;
  is_active: boolean;
  recurrence?: string;
  job_title?: string;
  current_status?: string;
  override_policy_id?: string | null;
  override_policy_name?: string | null;
  override_valid_from?: string | null;
  override_valid_until?: string | null;
  override_recurrence?: string;
  override_recurrence_count?: number | null;
  org_unit_id?: string | null;
  org_unit_name?: string | null;
}

export interface EmploymentSchemeCreateIn {
  employee_id: string;
  policy_id: string;
  start_date: string;
  end_date?: string | null;
  recurrence?: string;
  override_policy_id?: string | null;
  override_valid_from?: string | null;
  override_valid_until?: string | null;
  override_recurrence?: string;
  override_recurrence_count?: number | null;
}


export interface PunchCreateIn {
  timestamp: string;      // ISO datetime
  punch_type?: string;    // "WORK" (default)
  is_manual?: boolean;
  employee_id: string;
  latitude?: number | null;
  longitude?: number | null;
}

export interface PunchOut {
  id: string;
  punch_type: string;
  start_at: string;
  end_at: string | null;
  duration: number;
  is_manual_entry: boolean;
}

export interface SelfPunchIn {
  timestamp: string;      // ISO datetime
  latitude?: number | null;
  longitude?: number | null;
}

export interface SelfPunchOut {
  punch: PunchOut;
  action: 'in' | 'out';
  employee_id: string;
}

export interface DailyViewEntryOut {
  id: string;
  employee_id: string;
  employee_name: string;
  first_name?: string;
  last_name?: string;
  avatar_url?: string | null;
  job_title?: string | null;
  org_unit_id?: string | null;
  org_unit_name?: string | null;

  register_date: string;

  check_in?: string | null;        // HH:mm
  check_out?: string | null;       // HH:mm
  check_in_at?: string | null;     // ISO datetime
  check_out_at?: string | null;    // ISO datetime
  check_in_punch_id?: string | null; // UUID pour edition inline
  check_out_punch_id?: string | null;
  is_manual_entry: boolean;

  expected_in?: string | null;     // HH:mm
  expected_out?: string | null;    // HH:mm
  expected_break_duration?: number | null;  // minutes

  is_working_day: boolean;
  schedule_name?: string | null;
  schedule_source?: string | null;  // "policy" | "override" | "holiday" | "none"

  recorded_work: string;  // ISO duration
  recorded_break: string;
  overtime: string;
  shortfall: string;
  status: string;
  remarks?: string | null;

  is_locked: boolean;
  is_finalized: boolean;
  anomalies: string[];
}


/**
 * Endpoints API pour la gestion des présences (attendance)
 * Base path: /api/attendance...
 *
 * Note: les URLs sont SANS slash final pour correspondre
 * au routage Django-Ninja (APPEND_SLASH ne retire pas les slashes).
 */
export const attendanceEndpoint = {

  /**
   * POST /api/scheduling/shifts
   * Crée une nouvelle politique de shift avec sa configuration hebdomadaire
   */
  createShiftPolicy: async (data: ShiftPolicyCreateIn): Promise<ShiftPolicyOut> => {
    const endpoint = new APIEndPoint('/api/scheduling/shifts', '/api/scheduling/shifts');
    return await endpoint.create(data);
  },

  /**
   * GET /api/scheduling/shifts
   * Liste toutes les politiques de shift
   */
  listShiftPolicies: async (params?: { search?: string; ordering?: string }): Promise<PaginatedResponse<ShiftPolicyOut>> => {
    const endpoint = new APIEndPoint('/api/scheduling/shifts', '/api/scheduling/shifts');
    return await endpoint.list(params);
  },

  /**
   * PATCH /api/scheduling/policies/{policy_id}
   * Met à jour les champs de base d'une politique
   */
  updateShiftPolicy: async (policyId: string, data: ShiftPolicyUpdateIn): Promise<ShiftPolicyOut> => {
    const endpoint = new APIEndPoint(
      `/api/scheduling/policies/${policyId}`,
      `/api/scheduling/policies/${policyId}`
    );
    return await endpoint.partial_update(data);
  },

  /**
   * DELETE /api/scheduling/policies/{policy_id}
   * Supprime une politique de shift
   */
  deleteShiftPolicy: async (policyId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/scheduling/policies/${policyId}`,
      `/api/scheduling/policies/${policyId}`
    );
    return await endpoint.destroy();
  },

  // ==========================================
  // Policy Assignments (EmploymentScheme)
  // ==========================================

  /**
   * GET /api/scheduling/assignments
   * Liste toutes les affectations (policy assignments)
   */
  listAssignments: async (params?: { 
    page?: number; 
    page_size?: number;
    search?: string;
    org_unit?: string;
    recurrence?: string;
    ordering?: string;
  }): Promise<PaginatedResponse<EmploymentSchemeOut>> => {
    const endpoint = new APIEndPoint('/api/scheduling/assignments', '/api/scheduling/assignments');
    return await endpoint.list(params || { page: 1, page_size: 10 });
  },

  /**
   * POST /api/scheduling/assignments
   * Crée une affectation policy → employé
   */
  createAssignment: async (data: EmploymentSchemeCreateIn): Promise<EmploymentSchemeOut> => {
    const endpoint = new APIEndPoint('/api/scheduling/assignments', '/api/scheduling/assignments');
    return await endpoint.create(data);
  },

  /**
   * DELETE /api/scheduling/assignments/{assignment_id}
   * Supprime une affectation
   */
  deleteAssignment: async (assignmentId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/scheduling/assignments/${assignmentId}`,
      `/api/scheduling/assignments/${assignmentId}`
    );
    return await endpoint.destroy();
  },

  /**
   * PATCH /api/scheduling/assignments/{assignment_id}
   * Met à jour partiellement une affectation existante
   */
  updateAssignment: async (assignmentId: string, data: Partial<EmploymentSchemeCreateIn>): Promise<EmploymentSchemeOut> => {
    const endpoint = new APIEndPoint(
      `/api/scheduling/assignments/${assignmentId}`,
      `/api/scheduling/assignments/${assignmentId}`
    );
    return await endpoint.partial_update(data);
  },

  // ==========================================
  // Daily View & Register
  // ==========================================

  /**
   * GET /api/attendance/daily-view
   * Vue quotidienne enrichie des pointages
   */
  getDailyView: async (params: {
    date: string;
    search?: string;
    org_unit?: string;
    status?: string;
  }): Promise<DailyViewEntryOut[]> => {
    const endpoint = new APIEndPoint('/api/attendance/daily-view', '/api/attendance/daily-view');
    return await endpoint.list(params);
  },

  /**
   * POST /api/attendance/registry/daily-registers/finalize
   * Finalise un registre quotidien
   */
  finalizeDay: async (data: { date: string }): Promise<any> => {
    const endpoint = new APIEndPoint('/api/attendance/registry/daily-registers/finalize', '/api/attendance/registry/daily-registers/finalize');
    return await endpoint.create(data);
  },

  /**
   * POST /api/attendance/registry/daily-registers/unfinalize
   * Dé-finalise un registre quotidien
   */
  unfinalizeDay: async (data: { date: string }): Promise<any> => {
    const endpoint = new APIEndPoint('/api/attendance/registry/daily-registers/unfinalize', '/api/attendance/registry/daily-registers/unfinalize');
    return await endpoint.create(data);
  },

  /**
   * PATCH /api/attendance/timesheets/{timesheet_id}
   * Met à jour le statut ou les remarques d'une timesheet (ex: marquer absence justifiée)
   */
  updateTimesheet: async (timesheetId: string, data: { status?: string; remarks?: string }): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/attendance/timesheets/${timesheetId}`,
      `/api/attendance/timesheets/${timesheetId}`
    );
    return await endpoint.partial_update(data);
  },

  /**
   * PATCH /api/attendance/punch/{punch_id}
   * Corrige un pointage
   */
  adjustPunch: async (punchId: string, data: { start_at?: string; end_at?: string }): Promise<any> => {
    const endpoint = new APIEndPoint(
      `/api/attendance/punch/${punchId}`,
      `/api/attendance/punch/${punchId}`
    );
    return await endpoint.partial_update(data);
  },

  /**
   * POST /api/attendance/punches/manual
   * Crée un nouveau pointage manuel par les RH (quand aucun punchId n'existe)
   */
  recordPunch: async (data: PunchCreateIn): Promise<PunchOut> => {
    const endpoint = new APIEndPoint(
      '/api/attendance/punches/manual',
      '/api/attendance/punches/manual'
    );
    return await endpoint.create(data);
  },

  /**
   * POST /api/attendance/punches/self
   * Auto-pointage par l'employé (clock-in/clock-out)
   */
  selfPunch: async (data: SelfPunchIn): Promise<SelfPunchOut> => {
    const endpoint = new APIEndPoint(
      '/api/attendance/punches/self',
      '/api/attendance/punches/self'
    );
    return await endpoint.create(data);
  },
};

