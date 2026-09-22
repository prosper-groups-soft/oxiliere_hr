<script lang="ts">
	// OrgUnitField — renderer riche du type `orgUnit` (api §14). Vit dans le
	// module jobs (propriétaire de la source), même pattern qu'EmployeePicker :
	// le rendu métier (badge de type, indentation hiérarchique par `level`,
	// effectif) reste côté module, la logique de source/cascade reste dans forms/
	// via createBusinessOptions.
	import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
	import FieldLabel from '@/hr/forms/components/renderers/shared/FieldLabel.svelte';
	import FieldMessages from '@/hr/forms/components/renderers/shared/FieldMessages.svelte';
	import { createBusinessOptions } from '@/hr/forms/components/renderers/business/business-options.svelte';
	import { multiSelectLabel } from '@/hr/forms/components/renderers/field-helpers.js';
	import * as Select from '@/components/ui/select/index.js';
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

	const isMultiple = $derived(biz.isMultiple);
	const allOpts = $derived(biz.allOpts as Opt[]);
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const multiVals = $derived(Array.isArray(field.value) ? field.value.map((v) => String(v)) : []);
	const multiLabel = $derived(multiSelectLabel(multiVals, allOpts));
	const typeaheadItems = $derived(allOpts.map((o) => ({ value: String(o.value), label: o.label })));

	// ── Cache d'options cumulées : la recherche filtre allOpts (source distante),
	// or les éléments sélectionnés doivent rester affichés (nom, badge de type)
	// dans le trigger même quand ils sortent des résultats. On mémorise donc
	// toute option déjà chargée et on lit le trigger depuis ce cache. ──
	let knownOpts = $state<Map<string, Opt>>(new Map());
	$effect(() => {
		for (const o of allOpts) knownOpts.set(String(o.value), o);
	});
	const optOf = (v: string): Opt | undefined => knownOpts.get(v);

	// ── Identité visuelle par type d'unité (OrgUnitType backend) — classes
	// Tailwind figées pour préserver la détection des classes (pas de
	// construction dynamique). Icônes Lucide via AppIcon (registre projet). ──
	const TYPE_META: Record<string, { icon: string; badge: string; iconCls: string }> = {
		DIRECTION: { icon: 'landmark', badge: 'bg-slate-100 text-slate-700', iconCls: 'text-slate-500' },
		DEPARTMENT: { icon: 'building', badge: 'bg-blue-50 text-blue-700', iconCls: 'text-blue-500' },
		DIVISION: { icon: 'network', badge: 'bg-violet-50 text-violet-700', iconCls: 'text-violet-500' },
		TEAM: { icon: 'users', badge: 'bg-emerald-50 text-emerald-700', iconCls: 'text-emerald-500' },
		SECTION: { icon: 'layers', badge: 'bg-amber-50 text-amber-700', iconCls: 'text-amber-500' },
		SERVICE: { icon: 'briefcase', badge: 'bg-rose-50 text-rose-700', iconCls: 'text-rose-500' },
		FUNCTION: { icon: 'crosshair', badge: 'bg-teal-50 text-teal-700', iconCls: 'text-teal-500' },
		BRANCH: { icon: 'git-branch', badge: 'bg-cyan-50 text-cyan-700', iconCls: 'text-cyan-500' },
		PROJECT: { icon: 'zap', badge: 'bg-fuchsia-50 text-fuchsia-700', iconCls: 'text-fuchsia-500' }
	};
	const FALLBACK_META = { icon: 'building', badge: 'bg-muted text-muted-foreground', iconCls: 'text-slate-400' };

	function metaOf(o: Opt) {
		// Type depuis sublabel/raw (adapter registre) ou suffixe « (TYPE) » du
		// label — les sources injectées (mocks) l'utilisent à la place du sublabel.
		const t = typeTextOf(o);
		return t ? (TYPE_META[t] ?? FALLBACK_META) : FALLBACK_META;
	}

	function typeTextOf(o: Opt): string {
		// Adapter registre (sublabel) ou entité brute — plusieurs noms possibles
		// selon le backend (type, unit_type, node_type). Sinon suffixe « (TYPE) »
		// du label (sources injectées / mocks).
		const direct = String(
			o.sublabel ?? o.raw?.type ?? o.raw?.unit_type ?? o.raw?.node_type ?? ''
		).toUpperCase();
		if (direct) {
			console.log('[OrgUnitField] type détecté pour', o.label, '→', direct);
			return direct;
		}
		const m = String(o.label).match(/\(([A-Z_]+)\)$/);
		if (m) return m[1];
		return '';
	}

	// ── Hiérarchie : indentation par `level` (0 = racine) renvoyé par le
	// backend sur la liste plate. Absent (mock/legacy) → pas d'indentation. ──
	const indentOf = (o: Opt): number => {
		const lv = Number(o.raw?.level);
		return Number.isFinite(lv) && lv > 0 ? Math.min(lv, 4) : 0;
	};

	// Effectif backend (employee_count | employeeCount | subUnitCount).
	const headcountOf = (o: Opt): string | undefined => {
		const n = o.raw?.employee_count ?? o.raw?.employeeCount;
		if (n != null && Number.isFinite(Number(n))) return `${n}`;
		return undefined;
	};

	const selectedOpt = $derived(singleVal ? optOf(singleVal) : undefined);

	function handleSingle(v: string | undefined) {
		const next = v ?? '';
		field.setValue(next || null);
		config.onChange?.(next || null);
	}

	function handleMulti(v: string[] | undefined) {
		const next = v ?? [];
		field.setValue(next);
		config.onChange?.(next);
	}

	function onQueryInput(e: Event) {
		biz.onSearchInput((e.currentTarget as HTMLInputElement).value);
	}
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />

	{#snippet orgRow(o: Opt)}
		{@const indent = indentOf(o)}
		{@const meta = metaOf(o)}
		{@const headcount = headcountOf(o)}
		<Select.Item value={String(o.value)} label={o.label}>
			<span class="flex w-full items-center gap-2">
				<span class="shrink-0" style="width: {indent * 0.75}rem"></span>
				<span class="flex flex-1 items-center gap-2 leading-tight">
					<AppIcon name={meta.icon} size={14} class="shrink-0 {meta.iconCls}" />
					<span class="text-sm">{typeTextOf(o) ? o.label.replace(/ \([A-Z_]+\)$/, '') : o.label}</span>
					<span class="rounded px-1 py-0.5 text-[0.6rem] font-semibold uppercase {meta.badge}">{typeTextOf(o)}</span>
					{#if headcount}
						<span class="ml-auto text-xs text-muted-foreground">{headcount}</span>
					{/if}
				</span>
			</span>
		</Select.Item>
	{/snippet}

	{#if isMultiple}
		<Select.Root
			type="multiple"
			value={multiVals}
			onValueChange={handleMulti}
			disabled={field.isDisabled || biz.loading}
			onOpenChange={(open) => { if (open) biz.ensureLoaded(); else field.blur(); }}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full min-w-0 text-sm" size="sm">
				{#if multiVals.length === 0}
					<span class="flex items-center gap-2 text-sm">
						<AppIcon name="building" size={15} class="shrink-0 text-slate-300" />
						<span class="text-sm">{config.placeholder || 'Sélectionner…'}</span>
					</span>
				{:else}
					<span class="flex w-full min-w-0 flex-nowrap items-center gap-1 overflow-hidden">
						{#each multiVals.slice(0, 2) as v (v)}
							{@const opt = optOf(v)}
							{@const meta = opt ? metaOf(opt) : FALLBACK_META}
							{@const typeText = opt ? typeTextOf(opt) : ''}
							<span class="flex min-w-0 items-center gap-1 rounded bg-muted px-1.5 py-0.5 text-xs">
								<AppIcon name={meta.icon} size={12} class="shrink-0 {meta.iconCls}" />
								<span class="truncate text-xs">{opt ? opt.label.replace(/ \([A-Z_]+\)$/, '') : v}</span>
								{#if typeText}
									<span class="shrink-0 rounded px-1 text-[0.55rem] font-semibold uppercase {meta.badge}">{typeText}</span>
								{/if}
							</span>
						{/each}
						{#if multiVals.length > 2}
							<span class="shrink-0 rounded-full bg-muted px-1.5 py-0.5 text-xs text-muted-foreground">
								+{multiVals.length - 2}
							</span>
						{/if}
					</span>
				{/if}
			</Select.Trigger>
			<Select.Content
				class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0"
			>
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input
						type="text"
						placeholder="Rechercher…"
						class="h-8"
						onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
						oninput={onQueryInput}
					/>
				</div>
				{#each allOpts as o (String(o.value))}
					{@render orgRow(o)}
				{/each}
				{#if biz.loading}
					<p class="flex justify-center px-3 py-4">
						<AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" />
					</p>
				{:else if allOpts.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun résultat</p>
				{/if}
				{#if biz.hasMore}
					<div class="flex justify-end px-4 pb-1.5">
						<button
							type="button"
							class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline"
							onclick={() => biz.loadMore()}
						>
							Voir plus +
						</button>
					</div>
				{/if}
						</Select.Content>
					</Select.Root>
				{:else}
		<Select.Root
			type="single"
			value={singleVal}
			onValueChange={handleSingle}
			disabled={field.isDisabled || biz.loading}
			items={typeaheadItems}
			allowDeselect={!config.required}
			onOpenChange={(open) => { if (open) biz.ensureLoaded(); else field.blur(); }}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				<span class="flex items-center gap-2 text-sm">
					{#if selectedOpt}
						{@const meta = metaOf(selectedOpt)}
						<AppIcon name={meta.icon} size={15} class="shrink-0 {meta.iconCls}" />
						<span class="text-sm">{typeTextOf(selectedOpt) ? selectedOpt.label.replace(/ \([A-Z_]+\)$/, '') : selectedOpt.label}</span>
						<span class="rounded px-1 py-0.5 text-[0.6rem] font-semibold uppercase {meta.badge}">
							{typeTextOf(selectedOpt)}
						</span>
					{:else}
						<AppIcon name="building" size={15} class="shrink-0 text-slate-300" />
						{config.placeholder || 'Sélectionner…'}
					{/if}
				</span>
			</Select.Trigger>
			<Select.Content
				class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0"
			>
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input
						type="text"
						placeholder="Rechercher…"
						class="h-8"
						onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
						oninput={onQueryInput}
					/>
				</div>
				{#each allOpts as o (String(o.value))}
					{@render orgRow(o)}
				{/each}
				{#if biz.loading}
					<p class="flex justify-center px-3 py-4">
						<AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" />
					</p>
				{:else if allOpts.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun résultat</p>
				{/if}
				{#if biz.hasMore}
					<div class="flex justify-end px-4 pb-1.5">
						<button
							type="button"
							class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline"
							onclick={() => biz.loadMore()}
						>
							Voir plus +
						</button>
					</div>
				{/if}
						</Select.Content>
					</Select.Root>
				{/if}
	<FieldMessages {config} {field} />
</div>
