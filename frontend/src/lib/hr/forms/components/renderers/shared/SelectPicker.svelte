<script lang="ts">
	// Picker générique (shared) : Select shadcn + recherche intégrée optionnelle.
	// Deux modes de recherche :
	//  - locale (défaut) : filtre `options` côté client pendant la frappe
	//  - déléguée (`onSearch`) : émet la requête au parent (recherche serveur debounce),
	//    sans filtrage local — le parent met à jour `options`.
	// La barre de recherche est sticky en haut du menu (pattern PhoneField) :
	// le bouton scroll-up est masqué pour ne pas la recouvrir.
	// Rendu riche optionnel : `groups` (Select.Group par catégorie) et
	// `itemIcon` (drapeau flagcdn par item, ex: pays).
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import CountryFlag from '@/hr/components/shared/country/CountryFlag.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
	import { t } from '../../../validation/i18n.js';

	interface Option {
		label: string;
		value: unknown;
		/** Sous-titre optionnel (provenant de l'adapter du binding). */
		sublabel?: string;
		/** Entité non supprimable (behavior manageable) — bouton 🗑 désactivé. */
		undeletable?: boolean;
	}

	let {
		id,
		name,
		multiple,
		options,
		groups = undefined,
		itemIcon = undefined,
		singleValue = '',
		multiValues = [],
		multiLabel = '',
		placeholder = 'Sélectionner…',
		searchPlaceholder = undefined,
		emptyText = 'Aucun résultat',
		searchable = false,
		onSearch,
		disabled = false,
		loading = false,
		typeaheadItems = undefined,
		allowDeselect = true,
		onOpenChange = undefined,
		hasMore = false,
		onLoadMore = undefined,
		manualLoadText = undefined,
		onManualLoad = undefined,
		clearable = false,
		onClear = undefined,
		sortable = false,
		creatable = false,
		onCreate = undefined,
		manageable = false,
		onUpdate = undefined,
		onDelete = undefined,
		virtual = undefined,
		onSingle,
		onMulti
	}: {
		id: string;
		name?: string;
		multiple: boolean;
		/** Liste plate — ignorée si `groups` est fourni. */
		options: Option[];
		/** Rendu groupé (ex: orgUnit par type). Chaque groupe est rendu avec Select.Group. */
		groups?: Array<{ label: string; options: Option[] }> | undefined;
		/** Icône (code ISO → drapeau flagcdn) rendue à gauche de chaque option + trigger. */
		itemIcon?: ((opt: Option) => string | undefined) | undefined;
		singleValue?: string;
		multiValues?: string[];
		multiLabel?: string;
		placeholder?: string;
		searchPlaceholder?: string;
		/** Placeholder de la recherche — défaut « Rechercher ou créer… » si creatable. */
		/** Message affiché quand aucune option (ex: « Sélectionnez d'abord un pays »). */
		emptyText?: string;
		/** Affiche la barre de recherche dans le menu. */
		searchable?: boolean;
		/** Si fourni : recherche déléguée au parent (serveur) — pas de filtre local. */
		onSearch?: (query: string) => void;
		disabled?: boolean;
		/** État de chargement de la source (rendu local : spinner dans le menu). */
		loading?: boolean;
		typeaheadItems?: Array<{ value: string; label: string }> | undefined;
		allowDeselect?: boolean;
		/** Ouverture/fermeture du menu — déclencheur du chargement lazy. */
		onOpenChange?: ((open: boolean) => void) | undefined;
		/** paginated/infinite : affiche « Voir plus » et émet le clic. */
		hasMore?: boolean;
		onLoadMore?: (() => void) | undefined;
		/** manual : libellé du bouton dans le menu (ex « Rechercher ») + action. */
		manualLoadText?: string | undefined;
		onManualLoad?: (() => void) | undefined;
		/** Behavior clearable : bouton × dans le trigger (onClear du parent). */
		clearable?: boolean;
		onClear?: (() => void) | undefined;
		/** Behavior sortable : bouton de tri A→Z/Z→A dans le menu. */
		sortable?: boolean;
		/** Behavior creatable : ligne « Ajouter « query » » dans le menu (quand la
		 * recherche ne matche pas exactement une option). */
		creatable?: boolean;
		onCreate?: ((label: string) => void) | undefined;
		/** Behavior manageable : actions modifier/supprimer par option (rename inline + suppression
		 * avec confirmation inline). Les callbacks renvoient une promesse — rejetée
		 * = échec, l'état inline est conservé (erreur affichée par le parent). */
		manageable?: boolean;
		onUpdate?: ((id: string, label: string) => Promise<unknown>) | undefined;
		onDelete?: ((id: string) => Promise<unknown>) | undefined;
		/** Behavior virtualized : fenêtrage des options (listes > 1000 items).
		 * Listes plates uniquement — ignoré si `groups`. */
		virtual?: { itemHeight?: number; overscan?: number } | undefined;
		onSingle: (v: string | undefined) => void;
		onMulti: (v: string[] | undefined) => void;
	} = $props();

	let query = $state('');

	// Creatable : le placeholder de recherche annonce la création (surcharge
	// possible via la prop searchPlaceholder).
	const effectiveSearchPlaceholder = $derived(
		creatable ? (searchPlaceholder ?? 'Rechercher ou créer…') : (searchPlaceholder ?? 'Rechercher…')
	);

	/** Filtre local (recherche non déléguée) d'une liste d'options. */
	function localFilter(opts: Option[]): Option[] {
		if (searchable && !onSearch && query.trim()) {
			const q = query.trim().toLowerCase();
			return opts.filter((o) => o.label.toLowerCase().includes(q));
		}
		return opts;
	}

	const sortedOptions = $derived.by(() => {
		if (!sortable || !sortDir || groups) return options;
		const arr = [...options];
		arr.sort((a, b) =>
			sortDir === 'asc'
				? a.label.localeCompare(b.label, 'fr')
				: b.label.localeCompare(a.label, 'fr')
		);
		return arr;
	});
	const filteredOptions = $derived(localFilter(sortedOptions));
	const filteredGroups = $derived(
		groups?.map((g) => ({ label: g.label, options: localFilter(g.options) })).filter((g) => g.options.length > 0)
	);
	const isEmpty = $derived(
		groups ? (filteredGroups?.length ?? 0) === 0 : filteredOptions.length === 0
	);

	function onQueryInput() {
		if (onSearch) onSearch(query);
		scrollTop = 0; // nouvelle recherche → fenêtre virtuelle en haut
	}

	function onOpenChangeInternal(open: boolean) {
		if (!open) query = '';
		onOpenChange?.(open);
	}

	// ── Sortable : tri alphabétique des options (listes plates) ──
	let sortDir = $state<'asc' | 'desc' | null>(null);

	function toggleSort() {
		sortDir = sortDir === 'asc' ? 'desc' : 'asc';
	}

	// ── Clearable ──
	const hasValue = $derived(
		multiple ? multiValues.length > 0 : singleValue !== '' && singleValue != null
	);

	function handleClear(e: MouseEvent) {
		e.preventDefault();
		e.stopPropagation();
		onClear?.();
	}

	// ── Virtualized : fenêtrage simple sur hauteur d'item fixe ──
	let virtEl: HTMLElement | null = $state(null);
	let scrollTop = $state(0);
	const VIRT_VIEWPORT_H = 288; // max-h-72
	const itemH = $derived(virtual?.itemHeight ?? 36);
	const overscan = $derived(virtual?.overscan ?? 4);
	const virtTotal = $derived(virtual && !groups ? filteredOptions.length : 0);
	const virtStart = $derived(
		virtTotal > 0 ? Math.max(0, Math.floor(scrollTop / itemH) - overscan) : 0
	);
	const virtEnd = $derived(
		virtTotal > 0 ? Math.min(virtTotal, Math.ceil((scrollTop + VIRT_VIEWPORT_H) / itemH) + overscan) : 0
	);
	const virtWindow = $derived(virtTotal > 0 ? filteredOptions.slice(virtStart, virtEnd) : []);

	/** Code drapeau de l'option sélectionnée (pour le trigger). */
	const selectedIcon = $derived.by(() => {
		if (!itemIcon) return undefined;
		const sel = options.find((o) => String(o.value) === singleValue);
		return sel ? itemIcon(sel) : undefined;
	});

	// ── Creatable : « Ajouter « query » » si la recherche ne matche pas exactement ──
	const q = $derived(query.trim());
	const exactMatch = $derived(
		[...(options ?? []), ...((groups ?? []).flatMap((g) => g.options))].some(
			(o) => o.label.trim().toLowerCase() === q.toLowerCase()
		)
	);
	const showCreate = $derived(creatable && q.length > 0 && !exactMatch);
	function handleCreate() {
		onCreate?.(q);
		query = '';
	}

	// ── Manageable : renommage / suppression inline (behavior manageable) ──
	let editingId = $state<string | null>(null);
	let editValue = $state('');
	let deletingId = $state<string | null>(null);
	let busyId = $state<string | null>(null);

	function startEdit(id: string, label: string) {
		editingId = id;
		editValue = label;
		deletingId = null;
	}

	function cancelEdit() {
		editingId = null;
		editValue = '';
	}

	async function submitEdit() {
		const id = editingId;
		const name = editValue.trim();
		if (!id || !name || busyId) return;
		busyId = id;
		try {
			await onUpdate?.(id, name);
			cancelEdit();
		} finally {
			busyId = null;
		}
	}

	async function confirmDelete() {
		const id = deletingId;
		if (!id || busyId) return;
		busyId = id;
		try {
			await onDelete?.(id);
			deletingId = null;
		} finally {
			busyId = null;
		}
	}

	/** Stoppe la propagation pour que le clic n'atteigne pas Select.Item (sélection). */
	function stop(e: Event) {
		e.stopPropagation();
		e.preventDefault();
	}
</script>

{#snippet optionActions(opt: Option)}
	{#if manageable && !editingId && !deletingId}
		<span class="flex items-center gap-0.5" onmousedown={stop} onclick={stop} role="none">
			{#if onUpdate}
				<button
					type="button"
					tabindex="-1"
					class="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
					onclick={() => startEdit(String(opt.value), opt.label)}
					title={t('behavior.manageable.edit')}
				>
					<AppIcon name="edit" size={15} />
				</button>
			{/if}
			{#if onDelete}
				<button
					type="button"
					tabindex="-1"
					class="rounded p-1 text-red-500 hover:bg-destructive/10 hover:text-destructive disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
					disabled={opt.undeletable}
					onclick={() => (deletingId = String(opt.value))}
					title={opt.undeletable ? t('behavior.manageable.undeletable') : t('behavior.manageable.remove')}
				>
					<AppIcon name="trash" size={15} />
				</button>
			{/if}
		</span>
	{/if}
{/snippet}

{#snippet itemRow(opt: Option)}
	{#if manageable && editingId === String(opt.value)}
		<!-- Renommage inline : la ligne devient un input (l'item Select n'est pas rendu) -->
		<div class="flex items-center gap-1 px-2 py-1">
			<input
				type="text"
				bind:value={editValue}
				class="h-7 flex-1 rounded-md border bg-background px-2 text-sm"
				onmousedown={(e) => e.stopPropagation()}
				onkeydown={(e: KeyboardEvent) => {
					if (e.key === 'Enter') submitEdit();
					else if (e.key === 'Escape') cancelEdit();
				}}
			/>
			<button
				type="button"
				class="rounded p-1 text-emerald-600 hover:bg-emerald-50 disabled:opacity-50"
				disabled={!editValue.trim() || busyId === String(opt.value)}
				onclick={submitEdit}
				title={t('action.confirm')}
			>
				<AppIcon name="check" size={15} />
			</button>
			<button
				type="button"
				class="rounded p-1 text-muted-foreground hover:bg-accent"
				onclick={cancelEdit}
				title={t('action.cancel')}
			>
				<AppIcon name="x" size={15} />
			</button>
		</div>
	{:else if manageable && deletingId === String(opt.value)}
		<!-- Suppression inline : confirmation en ligne -->
		<div class="flex items-center gap-1 px-2 py-1">
			<span class="flex-1 truncate text-sm text-destructive">
				{t('behavior.manageable.confirmRemove', { label: opt.label })}
			</span>
			<button
				type="button"
				class="rounded p-1 text-destructive hover:bg-destructive/10 disabled:opacity-50"
				disabled={busyId === String(opt.value)}
				onclick={confirmDelete}
				title={t('action.confirm')}
			>
				<AppIcon name="check" size={15} />
			</button>
			<button
				type="button"
				class="rounded p-1 text-muted-foreground hover:bg-accent"
				onclick={() => (deletingId = null)}
				title={t('action.cancel')}
			>
				<AppIcon name="x" size={15} />
			</button>
		</div>
	{:else}
		<div class="flex items-center gap-0.5">
			<Select.Item value={String(opt.value)} label={opt.label} class="min-w-0 flex-1">
				<span class="flex items-center gap-2">
					{#if itemIcon}
						{@const icon = itemIcon(opt)}
						{#if icon}<CountryFlag code={icon} size={20} />{/if}{/if}
					<span class="min-w-0 flex-1">
						<span class="block truncate text-sm">{opt.label}</span>
						{#if opt.sublabel}
							<span class="block truncate text-xs text-muted-foreground">{opt.sublabel}</span>
						{/if}
					</span>
				</span>
			</Select.Item>
			{@render optionActions(opt)}
		</div>
	{/if}
{/snippet}

{#snippet contentBody()}
	{#if searchable || sortable}
		<div class="sticky top-0 z-10 -mx-1 mb-1 flex items-center gap-1 border-b bg-white px-1.5 pb-1.5 pt-3">
			{#if searchable}
				<Input
					type="text"
					bind:value={query}
					placeholder={effectiveSearchPlaceholder}
					class="h-8 flex-1"
					onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
					oninput={onQueryInput}
				/>
			{/if}
			{#if sortable && !groups}
				<button
					type="button"
					class="h-8 shrink-0 rounded-md border px-2 text-xs text-muted-foreground hover:bg-accent hover:text-foreground"
					onclick={toggleSort}
					title={sortDir === 'desc' ? 'Z→A' : 'A→Z'}
				>
					{sortDir === 'desc' ? 'Z→A' : 'A→Z'}
				</button>
			{/if}
		</div>
	{/if}
	{#if virtTotal > 0}
		<!-- Fenêtrage : conteneur scrollable interne, items positionnés en absolu —
		     seuls les items visibles (+ overscan) sont rendus. -->
		<div
			class="max-h-72 overflow-y-auto"
			bind:this={virtEl}
			onscroll={(e) => (scrollTop = (e.currentTarget as HTMLElement).scrollTop)}
		>
			<div style="height: {virtTotal * itemH}px; position: relative;">
				<div style="position: absolute; top: {virtStart * itemH}px; left: 0; right: 0;">
					{#each virtWindow as opt (String(opt.value))}
						{@render itemRow(opt)}
					{/each}
				</div>
			</div>
		</div>
	{:else}
		{#if filteredGroups && filteredGroups.length > 0}
			{#each filteredGroups as g (g.label)}
				<Select.Group>
					<Select.Label class="text-xs font-semibold text-muted-foreground">{g.label}</Select.Label>
					{#each g.options as opt (String(opt.value))}
						{@render itemRow(opt)}
					{/each}
				</Select.Group>
			{/each}
		{:else}
			{#each filteredOptions as opt (String(opt.value))}
				{@render itemRow(opt)}
			{/each}
		{/if}
	{/if}
	{#if loading}
		<p class="flex justify-center px-3 py-4">
			<AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" />
		</p>
	{:else if isEmpty && !showCreate}
		<p class="px-3 py-4 text-center text-sm text-muted-foreground">{emptyText}</p>
	{/if}
	{#if showCreate}
		<div class="border-t p-1.5">
			<button
				type="button"
				class="flex w-full items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-center text-sm text-primary hover:bg-accent"
				onclick={handleCreate}
			>
				<AppIcon name="plus" size={15} />
				{t('behavior.creatable.add', { query: q })}
			</button>
		</div>
	{/if}
	{#if manualLoadText && onManualLoad}
		<div class="border-t p-1.5">
			<button
				type="button"
				class="w-full rounded-md px-2 py-1.5 text-center text-sm text-primary hover:bg-accent"
				onclick={() => onManualLoad?.()}
			>
				{manualLoadText}
			</button>
		</div>
	{/if}
	{#if hasMore && onLoadMore}
		<div class="flex justify-end px-4 pb-1.5">
			<button
				type="button"
				class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline"
				onclick={() => onLoadMore?.()}
			>
				Voir plus +
			</button>
		</div>
	{/if}
{/snippet}

{#if multiple}
	<Select.Root
		type="multiple"
		value={multiValues}
		onValueChange={onMulti}
		{disabled}
		onOpenChange={onOpenChangeInternal}
	>
		<div class="relative w-full">
			<Select.Trigger {id} data-field={name} class={clearable ? 'w-full pr-8 text-sm' : 'w-full text-sm'} size="sm">
				{multiLabel || placeholder}
			</Select.Trigger>
			{#if clearable && hasValue && !disabled}
				<button
					type="button"
					class="absolute right-3.5 top-1/2 -translate-y-1/2 text-sm text-muted-foreground hover:text-foreground"
					aria-label={t('field.clear')}
					onclick={handleClear}
				>
					×
				</button>
			{/if}
		</div>
		<Select.Content
			class="z-100 max-h-72 bg-popover *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0"
		>
			{@render contentBody()}
		</Select.Content>
	</Select.Root>
{:else}
	<Select.Root
		type="single"
		value={singleValue}
		onValueChange={onSingle}
		{disabled}
		items={typeaheadItems}
		{allowDeselect}
		onOpenChange={onOpenChangeInternal}
	>
		<div class="relative w-full">
			<Select.Trigger {id} data-field={name} class={clearable ? 'w-full pr-8 text-sm' : 'w-full text-sm'} size="sm">
				<span class="flex items-center gap-2 text-sm">
					{#if selectedIcon}<CountryFlag code={selectedIcon} size={20} />{/if}
					{options.find((o) => String(o.value) === singleValue)?.label ?? placeholder}
				</span>
			</Select.Trigger>
			{#if clearable && hasValue && !disabled}
				<button
					type="button"
					class="absolute right-3.5 top-1/2 -translate-y-1/2 text-sm text-muted-foreground hover:text-foreground"
					aria-label={t('field.clear')}
					onclick={handleClear}
				>
					×
				</button>
			{/if}
		</div>
		<Select.Content
			class="z-100 max-h-72 bg-popover *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0"
		>
			{@render contentBody()}
		</Select.Content>
	</Select.Root>
{/if}
