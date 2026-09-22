<script lang="ts">
	// Champ pays dédié (Lot D) : liste statique COUNTRY_OPTIONS (constante projet —
	// principe standalone, import direct toléré pour les constantes statiques),
	// drapeaux flagcdn + recherche locale (pattern PhoneField : sticky en haut du menu).
	// La valeur stockée reste le code ISO 2 lettres (ex: "CD"), serializable.
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import CountryFlag from '@/hr/components/shared/country/CountryFlag.svelte';
	import { COUNTRY_OPTIONS } from '@/hr/modules/employees/constants/countries';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';
	import { isMultipleSelection, multiSelectLabel } from '../field-helpers.js';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	let query = $state('');

	const isMultiple = $derived(isMultipleSelection(config));
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const multiVals = $derived(Array.isArray(field.value) ? field.value.map((v) => String(v)) : []);

	// Tri alphabétique français, RD Congo reste en tête (contexte métier RDC)
	const sortedOptions = $derived(
		[...COUNTRY_OPTIONS].sort((a, b) =>
			a.value === 'CD' ? -1 : b.value === 'CD' ? 1 : a.label.localeCompare(b.label, 'fr')
		)
	);

	const filteredOptions = $derived.by(() => {
		const q = query.trim().toLowerCase();
		if (!q) return sortedOptions;
		return sortedOptions.filter(
			(c) => c.label.toLowerCase().includes(q) || c.code.toLowerCase().includes(q)
		);
	});

	const multiLabel = $derived(multiSelectLabel(multiVals, sortedOptions));
	const selectedCountry = $derived(COUNTRY_OPTIONS.find((c) => c.value === singleVal));

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

	{#if isMultiple}
		<Select.Root
			type="multiple"
			value={multiVals}
			onValueChange={handleMulti}
			disabled={field.isDisabled || field.isReadonly}
			onOpenChange={(open) => { if (!open) { query = ''; field.blur(); } }}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				{multiLabel || (config.placeholder ?? 'Sélectionner…')}
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden">
				<div class="sticky top-0 z-10 -mx-1 -mt-1 mb-1 border-b bg-popover p-1.5">
					<Input
						type="text"
						bind:value={query}
						placeholder="Rechercher un pays…"
						class="h-8"
						onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
					/>
				</div>
				{#each filteredOptions as c (c.value)}
					<Select.Item value={c.value} label={c.label}>
						<span class="flex items-center gap-2">
							<CountryFlag code={c.code} size={20} />
							<span class="flex-1 text-sm">{c.label}</span>
							<span class="text-muted-foreground tabular-nums text-[0.82rem]">{c.code}</span>
						</span>
					</Select.Item>
				{:else}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun pays trouvé</p>
				{/each}
			</Select.Content>
		</Select.Root>
	{:else}
		<Select.Root
			type="single"
			value={singleVal}
			onValueChange={handleSingle}
			disabled={field.isDisabled || field.isReadonly}
			allowDeselect={!config.required}
			onOpenChange={(open) => { if (!open) { query = ''; field.blur(); } }}
		>
			<Select.Trigger id={field.id} data-field={field.name} class="w-full text-sm" size="sm">
				<span class="flex items-center gap-2 text-sm">
					{#if selectedCountry}<CountryFlag code={selectedCountry.code} size={20} />{/if}
					{selectedCountry?.label ?? (config.placeholder ?? 'Sélectionner un pays…')}
				</span>
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 *:data-[slot=select-scroll-up-button]:hidden">
				<div class="sticky top-0 z-10 -mx-1 -mt-1 mb-1 border-b bg-popover p-1.5">
					<Input
						type="text"
						bind:value={query}
						placeholder="Rechercher un pays…"
						class="h-8"
						onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
					/>
				</div>
				{#each filteredOptions as c (c.value)}
					<Select.Item value={c.value} label={c.label}>
						<span class="flex items-center gap-2">
							<CountryFlag code={c.code} size={20} />
							<span class="flex-1 text-sm">{c.label}</span>
							<span class="text-muted-foreground tabular-nums text-[0.82rem]">{c.code}</span>
						</span>
					</Select.Item>
				{:else}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun pays trouvé</p>
				{/each}
			</Select.Content>
		</Select.Root>
	{/if}

	<FieldMessages {config} {field} />
</div>
