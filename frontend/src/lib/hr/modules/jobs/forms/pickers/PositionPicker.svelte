<script lang="ts">
	// PositionPicker — renderer riche du type `position`.
	// Data-aware : lit le raw JobPosition (job_family, org_unit, seniority_levels).
	import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
	import FieldLabel from '@/hr/forms/components/renderers/shared/FieldLabel.svelte';
	import FieldMessages from '@/hr/forms/components/renderers/shared/FieldMessages.svelte';
	import { createBusinessOptions } from '@/hr/forms/components/renderers/business/business-options.svelte';
	import { resolveTypeEntity } from '@/hr/forms/core/typeRegistry.js';
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';
	import type { JobPosition } from '@/hr/modules/jobs/types/types.js';

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

	type Opt = { label: string; value: unknown; sublabel?: string; raw?: JobPosition | any };

	function rawOf(o: Opt | undefined): JobPosition | undefined {
		return o?.raw as JobPosition | undefined;
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

	let resolved = $state<JobPosition | null>(null);
	
	$effect(() => {
		const id = singleVal;
		if (!id || isMultiple || allOpts.some((o) => String(o.value) === id)) {
			resolved = null;
			return;
		}
		let alive = true;
		resolveTypeEntity<JobPosition>(config.type, id)
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


{#snippet positionRow(o: Opt)}
	{@const raw = rawOf(o)}
	<Select.Item value={String(o.value)} label={o.label} class="py-2">
		<span class="flex w-full items-center gap-2.5">
			<span class="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50">
				<AppIcon name="briefcase" size={15} class="text-slate-500" />
			</span>
			<span class="min-w-0 flex-1 leading-normal">
				<span class="truncate text-sm font-medium">{o.label}</span>
				<span class="mt-1 flex flex-col gap-0.5 text-[0.8rem] font-normal text-slate-600">
					{#if raw?.job_family?.name}
						<span class="flex items-center gap-1.5">
							<AppIcon name="layers" size={13} class="shrink-0 text-slate-400" />
							<span class="shrink-0 font-medium text-slate-400 text-[0.85rem]">Famille :</span>
							<span class="truncate text-[0.85rem]">{raw.job_family.name}</span>
						</span>
					{/if}
					{#if raw?.org_unit?.name}
						<span class="flex items-center gap-1.5">
							<AppIcon name="building-2" size={13} class="shrink-0 text-slate-400" />
							<span class="shrink-0 font-medium text-slate-400 text-[0.85rem]">Unité :</span>
							<span class="truncate text-[0.85rem]">{raw.org_unit.name}</span>
						</span>
					{/if}
					{#if raw?.seniority_levels?.length}
						<span class="flex items-center gap-1.5">
							<AppIcon name="award" size={13} class="shrink-0 text-slate-400" />
							<span class="shrink-0 font-medium text-slate-400 text-[0.85rem]">Niveaux :</span>
							<span class="text-[0.85rem]">{raw.seniority_levels.length} niveau{raw.seniority_levels.length > 1 ? 'x' : ''}</span>
						</span>
					{/if}
				</span>
			</span>
		</span>
	</Select.Item>
{/snippet}


<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />

	{#if isMultiple}
		<Select.Root type="multiple" value={multiVals} onValueChange={handleMulti} disabled={field.isDisabled || biz.loading} onOpenChange={(open) => open && biz.ensureLoaded()}>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full min-w-0 text-sm" size="sm">
				{#if multiVals.length === 0}{#if biz.loading}<AnimateSpin class="size-3 border-slate-400" text="" />{:else}<span class="text-sm">{config.placeholder || 'Sélectionner un poste…'}</span>{/if}
				{:else}<span class="truncate text-sm">{multiVals.length} poste{multiVals.length > 1 ? 's' : ''}</span>{/if}
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0">
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input type="text" placeholder="Rechercher…" class="h-8" onkeydown={(e: KeyboardEvent) => e.stopPropagation()} oninput={onQueryInput} />
				</div>
				{#each allOpts as o (String(o.value))}{@render positionRow(o)}{/each}
				{#if biz.loading}<p class="flex justify-center px-3 py-4"><AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" /></p>
				{:else if allOpts.length === 0}<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun poste</p>{/if}
				{#if biz.hasMore}<div class="flex justify-end px-4 pb-1.5"><button type="button" class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline" onclick={() => biz.loadMore()}>Voir plus +</button></div>{/if}
			</Select.Content>
		</Select.Root>
	{:else}
		<Select.Root type="single" value={singleVal} onValueChange={handleSingle} disabled={field.isDisabled || biz.loading} items={typeaheadItems} allowDeselect={!config.required} onOpenChange={(open) => open && biz.ensureLoaded()}>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				<span class="flex w-full items-center gap-2 text-sm">
					<span class="flex h-7 w-7 shrink-0 items-center justify-center rounded-lg border border-slate-200 bg-slate-50"><AppIcon name="briefcase" size={14} class="text-slate-500" /></span>
					{#if triggerLabel}
						<span class="flex min-w-0 flex-1 items-center gap-2">
							<span class="truncate text-sm font-medium">{triggerLabel}</span>
						</span>
					{:else if biz.loading}<AnimateSpin class="size-3 border-slate-400" text="Chargement des postes" textPosition="right" />
					{:else}<span class="text-sm">{config.placeholder || 'Sélectionner un poste…'}</span>{/if}
				</span>
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden [&>div:not([data-slot])]:pt-0">
				<div class="sticky top-0 z-10 -mx-1 mb-1 border-b bg-white px-1.5 pb-1.5 pt-3">
					<Input type="text" placeholder="Rechercher…" class="h-8" onkeydown={(e: KeyboardEvent) => e.stopPropagation()} oninput={onQueryInput} />
				</div>
				{#each allOpts as o (String(o.value))}{@render positionRow(o)}{/each}
				{#if biz.loading}<p class="flex justify-center px-3 py-4"><AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" /></p>
				{:else if allOpts.length === 0}<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun poste</p>{/if}
				{#if biz.hasMore}<div class="flex justify-end px-4 pb-1.5"><button type="button" class="text-[0.85rem] text-muted-foreground hover:text-primary hover:underline" onclick={() => biz.loadMore()}>Voir plus +</button></div>{/if}
			</Select.Content>
		</Select.Root>
	{/if}
	<FieldMessages {config} {field} />
</div>
