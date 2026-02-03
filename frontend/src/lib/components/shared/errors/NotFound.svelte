<script lang="ts">
	import type OxilereError from '$lib/utilities/errors';
	import { cn } from '@/utils';

	interface Props {
		error: OxilereError;
		showHomeButton?: boolean;
		showBackButton?: boolean;
		class?: string;
		backUrl?: string;
	}

	let {
		error,
		showHomeButton = true,
		showBackButton = true,
		backUrl = '/',
		class: className = ''
	}: Props = $props();

	const title = error.message || 'Page non trouvée';
	const message =
		error.details || "La ressource que vous recherchez n'existe pas ou a été déplacée.";
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
					d="M9.172 16.172a4 4 0 015.656 0M9 10h.01M15 10h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"
				/>
			</svg>
		</div>

		<h1 class="mb-4 text-6xl font-bold text-gray-900">404</h1>

		<h2 class="mb-3 text-2xl font-semibold text-gray-800">
			{title}
		</h2>

		<p class="mb-8 text-gray-600">
			{message}
		</p>

		{#if showHomeButton || showBackButton}
			<div class="flex flex-col justify-center gap-3 sm:flex-row">
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
								d="M10 19l-7-7m0 0l7-7m-7 7h18"
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
