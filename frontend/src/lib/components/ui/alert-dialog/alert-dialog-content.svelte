<script lang="ts">
	import { AlertDialog as AlertDialogPrimitive } from "bits-ui";
	import AlertDialogOverlay from "./alert-dialog-overlay.svelte";
	import { cn } from "@/utilities/common/css";
	import { 
    type WithoutChild, 
    type WithoutChildrenOrChild 
  } from "@/utilities/common/types";

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

	<div class="fixed inset-0 z-50 flex items-center justify-center pointer-events-none">
		<AlertDialogPrimitive.Content
			bind:ref
			data-slot="alert-dialog-content"
			class={cn(
				"bg-background grid w-full max-w-[calc(100%-2rem)] gap-4 rounded-lg border p-6 shadow-lg sm:max-w-lg pointer-events-auto",
				"alert-dialog-animate",
				className
			)}
			{...restProps}
		/>
	</div>
</AlertDialogPrimitive.Portal>


<style>
	:global([data-state="open"] .alert-dialog-animate) {
		animation: alert-dialog-in 200ms cubic-bezier(0.16, 1, 0.3, 1);
	}
	:global([data-state="closed"] .alert-dialog-animate) {
		animation: alert-dialog-out 150ms cubic-bezier(0.4, 0, 0.2, 1);
	}

	@keyframes alert-dialog-in {
		from {
			opacity: 0;
			transform: scale(0.95) translateY(-10px);
		}
		to {
			opacity: 1;
			transform: scale(1) translateY(0);
		}
	}

	@keyframes alert-dialog-out {
		from {
			opacity: 1;
			transform: scale(1) translateY(0);
		}
		to {
			opacity: 0;
			transform: scale(0.95) translateY(-10px);
		}
	}
</style>

