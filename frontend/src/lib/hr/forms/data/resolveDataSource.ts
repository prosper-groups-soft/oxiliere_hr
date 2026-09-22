// Résolution des DataSources (api §7) : static | function | api | store → options normalisées.
// Le cas `api` passe par APIEndPoint (axios + auth/CSRF/refresh) au lieu de fetch natif.
// Cache mémoire si `ds.cache` présent. Erreur → [] (le caller gère loading/error).
import type { DataSourceConfig } from '../core/types.js';
import APIEndPoint from '@/hr/utilities/http/rest';
import { getStoreSnapshot } from './storeSnapshots.js';

export interface ResolvedOption {
	label: string;
	value: unknown;
	/** Infos additionnelles transportées telles quelles (adapters métier, renderers riches). */
	sublabel?: string;
	raw?: unknown;
	disabled?: boolean;
}

/** Nœud d'arbre résolu (champ `tree`) — option + sous-arbre récursif. */
export interface ResolvedNode {
	label: string;
	value: unknown;
	disabled?: boolean;
	children?: ResolvedNode[];
}

export interface ResolveParams {
	search?: string;
	filter?: Record<string, any>;
	/** Chargement paginé (load 'paginated'/'infinite') — 1-based. */
	page?: number;
	pageSize?: number;
	/** Contourne la lecture du cache (lecture fraîche après mutation — le
	 * résultat recharge quand même le cache pour les lectures suivantes). */
	fresh?: boolean;
}

interface CacheEntry {
	at: number;
	data: ResolvedOption[];
}

const cache = new Map<string, CacheEntry>();

/** Réservé aux tests : vide le cache mémoire. */
export function clearDataSourceCache(): void {
	cache.clear();
}

// ── Cache session/persistent (api §7, metamodel §7) ───────────
// sessionStorage/localStorage : JSON {at, data}. TTL vérifié à la lecture.
// Toute erreur de stockage (quota, serialization, mode privé) → fallback memory
// silencieux. Seules les données sérialisables passent (les File/fonctions
// échouent au try JSON → fallback memory).

function storageFor(strategy: 'session' | 'persistent'): Storage | null {
	try {
		if (typeof window === 'undefined') return null;
		return strategy === 'session' ? window.sessionStorage : window.localStorage;
	} catch {
		return null;
	}
}

function storageKeyOf(key: string): string {
	return `hrforms:ds:${key}`;
}

function readStorage(storage: Storage, key: string, ttl: number): CacheEntry | null {
	try {
		const raw = storage.getItem(storageKeyOf(key));
		if (!raw) return null;
		const entry = JSON.parse(raw) as CacheEntry;
		if (!entry || typeof entry.at !== 'number' || !Array.isArray(entry.data)) return null;
		if (Date.now() - entry.at >= ttl) {
			storage.removeItem(storageKeyOf(key));
			return null;
		}
		return entry;
	} catch {
		return null;
	}
}

function writeStorage(storage: Storage, key: string, entry: CacheEntry): boolean {
	try {
		storage.setItem(storageKeyOf(key), JSON.stringify(entry));
		return true;
	} catch {
		return false;
	}
}

/** Remplit le cache selon la stratégie (memory par défaut). Retourne le hit de
 * stockage éventuel pour éviter une double lecture. */
function cacheGet(ds: DataSourceConfig, key: string, ttl: number): CacheEntry | null {
	const strategy = ds.cache?.strategy ?? 'memory';
	if (strategy === 'memory') return cache.get(key) ?? null;
	const storage = storageFor(strategy);
	if (!storage) return null;
	const hit = readStorage(storage, key, ttl);
	// Réchauffe le cache mémoire avec la donnée de stockage (lecture rapide)
	if (hit) cache.set(key, hit);
	return hit;
}

function cacheSet(ds: DataSourceConfig, key: string, entry: CacheEntry): void {
	cache.set(key, entry); // memory toujours tenu (fallback + réchauffement)
	const strategy = ds.cache?.strategy ?? 'memory';
	if (strategy === 'memory') return;
	// Ne sérialise que du JSON-valide (File/fonctions → catch → memory seul)
	const storage = storageFor(strategy);
	if (storage) writeStorage(storage, key, entry);
}

function cacheKey(
	ds: DataSourceConfig,
	search?: string,
	filter?: Record<string, any>,
	page?: number,
	pageSize?: number
): string {
	const { ...rest } = ds as unknown as Record<string, unknown>;
	delete rest.fn;
	delete rest.transform;
	// page/pageSize font partie de la clé : sans eux, la page 2 est servie du
	// cache de la page 1 → doublons à la concaténation (« Voir plus »).
	return JSON.stringify({ ds: rest, search: search ?? '', filter: filter ?? null, page: page ?? null, pageSize: pageSize ?? null });
}

/** Normalise un tableau brut : {label,value} direct ou objets {id,name/title} → {value,label}. */
export function normalizeOptions(raw: unknown): ResolvedOption[] {
	const arr = extractArray(raw);
	if (!Array.isArray(arr)) return [];
	const out: ResolvedOption[] = [];
	for (const item of arr) {
		if (item == null) continue;
		if (typeof item === 'object') {
			const o = item as Record<string, unknown>;
			if ('label' in o && 'value' in o) {
				// Déjà normalisée — on préserve les extras (sublabel, raw, disabled)
				// posés en amont (ex. adaptateurs defineBusinessType) au lieu de les
				// écraser, sinon les renderers riches perdent le contexte métier.
				out.push({
					label: String(o.label),
					value: o.value,
					...(o.sublabel != null ? { sublabel: String(o.sublabel) } : {}),
					...(o.raw !== undefined ? { raw: o.raw } : {}),
					...(o.disabled !== undefined ? { disabled: o.disabled === true } : {})
				});
			} else {
				const value = o.id ?? o.code ?? o.key ?? o.value;
				const label = o.label ?? o.name ?? o.title ?? value;
				out.push({ label: String(label ?? ''), value: value ?? item });
			}
		} else {
			out.push({ label: String(item), value: item });
		}
	}
	return out;
}

/** Normalise un tableau brut en nœuds d'arbre : {label,value,children} direct ou
 * objets {id,name/title,children/items/nodes} → {value,label,children} (récursif). */
export function normalizeTreeNodes(raw: unknown): ResolvedNode[] {
	const arr = extractArray(raw);
	if (!Array.isArray(arr)) return [];
	const walk = (item: unknown): ResolvedNode | null => {
		if (item == null) return null;
		if (typeof item !== 'object') return { label: String(item), value: item };
		const o = item as Record<string, unknown>;
		const value = o.value ?? o.id ?? o.code ?? o.key;
		const label = o.label ?? o.name ?? o.title ?? value;
		const childRaw = o.children ?? o.items ?? o.nodes;
		return {
			label: String(label ?? ''),
			value: value ?? item,
			disabled: o.disabled === true ? true : undefined,
			children: Array.isArray(childRaw)
				? childRaw.map(walk).filter((n): n is ResolvedNode => n != null)
				: undefined
		};
	};
	return arr.map(walk).filter((n): n is ResolvedNode => n != null);
}

function extractArray(raw: unknown): unknown {
	if (Array.isArray(raw)) return raw;
	if (typeof raw === 'object' && raw !== null) {
		const o = raw as Record<string, unknown>;
		for (const k of ['options', 'items', 'data', 'results']) {
			if (Array.isArray(o[k])) return o[k];
		}
	}
	return raw;
}

export async function resolveDataSource(
	ds: DataSourceConfig | undefined,
	params?: ResolveParams
): Promise<ResolvedOption[]> {
	if (!ds) return [];
	const search = params?.search;
	const filter = params?.filter;
	const page = params?.page;
	const pageSize = params?.pageSize;

	// Cache (memory / session / persistent, api §7) — saisi sauf si fresh
	// (rechargement après mutation : create/update/remove).
	if (ds.cache) {
		const key = ds.cache.key ?? cacheKey(ds, search, filter, page, pageSize);
		if (!params?.fresh) {
			const hit = cacheGet(ds, key, ds.cache.ttl);
			if (hit) return hit.data;
		}
		const data = await load(ds, search, filter, page, pageSize);
		cacheSet(ds, key, { at: Date.now(), data });
		return data;
	}
	return load(ds, search, filter, page, pageSize);
}

async function loadRaw(
	ds: DataSourceConfig,
	search?: string,
	filter?: Record<string, any>,
	page?: number,
	pageSize?: number
): Promise<unknown> {
	switch (ds.type) {
		case 'static':
			return ds.values;
		case 'function':
			return await ds.fn({ search, filter, page, pageSize });
		case 'promise':
			// Promesse déjà déclenchée par l'appelant — résolue une fois ici
			return await ds.promise;
		case 'api': {
			const query: Record<string, any> = { ...(ds.params ?? {}) };
			if (search) query.search = search;
			if (filter) Object.assign(query, filter);
			const endpoint = new APIEndPoint(ds.endpoint, ds.endpoint);
			const json =
				(ds.method ?? 'GET').toUpperCase() === 'POST'
					? await endpoint.create(query)
					: await endpoint.list(query);
			return ds.transform ? ds.transform(json) : json;
		}
		case 'store':
			return getStoreSnapshot(ds.store, ds.property);
		default:
			return [];
	}
}

async function load(
	ds: DataSourceConfig,
	search?: string,
	filter?: Record<string, any>,
	page?: number,
	pageSize?: number
): Promise<ResolvedOption[]> {
	try {
		return normalizeOptions(await loadRaw(ds, search, filter, page, pageSize));
	} catch {
		return [];
	}
}

/** Comme resolveDataSource mais préserve la hiérarchie (champ `tree`) :
 * {label,value,children} ou {id,name,children} → ResolvedNode[] récursif. */
export async function resolveTreeDataSource(
	ds: DataSourceConfig | undefined,
	params?: ResolveParams
): Promise<ResolvedNode[]> {
	if (!ds) return [];
	if (ds.type === 'static') return normalizeTreeNodes(ds.values);
	const search = params?.search;
	const filter = params?.filter;
	if (ds.cache) {
		const key = (ds.cache.key ?? cacheKey(ds, search, filter)) + '#tree';
		const hit = cacheGet(ds, key, ds.cache.ttl);
		if (hit) return hit.data as ResolvedNode[];
		const data = await normalizeTreeNodes(await loadRaw(ds, search, filter));
		cacheSet(ds, key, { at: Date.now(), data: data as ResolvedOption[] });
		return data;
	}
	try {
		return normalizeTreeNodes(await loadRaw(ds, search, filter));
	} catch {
		return [];
	}
}
