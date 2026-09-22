<script lang="ts">
	import Label from '@/components/ui/label/label.svelte';
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';

	let {
		config,
		field,
		class: cls = 'text-[0.82rem] font-medium'
	}: { config: FieldConfig; field: FieldInstance; class?: string } = $props();
</script>

{#if config.label}
	<Label for={field.id} class={cls}>
		{config.label}
		{#if config.required}
			<span class="text-destructive text-sm">*</span>
		{/if}
	</Label>
{/if}
