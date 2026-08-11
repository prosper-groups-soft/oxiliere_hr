/**
 * payrollConfig.api.svelte.ts — Client API dédié à la configuration de paie.
 *
 * Responsabilité unique : états async et appels aux endpoints
 * /payroll/configuration/*, /payroll/adjustments/*, /payroll/fiscal/*
 */

import { writable, get } from 'svelte/store';
import type {
	PayrollConfiguration, PayrollConfigurationUpdate,
	SMIGConfiguration, TaxBracketConfig, PayrollAdjustmentConfig,
	OvertimeRule, LegalAllowanceConfig, SocialContributionRate,
} from '../../types/types';
import type { ExchangeRateResponse } from '@/features/payroll/queries/payroll';
import {
	updatePayrollConfiguration as apiUpdateConfiguration,
	togglePayrollAdjustment as apiToggleAdjustment,
	createPayrollAdjustment as apiCreateAdjustment,
	updatePayrollAdjustment as apiUpdateAdjustment,
	deletePayrollAdjustment as apiDeleteAdjustment,
	updateOvertimeRule as apiUpdateOvertimeRule,
	updateLegalAllowance as apiUpdateLegalAllowance,
	resetLegalAllowances as apiResetLegalAllowances,
	resetPayrollAdjustments as apiResetPayrollAdjustments,
	updateProfessionalCategory as apiUpdateProfessionalCategory,
	resetProfessionalCategories as apiResetProfessionalCategories,
} from '@/features/payroll/queries/payroll';
import type { ProfessionalCategory } from '../../types/types';


export type AsyncState = 'idle' | 'loading' | 'success' | 'empty' | 'error' | 'offline';

interface PayrollConfigApiState {
	configState: AsyncState;
	errors: Record<string, string | null>;
	isOnline: boolean;
}

function createPayrollConfigApiStore() {
	const state = writable<PayrollConfigApiState>({
		configState: 'idle',
		errors: {},
		isOnline: typeof navigator !== 'undefined' ? navigator.onLine : true,
	});

	const { subscribe } = state;

	function setDomainState(newState: AsyncState, errorMsg?: string) {
		state.update(s => ({
			...s,
			configState: newState,
			errors: { ...s.errors, config: errorMsg ?? null }
		}));
	}

	async function withState<T>(
		fn: () => Promise<T>,
		isEmpty: (result: T) => boolean = () => false,
	): Promise<T | null> {
		if (!get(state).isOnline) { setDomainState('offline'); return null; }
		setDomainState('loading');
		try {
			const result = await fn();
			setDomainState(isEmpty(result) ? 'empty' : 'success');
			return result;
		} catch (err: any) {
			setDomainState('error', err.message ?? 'Erreur inconnue');
			return null;
		}
	}

	if (typeof window !== 'undefined') {
		window.addEventListener('online', () => state.update(s => ({ ...s, isOnline: true })));
		window.addEventListener('offline', () => state.update(s => ({ ...s, isOnline: false })));
	}

	return {
		subscribe,

		async fetchConfiguration(): Promise<PayrollConfiguration | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.configuration().queryFn();
			});
		},

		async fetchSMIG(): Promise<SMIGConfiguration[] | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.smigList().queryFn();
			});
		},

		async fetchTaxBrackets(): Promise<TaxBracketConfig[] | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.taxBrackets().queryFn();
			});
		},

		async fetchAdjustmentTypes(): Promise<PayrollAdjustmentConfig[] | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.adjustments().queryFn();
			});
		},

		async fetchOvertimeRules(): Promise<OvertimeRule[] | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.overtimeRules().queryFn();
			});
		},

		async fetchLegalAllowances(): Promise<LegalAllowanceConfig[] | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.legalAllowances().queryFn();
			});
		},

		async fetchSocialContributions(): Promise<SocialContributionRate[] | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.socialContributions().queryFn();
			});
		},

		async fetchExchangeRate(): Promise<ExchangeRateResponse | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.payrollQueryOptions.exchangeRate().queryFn();
			});
		},

		async updateConfiguration(data: PayrollConfigurationUpdate): Promise<PayrollConfiguration | null> {
			return withState(() => apiUpdateConfiguration(data));
		},

		async toggleAdjustmentActive(adjustmentId: string, isActive: boolean): Promise<PayrollAdjustmentConfig | null> {
			return withState(() => apiToggleAdjustment(adjustmentId, isActive));
		},

		async createAdjustment(data: Partial<PayrollAdjustmentConfig>): Promise<PayrollAdjustmentConfig | null> {
			return withState(() => apiCreateAdjustment(data));
		},

		async updateAdjustment(adjustmentId: string, data: Partial<PayrollAdjustmentConfig>): Promise<PayrollAdjustmentConfig | null> {
			return withState(() => apiUpdateAdjustment(adjustmentId, data));
		},

		async deleteAdjustment(adjustmentId: string): Promise<{ message: string } | null> {
			return withState(() => apiDeleteAdjustment(adjustmentId));
		},

		async updateOvertimeRule(ruleId: string, data: Partial<OvertimeRule>): Promise<OvertimeRule | null> {
			return withState(() => apiUpdateOvertimeRule(ruleId, data));
		},

		async updateLegalAllowance(allowanceId: string, data: Partial<LegalAllowanceConfig>): Promise<LegalAllowanceConfig | null> {
			return withState(() => apiUpdateLegalAllowance(allowanceId, data));
		},

		async resetLegalAllowances(): Promise<{ status: string; reset_count: number } | null> {
			return withState(() => apiResetLegalAllowances());
		},

		async resetAdjustments(): Promise<{ status: string; reset_count: number } | null> {
			return withState(() => apiResetPayrollAdjustments());
		},

		async fetchProfessionalCategories(): Promise<ProfessionalCategory[] | null> {
			return withState(async () => {
				const mod = await import('@/features/payroll/queries/payroll');
				return mod.fetchProfessionalCategories();
			});
		},

		async updateProfessionalCategory(categoryId: string, data: Partial<ProfessionalCategory>): Promise<ProfessionalCategory | null> {
			return withState(() => apiUpdateProfessionalCategory(categoryId, data));
		},

		async resetProfessionalCategories(): Promise<{ status: string; reset_count: number } | null> {
			return withState(() => apiResetProfessionalCategories());
		},

		resetErrors() {
			state.update(s => ({ ...s, errors: {} }));
		},
	};
}


export const payrollConfigApiStore = createPayrollConfigApiStore();

