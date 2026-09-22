import { createQuery, createMutation, useQueryClient } from '@tanstack/svelte-query';
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import { leaveRequestsEndpoint, toBackendCategory } from '../api/leaveRequests.endpoints';
import { leaveRequestsService } from '../services/leaveRequests.service';
import type { LeaveType, CircumstanceType } from '../types/types';
import { leaveSettingsService } from '@/hr/modules/leaves/services/leaveSettings.service';
import { DEFAULT_COUNTRY_CODE } from '@/hr/constants';
import type { LeaveConfig, SpecialLeave } from '@/hr/modules/leaves/types/leaveSettings.types';
import type { CircumstanceLeaveRule, LeavePolicy } from '@/hr/modules/leaves/schemas/leaveSettings.schemas';
import { DEFAULT_LEAVE_CONFIG } from '@/hr/modules/leaves/types/leaveSettings.types';
import { FRONTEND_CIRCUMSTANCE_TYPES, CIRCUMSTANCE_TYPE_LABELS, CIRCUMSTANCE_TYPE_ICONS } from '../constants/leaves';


// QUERY KEYS
export const leaveQueryKeys = {
  all: ['leaves'] as const,
  requests: () => [...leaveQueryKeys.all, 'requests'] as const,
  list: (page?: number, limit?: number, search?: string, filters?: any, sortBy?: string, sortOrder?: string) =>
    [...leaveQueryKeys.requests(), page ?? 1, limit ?? 10, search ?? '', filters ?? {}, sortBy ?? 'createdAt', sortOrder ?? 'desc'] as const,
  pendingCount: () => [...leaveQueryKeys.requests(), 'pending-count'] as const,
  balances: (employeeId?: string) => [...leaveQueryKeys.all, 'balances', employeeId] as const,
  balanceSummary: (employeeId: string) => [...leaveQueryKeys.all, 'balance-summary', employeeId] as const,
  workingDays: (employeeId: string, start: string, end: string) =>
    [...leaveQueryKeys.all, 'working-days', employeeId, start, end] as const,
  leaveConfig: () => [...leaveQueryKeys.all, 'leave-config'] as const,
  teamPlanner: (year: number, month: number) => [...leaveQueryKeys.all, 'team-planner', year, month] as const,
};


export function useLeaveRequestsQuery(
  page: () => number = () => 1,
  limit: () => number = () => 10,
  search: () => string = () => '',
  filters: () => { type?: string[]; status?: string[]; orgUnit?: string[] } = () => ({}),
  sortBy: () => string = () => 'createdAt',
  sortOrder: () => 'asc' | 'desc' = () => 'desc'
) {
  return createQuery({
    get queryKey() {
      return leaveQueryKeys.list(page(), limit(), search(), filters(), sortBy(), sortOrder());
    },
    queryFn: () => leaveRequestsService.listRequests(page(), limit(), search(), filters(), sortBy(), sortOrder()),
    staleTime: 1000 * 60 * 2, // 2 min
    gcTime: 1000 * 60 * 5,    // 5 min
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


export function usePendingCountQuery() {
  return createQuery({
    queryKey: leaveQueryKeys.pendingCount(),
    queryFn: () => leaveRequestsEndpoint.getPendingCount(),
    staleTime: 1000 * 60 * 2,
    gcTime: 1000 * 60 * 5,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


export function useTeamPlannerQuery(year: () => number, month: () => number) {
  return createQuery({
    get queryKey() {
      return leaveQueryKeys.teamPlanner(year(), month());
    },
    queryFn: () => leaveRequestsEndpoint.getTeamPlanner(year(), month()),
    staleTime: 1000 * 60 * 2,
    gcTime: 1000 * 60 * 5,
    refetchOnWindowFocus: true,
    refetchOnReconnect: true,
  });
}


/**
 * Mutation pour créer une demande de congé (pour un employé, via RH)
 */
export function useCreateLeaveRequestMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      employeeId,
      type,
      startDate,
      endDate,
      reason,
      circumstanceType,
      attachment,
    }: {
      employeeId: string;
      type: LeaveType;
      startDate: string;
      endDate: string;
      reason: string;
      circumstanceType?: string;
      attachment?: File;
    }) => {
      const payload: Parameters<typeof leaveRequestsEndpoint.createForEmployee>[1] = {
        category: toBackendCategory(type),
        start_date: startDate,
        end_date: endDate,
        comment: reason,
      };
      if (circumstanceType) {
        payload.circumstance_type = circumstanceType;
      }
      if (attachment) {
        payload.attachment = attachment;
      }
      return leaveRequestsEndpoint.createForEmployee(employeeId, payload);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.requests() });
      await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.balances() });
      await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.balanceSummary('') });
      notification.toast.success('Demande de congé créée avec succès');
    },
    onError: (error) => {
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
    },
  });
}


/**
 * Mutation pour approuver une demande de congé
 */
export function useApproveLeaveRequestMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: (requestId: string) => leaveRequestsEndpoint.approve(requestId),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.requests() });
      notification.toast.success('Demande approuvée');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation pour refuser une demande de congé
 */
export function useRejectLeaveRequestMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({ requestId, reason }: { requestId: string; reason?: string }) =>
      leaveRequestsEndpoint.reject(requestId, reason),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.requests() });
      notification.toast.success('Demande refusée');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Mutation pour modifier une demande de congé en attente
 */
export function useUpdateLeaveRequestMutation() {
  const queryClient = useQueryClient();

  return createMutation({
    mutationFn: ({
      requestId,
      type,
      startDate,
      endDate,
      reason,
      circumstanceType,
      attachment,
    }: {
      requestId: string;
      type: LeaveType;
      startDate: string;
      endDate: string;
      reason: string;
      circumstanceType?: string;
      attachment?: File;
    }) => {
      const payload: Parameters<typeof leaveRequestsEndpoint.update>[1] = {
        category: toBackendCategory(type),
        start_date: startDate,
        end_date: endDate,
        comment: reason,
      };
      if (circumstanceType) {
        payload.circumstance_type = circumstanceType;
      }
      if (attachment) {
        payload.attachment = attachment;
      }
      return leaveRequestsEndpoint.update(requestId, payload);
    },
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.requests() });
      await queryClient.invalidateQueries({ queryKey: leaveQueryKeys.balances() });
      notification.toast.success('Demande modifiée avec succès');
    },
    onError: (error) => {
      notification.toast.error(getFriendlyErrorMessage(error));
    },
  });
}


/**
 * Query pour récupérer le solde réel d'un employé depuis la DB
 */
export function useBalanceSummaryQuery(employeeId: string) {
  return createQuery({
    queryKey: leaveQueryKeys.balanceSummary(employeeId),
    queryFn: () => leaveRequestsEndpoint.getBalanceSummary(employeeId),
    staleTime: 1000 * 60 * 2, // 2 min
    gcTime: 1000 * 60 * 5,    // 5 min
    enabled: !!employeeId,
  });
}


// Leave Config (single object from combined endpoints)

function buildLeaveConfig(
  policy: LeavePolicy,
  circumstanceRules: CircumstanceLeaveRule[],
  seniorityRules: Array<{ id?: string; years_of_service: number; bonus_days: number }>
): LeaveConfig {
  const specialLeaves: SpecialLeave[] = [];

  for (const rule of circumstanceRules) {
    const frontendType = FRONTEND_CIRCUMSTANCE_TYPES[rule.type] as CircumstanceType | undefined;
    if (!frontendType) continue;
    const label = CIRCUMSTANCE_TYPE_LABELS[frontendType];
    const icon = CIRCUMSTANCE_TYPE_ICONS[frontendType];
    specialLeaves.push({
      type: frontendType,
      label,
      daysAllowed: rule.duration_days,
      description: rule.description || '',
      icon,
      isPaid: rule.is_paid,
    });
  }

  const seniorityBonus: LeaveConfig['seniorityBonus'] = seniorityRules?.length > 0
    ? {
        enabled: true,
        yearsPerBonus: seniorityRules[0].years_of_service,
        bonusDays: seniorityRules[0].bonus_days,
      }
    : { enabled: false, yearsPerBonus: 5, bonusDays: 1 };

  return {
    annualLeaveDays: policy.standard_annual_days,
    specialLeaves,
    seniorityBonus,
    allowsCarryOver: policy.allows_carry_over ?? false,
    maxCarryOverDays: policy.max_carry_over_days ?? 10,
    carryOverExpirationMonth: policy.carry_over_expiration_month ?? 3,
    allowHalfDays: true,
    requireApproval: true,
    maxConsecutiveDays: policy.max_consecutive_days ?? 30,
    noticePeriodDays: policy.notice_period_days ?? 15,
  };
}


/**
 * Query unique qui retourne un objet LeaveConfig complet.
 * Combine les appels policies + circumstance rules + seniority rules
 * et transforme le tout en un seul objet typé.
 */
export function useLeaveConfigQuery() {
  return createQuery({
    queryKey: leaveQueryKeys.leaveConfig(),
    queryFn: async () => {
      const policies = await leaveSettingsService.listPolicies();
      if (!policies?.length) {
        return { ...DEFAULT_LEAVE_CONFIG };
      }

      const cdPolicy = policies.find(p => p.country_code === DEFAULT_COUNTRY_CODE) || policies[0];
      if (!cdPolicy?.id) {
        return { ...DEFAULT_LEAVE_CONFIG };
      }

      const [circumstanceRules, seniorityRules] = await Promise.all([
        leaveSettingsService.listCircumstanceRules(cdPolicy.id),
        leaveSettingsService.listSeniorityRules(cdPolicy.id),
      ]);

      return buildLeaveConfig(cdPolicy, circumstanceRules ?? [], seniorityRules ?? []);
    },
    staleTime: 1000 * 60 * 5, // 5 min
    gcTime: 1000 * 60 * 10,   // 10 min
  });
}

