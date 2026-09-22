<script lang="ts">
	// BankPicker — renderer riche du type `bankInstitution`.
	// Data-aware : lit le raw BankInstitutionBackendResponse (name, code,
	// swift_code, is_mobile_money, country_code, logo).
	import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
	import FieldLabel from '@/hr/forms/components/renderers/shared/FieldLabel.svelte';
	import FieldMessages from '@/hr/forms/components/renderers/shared/FieldMessages.svelte';
	import { createBusinessOptions } from '@/hr/forms/components/renderers/business/business-options.svelte';
	import { resolveTypeEntity } from '@/hr/forms/core/typeRegistry.js';
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
	import type { BankInstitutionBackendResponse } from '@/hr/modules/banking/types/types.js';
	import { getMediaUrl } from '@/hr/utilities/common/media';

	let {
		config,
		field,
		form
	}: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	// svelte-ignore state_referenced_locally
	const biz = createBusinessOptions(config, field, form);

	const isMultiple = $derived(biz.isMultiple);
	const allOpts = $derived(biz.allOpts as Opt[]);
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const multiVals = $derived(Array.isArray(field.value) ? field.value.map((v) => String(v)) : []);
	const typeaheadItems = $derived(allOpts.map((o) => ({ value: String(o.value), label: o.label })));

	type Opt = { label: string; value: unknown; sublabel?: string; raw?: BankInstitutionBackendResponse | any };

	function rawOf(o: Opt | undefined): BankInstitutionBackendResponse | undefined {
		return o?.raw as BankInstitutionBackendResponse | undefined;
	}
	
	function kindOf(raw?: BankInstitutionBackendResponse): string {
		return raw?.is_mobile_money ? 'Mobile money' : 'Banque';
	}
	
	function logoOf(raw?: BankInstitutionBackendResponse): string | undefined {
		return raw?.logo ? getMediaUrl(raw.logo) : undefined;
	}
	
	function initialsOf(raw?: BankInstitutionBackendResponse): string {
		return (raw?.name ?? '').split(/\s+/).map((w) => w[0]).join('').slice(0, 2).toUpperCase() || '—';
	}

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

	let resolved = $state<BankInstitutionBackendResponse | null>(null);
	
	$effect(() => {
		const id = singleVal;
		if (!id || isMultiple || allOpts.some((o) => String(o.value) === id)) {
			resolved = null;
			return;
		}
		let alive = true;
		resolveTypeEntity<BankInstitutionBackendResponse>(config.type, id)
			.then((p) => { if (alive) resolved = p; })
			.catch(() => { if (alive) resolved = null; });
		return () => { alive = false; };
	});

	const selectedOpt = $derived(allOpts.find((o) => String(o.value) === singleVal));
	const triggerRaw = $derived(rawOf(selectedOpt) ?? resolved ?? undefined);
	const triggerLabel = $derived(triggerRaw?.name ?? selectedOpt?.label ?? '');

	// ── Recherche locale (pattern SelectPicker) : la source banques est un
	// tableau non paginé déjà chargé en mémoire (fetch ignore le param search) —
	// filtre client sur label/code/swift/pays/type, sans délégation serveur. ──
	let query = $state('');

	function localFilter(opts: Opt[]): Opt[] {
		const q = query.trim().toLowerCase();
		if (!q) return opts;
		return opts.filter((o) => {
			const raw = rawOf(o);
			const hay = `${o.label} ${raw?.code ?? ''} ${raw?.swift_code ?? ''} ${raw?.country_code ?? ''} ${kindOf(raw)}`.toLowerCase();
			return hay.includes(q);
		});
	}

	const filteredOpts = $derived(localFilter(allOpts));
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	{#snippet bankRow(o: Opt)}
		{@const raw = rawOf(o)}
		<Select.Item value={String(o.value)} label={o.label} class="py-2">
			<span class="flex w-full items-center gap-2.5">
				<span class="flex h-8 w-8 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-slate-200 bg-slate-50 text-[0.7rem] font-bold text-slate-600">
					{#if raw && logoOf(raw)}<img src={logoOf(raw)} alt={o.label} class="h-full w-full object-cover" />{:else}{initialsOf(raw)}{/if}
				</span>
				<span class="min-w-0 flex-1 leading-tight">
					<span class="truncate text-sm font-medium">{o.label}</span>
					<span class="mt-0.5 block truncate text-[0.8rem] text-muted-foreground">{kindOf(raw)}{#if raw?.code} · {raw.code}{/if}{#if raw?.country_code} · {raw.country_code}{/if}</span>
				</span>
				<AppIcon name={raw?.is_mobile_money ? 'smartphone' : 'landmark'} size={15} class="ml-auto shrink-0 text-slate-400" />
			</span>
		</Select.Item>
	{/snippet}

	{#if isMultiple}
		<Select.Root type="multiple" value={multiVals} onValueChange={handleMulti} disabled={field.isDisabled || biz.loading} onOpenChange={(open) => { if (open) biz.ensureLoaded(); else { query = ''; field.blur(); } }}>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full min-w-0 text-sm" size="sm">
				{#if multiVals.length === 0}
					{#if biz.loading}<AnimateSpin class="size-3 border-slate-400" text="" />{:else}<span class="text-sm">{config.placeholder || 'Sélectionner une banque…'}</span>{/if}
				{:else}<span class="truncate text-sm">{multiVals.length} banque{multiVals.length > 1 ? 's' : ''}</span>{/if}
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0">
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input type="text" placeholder="Rechercher…" class="h-8" onkeydown={(e: KeyboardEvent) => e.stopPropagation()} bind:value={query} />
				</div>
				{#each filteredOpts as o (String(o.value))}{@render bankRow(o)}{/each}
				{#if biz.loading}<p class="flex justify-center px-3 py-4"><AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" /></p>
				{:else if filteredOpts.length === 0}<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucune banque</p>{/if}
			</Select.Content>
		</Select.Root>
	{:else}
		<Select.Root type="single" value={singleVal} onValueChange={handleSingle} disabled={field.isDisabled || biz.loading} items={typeaheadItems} allowDeselect={!config.required} onOpenChange={(open) => { if (open) biz.ensureLoaded(); else { query = ''; field.blur(); } }}>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				<span class="flex w-full items-center gap-2 text-sm">
					<span class="flex h-7 w-7 shrink-0 items-center justify-center overflow-hidden rounded-lg border border-slate-200 bg-slate-50 text-[0.65rem] font-bold text-slate-600">
						{#if triggerRaw && logoOf(triggerRaw)}<img src={logoOf(triggerRaw)} alt={triggerLabel} class="h-full w-full object-cover" />{:else}{initialsOf(triggerRaw)}{/if}
					</span>
					{#if triggerLabel}
						<span class="truncate text-sm font-medium">{triggerLabel}</span>
						{#if triggerRaw}<span class="hidden truncate text-xs text-muted-foreground sm:inline">{kindOf(triggerRaw)} · {triggerRaw.code}</span>{/if}
					{:else if biz.loading}<AnimateSpin class="size-3 border-slate-400" text="Chargement des banques" textPosition="right" />
					{:else}<span class="text-sm">{config.placeholder || 'Sélectionner une banque…'}</span>{/if}
				</span>
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0">
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input type="text" placeholder="Rechercher…" class="h-8" onkeydown={(e: KeyboardEvent) => e.stopPropagation()} bind:value={query} />
				</div>
				{#each filteredOpts as o (String(o.value))}{@render bankRow(o)}{/each}
				{#if biz.loading}<p class="flex justify-center px-3 py-4"><AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" /></p>
				{:else if filteredOpts.length === 0}<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucune banque</p>{/if}
			</Select.Content>
		</Select.Root>
	{/if}
	<FieldMessages {config} {field} />
</div>
