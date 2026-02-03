<script lang="ts">
	import type { WithElementRef } from '$lib/utils';
	import { cn } from '$lib/utils';
	import { FileX } from '@lucide/svelte';
	import type { Component } from 'svelte';
	import type { HTMLAttributes } from 'svelte/elements';

	let {
		title,
		description = 'Aucun enregistrement.',
		icon: Icon = FileX,
		iconSize = 64,
		iconClass = 'text-muted-foreground',
		class: className,
		children
	}: WithElementRef<HTMLAttributes<HTMLDivElement>> & {
		title?: string;
		description?: string;
		icon?: Component;
		iconSize?: number;
		iconClass?: string;
	} = $props();
</script>

<div class={cn('flex h-full flex-col items-center justify-center py-12', className)}>
	<div class="bg-muted/50 mb-6 rounded-full p-2 md:p-6">
		<Icon size={iconSize} class={cn('transition-colors', iconClass)} />
	</div>

	{#if title}
		<h3 class="text-foreground mb-2 text-lg font-semibold">{title}</h3>
	{/if}

	<p class="text-muted-foreground mb-6 max-w-md text-center text-sm">{description}</p>

	{#if children}
		<div class="flex flex-col items-center gap-2">
			{@render children()}
		</div>
	{/if}
</div>
