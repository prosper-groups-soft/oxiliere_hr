/**
 * runs — Baril du domaine "Cycles de paie & wizard (S1–S7)"
 *
 * Exporte la couche API et le store de cycle de paie (liste, filtres,
 * pagination, cycle de vie du run).
 *
 *   import { payrollRunStore, payrollRunApiStore } from '@/hr/payroll/stores/runs';
 */

export { payrollRunApiStore } from './payrollRun.client.svelte';
export { payrollRunStore } from './payrollRunStore.svelte';
export type { AsyncState } from './payrollRun.client.svelte';
