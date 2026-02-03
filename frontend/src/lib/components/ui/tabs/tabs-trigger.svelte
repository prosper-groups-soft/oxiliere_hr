<script lang="ts">
	import { Tabs as TabsPrimitive } from "bits-ui";
	import { cn, type WithElementRef } from "$lib/utils.js";
    import { tv, type VariantProps } from "tailwind-variants";


	const TabsTriggerVariants = tv(
		{
			base: "inline-flex items-center whitespace-nowrap transition-all disabled:pointer-events-none",
			variants: {
				variant: {
					default:
					"comet-body-s-accented justify-center rounded-md bg-transparent p-2 ring-offset-background hover:text-foreground-secondary focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 data-[state=active]:bg-primary data-[state=active]:text-primary-foreground data-[state=active]:hover:bg-primary-hover data-[state=active]:hover:text-primary-foreground",
					underline:
					"comet-body-s-accented border-b-2 border-transparent py-2 hover:text-foreground-secondary data-[state=active]:border-primary data-[state=active]:text-primary hover:data-[state=active]:text-primary-hover",
				},
				size: {
					default: "",
					sm: " text-xs",
					lg: "",
					icon: "size-9",
				},
			},
			defaultVariants: {
				variant: "default",
				size: "default",
			},
		},
	);

	type TabTriggerProps = WithElementRef<
        TabsPrimitive.TriggerProps &
        VariantProps<typeof TabsTriggerVariants> 
    >

	let {
		ref = $bindable(null),
		class: className,
		variant,
		size,
		...restProps
	}: TabTriggerProps = $props();
</script>

<TabsPrimitive.Trigger
	bind:ref
	data-slot="tabs-trigger"
	class={cn(
		TabsTriggerVariants({ variant, size }),
		className
	)}
	{...restProps}
/>
