<script lang="ts">
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import Textarea from '@/components/ui/textarea/textarea.svelte';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	// Max : config.maxLength explicite ou premier validator maxLength.
	const maxLength = $derived(
		config.maxLength ??
			(config.validators ?? []).find((v: any) => v.type === 'maxLength')?.params?.value ??
			undefined
	);

	const count = $derived(String(field.value ?? '').length);
	const ratio = $derived(maxLength ? count / maxLength : 0);

	// Couleur du compteur : normal → proche de la limite (≥80%) → dépassement
	const counterCls = $derived(
		maxLength && ratio > 1
			? 'text-destructive'
			: maxLength && ratio >= 0.8
				? 'text-amber-600 dark:text-amber-400'
				: 'text-muted-foreground'
	);
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	<Textarea
		id={field.id}
		data-field={field.name}
		value={field.value ?? ''}
		placeholder={config.placeholder}
		maxlength={maxLength}
		disabled={field.isDisabled}
		readonly={field.isReadonly}
		aria-invalid={!field.isValid}
		oninput={(e) => {
			field.setValue((e.target as HTMLTextAreaElement).value);
			config.onInput?.((e.target as HTMLTextAreaElement).value);
		}}
		onblur={() => field.blur()}
		onfocus={() => field.focus()}
	/>
	<!-- Compteur aligné à droite ; devient visible quand le champ a du contenu ou une limite -->
	{#if count > 0 || maxLength}
		<div class="flex justify-end">
			<span class="text-[0.82rem] tabular-nums {counterCls}">
				{count}{maxLength ? ` / ${maxLength}` : ''}
			</span>
		</div>
	{/if}
	<FieldMessages {config} {field} />
</div>
