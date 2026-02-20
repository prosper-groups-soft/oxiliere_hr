<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";
	import { cn } from "@/utilities/common/css";
	import type { WithElementRef } from "@/utilities/common/types";

	let {
		ref = $bindable(null),
		class: className,
		children,
		...restProps
	}: WithElementRef<HTMLAttributes<HTMLDivElement>> = $props();
</script>


<div
	bind:this={ref}
	data-slot="card"
	class={cn(
		"bg-card text-card-foreground flex flex-col gap-6 shadow-xs rounded-xl border-0 py-6 border-border",
		className
	)}
	{...restProps}
>
	{@render children?.()}
</div>

