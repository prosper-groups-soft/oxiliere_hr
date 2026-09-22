/**
 * configuration — Baril du domaine "Configuration & paramètres de paie"
 *
 * Exporte la couche API, le store de configuration (SMIG, barème fiscal,
 * taux de change, ajustements…) et le store UI de l'écran "Paramètres de paie".
 *
 *   import { payrollConfigStore, payrollSettingsStore } from '@/hr/modules/payroll/stores/configuration';
 */

export { payrollConfigApiStore } from './payrollConfig.client.svelte';
export { payrollConfigStore } from './payrollConfigStore.svelte';
export { payrollSettingsStore } from './payrollSettingsStore.svelte';
export type { EditableConfigField, SettingsViewState } from './payrollSettingsStore.svelte';
export type { AsyncState } from './payrollConfig.client.svelte';
