import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { attendanceService } from '../services/attendance.service';
import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import type { PaginatedResponse, EmploymentSchemeOut, EmploymentSchemeCreateIn, DailyViewEntryOut, PunchCreateIn } from '../api/attendance.endpoints';


export const assignmentQueryKeys = {
  all: ['assignments'] as const,
  list: (page: number = 1, limit: number = 50, search?: string, orgUnit?: string, recurrence?: string, ordering?: string) =>
    [...assignmentQueryKeys.all, 'list', page, limit, search ?? '', orgUnit ?? '', recurrence ?? '', ordering ?? 'name'] as const,
};

export const policyQueryKeys = {
  all: ['policies'] as const,
  list: (search?: string, ordering?: string) =>
    [...policyQueryKeys.all, 'list', search ?? '', ordering ?? 'name'] as const,
};

export const dailyViewQueryKeys = {
  all: ['daily-view'] as const,
  list: (date: string, search?: string, orgUnit?: string, status?: string) =>
    [...dailyViewQueryKeys.all, 'list', date, search ?? '', orgUnit ?? '', status ?? ''] as const,
};


/**
 * TanStack Query for fetching all policy assignments with pagination.
 */
export function useAssignmentsQuery(
  page: () => number = () => 1,
  limit: () => number = () => 10,
  search: () => string = () => '',
  orgUnit: () => string = () => '',
  recurrence: () => string = () => '',
  sortBy: () => string = () => 'name',
  sortOrder: () => 'asc' | 'desc' = () => 'asc',
) {
  return createQuery({
    get queryKey() {
      const ordering = sortOrder() === 'desc' ? `-${sortBy()}` : sortBy();
      return assignmentQueryKeys.list(page(), limit(), search(), orgUnit(), recurrence(), ordering);
    },
    queryFn: (): Promise<PaginatedResponse<EmploymentSchemeOut>> =>
      attendanceService.listAssignments({
        page: page(),
        page_size: limit(),
        search: search() || undefined,
        org_unit: orgUnit() || undefined,
        recurrence: recurrence() || undefined,
        ordering: (() => {
          const order = sortOrder() === 'desc' ? `-${sortBy()}` : sortBy();
          return order;
        })(),
      }),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * TanStack Query for fetching shift policies with optional search & ordering.
 */
export function usePoliciesQuery(
  search: () => string = () => '',
  ordering: () => string = () => 'name',
) {
  return createQuery({
    get queryKey() {
      return policyQueryKeys.list(search(), ordering());
    },
    queryFn: () => attendanceService.listPolicies({
      search: search() || undefined,
      ordering: ordering() || undefined,
    }),
    staleTime: 1000 * 60 * 5,
    gcTime: 1000 * 60 * 10,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * TanStack Query for fetching the enriched daily view entries.
 */
export function useDailyViewQuery(
  date: () => string,
  search: () => string = () => '',
  orgUnit: () => string = () => '',
  status: () => string = () => '',
) {
  return createQuery<DailyViewEntryOut[], Error, DailyViewEntryOut[], readonly ["daily-view", "list", string, string, string, string]>({
    get queryKey() {
      return dailyViewQueryKeys.list(date(), search(), orgUnit(), status());
    },
    queryFn: (): Promise<DailyViewEntryOut[]> =>
      attendanceService.getDailyView({
        date: date(),
        search: search() || undefined,
        org_unit: orgUnit() || undefined,
        status: status() || undefined,
      }),
    placeholderData: (previousData) => previousData,
    staleTime: 1000 * 60 * 2,
    gcTime: 1000 * 60 * 10,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * Mutation for creating a policy assignment (base or override).
 */
export function useCreateAssignmentMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: {
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
    }) => attendanceService.createAssignment(data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assignmentQueryKeys.all });
    },
  });
}


/**
 * Mutation for updating an existing policy assignment (PATCH).
 */
export function useUpdateAssignmentMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      assignmentId,
      data,
    }: {
      assignmentId: string;
      data: Partial<EmploymentSchemeCreateIn>;
    }) => attendanceService.updateAssignment(assignmentId, data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assignmentQueryKeys.all });
    },
  });
}


/**
 * Extracts total count from paginated response.
 */
export function getAssignmentTotalCount(data: PaginatedResponse<EmploymentSchemeOut> | undefined): number {
  return data?.count ?? 0;
}


/**
 * Mutation for deleting a policy assignment.
 */
export function useDeleteAssignmentMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (id: string) => attendanceService.deleteAssignment(id),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: assignmentQueryKeys.all });
    },
  });
}


/**
 * Mutation for finalizing a daily register.
 */
export function useFinalizeDayMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (date: string) => attendanceService.finalizeDailyRegister(date),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dailyViewQueryKeys.all });
    },
  });
}


/**
 * Mutation for unfinalizing a daily register.
 */
export function useUnfinalizeDayMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (date: string) => attendanceService.unfinalizeDailyRegister(date),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dailyViewQueryKeys.all });
    },
  });
}


/**
 * Mutation for updating a timesheet status/remarks (e.g. mark absence as excused).
 */
export function useUpdateTimesheetMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ timesheetId, data }: { timesheetId: string; data: { status?: string; remarks?: string } }) =>
      attendanceService.updateTimesheetStatus(timesheetId, data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dailyViewQueryKeys.all });
      notification.toast.success('Statut mis à jour');
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for adjusting a punch.
 */
export function useAdjustPunchMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ punchId, data }: { punchId: string; data: { start_at?: string; end_at?: string } }) =>
      attendanceService.adjustPunch(punchId, data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dailyViewQueryKeys.all });
      notification.toast.success('Pointage mis à jour avec succès');
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for creating a new punch (when no punchId exists yet).
 */
export function useRecordPunchMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: PunchCreateIn) => attendanceService.recordPunch(data),

    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: dailyViewQueryKeys.all });
      notification.toast.success('Pointage créé avec succès');
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation for self check-in/out by the employee.
 */
export function useSelfPunchMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (data: import('../api/attendance.endpoints').SelfPunchIn) =>
      attendanceService.selfPunch(data),

    onSuccess: (result) => {
      queryClient.invalidateQueries({ queryKey: dailyViewQueryKeys.all });
      const actionLabel = result.action === 'in' ? "Pointage d'entrée enregistré" : 'Pointage de sortie enregistré';
      notification.toast.success(actionLabel);
    },

    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}
