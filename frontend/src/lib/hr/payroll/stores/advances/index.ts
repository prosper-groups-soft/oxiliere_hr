/**
 * advances — Baril du domaine "Avances sur salaire"
 *
 * Exporte la couche API (états async) et la couche store (état métier).
 * Les consommateurs externes importent depuis ce fichier :
 *
 *   import { advancesStore, advancesApiStore } from '@/hr/payroll/stores/advances';
 */

export { advancesApiStore } from './advances.client.svelte';
export { advancesStore } from './advancesStore.svelte';
export type { AsyncState } from './advances.client.svelte';

