<script lang="ts">
	import { cn } from "@/utilities/common/css";
	import type { WithElementRef } from "@/utilities/common/types";
	import type { HTMLAttributes } from "svelte/elements";

	let {
		ref = $bindable(null),
		class: className,
		inset,
		children,
		...restProps
	}: WithElementRef<HTMLAttributes<HTMLDivElement>> & {
		inset?: boolean;
	} = $props();
</script>


<div
	bind:this={ref}
	data-slot="dropdown-menu-label"
	data-inset={inset}
	class={cn("px-2 py-1.5 text-[0.88rem]! *:[font-size:inherit]! font-semibold data-inset:pl-8", className)}
	{...restProps}
>
	{@render children?.()}
</div>

