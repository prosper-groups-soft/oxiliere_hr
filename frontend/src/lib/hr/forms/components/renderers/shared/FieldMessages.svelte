<script lang="ts">
	import { slide } from 'svelte/transition';
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';

	let {
		config,
		field,
		extra = null
	}: {
		config: FieldConfig;
		field: FieldInstance;
		extra?: string | null;
	} = $props();
</script>

{#if extra}<p transition:slide={{ duration: 180 }} class="text-muted-foreground overflow-hidden text-[0.82rem]">{extra}</p>{/if}
{#if config.help && field.isValid}<p transition:slide={{ duration: 180 }} class="text-muted-foreground overflow-hidden text-[0.82rem]">{config.help}</p>{/if}
{#if !field.isValid}
	<p transition:slide={{ duration: 200 }} class="text-destructive overflow-hidden text-[0.82rem]" role="alert">
		{field.error}
	</p>
{/if}
