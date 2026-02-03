<script lang="ts">
	import OxilereError from '$lib/utilities/errors';
	import NetworkError from './errors/NetworkError.svelte';
	import NotFound from './errors/NotFound.svelte';
	import NotPermitted from './errors/NotPermitted.svelte';
	import UnknownError from './errors/UnknownError.svelte';
	import ValidationError from './errors/ValidationError.svelte';

	interface Props {
		error: Error;
		showHomeButton?: boolean;
		showBackButton?: boolean;
		showRetryButton?: boolean;
		backUrl?: string;
		class?: string;
		onRetry?: () => void;
		fieldMap?: Record<string, string>;
	}

	let {
		error: error_,
		showHomeButton = false,
		showBackButton = false,
		showRetryButton = false,
		backUrl = '/',
		onRetry,
		fieldMap,
		class: className = ''
	}: Props = $props();

	if (import.meta.env.DEV) {
		console.log(error_);
	}

	const error = $derived(OxilereError.parse(error_));
</script>

{#if error.isValidationError()}
	<ValidationError
		{error}
		{fieldMap}
		{showHomeButton}
		{showBackButton}
		{backUrl}
		class={className}
	/>
{:else if error.isNotFoundError()}
	<NotFound {error} {showHomeButton} {showBackButton} {backUrl} class={className} />
{:else if error.isForbiddenError()}
	<NotPermitted {error} {showHomeButton} {showBackButton} {backUrl} class={className} />
{:else if error.isNetworkError()}
	<NetworkError
		{error}
		{showHomeButton}
		{showBackButton}
		{showRetryButton}
		{backUrl}
		{onRetry}
		class={className}
	/>
{:else}
	<UnknownError
		{error}
		{showHomeButton}
		{showBackButton}
		{showRetryButton}
		{backUrl}
		{onRetry}
		class={className}
	/>
{/if}
