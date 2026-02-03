<script lang="ts">
	import type OxilereError from '@/utilities/errors';
	import { CircleAlert } from '@lucide/svelte';

	interface Props {
		error: OxilereError;
	}

	let { error }: Props = $props();

	const fieldErrors = Array.isArray(error.details) ? error.details : [];
	const hasMultipleErrors = fieldErrors.length > 1;
</script>

<div class="flex items-start gap-3">
	<CircleAlert class="h-5 w-5 shrink-0 text-orange-500" />
	<div class="flex-1 space-y-1">
		<p class="text-sm font-semibold">Erreur de validation</p>
		{#if fieldErrors.length > 0}
			<div class="space-y-0.5">
				{#each fieldErrors.slice(0, 2) as fieldError}
					<p class="text-muted-foreground text-xs">
						<span class="font-medium">{fieldError.field}:</span>
						{fieldError.message}
					</p>
				{/each}
				{#if fieldErrors.length > 2}
					<p class="text-muted-foreground text-xs italic">
						+{fieldErrors.length - 2} autre{fieldErrors.length - 2 > 1 ? 's' : ''} erreur{fieldErrors.length -
							2 >
						1
							? 's'
							: ''}
					</p>
				{/if}
			</div>
		{:else}
			<p class="text-muted-foreground text-xs">Veuillez vérifier les données saisies</p>
		{/if}
	</div>
</div>
