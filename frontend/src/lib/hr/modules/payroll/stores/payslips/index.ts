/**
 * payslips — Baril du domaine "Bulletins de paie"
 *
 * Exporte la couche API et le store de bulletins (génération, filtres,
 * statistiques, pagination).
 *
 *   import { payslipsStore, payslipsApiStore } from '@/hr/modules/payroll/stores/payslips';
 */

export { payslipsApiStore } from './payslips.client.svelte';
export { payslipsStore } from './payslipsStore.svelte';
export type { AsyncState } from './payslips.client.svelte';
