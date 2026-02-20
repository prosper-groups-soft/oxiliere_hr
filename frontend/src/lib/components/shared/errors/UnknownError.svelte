<script lang="ts">
	import type OxilereError from '@/utilities/http/errors';
	import { cn } from '@/utilities/common/css';

	interface Props {
		error: OxilereError;
		showHomeButton?: boolean;
		showBackButton?: boolean;
		showRetryButton?: boolean;
		backUrl?: string;
		onRetry?: () => void;
		class?: string;
	}

	let {
		error,
		showHomeButton = true,
		showBackButton = false,
		showRetryButton = true,
		backUrl = '/',
		onRetry,
		class: className = ''
	}: Props = $props();

	const title = error.message || 'Une erreur est survenue';
	const message = error.details || "Une erreur inattendue s'est produite. Veuillez réessayer.";
</script>

<div class={cn('flex min-h-[400px] items-center justify-center px-4', className)}>
	<div class="max-w-md text-center">
		<div class="mb-8">
			<svg
				class="mx-auto h-24 w-24 text-gray-400"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="1.5"
					d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
		</div>

		<h1 class="mb-4 text-6xl font-bold text-gray-900">{error.code}</h1>

		<h2 class="mb-3 text-2xl font-semibold text-gray-800">
			{title}
		</h2>

		<p class="mb-8 text-gray-600">
			{message}
		</p>

		{#if showHomeButton || showBackButton || showRetryButton}
			<div class="flex flex-col justify-center gap-3 sm:flex-row">
				{#if showRetryButton && onRetry}
					<button
						onclick={onRetry}
						class="inline-flex items-center justify-center rounded-lg border border-transparent bg-blue-600 px-6 py-3 text-base font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
					>
						<svg class="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
							/>
						</svg>
						Réessayer
					</button>
				{/if}

				{#if showHomeButton}
					<a
						href={backUrl}
						class="inline-flex items-center justify-center rounded-lg border border-transparent bg-blue-600 px-6 py-3 text-base font-medium text-white transition-colors hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
					>
						<svg class="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"
							/>
						</svg>
						Retour à l'accueil
					</a>
				{/if}

				{#if showBackButton}
					<button
						onclick={() => window.history.back()}
						class="inline-flex items-center justify-center rounded-lg border border-gray-300 bg-white px-6 py-3 text-base font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
					>
						Page précédente
					</button>
				{/if}
			</div>
		{/if}
	</div>
</div>

