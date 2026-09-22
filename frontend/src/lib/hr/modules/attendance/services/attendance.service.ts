import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { attendanceEndpoint } from '../api/attendance.endpoints';
import type { ShiftPolicyOut, ShiftPolicyCreateIn, ShiftPolicyUpdateIn, EmploymentSchemeOut, EmploymentSchemeCreateIn, PaginatedResponse, DailyViewEntryOut } from '../api/attendance.endpoints';


/**
 * Service pour la gestion des présences
 * Utilise les endpoints dédiés dans le dossier api/
 */
class AttendanceService {

  // Shift Policies

  async listPolicies(params?: { search?: string; ordering?: string }): Promise<ShiftPolicyOut[]> {
    try {
      const response = await attendanceEndpoint.listShiftPolicies(params);
      return response.results ?? [];
    } catch (error: any) {
      console.error('[AttendanceService] listPolicies error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async createPolicy(data: ShiftPolicyCreateIn): Promise<ShiftPolicyOut> {
    try {
      const policy = await attendanceEndpoint.createShiftPolicy(data);
      notification.toast.success('Modèle de travail créé avec succès');
      return policy;
    } catch (error: any) {
      console.error('[AttendanceService] createPolicy error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async updatePolicy(policyId: string, data: ShiftPolicyUpdateIn): Promise<ShiftPolicyOut> {
    try {
      const policy = await attendanceEndpoint.updateShiftPolicy(policyId, data);
      notification.toast.success('Modèle de travail mis à jour');
      return policy;
    } catch (error: any) {
      console.error('[AttendanceService] updatePolicy error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async deletePolicy(policyId: string): Promise<void> {
    try {
      await attendanceEndpoint.deleteShiftPolicy(policyId);
      notification.toast.success('Modèle de travail supprimé');
    } catch (error: any) {
      console.error('[AttendanceService] deletePolicy error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  
  // Policy Assignments (EmploymentScheme)

  async listAssignments(params?: { 
    page?: number; 
    page_size?: number;
    search?: string;
    org_unit?: string;
    recurrence?: string;
    ordering?: string;
  }): Promise<PaginatedResponse<EmploymentSchemeOut>> {
    try {
      return await attendanceEndpoint.listAssignments(params || { page: 1, page_size: 10 });
    } catch (error: any) {
      console.error('[AttendanceService] listAssignments error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async createAssignment(data: EmploymentSchemeCreateIn): Promise<EmploymentSchemeOut> {
    try {
      return await attendanceEndpoint.createAssignment(data);
    } catch (error: any) {
      console.error('[AttendanceService] createAssignment error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async updateAssignment(assignmentId: string, data: Partial<EmploymentSchemeCreateIn>): Promise<EmploymentSchemeOut> {
    try {
      return await attendanceEndpoint.updateAssignment(assignmentId, data);
    } catch (error: any) {
      console.error('[AttendanceService] updateAssignment error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async deleteAssignment(assignmentId: string): Promise<void> {
    try {
      await attendanceEndpoint.deleteAssignment(assignmentId);
    } catch (error: any) {
      console.error('[AttendanceService] deleteAssignment error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  
  // Daily View & Register

  async getDailyView(params: {
    date: string;
    search?: string;
    org_unit?: string;
    status?: string;
  }): Promise<DailyViewEntryOut[]> {
    try {
      return await attendanceEndpoint.getDailyView(params);
    } catch (error: any) {
      console.error('[AttendanceService] getDailyView error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async finalizeDailyRegister(date: string): Promise<any> {
    try {
      const result = await attendanceEndpoint.finalizeDay({ date });
      notification.toast.success('Registre de la journée finalisé avec succès');
      return result;
    } catch (error: any) {
      console.error('[AttendanceService] finalizeDailyRegister error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async unfinalizeDailyRegister(date: string): Promise<any> {
    try {
      const result = await attendanceEndpoint.unfinalizeDay({ date });
      notification.toast.success('Registre de la journée dé-finalisé');
      return result;
    } catch (error: any) {
      console.error('[AttendanceService] unfinalizeDailyRegister error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async updateTimesheetStatus(timesheetId: string, data: { status?: string; remarks?: string }): Promise<any> {
    try {
      const result = await attendanceEndpoint.updateTimesheet(timesheetId, data);
      return result;
    } catch (error: any) {
      console.error('[AttendanceService] updateTimesheet error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  async adjustPunch(punchId: string, data: { start_at?: string; end_at?: string }): Promise<any> {
    try {
      const result = await attendanceEndpoint.adjustPunch(punchId, data);
      return result;
    } catch (error: any) {
      console.error('[AttendanceService] adjustPunch error:', error);
      throw error;
    }
  }

  async recordPunch(data: import('../api/attendance.endpoints').PunchCreateIn): Promise<import('../api/attendance.endpoints').PunchOut> {
    try {
      const result = await attendanceEndpoint.recordPunch(data);
      return result;
    } catch (error: any) {
      console.error('[AttendanceService] recordPunch error:', error);
      throw error;
    }
  }

  async selfPunch(data: import('../api/attendance.endpoints').SelfPunchIn): Promise<import('../api/attendance.endpoints').SelfPunchOut> {
    try {
      const result = await attendanceEndpoint.selfPunch(data);
      return result;
    } catch (error: any) {
      console.error('[AttendanceService] selfPunch error:', error);
      throw error;
    }
  }
}

export const attendanceService = new AttendanceService();

