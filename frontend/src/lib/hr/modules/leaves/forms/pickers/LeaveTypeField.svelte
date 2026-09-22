<script lang="ts">
	// LeaveTypeField — renderer riche du type `leaveType` (api §14). Vit dans le
	// module leaves (propriétaire de la source). Le legacy LeaveRequestSheet
	// affiche un point coloré par catégorie (LEAVE_TYPE_COLORS) : on reprend ce
	// langage visuel ici pour une UI cohérente. Source statique du registre
	// (LEAVE_TYPE_OPTIONS), logique de rendu partagée via createBusinessOptions.
	import type { FieldConfig, FieldInstance, FormInstance } from '@/hr/forms/core/types.js';
	import FieldLabel from '@/hr/forms/components/renderers/shared/FieldLabel.svelte';
	import FieldMessages from '@/hr/forms/components/renderers/shared/FieldMessages.svelte';
	import { createBusinessOptions } from '@/hr/forms/components/renderers/business/business-options.svelte';
	import { multiSelectLabel } from '@/hr/forms/components/renderers/field-helpers.js';
	import { LEAVE_TYPE_COLORS } from '../../constants/leaves.js';
	import * as Select from '@/components/ui/select/index.js';
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

	// Couleurs de la catégorie (fallback dot slate si clé inconnue).
	const colorsOf = (o: Opt) =>
		LEAVE_TYPE_COLORS[String(o.value) as keyof typeof LEAVE_TYPE_COLORS] ?? LEAVE_TYPE_COLORS.unpaid;

	const selectedOpt = $derived(allOpts.find((o) => String(o.value) === singleVal));

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
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />

	{#snippet leaveRow(o: Opt)}
		{@const c = colorsOf(o)}
		<Select.Item value={String(o.value)} label={o.label}>
			<span class="flex w-full items-center gap-2.5">
				<span class="h-2.5 w-2.5 shrink-0 rounded-full {c.dot}"></span>
				<span class="flex-1 leading-tight text-sm">{o.label}</span>
				{#if o.sublabel}
					<span class="rounded-full px-1.5 py-0.5 text-[0.6rem] {c.bg} {c.text}">{o.sublabel}</span>
				{/if}
			</span>
		</Select.Item>
	{/snippet}

	{#if isMultiple}
		<Select.Root
			type="multiple"
			value={multiVals}
			onValueChange={handleMulti}
			disabled={field.isDisabled || biz.loading}
			onOpenChange={(open) => open && biz.ensureLoaded()}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				{multiLabel || config.placeholder || 'Sélectionner…'}
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden">
				{#each allOpts as o (String(o.value))}
					{@render leaveRow(o)}
				{/each}
				{#if biz.loading}
					<p class="flex justify-center px-3 py-4">
						<AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" />
					</p>
				{:else if allOpts.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun résultat</p>
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
			onOpenChange={(open) => open && biz.ensureLoaded()}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				<span class="flex items-center gap-2 text-sm">
					{#if selectedOpt}
						<span class="h-2.5 w-2.5 shrink-0 rounded-full {colorsOf(selectedOpt).dot}"></span>
						{selectedOpt.label}
					{:else}
						{config.placeholder || 'Sélectionner…'}
					{/if}
				</span>
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden">
				{#each allOpts as o (String(o.value))}
					{@render leaveRow(o)}
				{/each}
				{#if biz.loading}
					<p class="flex justify-center px-3 py-4">
						<AnimateSpin class="size-3.5 border-slate-400" text="Chargement…" textPosition="right" />
					</p>
				{:else if allOpts.length === 0}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun résultat</p>
				{/if}
			</Select.Content>
		</Select.Root>
	{/if}
	<FieldMessages {config} {field} />
</div>
