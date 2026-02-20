<script lang="ts">
	import type { HTMLAttributes } from "svelte/elements";
	import { cn } from "@/utilities/common/css";
  import type { WithElementRef } from "@/utilities/common/types";

	let {
		ref = $bindable(null),
		class: className,
		children,
		...restProps
	}: WithElementRef<HTMLAttributes<HTMLElement>> = $props();
</script>


<div
	bind:this={ref}
	data-slot="sidebar-footer"
	data-sidebar="footer"
	class={cn("flex flex-col gap-2 p-2", className)}
	{...restProps}
>
	{@render children?.()}
</div>

