<script lang="ts">
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import Checkbox from '@/components/ui/checkbox/checkbox.svelte';
	import Switch from '@/components/ui/switch/switch.svelte';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	const isSwitch = $derived(config.type === 'switch');
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<div class="flex items-center gap-2">
		{#if isSwitch}
			<Switch
				id={field.id}
				checked={!!field.value}
				disabled={field.isDisabled}
				onCheckedChange={(v) => field.setValue(v)}
			/>
		{:else}
			<Checkbox
				id={field.id}
				checked={!!field.value}
				disabled={field.isDisabled}
				onCheckedChange={(v) => field.setValue(v === true)}
			/>
		{/if}
		<FieldLabel {config} {field} />
	</div>
	<FieldMessages {config} {field} />
</div>



