<script lang="ts">
	import type OxilereError from '@/utilities/http/errors';
	import { ShieldAlert } from '@lucide/svelte';

	interface Props {
		error: OxilereError;
	}

	let { error }: Props = $props();

	const message =
		typeof error.details === 'object' && error.details && 'detail' in error.details
			? error.details.detail
			: "Vous n'avez pas les permissions nécessaires";
</script>

<div class="flex items-start gap-3">
	<ShieldAlert class="h-5 w-5 shrink-0 text-amber-500" />
	<div class="flex-1 space-y-1">
		<p class="text-sm font-semibold">Accès refusé</p>
		<p class="text-muted-foreground text-xs">{message}</p>
	</div>
</div>

