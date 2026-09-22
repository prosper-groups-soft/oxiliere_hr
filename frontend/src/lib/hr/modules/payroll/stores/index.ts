/**
 * stores — Baril global de la feature payroll
 *
 * Point d'entrée unique pour le nouveau code. Ré-exporte les 4 barils
 * de domaine ainsi que les façades rétrocompat :
 *
 *   import { payrollStore, payrollRunStore, payrollConfigStore } from '@/hr/modules/payroll/stores';
 *
 * Les façades `payroll.svelte` / `payroll.client.svelte` restent disponibles
 * pour la rétrocompatibilité (imports directs existants).
 */

export * from './advances';
export * from './configuration';
export * from './runs';
export * from './payslips';

export { payrollStore } from './payroll.svelte';
export { payrollApiStore } from './payroll.client.svelte';
export type { AsyncState } from './payroll.client.svelte';

