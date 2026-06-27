<script lang="ts">
	import type { WithElementRef } from '@/utilities/common/types';
	import { cn } from '@/utilities/common/css';
	import type { HTMLAttributes } from 'svelte/elements';
  import AppIcon from '@/components/layout/elements/AppIcon.svelte';

	let {
		title,
		description = 'Aucun enregistrement.',
		icon = 'file-x',
		iconSize = 30,
		iconClass = 'text-slate-400',
		iconContainerClass = 'bg-slate-50',
		iconStrokeWidth = 1.5,
		class: className,
    	titleSize = "0.91rem",
    	descriptionSize = "0.84rem",
		children
	}: WithElementRef<HTMLAttributes<HTMLDivElement>> & {
		title?: string;
		description?: string;
		icon?: string;
		iconSize?: number;
		iconClass?: string;
		iconContainerClass?: string;
    	titleSize?: string;
    	descriptionSize?: string; 
		iconStrokeWidth?: number;
	} = $props();

	const containerSize = $derived(iconSize + 40);
</script>


<div class={cn('h-full flex flex-col items-center justify-center py-12 px-4 text-center', className)}>
	<div 
		class={cn('rounded-2xl flex items-center justify-center mb-4', iconContainerClass)}
		style="width: {containerSize}px; height: {containerSize}px;"
	>
		<AppIcon 
			name={icon} 
			size={iconSize} 
			strokeWidth={iconStrokeWidth}
			class={cn('transition-colors', iconClass)} 
		/>
	</div>

	{#if title}
		<span class="font-bold text-slate-800 mb-1 text-[{titleSize}]">{title}</span>
	{/if}

	<p class="text-slate-600 max-w-90 text-[{descriptionSize}] leading-relaxed mb-5">{description}</p>

	{#if children}
		<div class="flex flex-col items-center gap-2">
			{@render children()}
		</div>
	{/if}
</div>

