<script lang="ts">
	import { cn } from "@/utilities/common/css";
  import type { WithElementRef } from "@/utilities/common/types";
	import type { HTMLAttributes } from "svelte/elements";

	let {
		ref = $bindable(null),
		class: className,
		children,
		...restProps
	}: WithElementRef<HTMLAttributes<HTMLTableSectionElement>> = $props();
</script>


<thead
	bind:this={ref}
	data-slot="table-header"
	class={cn("[&_tr]:border-b", className)}
	{...restProps}
>
	{@render children?.()}
</thead>

