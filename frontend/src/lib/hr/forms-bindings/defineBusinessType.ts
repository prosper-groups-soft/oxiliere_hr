// Helper d'enregistrement des types métier data-aware (api §14).
// Traduit une BizTypeDefinition (contrat app-side) en TypeDefinition du registre
// forms. Le renderer reste le BusinessField générique à ce stade (P0) — les
// pickers riches arriveront lot par lot (P3+).
import { registerType, validators } from '@/hr/forms/index.js';
import type { DataSourceConfig, TypeDefinition } from '@/hr/forms/core/types.js';
import type { BizEntity, BizTypeDefinition, BizSearchParams } from './types.js';

const DEFAULT_PAGE_SIZE = 10;

/** Normalise les formes de retour courantes des backends : tableau, {results},
 * {items}, {data} — resolveDataSource refait le même travail en aval, on passe
 * simplement l'objet à travers. */
function unwrap(raw: unknown): unknown[] {
	if (Array.isArray(raw)) return raw;
	if (raw && typeof raw === 'object') {
		const o = raw as Record<string, unknown>;
		for (const k of ['results', 'items', 'data', 'options']) {
			if (Array.isArray(o[k])) return o[k] as unknown[];
		}
	}
	return [];
}

/** Construit la DataSourceConfig fonction à partir d'un fetch d'entités.
 * def.paginated === false : la source renvoie la liste complète — pas de
 * pagination moteur (pas de « Voir plus », pas de re-concaténation). */
function dataSourceOf<T extends BizEntity>(def: BizTypeDefinition<T>): DataSourceConfig {
	const paginated = def.paginated !== false;
	const pageSize = def.pageSize ?? DEFAULT_PAGE_SIZE;
	return {
		type: 'function',
		load: paginated ? 'paginated' : undefined,
		pageSize,
		cache: def.cacheTtl ? { ttl: def.cacheTtl, strategy: 'memory' } : undefined,
		fn: async (params?: { search?: string; page?: number; pageSize?: number; filter?: Record<string, any> }) => {
			const p: BizSearchParams = {
				search: params?.search,
				page: params?.page ?? 1,
				pageSize: params?.pageSize ?? pageSize,
				filter: params?.filter
			};
			const raw = await def.fetch(p);
			const items = unwrap(raw);
			// Les formes non paginées ignorent page/pageSize — filtrage client de secours.
			const search = (p.search ?? '').trim().toLowerCase();
			const mapped = items.map((e) => {
				const entity = e as T;
				return {
					label: def.adapter.label(entity),
					value: def.adapter.value(entity),
					...(def.adapter.sublabel ? { sublabel: def.adapter.sublabel(entity) } : {}),
					...(def.adapter.undeletable?.(entity) ? { undeletable: true } : {}),
					raw: entity
				};
			});
			return search && items.length && items.length < pageSize
				? mapped.filter(
						(o) =>
							o.label.toLowerCase().includes(search) ||
							(def.adapter.haystack?.(o.raw as T) ?? '').toLowerCase().includes(search)
					)
				: mapped;
		}
	};
}

/**
 * Enregistre un type métier data-aware dans le registre forms.
 *
 * @example
 * defineBusinessType('employee', {
 *   fetch: ({ search, page, pageSize }) => employeesEndpoint.list({ search, page, limit: pageSize }),
 *   adapter: { value: (e) => String(e.id), label: (e) => e.name, sublabel: (e) => e.jobTitle },
 *   cacheTtl: 60_000
 * });
 */
export function defineBusinessType<T extends BizEntity>(
	name: string,
	def: BizTypeDefinition<T>
): void {
	const definition: TypeDefinition = {
		valueType: 'string',
		defaultRenderer: def.renderer ?? 'business',
		defaultDataSource: dataSourceOf(def),
		resolve: def.resolve as TypeDefinition['resolve'],
		defaultBehaviors: def.behaviors ?? ['searchable'],
		defaultValidators: [
			validators.exists({
				fn: async (value: unknown) => {
					if (value == null || value === '') return true;
					const entity = def.resolve ? await def.resolve(String(value)) : null;
					return entity != null;
				}
			}),
			...(def.validators ?? [])
		]
	};
	registerType(name, definition);
}
