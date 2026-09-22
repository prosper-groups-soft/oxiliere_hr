// Binding du type `leaveType` (lot P6) — vit dans le module leaves qui possède
// la source (règle avancement §2.1). Enregistré via forms-bindings/index.ts,
// jamais importé directement par les consommateurs.
//
// Arbitrage : `leaveType` n'est PAS une entité avec id côté backend — c'est un
// enum frontend (annual | sick | circumstantial | unpaid) traduit en catégorie
// backend via toBackendCategory (LEAVE_TYPE_LABELS / BACKEND_LEAVE_CATEGORIES).
// La valeur soumise est donc la clé LeaveType, pas un id. Source statique
// = LEAVE_TYPE_OPTIONS (source unique, pas de duplication).
// TODO backend : si des types de congé configurables (entités) arrivent,
// basculer le binding vers l'endpoint correspondant + adapter {label, solde}.
import { registerType } from '@/hr/forms/index.js';
import { LEAVE_TYPE_OPTIONS } from '@/hr/modules/leaves/constants/leaves.js';
import LeaveTypeField from '../pickers/LeaveTypeField.svelte';

let registered = false;

/** Enregistre les types métier du module leaves (idempotent). */
export function registerLeaveTypes(): void {
	if (registered) return;
	registered = true;

	registerType('leaveType', {
		valueType: 'string',
		defaultRenderer: LeaveTypeField,
		defaultDataSource: {
			type: 'static',
			values: LEAVE_TYPE_OPTIONS.map((o) => ({ label: o.label, value: o.value }))
		}
	});
}
