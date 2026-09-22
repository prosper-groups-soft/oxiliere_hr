// Binding data-aware du type `payroll` (lot P6) — vit dans le module payroll
// qui possède la source (règle avancement §2.1). Enregistré via
// forms-bindings/index.ts, jamais importé directement par les consommateurs.
//
// Arbitrage : le catalogue décrit `payroll` comme « périodes paie ». Il n'existe
// pas d'API périodes dédiée — les runs (/api/payroll/runs/) portent la période
// (period_label, start_date/end_date). Le binding est donc branché sur les runs.
// La liste est courte (quelques runs) : fetch sans pagination backend, la
// recherche est assurée par le filtre client de secours de defineBusinessType.
import { defineBusinessType } from '@/hr/forms-bindings/defineBusinessType.js';
import { validators } from '@/hr/forms/index.js';
import { PayrollApi } from '@/hr/modules/payroll/api/payroll.endpoints.js';
import type { PayrollRunApiOut } from '@/hr/modules/payroll/types/types.js';
import { periodLabelFromDates } from '@/hr/modules/payroll/types/types.js';
import PayPeriodPicker from '../pickers/PayPeriodPicker.svelte';

let registered = false;

/** Enregistre les types métier du module payroll (idempotent). */
export function registerPayrollTypes(): void {
	if (registered) return;
	registered = true;

	defineBusinessType<PayrollRunApiOut>('payroll', {
		fetch: async () => PayrollApi.runs.list(),
		resolve: (id) => PayrollApi.runs.retrieve(id),
		adapter: {
			value: (r) => r.id,
			label: (r) =>
				r.start_date && r.end_date
					? periodLabelFromDates(r.start_date, r.end_date)
					: (r.period_label || r.code),
			sublabel: (r) => `${r.start_date} → ${r.end_date} · ${r.status}`,
			haystack: (r) => `${r.period_label ?? ''} ${r.code} ${r.start_date} ${r.end_date} ${r.status}`
		},
		pageSize: 10,
		renderer: PayPeriodPicker,
		cacheTtl: 60_000,
		behaviors: ['searchable'],
		validators: [
			validators.custom(async (v) => {
				if (v == null || v === '') return true;
				const run = await PayrollApi.runs.retrieve(String(v)).catch(() => null) as PayrollRunApiOut | null;
				return run?.status !== 'CANCELED';
			}, 'Période annulée — choisissez une période active')
		]
	});
}
