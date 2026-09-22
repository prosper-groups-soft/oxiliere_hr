<script lang="ts">
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import Input from '@/components/ui/input/input.svelte';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	// Bornes natives : config.min/max direct, ou validateurs minDate/maxDate.
	// Normalisées en yyyy-MM-dd (format attendu par l'input date natif).
	function toInputDate(v: unknown): string | undefined {
		if (v == null || v === '') return undefined;
		const d = new Date(String(v));
		if (Number.isNaN(d.getTime())) return undefined;
		return d.toISOString().slice(0, 10);
	}

	const findDateValidator = (type: 'minDate' | 'maxDate') =>
		(config.validators ?? []).find((v) => v.type === type)?.params?.value;

	const min = $derived(toInputDate(config.min ?? findDateValidator('minDate')));
	const max = $derived(toInputDate(config.max ?? findDateValidator('maxDate')));
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	<Input
		id={field.id}
		data-field={field.name}
		type="date"
		value={field.value ?? ''}
		{min}
		{max}
		disabled={field.isDisabled}
		readonly={field.isReadonly}
		aria-invalid={!field.isValid}
		oninput={(e) => {
			const v = (e.target as HTMLInputElement).value;
			field.setValue(v || null);
			config.onInput?.(v || null);
		}}
		onblur={() => field.blur()}
		onfocus={() => field.focus()}
	/>
	<FieldMessages {config} {field} />
</div>
