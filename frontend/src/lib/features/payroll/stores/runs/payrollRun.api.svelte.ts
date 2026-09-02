/**
 * payrollRun.api.svelte.ts — Client API dédié aux exécutions de paie.
 *
 * Responsabilité unique : états async et appels aux endpoints /payroll/runs/*
 */

import { writable, get } from 'svelte/store';
import type { PayrollRun, PayrollRunApiOut, PayrollRunDetailApiOut, PayrollRunSummaryApiOut } from '../../types/types';
import {
	createPayrollRun as apiCreateRun,
	updatePayrollRun as apiUpdateRun,
	processPayrollRun as apiProcessRun,
	completePayrollRun as apiCompleteRun,
	reviewPayrollRun as apiReviewRun,
	approvePayrollRun as apiApproveRun,
	cancelPayrollRun as apiCancelRun,
} from '@/features/payroll/queries/payroll';


export type AsyncState = 'idle' | 'loading' | 'success' | 'empty' | 'error' | 'offline';

interface PayrollRunApiState {
	listState: AsyncState;
	detailState: AsyncState;
	errors: Record<string, string | null>;
	isOnline: boolean;
}

function createPayrollRunApiStore() {
	const state = writable<PayrollRunApiState>({
		listState: 'idle',
		detailState: 'idle',
		errors: {},
		isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
	});

	const { subscribe } = state;

	function setDomainState(domain: 'listState' | 'detailState', newState: AsyncState, errorMsg?: string) {
		state.update(s => ({
			...s,
			[domain]: newState,
			errors: { ...s.errors, [domain]: errorMsg ?? null }
		}));
	}

	async function withState<T>(
		domain: 'listState' | 'detailState',
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

		async fetchRunList(filters: { page?: number; pageSize?: number; status?: string; period?: string; search?: string; orgUnit?: string }) {
			return withState('listState', async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.runList(filters).queryFn();
			}, (r) => !r?.results?.length);
		},

		async fetchRunDetail(runId: string): Promise<PayrollRunDetailApiOut | null> {
			return withState('detailState', async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.runDetail(runId).queryFn();
			});
		},

		async fetchRunSummary(runId: string): Promise<PayrollRunSummaryApiOut | null> {
			return withState('detailState', async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.runSummary(runId).queryFn();
			});
		},

		async createRun(data: {
			start_date: string; end_date: string; exchange_rate_applied?: number | null;
			selection_scope?: 'all' | 'org_units' | 'employees';
			org_unit_ids?: string[];
			employee_ids?: string[];
		}): Promise<PayrollRunApiOut | null> {
			return withState('listState', () => apiCreateRun(data));
		},

		async updateRun(runId: string, data: Partial<PayrollRun>) {
			return withState('detailState', () => apiUpdateRun(runId, data));
		},

		async processRun(runId: string) {
			return withState('detailState', () => apiProcessRun(runId));
		},

		async completeRun(runId: string): Promise<PayrollRunApiOut | null> {
			return withState('detailState', () => apiCompleteRun(runId));
		},

		async reviewRun(runId: string): Promise<PayrollRunApiOut | null> {
			return withState('detailState', () => apiReviewRun(runId));
		},

		async approveRun(runId: string): Promise<PayrollRunApiOut | null> {
			return withState('detailState', () => apiApproveRun(runId));
		},

		async cancelRun(runId: string): Promise<PayrollRunApiOut | null> {
			return withState('detailState', () => apiCancelRun(runId));
		},

		resetErrors() {
			state.update(s => ({ ...s, errors: {} }));
		},

		/** Récupère le dernier message d'erreur d'un domaine (pour propaguer
		 *  l'erreur du backend jusqu'au formulaire). */
		getLastError(domain: 'listState' | 'detailState'): string | null {
			return get(state).errors[domain] ?? null;
		},
	};
}


export const payrollRunApiStore = createPayrollRunApiStore();

