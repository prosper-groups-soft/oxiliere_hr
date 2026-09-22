// Binding data-aware du type `group` (lot P7) — vit dans le module admin/access
// qui possède la source (règle avancement §2.1). Enregistré via
// forms-bindings/index.ts, jamais importé directement par les consommateurs.
//
// Particularité : les groupes d'accès sont identifiés par leur **slug** (pas un
// id numérique) — la valeur soumise est le slug, resolve via groupsEndpoint.get.
import { defineBusinessType } from '@/hr/forms-bindings/defineBusinessType.js';
import { groupsEndpoint } from '@/hr/modules/admin/access/api/index.js';
import type { Group } from '@/hr/modules/admin/access/types/access.types.js';
import GroupPicker from '../pickers/GroupPicker.svelte';

let registered = false;

/** Le slug du groupe joue le role d'identifiant (Group n'expose pas d'id). */
type GroupEntity = Group & { id: string };

/** Enregistre les types métier du module access (idempotent). */
export function registerAccessTypes(): void {
	if (registered) return;
	registered = true;

	defineBusinessType<GroupEntity>('group', {
		fetch: async () => (await groupsEndpoint.list()) as GroupEntity[],
		resolve: async (id) => ((await groupsEndpoint.get(id)) as GroupEntity) ?? null,
		adapter: {
			value: (g) => g.slug,
			label: (g) => g.name,
			sublabel: (g) => `${g.member_count} membre${g.member_count === 1 ? '' : 's'}${g.role_count ? ` · ${g.role_count} rôles` : ''}`,
			haystack: (g) => `${g.name} ${g.slug} ${g.app ?? ''} ${(g.roles ?? []).map((r) => r.name).join(' ')}`
		},
		pageSize: 10,
		renderer: GroupPicker,
		cacheTtl: 60_000,
		behaviors: ['searchable']
	});
}