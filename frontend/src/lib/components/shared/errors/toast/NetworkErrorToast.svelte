<script lang="ts">
	import type OxilereError from '@/utilities/errors';
	import { WifiOff } from '@lucide/svelte';

	interface Props {
		error: OxilereError;
	}

	let { error }: Props = $props();

	const message =
		typeof error.details === 'object' && error.details && 'detail' in error.details
			? error.details.detail
			: 'Vérifiez votre connexion internet';
</script>

<div class="flex items-start gap-3">
	<WifiOff class="h-5 w-5 shrink-0 text-red-500" />
	<div class="flex-1 space-y-1">
		<p class="text-sm font-semibold">Problème de connexion</p>
		<p class="text-muted-foreground text-xs">{message}</p>
	</div>
</div>
