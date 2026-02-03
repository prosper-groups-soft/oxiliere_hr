<script lang="ts">
	import { Tabs as TabsPrimitive } from "bits-ui";
	import { cn, type WithElementRef } from "$lib/utils.js";
    import { tv, type VariantProps } from "tailwind-variants";

	const TabsListVariants = tv(
	{
		base: " inline-flex w-full items-center overflow-x-auto",
		variants: {
		variant: {
			default: "gap-2 rounded-lg bg-muted p-1",
			underline: "gap-8 border-b px-1",
		},
		},
		defaultVariants: {
		variant: "default",
		},
	},
	);

	type TabListProps = WithElementRef<
        TabsPrimitive.ListProps &
        VariantProps<typeof TabsListVariants> 
    >
	
	let {
		ref = $bindable(null),
		class: className,
		variant,
		...restProps
	}: TabListProps = $props();
</script>

<TabsPrimitive.List
	bind:ref
	data-slot="tabs-list"
	class={cn(
		TabsListVariants({ variant }),
		className
	)}
	{...restProps}
/>
