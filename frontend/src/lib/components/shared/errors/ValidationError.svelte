<script lang="ts">
	import type OxilereError from '$lib/utilities/errors';
	import type { FieldError } from '$lib/utilities/errors';
	import { cn } from '@/utils';

	interface Props {
		error: OxilereError;
		fieldMap?: Record<string, string>;
		showHomeButton?: boolean;
		showBackButton?: boolean;
		backUrl?: string;
		class?: string;
	}

	let {
		error,
		fieldMap,
		showHomeButton = false,
		showBackButton = false,
		backUrl = '/',
		class: className = ''
	}: Props = $props();

	const errors: FieldError[] = $derived(
		fieldMap && Array.isArray(error.details)
			? error.mappedErrors(fieldMap)
			: Array.isArray(error.details)
				? error.details
				: []
	);

	const title = 'Erreur de validation';
	const message = 'Veuillez corriger les erreurs suivantes :';
</script>

<div class={cn('rounded-lg border border-red-200 bg-red-50 p-6', className)}>
	<div class="flex items-start">
		<div class="shrink-0">
			<svg class="h-6 w-6 text-red-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
				<path
					stroke-linecap="round"
					stroke-linejoin="round"
					stroke-width="2"
					d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"
				/>
			</svg>
		</div>

		<div class="ml-3 flex-1">
			<h3 class="text-base font-semibold text-red-800">
				{title}
			</h3>

			<p class="mt-1 text-sm text-red-700">
				{message}
			</p>

			{#if errors.length > 0}
				<ul class="mt-4 space-y-2">
					{#each errors as fieldError}
						<li class="flex items-start text-sm text-red-700">
							<svg
								class="mr-2 mt-0.5 h-4 w-4 shrink-0 text-red-400"
								fill="currentColor"
								viewBox="0 0 20 20"
							>
								<path
									fill-rule="evenodd"
									d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z"
									clip-rule="evenodd"
								/>
							</svg>
							<span>
								{#if fieldError.field}
									<strong class="font-medium">{fieldError.field}:</strong>
								{/if}
								{fieldError.message}
							</span>
						</li>
					{/each}
				</ul>
			{/if}

			{#if showHomeButton || showBackButton}
				<div class="mt-6 flex flex-col justify-center gap-3 sm:flex-row">
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
</div>
