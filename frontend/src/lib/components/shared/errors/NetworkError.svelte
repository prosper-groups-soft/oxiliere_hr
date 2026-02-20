<script lang="ts">
	import type OxilereError from '$lib/utilities/http/errors';
	import { cn } from '@/utilities/common/css';

	interface Props {
		error: OxilereError;
		showHomeButton?: boolean;
		showBackButton?: boolean;
		showRetryButton?: boolean;
		backUrl?: string;
		class?: string;
		onRetry?: () => void;
	}

	let {
		error,
		showHomeButton = false,
		showBackButton = true,
		showRetryButton = true,
		backUrl = '/',
		class: className = '',
		onRetry
	}: Props = $props();

	const title = error.message || 'Erreur de connexion';
	const message =
		error.details || 'Impossible de se connecter au serveur. Vérifiez votre connexion internet.';
</script>

<div class={cn('flex min-h-[400px] items-center justify-center px-4', className)}>
	<div class="max-w-md text-center">
		<div class="mb-8">
			<svg
				class="mx-auto h-24 w-24 text-red-400"
				fill="none"
				viewBox="0 0 24 24"
				stroke="currentColor"
			>
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="1.5"
					d="M18.364 5.636a9 9 0 010 12.728m0 0l-2.829-2.829m2.829 2.829L21 21M15.536 8.464a5 5 0 010 7.072m0 0l-2.829-2.829m-4.243 2.829a4.978 4.978 0 01-1.414-2.83m-1.414 5.658a9 9 0 01-2.167-9.238m7.824 2.167a1 1 0 111.414 1.414m-1.414-1.414L3 3m8.293 8.293l1.414 1.414"
				/>
			</svg>
		</div>

		<h1 class="mb-4 text-6xl font-bold text-gray-900">000</h1>

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
						onclick={() => window.location.reload()}
						class="inline-flex items-center justify-center rounded-lg border border-gray-300 bg-white px-6 py-3 text-base font-medium text-gray-700 transition-colors hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
					>
						<svg class="mr-2 h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
							<path
								stroke-linecap="round"
								stroke-linejoin="round"
								stroke-width="2"
								d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15"
							/>
						</svg>
						Recharger la page
					</button>
				{/if}
			</div>
		{/if}
	</div>
</div>

