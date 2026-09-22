// Logique partagée des champs à source de données (BusinessField, SelectField, CityField…).
// Encapsule : résolution de la DataSource (config ?? registre), stratégies de
// chargement (eager/lazy/manual — metamodel §7), pagination (paginated/infinite,
// page/pageSize passés à la source, concat des pages), recherche debouncée,
// cascade reload sur dependsOn/reloadIf, clearOnSourceChange.
// Extrait en .svelte.ts (runes) pour être réutilisé sans dupliquer les renderers.
import type { FieldConfig, FieldInstance, FormInstance, ApiDataSource, DataSourceConfig } from '../../../core/types.js';
import { resolveDataSource } from '../../../data/resolveDataSource.js';
import { getTypeDefinition } from '../../../core/typeRegistry.js';
import { collectSourceKeys, evalCondition, normalizeDependsOn } from '../../../core/dependencies.js';
import { isMultipleSelection, staticOptions } from '../field-helpers.js';

export type Option = { label: string; value: unknown };

const DEFAULT_PAGE_SIZE = 10;

export function createBusinessOptions(
	config: FieldConfig,
	field: FieldInstance,
	form?: FormInstance<any>
) {
	let remoteOptions = $state<Option[]>([]);
	let loading = $state(false);
	let search = $state('');
	let debounce: ReturnType<typeof setTimeout> | undefined;

	// ── Pagination (load 'paginated'/'infinite') ──
	let page = $state(0); // dernière page chargée
	let hasMore = $state(false);

	// ── Stratégies lazy/manual ──
	let loadedOnce = $state(false); // premier chargement effectué (lazy : au focus)
	let manualLoaded = $state(false); // action explicite effectuée (manual)

	const effectiveDs = $derived(
		config.dataSource ?? getTypeDefinition(config.type)?.defaultDataSource
	);
	const debounceMs = $derived(
		(effectiveDs as ApiDataSource | undefined)?.debounceMs ?? 300
	);
	const isMultiple = $derived(isMultipleSelection(config));
	const staticOpts = $derived(staticOptions(config));
	const allOpts = $derived([...staticOpts, ...remoteOptions]);
	const isRemote = $derived(effectiveDs != null && effectiveDs.type !== 'static');
	const loadStrategy = $derived(effectiveDs?.load ?? 'eager');
	const isPaginated = $derived(loadStrategy === 'paginated' || loadStrategy === 'infinite');
	const pageSize = $derived(effectiveDs?.pageSize ?? DEFAULT_PAGE_SIZE);
	// manual : bouton « Rechercher » tant que l'utilisateur n'a pas déclenché
	const needsManualLoad = $derived(isRemote && loadStrategy === 'manual' && !manualLoaded);

	// ── Chargement initial + reload cascade (semantics §6.3 + plan Phase 3 §3) ──
	// Sources = dependsOn (+ clés Record de reloadIf via collectSourceKeys).
	const depSourceKeys = $derived(
		config.dependencies ? collectSourceKeys(config.dependencies) : []
	);
	const sourceLabels = $derived(
		form
			? depSourceKeys
					.map((k) => form.getConfig().fields.find((f) => f.name === k || f.id === k)?.label ?? k)
					.join(', ')
			: ''
	);
	const filterValues = $derived(
		Object.fromEntries((form ? depSourceKeys : []).map((k) => [k, form!.getValue(k as never)]))
	);
	const filterSig = $derived(JSON.stringify(filterValues));

	let lastSig: string | undefined;
	let lastDs: unknown;

	$effect(() => {
		const sig = filterSig;
		const ds = effectiveDs;
		const keys = depSourceKeys;
		if (!ds || ds.type === 'static') {
			remoteOptions = [];
			lastSig = sig;
			lastDs = ds;
			return;
		}
		const strategy = ds.load ?? 'eager';
		const dsChanged = ds !== lastDs;
		const first = lastSig === undefined;
		const sigChanged = !first && sig !== lastSig && keys.length > 0 && !!form;
		lastSig = sig;
		lastDs = ds;
		if (first || dsChanged) {
			if (dsChanged) {
				loadedOnce = false;
				manualLoaded = false;
				page = 0;
				hasMore = false;
			}
			// eager (défaut) : au montage. lazy/manual/paginated/infinite : aucun appel
			// au montage — la 1re page arrive à l'ouverture du menu (ensureLoaded) ou
			// sur l'action explicite (manual).
			if (strategy === 'eager') {
				loadedOnce = true;
				void loadRemote('', filterValues);
			}
			return;
		}
		if (!sigChanged) return;
		const dep = config.dependencies;
		const values = { ...(form!.values as Record<string, any>) };
		const should = dep?.reloadIf
			? (evalCondition(dep.reloadIf, values, dep.dependsOn) ?? true)
			: normalizeDependsOn(dep?.dependsOn).length > 0;
		if (!should) return;
		if (dep?.clearOnSourceChange) {
			field.setValue(isMultiple ? [] : null);
			config.onChange?.(isMultiple ? [] : null);
		}
		// Cascade : ne recharge que si la source a déjà été chargée (lazy/manual inclus)
		if (loadedOnce) void loadRemote(search.trim(), filterValues);
	});

	/** Charge (ou recharge) la source. mode 'next' : page suivante (concat).
	 * fresh=true : contourne le cache (rechargement après mutation). */
	async function loadRemote(
		query = '',
		filter?: Record<string, any>,
		mode: 'replace' | 'next' = 'replace',
		fresh = false
	) {
		const ds: DataSourceConfig | undefined = effectiveDs;
		if (!ds || ds.type === 'static') return;
		// static → pas de spinner : les options sont déjà dans staticOpts
		loading = true;
		try {
			const nextPage = mode === 'next' ? page + 1 : 1;
			let data = await resolveDataSource(ds, {
				search: query || undefined,
				filter,
				page: isPaginated ? nextPage : undefined,
				pageSize: isPaginated ? pageSize : undefined,
				fresh
			});
			// Garde anti-doublons : une source non paginée renvoyant la liste
			// complète à chaque « page » re-concaténerait les mêmes clés.
			if (mode === 'next') {
				const seen = new Set(remoteOptions.map((o) => String(o.value)));
				data = data.filter((o) => !seen.has(String(o.value)));
			}
			remoteOptions = mode === 'next' ? [...remoteOptions, ...data] : data;
			page = nextPage;
			// Page partielle → il reste peut-être une page après ; page vide après
			// dédoublonnage → source non paginée, plus rien à charger.
			hasMore = isPaginated && data.length >= pageSize;
		} catch {
			if (mode !== 'next') remoteOptions = [];
		} finally {
			loading = false;
		}
	}

	/** lazy/paginated/infinite : premier chargement à l'ouverture du menu.
	 * manual est exclu : il exige l'action explicite (manualLoad).
	 * Déjà chargé : une recherche précédente laisse `search` filtrer la liste —
	 * réinitialisée au reopen pour retrouver la liste complète. */
	function ensureLoaded(): void {
		if (!isRemote || loadStrategy === 'manual') return;
		if (!loadedOnce) {
			loadedOnce = true;
			void loadRemote('', filterValues);
			return;
		}
		if (search) {
			search = '';
			void loadRemote('', filterValues);
		}
	}

	/** manual : chargement sur action explicite (bouton « Rechercher »). */
	function manualLoad(): void {
		if (!isRemote || loadedOnce) return;
		loadedOnce = true;
		manualLoaded = true;
		void loadRemote('', filterValues);
	}

	/** paginated/infinite : « Voir plus ». */
	function loadMore(): void {
		if (!isRemote || loading || !hasMore) return;
		void loadRemote(search.trim(), filterValues, 'next');
	}

	/** Recharge la liste (après création/renommage/suppression — behavior
	 * manageable/creatable) : contournement du cache du binding (lecture fraîche)
	 * et réinitialisation de la recherche en cours. */
	function reload(): void {
		if (!isRemote) return;
		loadedOnce = true;
		search = '';
		void loadRemote('', filterValues, 'replace', true);
	}

	function onSearchInput(v: string) {
		search = v;
		clearTimeout(debounce);
		const q = search.trim();
		debounce = setTimeout(() => void loadRemote(q, filterValues), debounceMs);
	}

	return {
		// Réactifs : getters pour préserver la traçabilité $derived
		get loading() {
			return loading;
		},
		get allOpts() {
			return allOpts;
		},
		get isMultiple() {
			return isMultiple;
		},
		get isRemote() {
			return isRemote;
		},
		get depSourceKeys() {
			return depSourceKeys;
		},
		get sourceLabels() {
			return sourceLabels;
		},
		get loadStrategy() {
			return loadStrategy;
		},
		get needsManualLoad() {
			return needsManualLoad;
		},
		get hasMore() {
			return hasMore;
		},
		ensureLoaded,
		manualLoad,
		loadMore,
		reload,
		onSearchInput,
		clear: () => {
			field.setValue(isMultiple ? [] : null);
			config.onChange?.(isMultiple ? [] : null);
		}
	};
}
