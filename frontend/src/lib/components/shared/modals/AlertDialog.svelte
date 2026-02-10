<script lang="ts" module>
	import { tv, type VariantProps } from 'tailwind-variants';

	export const alertDialogVariants = tv({
		slots: {
			iconContainer: 'flex h-12 w-12 flex-shrink-0 items-center justify-center rounded-full',
			icon: 'h-6 w-6',
			confirmButton:
				'inline-flex w-full justify-center rounded-md px-3 py-2 text-sm font-semibold shadow-sm sm:w-auto disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
		},
		variants: {
			type: {
				info: {
					iconContainer: 'bg-blue-100',
					icon: 'text-blue-600',
					confirmButton: 'bg-blue-600 hover:bg-blue-700 text-white focus-visible:ring-blue-500'
				},
				danger: {
					iconContainer: 'bg-red-100',
					icon: 'text-red-600',
					confirmButton: 'bg-red-600 hover:bg-red-700 text-white focus-visible:ring-red-500'
				},
				warning: {
					iconContainer: 'bg-amber-100',
					icon: 'text-amber-600',
					confirmButton: 'bg-amber-600 hover:bg-amber-700 text-white focus-visible:ring-amber-500'
				},
				success: {
					iconContainer: 'bg-green-100',
					icon: 'text-green-600',
					confirmButton: 'bg-green-600 hover:bg-green-700 text-white focus-visible:ring-green-500'
				}
			}
		},
		defaultVariants: {
			type: 'info'
		}
	});

	export type AlertDialogVariant = VariantProps<typeof alertDialogVariants>['type'];
</script>

<script lang="ts">
	import * as AlertDialog from '$lib/components/ui/alert-dialog/index.js';
	import { Spinner } from '$lib/components/ui/spinner/index.js';
	import { isPromise } from '$lib/utilities/common/func';
	import { cn } from '@/utils';
	import { CircleAlert, CircleCheck, Info, TriangleAlert } from '@lucide/svelte';

	interface Props {
		title: string;
		message: string;
		type: AlertDialogVariant;
		isOpen: boolean;
		show_icon?: boolean;
		onYes?: (() => void) | (() => Promise<any>);
		onNo?: (() => void) | (() => Promise<any>);
		yesText?: string;
		noText?: string;
		showCancel?: boolean;
		class?: string;
	}

	let {
		title,
		message,
		type = 'info',
		isOpen = $bindable(false),
		show_icon = true,
		onYes,
		onNo,
		yesText = 'Confirm',
		noText = 'Cancel',
		showCancel = true,
		class: className = ''
	}: Props = $props();

	let loading = $state(false);

	// Icon mapping based on type
	const iconMap = {
		info: Info,
		danger: CircleAlert,
		warning: TriangleAlert,
		success: CircleCheck
	};

	const IconComponent = iconMap[type];
	const variants = alertDialogVariants({ type });

	function closeModal() {
		isOpen = false;
	}

	async function handleYes() {
		if (!onYes) return;

		const result = onYes();
		if (isPromise(result)) {
			loading = true;
			try {
				await result;
				closeModal();
			} finally {
				loading = false;
			}
		} else {
			closeModal();
		}
	}

	async function handleNo() {
		if (onNo) {
			const result = onNo();
			if (isPromise(result)) {
				loading = true;
				try {
					await result;
				} finally {
					loading = false;
				}
			}
		}
		closeModal();
	}
</script>

<AlertDialog.Root bind:open={isOpen}>
	<AlertDialog.Content class={cn('z-50 sm:max-w-lg', className)}>
		<AlertDialog.Header>
			<div class="flex items-start space-x-4">
				{#if show_icon}
					<div class={variants.iconContainer()}>
						<IconComponent class={variants.icon()} />
					</div>
				{/if}

				<div class="min-w-0 flex-1">
					<AlertDialog.Title class="text-lg font-semibold text-gray-900">
						{title}
					</AlertDialog.Title>
					<AlertDialog.Description class="mt-2 text-sm text-gray-600">
						{message}
					</AlertDialog.Description>
				</div>
			</div>
		</AlertDialog.Header>

		<AlertDialog.Footer
			class="flex flex-col-reverse space-y-2 space-y-reverse sm:flex-row sm:justify-end sm:space-x-2 sm:space-y-0"
		>
			{#if showCancel}
				<button
					type="button"
					class="inline-flex w-full justify-center rounded-md bg-white px-3 py-2 text-sm font-semibold text-gray-900 shadow-sm ring-1 ring-inset ring-gray-300 transition-colors hover:bg-gray-50 focus-visible:ring-2 focus-visible:ring-gray-500 disabled:cursor-not-allowed disabled:opacity-50 sm:w-auto"
					onclick={handleNo}
					disabled={loading}
				>
					{noText}
				</button>
			{/if}

			{#if onYes}
				<button
					type="button"
					class={variants.confirmButton()}
					onclick={handleYes}
					disabled={loading}
				>
					{#if loading}
						<Spinner size="small" class="mr-2 text-current" />
					{/if}
					{yesText}
				</button>
			{/if}
		</AlertDialog.Footer>
	</AlertDialog.Content>
</AlertDialog.Root>

