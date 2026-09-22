<script lang="ts">
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import Input from '@/components/ui/input/input.svelte';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	const min = $derived(config.min ?? undefined);
	const max = $derived(config.max ?? undefined);
	const step = $derived(config.step ?? undefined);

	// Mode view (readonly global) : affichage formaté fr-FR, la valeur stockée
	// reste le nombre nu — l'input number natif ne rend pas les milliers lisibles.
	const viewDisplay = $derived.by(() => {
		if (!field.isReadonly || field.value == null || field.value === '') return undefined;
		const n = Number(field.value);
		if (Number.isNaN(n)) return String(field.value);
		return new Intl.NumberFormat('fr-FR', { useGrouping: true }).format(n);
	});
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	{#if viewDisplay !== undefined}
		<div
			id={field.id}
			data-field={field.name}
			class="flex h-9 w-full items-center rounded-md border border-input bg-transparent px-3 py-1 text-sm tabular-nums shadow-xs opacity-60"
		>
			{viewDisplay}
		</div>
	{:else}
		<Input
			id={field.id}
			data-field={field.name}
			type="number"
			value={field.value ?? ''}
			{min}
			{max}
			{step}
			placeholder={config.placeholder ?? config.help}
			disabled={field.isDisabled}
			readonly={field.isReadonly}
			aria-invalid={!field.isValid}
			oninput={(e) => {
				const raw = (e.target as HTMLInputElement).value;
				const next = raw === '' ? null : Number(raw);
				field.setValue(Number.isNaN(next) ? raw : next);
				config.onInput?.(next);
			}}
			onblur={() => field.blur()}
			onfocus={() => field.focus()}
		/>
	{/if}
	<FieldMessages {config} {field} />
</div>
