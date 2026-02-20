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
	data-slot="card-description"
	class={cn("text-muted-foreground text-sm", className)}
	{...restProps}
>
	{@render children?.()}
</div>

