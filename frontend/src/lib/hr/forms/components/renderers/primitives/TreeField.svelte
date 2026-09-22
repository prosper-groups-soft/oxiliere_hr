<script lang="ts">
	// Champ tree (V1, api §4 / catalogue) : rendu arborescent d'une DataSource
	// hiérarchique — { label, value, children? } (ou {id,name,children}) résolue
	// via resolveTreeDataSource. Premier client : orgUnit
	// (DIRECTION → DEPARTMENT → TEAM). La valeur stockée est le `value` du/des
	// nœud(s) sélectionné(s) (scalaire en single, tableau d'ids en multiple) —
	// hydratation/validation/payload du moteur restent standard.
	import type { FieldInstance, FormInstance, TreeFieldConfig } from '../../../core/types.js';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import Input from '@/components/ui/input/input.svelte';
	import { getTypeDefinition } from '../../../core/typeRegistry.js';
	import { collectSourceKeys } from '../../../core/dependencies.js';
	import { resolveTreeDataSource, type ResolvedNode } from '../../../data/resolveDataSource.js';
	import { t } from '../../../validation/i18n.js';
	import { slide } from 'svelte/transition';
	import { hasBehavior } from '../../../core/behaviors.js';

	let {
		config,
		field,
		form
	}: { config: TreeFieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	const COLLAPSE_MS = 200;

	const isMultiple = $derived(
		config.selection === 'multiple' || hasBehavior(config, 'multiSelect')
	);
	const searchable = $derived(config.searchable === true);

	// ── Source (eager au montage + cascade dependsOn — subset de business-options) ──
	let nodes = $state<ResolvedNode[]>([]);
	let loading = $state(false);
	const effectiveDs = $derived(
		config.dataSource ?? getTypeDefinition(config.type)?.defaultDataSource
	);
	const depSourceKeys = $derived(
		config.dependencies ? collectSourceKeys(config.dependencies) : []
	);
	const filterValues = $derived(
		Object.fromEntries((form ? depSourceKeys : []).map((k) => [k, form!.getValue(k as never)]))
	);
	const filterSig = $derived(JSON.stringify(filterValues));

	let lastSig: string | undefined;
	let loaded = false;

	$effect(() => {
		const ds = config.dataSource ?? getTypeDefinition(config.type)?.defaultDataSource;
		const sig = filterSig;
		const sigChanged = lastSig !== undefined && sig !== lastSig;
		lastSig = sig;
		if (sigChanged && loaded) void load();
		if (!loaded) {
			loaded = true;
			void load();
		}
	});

	async function load() {
		loading = true;
		try {
			nodes = await resolveTreeDataSource(effectiveDs, { filter: filterValues });
			applyDefaultExpanded();
		} finally {
			loading = false;
		}
	}

	// ── Expansion : id → déplié ? Défaut : les N premiers niveaux (defaultExpandedDepth). ──
	let expanded = $state<Record<string, boolean>>({});
	function applyDefaultExpanded() {
		const depth = config.defaultExpandedDepth ?? 1;
		const next: Record<string, boolean> = {};
		const walk = (list: ResolvedNode[], d: number) => {
			for (const n of list) {
				if (n.children?.length && d < depth) next[String(n.value)] = true;
				if (n.children?.length) walk(n.children, d + 1);
			}
		};
		walk(nodes, 0);
		expanded = next;
	}
	function toggleNode(n: ResolvedNode) {
		const k = String(n.value);
		expanded = { ...expanded, [k]: !expanded[k] };
	}
	function setAllExpanded(list: ResolvedNode[], v: boolean) {
		const next: Record<string, boolean> = v ? { ...expanded } : {};
		const walk = (ns: ResolvedNode[]) => {
			for (const n of ns) {
				if (n.children?.length) {
					next[String(n.value)] = true;
					walk(n.children);
				}
			}
		};
		if (v) walk(list);
		expanded = next;
	}
	const anyExpanded = $derived(Object.values(expanded).some(Boolean));

	// ── Recherche client-side : garde les matches + leurs ancêtres ; filtre actif ⇒ tout déplié. ──
	let query = $state('');
	const filtered = $derived.by(() => {
		const q = query.trim().toLowerCase();
		if (!q) return nodes;
		const walk = (list: ResolvedNode[]): ResolvedNode[] => {
			const out: ResolvedNode[] = [];
			for (const n of list) {
				const kids = n.children ? walk(n.children) : [];
				if (n.label.toLowerCase().includes(q) || kids.length > 0) {
					out.push({ ...n, children: n.children ? kids : undefined });
				}
			}
			return out;
		};
		const kids = walk(nodes); // eslint-disable-line
		return kids;
	});
	const isFiltering = $derived(query.trim().length > 0);

	// ── Sélection ──
	const selectedKeys = $derived.by(() => {
		if (isMultiple) {
			const arr = Array.isArray(field.value) ? field.value : [];
			return new Set(arr.map((v) => String(v)));
		}
		return new Set(field.value == null ? [] : [String(field.value)]);
	});
	function selectNode(n: ResolvedNode) {
		if (n.disabled || field.isDisabled || field.isReadonly) return;
		const key = String(n.value);
		if (isMultiple) {
			const arr = Array.isArray(field.value) ? [...field.value] : [];
			const idx = arr.findIndex((v) => String(v) === key);
			if (idx >= 0) arr.splice(idx, 1);
			else arr.push(n.value);
			field.setValue(arr);
			config.onChange?.(arr);
		} else {
			const next = selectedKeys.has(key) && !config.required ? null : n.value;
			field.setValue(next);
			config.onChange?.(next);
		}
	}

	// ── Labels (trigger view + mode view) : chemin « A / B / C » d'un nœud. ──
	const pathByValue = $derived.by(() => {
		const map = new Map<string, string[]>();
		const walk = (list: ResolvedNode[], path: string[]) => {
			for (const n of list) {
				const p = [...path, n.label];
				map.set(String(n.value), p);
				if (n.children) walk(n.children, p);
			}
		};
		walk(nodes, []);
		return map;
	});
	function pathOf(value: unknown): string {
		return (pathByValue.get(String(value)) ?? [String(value ?? '')]).join(' / ');
	}
	const viewDisplay = $derived.by(() => {
		if (!field.isReadonly || field.value == null || field.value === '') return undefined;
		if (isMultiple) {
			const arr = Array.isArray(field.value) ? field.value : [];
			return arr.length ? arr.map(pathOfLabel).join(', ') : undefined;
		}
		return pathOfLabel(field.value);
	});
	function pathOfLabel(v: unknown): string {
		return pathByValue.get(String(v))?.join(' / ') ?? String(v);
	}

	const hasChildren = $derived(nodes.some((n) => n.children?.length));
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	{#if viewDisplay !== undefined}
		<!-- Mode view : chemin du/des nœud(s) sélectionné(s) — pas d'arbre interactif -->
		<div
			id={field.id}
			data-field={field.name}
			class="flex min-h-9 w-full items-center rounded-md border border-input bg-transparent px-3 py-1 shadow-xs opacity-60"
		>
			<span class="truncate text-sm">{viewDisplay}</span>
		</div>
	{:else}
		{#if searchable}
			<div class="relative">
				<Input
					type="search"
					placeholder={t('field.tree.search')}
					bind:value={query}
					data-field={field.name}
					id={field.id}
					disabled={field.isDisabled}
					class="h-9 pr-8"
				/>
				<AppIcon
					name="search"
					size={14}
					class="pointer-events-none absolute right-2.5 top-1/2 -translate-y-1/2 text-muted-foreground"
				/>
			</div>
		{/if}
		<div
			class="max-h-64 overflow-y-auto rounded-md border bg-transparent p-1"
			role={isMultiple ? 'group' : 'listbox'}
			aria-label={config.label ?? field.name}
			aria-multiselectable={isMultiple || undefined}
			data-field={!searchable ? field.name : undefined}
		>
			{#if loading}
				<div class="flex items-center gap-2 px-2 py-2 text-xs text-muted-foreground">
					<AppIcon name="loader-circle" size={14} class="animate-spin" />
					{t('field.tree.loading')}
				</div>
			{:else if filtered.length === 0}
				<div class="px-2 py-2 text-xs text-muted-foreground">
					{isFiltering ? t('field.tree.noMatch') : t('field.tree.empty')}
				</div>
			{:else}
				{@render renderNodes(filtered, 0)}
			{/if}
		</div>
	{/if}
	{#if !field.isReadonly && (searchable || (isMultiple && selectedKeys.size > 0) || field.value != null)}
		<div class="flex items-center justify-between">
			<span class="truncate text-[0.82rem] text-muted-foreground">
				{#if isMultiple && selectedKeys.size > 0}
					{selectedKeys.size} sélectionné(s)
				{:else if field.value != null && !isMultiple}
					{pathOfLabel(field.value)}
				{/if}
			</span>
			{#if !isFiltering && hasChildren}
				<button
					type="button"
					class="shrink-0 text-[0.82rem] text-muted-foreground hover:text-foreground"
					onclick={() => setAllExpanded(filtered, !anyExpanded)}
				>
					{anyExpanded ? t('field.tree.collapseAll') : t('field.tree.expandAll')}
				</button>
			{/if}
		</div>
	{/if}
	<FieldMessages {config} {field} />
</div>

{#snippet renderNodes(list: ResolvedNode[], depth: number)}
	<ul class={depth === 0 ? '' : 'ml-4 border-l pl-1'} role="group">
		{#each list as n (String(n.value))}
			<li>
				<div class="flex items-center gap-1">
					{#if n.children?.length}
						<button
							type="button"
							class="flex h-6 w-6 shrink-0 items-center justify-center rounded text-muted-foreground hover:bg-accent hover:text-foreground"
							aria-expanded={isFiltering || expanded[String(n.value)]}
							aria-label={expanded[String(n.value)] ? t('field.tree.collapse') : t('field.tree.expand')}
							onclick={() => toggleNode(n)}
						>
							<AppIcon
								name="chevron-down"
								size={14}
								class="transition-transform duration-200 {(isFiltering || expanded[String(n.value)]) ? '' : '-rotate-90'}"
							/>
						</button>
					{:else}
						<span class="h-6 w-6 shrink-0"></span>
					{/if}
					<button
						type="button"
						class="flex min-w-0 flex-1 items-center gap-2 rounded-md px-2 py-1 text-left hover:bg-accent/50 disabled:opacity-40 {selectedKeys.has(String(n.value))
							? 'bg-accent font-medium'
							: ''}"
						role={isMultiple ? 'checkbox' : 'option'}
						aria-checked={selectedKeys.has(String(n.value))}
						aria-selected={!isMultiple ? selectedKeys.has(String(n.value)) : undefined}
						disabled={n.disabled || field.isDisabled}
						onclick={() => selectNode(n)}
					>
						{#if isMultiple}
							<span
								class="flex h-4 w-4 shrink-0 items-center justify-center rounded border {selectedKeys.has(String(n.value))
									? 'border-primary bg-primary text-primary-foreground'
									: 'border-input'}"
							>
								{#if selectedKeys.has(String(n.value))}
									<AppIcon name="check" size={12} />
								{/if}
							</span>
						{/if}
						<span class="truncate text-sm">{n.label}</span>
					</button>
				</div>
				{#if n.children?.length && (isFiltering || expanded[String(n.value)])}
					<div transition:slide={{ duration: COLLAPSE_MS }}>
						{@render renderNodes(n.children, depth + 1)}
					</div>
				{/if}
			</li>
		{/each}
	</ul>
{/snippet}
