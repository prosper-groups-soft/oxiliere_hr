<script lang="ts">
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import Input from '@/components/ui/input/input.svelte';
	import Label from '@/components/ui/label/label.svelte';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';
	import { staticOptions } from '../field-helpers.js';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	const opts = $derived(staticOptions(config));
	const layout = $derived((config as any).layout ?? 'vertical');
	const current = $derived(field.value == null ? '' : String(field.value));

	function choose(v: unknown) {
		field.setValue(v);
		config.onChange?.(v);
	}
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	<div
		role="radiogroup"
		aria-invalid={!field.isValid}
		class={layout === 'horizontal' ? 'flex flex-wrap gap-4' : 'grid gap-2'}
	>
		{#each opts as opt}
			{@const val = String(opt.value)}
			{@const optId = val ? `${field.id}-${val}` : field.id}
			<Label for={optId} class="flex cursor-pointer items-center gap-2 font-normal">
				<Input
					type="radio"
					id={optId}
					name={field.name}
					value={val}
					checked={current === val}
					disabled={field.isDisabled}
					onchange={() => choose(opt.value)}
					onblur={() => field.blur()}
					onfocus={() => field.focus()}
					class="size-5 w-auto shrink-0 rounded-full border-0 p-0"
				/>
				<span class="text-[0.82rem]">{opt.label}</span>
			</Label>
		{/each}
	</div>
	<FieldMessages {config} {field} />
</div>
