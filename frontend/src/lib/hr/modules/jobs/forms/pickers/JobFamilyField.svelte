<script lang="ts">
	// JobFamilyField (renderer riche du type `jobFamily` — api §14 : defaultRenderer
	// du registre). Autonome côté module jobs, propriétaire de la source : réutilise
	// la logique partagée du framework (createBusinessOptions, FieldLabel,
	// FieldMessages) et le contrat des behaviors (creatable/manageable — le
	// renderer ne connaît que les callbacks, jamais les endpoints).
	// UX dédiée : description multiligne (pas de truncate), compteur de postes
	// rattachés (badge), renommage nom + description inline, suppression inline
	// bloquée si postes rattachés, création nom + description — zéro modale.
	import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
	import { tick } from 'svelte';
	import { hasBehavior, getBehaviorConfig } from '@/hr/forms/core/behaviors.js';
	import FieldLabel from '@/hr/forms/components/renderers/shared/FieldLabel.svelte';
	import FieldMessages from '@/hr/forms/components/renderers/shared/FieldMessages.svelte';
	import { createBusinessOptions } from '@/hr/forms/components/renderers/business/business-options.svelte';
	import Input from '@/components/ui/input/input.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';

	let {
		config,
		field,
		form
	}: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	// svelte-ignore state_referenced_locally
	const biz = createBusinessOptions(config, field, form);

	type Opt = { label: string; value: unknown; sublabel?: string; raw?: any };
	const allOpts = $derived(biz.allOpts as Opt[]);
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const selected = $derived(allOpts.find((o) => String(o.value) === singleVal));

	// Behaviors : les callbacks vivent dans le binding (job-types.ts)
	const creatableCfg = $derived(
		hasBehavior(config, 'creatable')
			? getBehaviorConfig<{
					onCreate?: (value: string, extra?: Record<string, string>) => any;
				}>(config, 'creatable')
			: undefined
	);
	const manageCfg = $derived(
		hasBehavior(config, 'manageable')
			? getBehaviorConfig<{
					update?: (id: string, values: string | Record<string, string>) => Promise<any>;
					remove?: (id: string) => Promise<any>;
				}>(config, 'manageable')
			: undefined
	);
	const canCreate = $derived(!!creatableCfg?.onCreate);
	const canUpdate = $derived(!!manageCfg?.update);
	const canDelete = $derived(!!manageCfg?.remove);

	// ── Popover (pas de modale) : fermeture par clic extérieur / Escape ──
	let open = $state(false);
	let query = $state('');
	let error = $state('');
	let busy = $state(false);
	let rootEl: HTMLElement | null = $state(null);

	$effect(() => {
		if (!open) return;
		const onDocClick = (e: MouseEvent) => {
			if (!rootEl?.contains(e.target as Node)) open = false;
		};
		const onKey = (e: KeyboardEvent) => {
			if (e.key === 'Escape') open = false;
		};
		document.addEventListener('mousedown', onDocClick);
		document.addEventListener('keydown', onKey);
		return () => {
			document.removeEventListener('mousedown', onDocClick);
			document.removeEventListener('keydown', onKey);
		};
	});

	function toggle() {
		if (field.isDisabled || biz.loading) return;
		open = !open;
		if (open) biz.ensureLoaded();
	}

	// ── États inline : édition / suppression / création ──
	let editingId = $state<string | null>(null);
	let editName = $state('');
	let editDesc = $state('');
	let deletingId = $state<string | null>(null);
	let createOpen = $state(false);
	let newName = $state('');
	let newDesc = $state('');
	let createSectionEl: HTMLElement | null = $state(null);

	/** Ouvre le formulaire de création et fait défiler jusqu'à lui (menu et
	 * page si nécessaire) pour le rendre visible sans geste supplémentaire. */
	async function openCreate() {
		createOpen = true;
		error = '';
		await tick();
		createSectionEl?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
	}

	function countOf(o: Opt): number {
		return Number(o.raw?.positions_count ?? 0);
	}
	function descOf(o: Opt): string {
		return String(o.raw?.description ?? '');
	}
	function badgeLabel(count: number): string {
		return `${count} poste${count > 1 ? 's' : ''}`;
	}

	function selectValue(v: string) {
		field.setValue(v || null);
		config.onChange?.(v || null);
	}

	function startEdit(o: Opt) {
		editingId = String(o.value);
		editName = o.label;
		editDesc = descOf(o);
		deletingId = null;
		error = '';
	}

	function cancelEdit() {
		editingId = null;
		editName = '';
		editDesc = '';
	}

	async function submitEdit() {
		const id = editingId;
		const name = editName.trim();
		if (!id || !name || busy) return;
		busy = true;
		error = '';
		try {
			await manageCfg?.update?.(id, { name, description: editDesc.trim() });
			cancelEdit();
			biz.reload();
		} catch {
			error = 'Échec de la modification — vérifiez la connexion puis réessayez.';
		} finally {
			busy = false;
		}
	}

	async function confirmDelete() {
		const id = deletingId;
		if (!id || busy) return;
		busy = true;
		error = '';
		try {
			await manageCfg?.remove?.(id);
			deletingId = null;
			if (singleVal === id) selectValue('');
			biz.reload();
		} catch {
			error = 'Échec de la suppression — la famille est peut-être encore rattachée à des postes.';
			deletingId = null;
		} finally {
			busy = false;
		}
	}

	async function submitCreate() {
		const name = newName.trim();
		if (!name || busy) return;
		busy = true;
		error = '';
		try {
			const returned = await creatableCfg?.onCreate?.(name, { description: newDesc.trim() });
			const value = returned != null ? String(returned) : name;
			newName = '';
			newDesc = '';
			createOpen = false;
			selectValue(value);
			biz.reload();
		} catch {
			error = 'Échec de la création — vérifiez la connexion puis réessayez.';
		} finally {
			busy = false;
		}
	}

	function cancelCreate() {
		createOpen = false;
		newName = '';
		newDesc = '';
	}

	// Filtre local de secours (la recherche déléguée arrive en parallèle, debouncée)
	const filtered = $derived.by(() => {
		const q = query.trim().toLowerCase();
		if (!q) return allOpts;
		return allOpts.filter(
			(o) =>
				o.label.toLowerCase().includes(q) ||
				descOf(o).toLowerCase().includes(q) ||
				(o.sublabel ?? '').toLowerCase().includes(q)
		);
	});

	function onSearchInput(e: Event) {
		const v = (e.currentTarget as HTMLInputElement).value;
		query = v;
		biz.onSearchInput(v);
	}

	function startDelete(o: Opt) {
		deletingId = String(o.value);
		editingId = null;
		error = '';
	}
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name} bind:this={rootEl}>
	<FieldLabel {config} {field} />

	<div class="relative w-full">
		<!-- Trigger -->
		<button
			type="button"
			id={field.id}
			data-field={field.name}
			class="flex h-9 w-full items-center gap-2 rounded-md border border-slate-200 bg-white px-3 text-sm shadow-fine transition-colors hover:bg-slate-50 disabled:cursor-not-allowed disabled:opacity-60"
			disabled={field.isDisabled || biz.loading}
			onclick={toggle}
		>
			{#if selected}
				<span class="flex min-w-0 flex-1 items-center gap-2">
					<span class="truncate font-medium text-slate-900 text-sm">{selected.label}</span>
					{#if countOf(selected) > 0}
						<span class="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[0.7rem] text-muted-foreground">
							{badgeLabel(countOf(selected))}
						</span>
					{/if}
				</span>
			{:else if biz.loading}
				<AnimateSpin class="size-3 border-slate-400" text="Chargement…" textPosition="right" />
			{:else}
				<span class="text-muted-foreground text-sm">{config.placeholder ?? 'Sélectionner une famille…'}</span>
			{/if}
			<AppIcon name="chevron-down" size={16} class="ml-auto shrink-0 text-slate-400" />
		</button>
		{#if selected && !config.required && !field.isDisabled}
			<button
				type="button"
				class="absolute right-8 top-1/2 -translate-y-1/2 text-sm text-muted-foreground hover:text-foreground"
				aria-label="Effacer"
				onclick={(e) => {
					e.stopPropagation();
					selectValue('');
				}}
			>
				<AppIcon name="x" size={15} />
			</button>
		{/if}

		{#if open}
			<!-- Menu -->
			<div class="absolute left-0 right-0 top-full z-50 mt-1 overflow-hidden rounded-lg border bg-popover shadow-lg">
				<div class="sticky top-0 z-10 border-b bg-popover p-1.5">
					<Input
						type="text"
						bind:value={query}
						placeholder="Rechercher ou créer…"
						class="h-8"
						onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
						oninput={onSearchInput}
					/>
				</div>

				<div class="max-h-72 overflow-y-auto p-1">
					{#if biz.loading}
						<p class="flex justify-center py-4">
							<AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" />
						</p>
					{:else if filtered.length === 0}
						<p class="py-4 text-center text-sm text-muted-foreground">
							{query.trim() ? `Aucune famille pour « ${query.trim()} »` : 'Aucune famille'}
						</p>
					{/if}

					{#each filtered as o (String(o.value))}
						{#if editingId === String(o.value) && canUpdate}
							<!-- Renommage inline : nom + description -->
							<div class="rounded-md border border-primary/30 bg-accent/40 p-2">
								<div class="flex flex-col gap-1.5">
									<Input
										type="text"
										bind:value={editName}
										placeholder="Nom de la famille"
										class="h-8 text-sm"
									/>
									<Input
										type="text"
										bind:value={editDesc}
										placeholder="Description (optionnel)"
										class="h-8 text-sm"
									/>
								</div>
								<div class="mt-1.5 flex items-center justify-end gap-1">
									<button
										type="button"
										class="rounded p-1 text-muted-foreground hover:bg-accent"
										onclick={cancelEdit}
										title="Annuler"
									>
										<AppIcon name="x" size={15} />
									</button>
									<button
										type="button"
										class="rounded p-1 text-emerald-600 hover:bg-emerald-50 disabled:opacity-50"
										disabled={!editName.trim() || busy}
										onclick={submitEdit}
										title="Enregistrer"
									>
										<AppIcon name="check" size={15} />
									</button>
								</div>
							</div>
						{:else if deletingId === String(o.value) && canDelete}
							<!-- Suppression inline : confirmation -->
							<div class="flex items-center gap-2 rounded-md border border-destructive/30 p-2">
								<span class="flex-1 text-sm text-destructive">Supprimer « {o.label} » ?</span>
								<button
									type="button"
									class="rounded p-1 text-destructive hover:bg-destructive/10 disabled:opacity-50"
									disabled={busy}
									onclick={confirmDelete}
									title="Confirmer"
								>
									<AppIcon name="check" size={15} />
								</button>
								<button
									type="button"
									class="rounded p-1 text-muted-foreground hover:bg-accent"
									onclick={() => (deletingId = null)}
									title="Annuler"
								>
									<AppIcon name="x" size={15} />
								</button>
							</div>
						{:else}
							<!-- Ligne riche : nom + badge postes + description multiligne + actions -->
							<div
								class="group flex items-start gap-2 rounded-md px-2 py-1.5 transition-colors {singleVal ===
								String(o.value)
									? 'bg-accent'
									: 'hover:bg-accent/60'}"
							>
								<button
									type="button"
									class="flex min-w-0 flex-1 flex-col items-start gap-0.5 text-left"
									onclick={() => {
										selectValue(String(o.value));
										open = false;
									}}
								>
									<span class="flex items-center gap-1.5">
										<span class="truncate text-sm font-medium text-slate-800">{o.label}</span>
										{#if countOf(o) > 0}
											<span
												class="shrink-0 rounded-full bg-muted px-2 py-0.5 text-[0.7rem] text-muted-foreground"
											>
												{badgeLabel(countOf(o))}
											</span>
										{/if}
									</span>
									{#if descOf(o)}
										<span class="text-xs leading-snug text-muted-foreground">{descOf(o)}</span>
									{:else}
										<span class="flex items-center gap-1 text-xs text-slate-300">
											<AppIcon name="info" size={12} class="shrink-0" />
											Aucune description
										</span>
									{/if}
								</button>
								<span class="flex shrink-0 items-center gap-0.5 pt-0.5">
									{#if canUpdate}
										<button
											type="button"
											class="rounded p-1 text-muted-foreground hover:bg-accent hover:text-foreground"
											onclick={() => startEdit(o)}
											title="Renommer"
										>
											<AppIcon name="edit" size={15} />
										</button>
									{/if}
									{#if canDelete}
										<button
											type="button"
											class="rounded p-1 text-red-500 hover:bg-destructive/10 hover:text-destructive disabled:cursor-not-allowed disabled:opacity-40 disabled:hover:bg-transparent"
											disabled={countOf(o) > 0}
											onclick={() => startDelete(o)}
											title={countOf(o) > 0
												? 'Suppression impossible : des postes sont rattachés'
												: 'Supprimer'}
										>
											<AppIcon name="trash" size={15} />
										</button>
									{/if}
								</span>
							</div>
						{/if}
					{/each}
				</div>

				{#if canCreate}
					<!-- Création inline : nom + description -->
					<div class="border-t bg-slate-50/50 p-1.5" bind:this={createSectionEl}>
						{#if createOpen}
							<div class="flex flex-col gap-1.5">
								<Input
									type="text"
									bind:value={newName}
									placeholder="Nom de la famille"
									class="h-8 text-sm"
								/>
								<Input
									type="text"
									bind:value={newDesc}
									placeholder="Description (optionnel)"
									class="h-8 text-sm"
								/>
								<div class="flex items-center justify-end gap-1">
									<button
										type="button"
										class="rounded p-1 text-muted-foreground hover:bg-accent"
										onclick={cancelCreate}
										title="Annuler"
									>
										<AppIcon name="x" size={15} />
									</button>
									<button
										type="button"
										class="inline-flex h-8 items-center gap-1.5 rounded-md bg-primary px-3 text-sm font-medium text-primary-foreground hover:bg-primary/90 disabled:opacity-50"
										disabled={!newName.trim() || busy}
										onclick={submitCreate}
									>
										<AppIcon name="plus" size={15} />
										Ajouter
									</button>
								</div>
							</div>
						{:else}
							<button
								type="button"
								class="flex w-full items-center justify-center gap-1.5 rounded-md px-2 py-1.5 text-center text-sm text-primary hover:bg-accent"
								onclick={openCreate}
							>
								<AppIcon name="plus" size={15} />
								Ajouter une famille
							</button>
						{/if}
					</div>
				{/if}
			</div>
		{/if}
	</div>

	<FieldMessages {config} {field} />
	{#if error}
		<p class="text-xs text-destructive">{error}</p>
	{/if}
</div>
