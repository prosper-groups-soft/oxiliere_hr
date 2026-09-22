/**
 * advances.client.svelte.ts — Client API dédié aux avances sur salaire.
 *
 * Responsabilité unique : gérer les états de chargement async (idle → loading → success/error)
 * et appeler les endpoints /payroll/advances/* uniquement.
 */

import { writable, get } from 'svelte/store';
import {
  requestAdvance as apiRequestAdvance,
  approveAdvance as apiApproveAdvance,
  activateAdvance as apiActivateAdvance,
  rejectAdvance as apiRejectAdvance,
  submitAdvance as apiSubmitAdvance,
  updateAdvance as apiUpdateAdvance,
  updateAdvanceFields as apiUpdateAdvanceFields,
} from '@/hr/modules/payroll/queries/payroll';
import type { AdvanceCreatePayload, AdvanceUpdatePayload } from '../../types/types';


export type AsyncState = 'idle' | 'loading' | 'success' | 'empty' | 'error' | 'offline';


interface AdvancesApiState {
  listState: AsyncState;
  mutationState: AsyncState;
  errors: Record<string, string | null>;
  isOnline: boolean;
}


function createAdvancesApiStore() {
  const state = writable<AdvancesApiState>({
    listState: 'idle',
    mutationState: 'idle',
    errors: {},
    isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
  });

  const { subscribe } = state;

  function setDomainState(domain: keyof Pick<AdvancesApiState, 'listState' | 'mutationState'>, newState: AsyncState, errorMsg?: string) {
    state.update(s => ({
      ...s,
      [domain]: newState,
      errors: { ...s.errors, [domain]: errorMsg ?? null }
    }));
  }

  async function withState<T>(
    domain: keyof Pick<AdvancesApiState, 'listState' | 'mutationState'>,
    fn: () => Promise<T>,
    isEmpty: (result: T) => boolean = () => false,
  ): Promise<T | null> {
    if (!get(state).isOnline) { setDomainState(domain, 'offline'); return null; }
    setDomainState(domain, 'loading');
    try {
      const result = await fn();
      setDomainState(domain, isEmpty(result) ? 'empty' : 'success');
      return result;
    } catch (err: any) {
      setDomainState(domain, 'error', err.message ?? 'Erreur inconnue');
      return null;
    }
  }

  if (typeof window !== 'undefined') {
    window.addEventListener('online', () => state.update(s => ({ ...s, isOnline: true })));
    window.addEventListener('offline', () => state.update(s => ({ ...s, isOnline: false })));
  }

  return {
    subscribe,

    async fetchAdvances(filters?: { status?: string; search?: string; risk_level?: string }) {
      return withState('listState', async () => {
        const mod = await import('@/hr/modules/payroll/queries/payroll');
        return mod.payrollQueryOptions.advanceList(filters).queryFn();
      }, (r) => !r?.results?.length);
    },

    async createAdvance(data: AdvanceCreatePayload) {
      return withState('mutationState', () => apiRequestAdvance(data));
    },

    async approveAdvance(advanceId: string) {
      return withState('mutationState', () => apiApproveAdvance(advanceId));
    },

    async activateAdvance(advanceId: string) {
      return withState('mutationState', () => apiActivateAdvance(advanceId));
    },

    async updateAdvanceConfig(advanceId: string, data: AdvanceUpdatePayload) {
      return withState('mutationState', () => apiUpdateAdvance(advanceId, data as any));
    },

    async updateAdvance(advanceId: string, data: Record<string, any>) {
      return withState('mutationState', () => apiUpdateAdvanceFields(advanceId, data));
    },

    async submitAdvance(advanceId: string) {
      return withState('mutationState', () => apiSubmitAdvance(advanceId));
    },

    async rejectAdvance(advanceId: string, reason = '') {
      return withState('mutationState', () => apiRejectAdvance(advanceId, reason));
    },

    resetErrors() {
      state.update(s => ({ ...s, errors: {} }));
    },
  };
}


export const advancesApiStore = createAdvancesApiStore();

