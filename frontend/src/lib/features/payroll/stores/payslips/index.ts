/**
 * payslips — Baril du domaine "Bulletins de paie"
 *
 * Exporte la couche API et le store de bulletins (génération, filtres,
 * statistiques, pagination).
 *
 *   import { payslipsStore, payslipsApiStore } from '@/features/payroll/stores/payslips';
 */

export { payslipsApiStore } from './payslips.api.svelte';
export { payslipsStore } from './payslipsStore.svelte';
export type { AsyncState } from './payslips.api.svelte';
