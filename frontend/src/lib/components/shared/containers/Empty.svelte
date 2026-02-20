<script lang="ts">
	import type { WithElementRef } from '@/utilities/common/types';
	import { cn } from '@/utilities/common/css';
	import type { HTMLAttributes } from 'svelte/elements';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';

	let {
		title,
		description = 'Aucun enregistrement.',
		icon = 'file-x',
		iconSize = 32,
		iconClass = 'text-slate-400',
		class: className,
		children
	}: WithElementRef<HTMLAttributes<HTMLDivElement>> & {
		title?: string;
		description?: string;
		icon?: string;
		iconSize?: number;
		iconClass?: string;
	} = $props();
</script>


<div class={cn('h-full flex flex-col items-center justify-center py-12 px-4 text-center border border-slate-100 rounded-2xl bg-slate-50/50', className)}>
	<div class="h-17 w-17 rounded-full bg-slate-100 flex items-center justify-center mb-6">
		<AppIcon name={icon} size={iconSize} class={cn('transition-colors', iconClass)} />
	</div>

	{#if title}
		<h3 class="text-xl font-bold text-slate-800 mb-2">{title}</h3>
	{/if}

	<p class="text-slate-600 max-w-90 text-sm leading-relaxed mb-7">{description}</p>

	{#if children}
		<div class="flex flex-col items-center gap-2">
			{@render children()}
		</div>
	{/if}
</div>

