// Bindings data-aware des types « postes » (lot P5) — le module jobs possède
// la source (règle avancement §2.1). Enregistrés via forms-bindings/index.ts,
// jamais importés directement par les consommateurs.
import { defineBusinessType } from '@/hr/forms-bindings/defineBusinessType.js';
import { behaviors } from '@/hr/forms/index.js';
import { jobEndpoint } from '../../api/job.endpoints';
import type { JobFamily, JobPosition } from '../../types/types';
import type { SeniorityLevelBackendResponse } from '../../api/job.endpoints';
import JobFamilyField from '../pickers/JobFamilyField.svelte';
import PositionPicker from '../pickers/PositionPicker.svelte';
import SeniorityPicker from '../pickers/SeniorityPicker.svelte';

let registered = false;

/** Enregistre les types métier « postes » du module jobs (idempotent). */
export function registerJobTypes(): void {
	if (registered) return;
	registered = true;

	// ── jobFamily (nouveau type) — renderer riche JobFamilyField (CRUD inline :
	// création nom + description, renommage, suppression bloquée si postes
	// rattachés) ; la valeur stockée reste l'id ──
	defineBusinessType<JobFamily>('jobFamily', {
		// Renderer dédié (api §14) — remplace BusinessField générique pour ce type.
		renderer: JobFamilyField,
		// Liste non paginée (tableau simple) — pas de « Voir plus ».
		paginated: false,
		// Liste non paginée (tableau simple) — filtrage client de secours du helper.
		fetch: async ({ search }) => {
			const fams = await jobEndpoint.listFamilies();
			const q = (search ?? '').trim().toLowerCase();
			return q
				? fams.filter(
						(f) =>
							f.name.toLowerCase().includes(q) ||
							(f.description ?? '').toLowerCase().includes(q)
					)
				: fams;
		},
		// Pas de retrieve dédié — resolve via la liste (cache 60s amortit).
		resolve: async (id) => (await jobEndpoint.listFamilies()).find((f) => f.id === id) ?? null,
		adapter: {
			value: (f) => f.id,
			label: (f) => f.name,
			sublabel: (f) => {
				const count = f.positions_count ?? 0;
				const parts = [
					f.description || null,
					count > 0 ? `${count} poste${count > 1 ? 's' : ''}` : null
				].filter(Boolean);
				return parts.length ? parts.join(' — ') : undefined;
			},
			undeletable: (f) => (f.positions_count ?? 0) > 0,
			haystack: (f) => `${f.name} ${f.description ?? ''}`
		},
		// CRUD inline : creatable (POST, nom + description) + manageable (renommage
		// name/description, suppression — PATCH/DELETE /api/jobs/families/{id}).
		// La valeur stockée reste l'id.
		behaviors: [
			'searchable',
			behaviors.creatable({
				onCreate: async (name, extra) =>
					(await jobEndpoint.createFamily({ name, description: extra?.description })).id
			}),
			behaviors.manageable({
				update: (id, values) =>
					jobEndpoint.updateFamily(
						id,
						typeof values === 'string' ? { name: values } : values
					),
				remove: (id) => jobEndpoint.deleteFamily(id)
			})
		],
		cacheTtl: 60_000
	});

	// ── position — liste non paginée ; filtre client par orgUnit (cascade
	// dependsOn: 'orgUnitId' → filter.orgUnitId, cf. BizSearchParams.filter) ──
	defineBusinessType<JobPosition>('position', {
		fetch: async ({ search, filter }) => {
			let positions = await jobEndpoint.getPositions();
			const orgUnitId = filter?.orgUnitId;
			if (orgUnitId) {
				positions = positions.filter((p) => p.org_unit?.id === orgUnitId);
			}
			const q = (search ?? '').trim().toLowerCase();
			if (q) {
				positions = positions.filter(
					(p) =>
						p.name.toLowerCase().includes(q) ||
						(p.job_family?.name ?? '').toLowerCase().includes(q) ||
						(p.org_unit?.name ?? '').toLowerCase().includes(q)
				);
			}
			return positions;
		},
		resolve: async (id) => (await jobEndpoint.getPositions()).find((p) => p.id === id) ?? null,
		adapter: {
			value: (p) => p.id,
			label: (p) => p.name,
			sublabel: (p) => p.job_family?.name,
			haystack: (p) => `${p.name} ${p.job_family?.name ?? ''} ${p.org_unit?.name ?? ''} ${(p.skills ?? []).map((s) => s.name).join(' ')}`
		},
		cacheTtl: 60_000,
		renderer: PositionPicker,
		behaviors: ['searchable']
	});

	// ── seniorityLevel — définitions globales (GET /api/jobs/seniority-levels).
	// La cascade position→séniorité (grille par poste) est une config de champ
	// (dependsOn + filter) à déclarer dans les sheets consommateurs. ──
	defineBusinessType<SeniorityLevelBackendResponse>('seniorityLevel', {
		fetch: async ({ search }) => {
			const levels = await jobEndpoint.getSeniorityLevels();
			const q = (search ?? '').trim().toLowerCase();
			return q ? levels.filter((l) => l.label.toLowerCase().includes(q)) : levels;
		},
		adapter: {
			value: (l) => l.id,
			label: (l) => l.label,
			sublabel: (l) => `${l.level} · rang ${l.rank}`,
			haystack: (l) => `${l.label} ${l.level} ${(l.requirements ?? []).join(' ')}`
		},
		cacheTtl: 300_000, // définitions stables — TTL plus long
		renderer: SeniorityPicker
	});
}
