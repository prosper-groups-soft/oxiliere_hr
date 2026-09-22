/**
 * payslips.client.svelte.ts — Client API dédié aux bulletins de paie.
 *
 * Responsabilité unique : états async et appels aux endpoints /payroll/payslips/*
 */

import { writable, get } from 'svelte/store';
import type { PayrollFilters } from '../../types/types';


export type AsyncState = 'idle' | 'loading' | 'success' | 'empty' | 'error' | 'offline';

interface PayslipsApiState {
	listState: AsyncState;
	detailState: AsyncState;
	errors: Record<string, string | null>;
	isOnline: boolean;
}

function createPayslipsApiStore() {
	const state = writable<PayslipsApiState>({
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

		async fetchPayslipList(runId: string, filters?: PayrollFilters) {
			return withState('listState', async () => {
				const mod = await import('@/hr/modules/payroll/queries/payroll');
				return mod.payrollQueryOptions.payslipList(runId, filters).queryFn();
			}, (r) => !r?.results?.length);
		},

		async fetchPayslipDetail(payslipId: string) {
			return withState('detailState', async () => {
				const mod = await import('@/hr/modules/payroll/queries/payroll');
				return mod.payrollQueryOptions.payslipDetail(payslipId).queryFn();
			});
		},

		resetErrors() {
			state.update(s => ({ ...s, errors: {} }));
		},
	};
}


export const payslipsApiStore = createPayslipsApiStore();

