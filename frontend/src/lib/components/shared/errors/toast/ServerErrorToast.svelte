<script lang="ts">
	import type OxilereError from '@/utilities/errors';
	import { ServerCrash } from '@lucide/svelte';

	interface Props {
		error: OxilereError;
	}

	let { error }: Props = $props();

	const message =
		typeof error.details === 'object' && error.details && 'detail' in error.details
			? error.details.detail
			: 'Une erreur serveur est survenue';
</script>

<div class="flex items-start gap-3">
	<ServerCrash class="h-5 w-5 shrink-0 text-red-500" />
	<div class="flex-1 space-y-1">
		<p class="text-sm font-semibold">Erreur serveur</p>
		<p class="text-muted-foreground text-xs">{message}</p>
	</div>
</div>
