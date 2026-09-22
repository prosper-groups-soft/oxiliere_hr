// Behaviors (api §9, metamodel §8) : helpers de déclaration + résolution des
// behaviors effectifs d'un champ (behaviors déclarés + defaultBehaviors du
// registre de types, api §14). Pur TS, sans dépendance Svelte.
import type { BehaviorConfig, BehaviorType, FieldConfig, RepeaterConfig } from './types.js';
import { getTypeDefinition } from './typeRegistry.js';

/** Helpers de déclaration (`behaviors.repeater({ min: 1, max: 3 })`, …). */
export const behaviors = {
	searchable: (): BehaviorConfig => ({ type: 'searchable' }),
	clearable: (): BehaviorConfig => ({ type: 'clearable' }),
	multiSelect: (): BehaviorConfig => ({ type: 'multiSelect' }),
	sortable: (): BehaviorConfig => ({ type: 'sortable' }),
	creatable: (config?: {
		onCreate?: (value: string, extra?: Record<string, string>) => any;
		label?: string;
	}): BehaviorConfig => ({
		type: 'creatable',
		config
	}),
	/** Manageable : options renommables/supprimables inline dans le picker (
	 * callbacks branchés sur le CRUD du binding — aucune modale).
	 * `update` accepte un label (string, picker générique) ou un objet de valeurs
	 * (renderer riche, ex: { name, description }). Chaque callback renvoie une
	 * promesse : résolue → succès (liste rafraîchie), rejetée → échec affiché
	 * sous le champ et état inline conservé. */
	manageable: (config?: {
		update?: (id: string, values: string | Record<string, string>) => Promise<any>;
		remove?: (id: string) => Promise<any>;
	}): BehaviorConfig => ({
		type: 'manageable',
		config
	}),
	virtualized: (config?: { itemHeight?: number; overscan?: number }): BehaviorConfig => ({
		type: 'virtualized',
		config
	}),
	paginated: (config?: { pageSize?: number }): BehaviorConfig => ({
		type: 'paginated',
		config: { pageSize: config?.pageSize ?? 20 }
	}),
	debounced: (config?: { delayMs?: number }): BehaviorConfig => ({
		type: 'debounced',
		config: { delayMs: config?.delayMs ?? 300 }
	}),
	cached: (config?: { ttl?: number }): BehaviorConfig => ({
		type: 'cached',
		config: { ttl: config?.ttl ?? 60000 }
	}),
	repeater: (config?: Partial<RepeaterConfig>): BehaviorConfig => ({
		type: 'repeater',
		config: { min: 0, sortable: false, ...config }
	})
};

/** Behaviors effectifs : ceux du champ gagnent sur les defaultBehaviors du
 * registre (même règle d'override que les validateurs — api §14). */
export function getBehaviors(config: FieldConfig): BehaviorConfig[] {
	const declared = config.behaviors ?? [];
	const declaredTypes = new Set(declared.map((b) => b.type));
	const defaults = (getTypeDefinition(config.type)?.defaultBehaviors ?? [])
		.filter((t) => !declaredTypes.has(typeof t === 'string' ? t : t.type))
		.map((t) => (typeof t === 'string' ? ({ type: t } as BehaviorConfig) : t));
	return [...declared, ...defaults];
}

export function hasBehavior(config: FieldConfig, type: BehaviorType): boolean {
	return getBehaviors(config).some((b) => b.type === type);
}

export function getBehaviorConfig<C = Record<string, any>>(
	config: FieldConfig,
	type: BehaviorType
): C | undefined {
	return getBehaviors(config).find((b) => b.type === type)?.config as C | undefined;
}

export function repeaterConfigOf(config: FieldConfig): RepeaterConfig {
	return getBehaviorConfig<RepeaterConfig>(config, 'repeater') ?? {};
}
