<script lang="ts">
	import Eye from '@lucide/svelte/icons/eye';
	import EyeOff from '@lucide/svelte/icons/eye-off';
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import Input from '@/components/ui/input/input.svelte';
	import Button from '@/components/ui/button/button.svelte';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	let shown = $state(false);

	const value = $derived(String(field.value ?? ''));

	// ── Force du mot de passe : 4 critères, chacun vaut 1 point ──
	// (masquable via config.showStrength = false)
	const showStrength = $derived((config as any).showStrength !== false);
	const checks = $derived([
		value.length >= 8, // longueur minimale
		value.length >= 12, // longueur renforcée
		/[a-z]/.test(value) && /[A-Z]/.test(value), // casse mixte
		/\d/.test(value) && /[^a-zA-Z0-9]/.test(value) // chiffre + spécial
	]);
	const score = $derived(checks.filter(Boolean).length);

	const strengthLabels = ['Trop faible', 'Faible', 'Moyen', 'Bon', 'Excellent'];
	const strengthLabel = $derived(strengthLabels[score]);

	// Couleur des segments : tous les segments <= score prennent la couleur du niveau
	const barCls = $derived(
		[
			'bg-destructive', // 0 : trop faible (rouge)
			'bg-orange-500', // 1 : faible
			'bg-amber-500', // 2 : moyen
			'bg-yellow-500', // 3 : bon
			'bg-emerald-500' // 4 : excellent
		][score]
	);
	const labelCls = $derived(
		[
			'text-destructive',
			'text-orange-600 dark:text-orange-400',
			'text-amber-600 dark:text-amber-400',
			'text-yellow-600 dark:text-yellow-400',
			'text-emerald-600 dark:text-emerald-400'
		][score]
	);
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	<div class="relative">
		<Input
			id={field.id}
			data-field={field.name}
			type={shown ? 'text' : 'password'}
			value={field.value ?? ''}
			placeholder={config.placeholder ?? config.help}
			disabled={field.isDisabled}
			readonly={field.isReadonly}
			aria-invalid={!field.isValid}
			class="pr-10"
			oninput={(e) => {
				field.setValue((e.target as HTMLInputElement).value);
				config.onInput?.((e.target as HTMLInputElement).value);
			}}
			onblur={() => field.blur()}
			onfocus={() => field.focus()}
		/>
		<Button
			type="button"
			variant="ghost"
			size="icon"
			class="absolute top-1/2 right-1 -translate-y-1/2"
			disabled={field.isDisabled}
			onclick={() => (shown = !shown)}
			aria-label={shown ? 'Masquer le mot de passe' : 'Afficher le mot de passe'}
		>
			{#if shown}<EyeOff class="size-4" />{:else}<Eye class="size-4" />{/if}
		</Button>
	</div>

	<!-- Jauge de force : 4 segments + libellé, visible dès la première saisie -->
	{#if showStrength && value.length > 0}
		<div class="flex items-center gap-2" aria-live="polite">
			<div class="flex flex-1 gap-1">
				{#each Array.from({ length: 4 }, (_, i) => i) as i (i)}
					<div class="h-1 flex-1 rounded-full bg-muted {i < score ? barCls : ''}"></div>
				{/each}
			</div>
			<span class="text-[0.82rem] font-medium {labelCls}">{strengthLabel}</span>
		</div>
	{/if}

	<FieldMessages {config} {field} />
</div>

