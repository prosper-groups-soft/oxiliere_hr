<script lang="ts">
	import { cn } from "@/utilities/common/css";
  import type { WithElementRef } from "@/utilities/common/types";
	import type { HTMLThAttributes } from "svelte/elements";

	let {
		ref = $bindable(null),
		class: className,
		children,
		...restProps
	}: WithElementRef<HTMLThAttributes> = $props();
</script>


<th
	bind:this={ref}
	data-slot="table-head"
	class={cn(
		"text-foreground h-10 whitespace-nowrap bg-clip-padding px-2 text-left align-middle font-medium [&:has([role=checkbox])]:pe-0",
		className
	)}
	{...restProps}
>
	{@render children?.()}
</th>

