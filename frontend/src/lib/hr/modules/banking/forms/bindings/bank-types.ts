// Binding data-aware du type `bankInstitution` (lot P7) — vit dans le module
// banking qui possède la source (règle avancement §2.1). Enregistré via
// forms-bindings/index.ts, jamais importé directement par les consommateurs.
//
// Source : GET /api/banking/banks (tableau non paginé — la recherche est
// assurée par le filtre client de secours de defineBusinessType).
// Affichage convention catalogue : « Nom — type (banque / mobile money) ».
// La création de banque reste un flux admin dédié (createBank + seed) : pas de
// behavior creatable ici.
import { defineBusinessType } from '@/hr/forms-bindings/defineBusinessType.js';
import { registerType } from '@/hr/forms/index.js';
import { bankingEndpoint } from '@/hr/modules/banking/api/banking.endpoints.js';
import type { BankInstitutionBackendResponse } from '@/hr/modules/banking/types/types.js';
import BankPicker from '../pickers/BankPicker.svelte';
import { ACCOUNT_TYPE_LABELS, VERIFICATION_STATUS_LABELS } from '@/hr/modules/banking/constants/index.js';

let registered = false;

/** Enregistre les types métier du module banking (idempotent). */
export function registerBankTypes(): void {
	if (registered) return;
	registered = true;

	defineBusinessType<BankInstitutionBackendResponse>('bankInstitution', {
		fetch: async () => bankingEndpoint.listBanks(),
		// Pas de retrieve dédié côté backend — resolve via liste (pattern jobFamily).
		// listBanks() peut renvoyer un tableau ou une forme paginée {results} —
		// même normalisation que listInstitutions (service), sinon le .find échoue
		// et le trigger reste vide tant que le menu n'a pas chargé les options.
		resolve: async (id) => {
			const rawList = await bankingEndpoint.listBanks();
			const items = Array.isArray(rawList) ? rawList : ((rawList as any)?.results ?? []);
			return items.find((b: BankInstitutionBackendResponse) => b.id === id) ?? null;
		},
		adapter: {
			value: (b) => b.id,
			label: (b) => b.name,
			sublabel: (b) => `${b.is_mobile_money ? 'Mobile money' : 'Banque'} · ${b.code}`,
			haystack: (b) => `${b.name} ${b.code} ${b.swift_code ?? ''} ${b.country_code} ${b.is_mobile_money ? 'mobile money' : 'banque'}`
		},
		pageSize: 20,
		renderer: BankPicker,
		cacheTtl: 300_000,
		behaviors: ['searchable']
	});

	// ── Types statiques du domaine bancaire (compte) — pas des entités ──
	// bankAccountType : valeur frontend (checking…) → backend (CHECKING…)
	// via transform à la soumission ; parse lowercase à l'hydratation.
	registerType('bankAccountType', {
		valueType: 'string',
		defaultRenderer: 'business',
		defaultDataSource: {
			type: 'static',
			values: Object.entries(ACCOUNT_TYPE_LABELS).map(([value, label]) => ({ value, label }))
		},
		transform: (v) => {
			const map: Record<string, string> = {
				checking: 'CHECKING',
				savings: 'SAVINGS',
				salary: 'SALARY',
				mobile_money: 'OTHER'
			};
			return typeof v === 'string' ? (map[v] ?? 'CHECKING') : v;
		},
		parse: (v) => (typeof v === 'string' ? v.toLowerCase() : v)
	});

	// bankAccountStatus : frontend (pending…) → backend (PENDING…) via transform.
	registerType('bankAccountStatus', {
		valueType: 'string',
		defaultRenderer: 'business',
		defaultDataSource: {
			type: 'static',
			values: Object.entries(VERIFICATION_STATUS_LABELS).map(([value, label]) => ({ value, label }))
		},
		transform: (v) => (typeof v === 'string' ? v.toUpperCase() : v),
		parse: (v) => (typeof v === 'string' ? v.toLowerCase() : v)
	});
}
