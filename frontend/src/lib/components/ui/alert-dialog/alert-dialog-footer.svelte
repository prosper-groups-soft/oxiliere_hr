<script lang="ts">
	import { cn } from "@/utilities/common/css";
	import type { HTMLAttributes } from "svelte/elements";
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
	data-slot="alert-dialog-footer"
	class={cn("flex flex-col-reverse gap-2 sm:flex-row sm:justify-end", className)}
	{...restProps}
>
	{@render children?.()}
</div>

