<script lang="ts">
	import { AlertDialog as AlertDialogPrimitive } from "bits-ui";
	import AlertDialogOverlay from "./alert-dialog-overlay.svelte";
	import { cn } from "@/utilities/common/css";
	import { type WithoutChild, type WithoutChildrenOrChild } from "@/utilities/common/types";

	let {
		ref = $bindable(null),
		class: className,
		portalProps,
		onOutsideClick,
		...restProps
	}: WithoutChild<AlertDialogPrimitive.ContentProps> & {
		portalProps?: WithoutChildrenOrChild<AlertDialogPrimitive.PortalProps>;
		onOutsideClick?: () => void;
	} = $props();
</script>


<AlertDialogPrimitive.Portal {...portalProps}>
	<AlertDialogOverlay onclick={onOutsideClick} />
	
	<AlertDialogPrimitive.Content
		bind:ref
		data-slot="alert-dialog-content"
		class={cn(
			"bg-background fixed left-[50%] top-[50%] z-50 grid w-full max-w-[calc(100%-2rem)] translate-x-[-50%] translate-y-[-50%] gap-4 rounded-lg border p-6 shadow-lg sm:max-w-lg",
			className
		)}
		{...restProps}
	/>
</AlertDialogPrimitive.Portal>


