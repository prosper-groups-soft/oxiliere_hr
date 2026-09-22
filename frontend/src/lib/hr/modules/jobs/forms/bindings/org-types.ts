// Binding data-aware du type `orgUnit` — vit ici car le module jobs possède
// la source (règle avancement §2.1). Enregistré via forms-bindings/index.ts,
// jamais importé directement par les consommateurs.
import { defineBusinessType } from '@/hr/forms-bindings/defineBusinessType.js';
import { behaviors } from '@/hr/forms/index.js';
import { orgEndpoint } from '@/hr/modules/jobs/api/index.js';
import type { OrgUnit } from '@/hr/modules/jobs/types/org.types.js';
import OrgUnitField from '../pickers/OrgUnitField.svelte';

let registered = false;

/** Enregistre les types métier du module jobs (idempotent). */
export function registerOrgTypes(): void {
	if (registered) return;
	registered = true;

	defineBusinessType<OrgUnit>('orgUnit', {
		fetch: async ({ search, page, pageSize }) => {
			const res = await orgEndpoint.list({ search, page, limit: pageSize });
			return res.results ?? [];
		},
		resolve: (id) => orgEndpoint.retrieve(id),
		adapter: {
			value: (u) => u.id,
			label: (u) => u.name,
			sublabel: (u) => u.type,
			haystack: (u) => `${u.name} ${u.type}`
		},
		renderer: OrgUnitField,
		cacheTtl: 60_000,
		behaviors: [
			'searchable',
			behaviors.manageable({
				update: (id, values) =>
					orgEndpoint.update(id, typeof values === 'string' ? { name: values } : { name: String((values as any)?.name ?? values) }),
				remove: (id) => orgEndpoint.delete(id)
			})
		]
	});
}
