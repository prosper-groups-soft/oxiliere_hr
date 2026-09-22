<script lang="ts">
	// GroupPicker — renderer riche du type `group` (accès).
	// Data-aware : lit le raw Group (slug, name, app, roles, member_count, role_count).
	import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
	import FieldLabel from '@/hr/forms/components/renderers/shared/FieldLabel.svelte';
	import FieldMessages from '@/hr/forms/components/renderers/shared/FieldMessages.svelte';
	import { createBusinessOptions } from '@/hr/forms/components/renderers/business/business-options.svelte';
	import { resolveTypeEntity } from '@/hr/forms/core/typeRegistry.js';
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
	import type { Group } from '@/hr/modules/admin/access/types/access.types.js';

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

	type Opt = { label: string; value: unknown; sublabel?: string; raw?: (Group & { id?: string }) | any };

	function rawOf(o: Opt | undefined): (Group & { id?: string }) | undefined {
		return o?.raw as (Group & { id?: string }) | undefined;
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

	let resolved = $state<(Group & { id?: string }) | null>(null);
	$effect(() => {
		const id = singleVal;
		if (!id || isMultiple || allOpts.some((o) => String(o.value) === id)) {
			resolved = null;
			return;
		}
		let alive = true;
		resolveTypeEntity<Group & { id?: string }>(config.type, id)
			.then((p) => { if (alive) resolved = p; })
			.catch(() => { if (alive) resolved = null; });
		return () => { alive = false; };
	});

	const selectedOpt = $derived(allOpts.find((o) => String(o.value) === singleVal));
	const triggerRaw = $derived(rawOf(selectedOpt) ?? resolved ?? undefined);
	const triggerLabel = $derived(triggerRaw?.name ?? selectedOpt?.label ?? '');

	function onQueryInput(e: Event) {
		biz.onSearchInput((e.currentTarget as HTMLInputElement).value);
	}
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	{#snippet groupRow(o: Opt)}
		{@const raw = rawOf(o)}
		<Select.Item value={String(o.value)} label={o.label} class="py-2">
			<span class="flex w-full items-center gap-2.5">
				<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50">
					<AppIcon name="shield" size={15} class="text-slate-500" />
				</span>
				<span class="min-w-0 flex-1 leading-tight">
					<span class="truncate text-sm font-medium">{o.label}</span>
					<span class="mt-0.5 block truncate text-[0.8rem] text-muted-foreground">
						{raw?.member_count ?? 0} membre{(raw?.member_count ?? 0) > 1 ? 's' : ''}{#if raw?.role_count} · {raw.role_count} rôle{raw.role_count > 1 ? 's' : ''}{/if}{#if raw?.app} · {raw.app}{/if}
					</span>
				</span>
				<span class="ml-auto shrink-0 rounded-full bg-slate-100 px-2 py-0.5 text-[0.65rem] font-semibold text-slate-600">{raw?.slug ?? ''}</span>
			</span>
		</Select.Item>
	{/snippet}

	{#if isMultiple}
		<Select.Root type="multiple" value={multiVals} onValueChange={handleMulti} disabled={field.isDisabled || biz.loading} onOpenChange={(open) => open && biz.ensureLoaded()}>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full min-w-0 text-sm" size="sm">
				{#if multiVals.length === 0}{#if biz.loading}<AnimateSpin class="size-3 border-slate-400" text="" />{:else}<span class="text-sm">{config.placeholder || 'Sélectionner un groupe…'}</span>{/if}
				{:else}<span class="truncate text-sm">{multiVals.length} groupe{multiVals.length > 1 ? 's' : ''}</span>{/if}
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0">
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input type="text" placeholder="Rechercher…" class="h-8" onkeydown={(e: KeyboardEvent) => e.stopPropagation()} oninput={onQueryInput} />
				</div>
				{#each allOpts as o (String(o.value))}{@render groupRow(o)}{/each}
				{#if biz.loading}<p class="flex justify-center px-3 py-4"><AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" /></p>
				{:else if allOpts.length === 0}<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun groupe</p>{/if}
			</Select.Content>
		</Select.Root>
	{:else}
		<Select.Root type="single" value={singleVal} onValueChange={handleSingle} disabled={field.isDisabled || biz.loading} items={typeaheadItems} allowDeselect={!config.required} onOpenChange={(open) => open && biz.ensureLoaded()}>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				<span class="flex w-full items-center gap-2 text-sm">
					<span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50"><AppIcon name="shield" size={14} class="text-slate-500" /></span>
					{#if triggerLabel}<span class="truncate text-sm font-medium">{triggerLabel}</span>{#if triggerRaw}<span class="hidden truncate text-xs text-muted-foreground sm:inline">{triggerRaw.member_count} membres</span>{/if}
					{:else if biz.loading}<AnimateSpin class="size-3 border-slate-400" text="Chargement des groupes" textPosition="right" />
					{:else}<span class="text-sm">{config.placeholder || 'Sélectionner un groupe…'}</span>{/if}
				</span>
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0">
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input type="text" placeholder="Rechercher…" class="h-8" onkeydown={(e: KeyboardEvent) => e.stopPropagation()} oninput={onQueryInput} />
				</div>
				{#each allOpts as o (String(o.value))}{@render groupRow(o)}{/each}
				{#if biz.loading}<p class="flex justify-center px-3 py-4"><AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" /></p>
				{:else if allOpts.length === 0}<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun groupe</p>{/if}
			</Select.Content>
		</Select.Root>
	{/if}
	<FieldMessages {config} {field} />
</div>
