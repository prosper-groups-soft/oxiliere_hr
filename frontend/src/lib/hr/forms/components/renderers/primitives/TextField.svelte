<script lang="ts">
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import Input from '@/components/ui/input/input.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';
	import { inputTypeFor } from '../field-helpers.js';
	import { hasBehavior } from '../../../core/behaviors.js';
	import { t } from '../../../validation/i18n.js';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	// email : normalisation (trim + minuscules) + état de validité live discret
	const isEmail = $derived(config.type === 'email');
	const emailValue = $derived(isEmail ? String(field.value ?? '') : '');
	const EMAIL_RE = /^[^\s@]+@[^\s@]+\.[^\s@]{2,}$/;
	// null = pas encore d'avis (champ vide), sinon validité de la saisie
	const emailState = $derived(emailValue === '' ? null : EMAIL_RE.test(emailValue));

	// url : aperçu favicon + domaine sous l'input quand la saisie ressemble à une URL.
	// FieldType n'a pas de type 'url' dédié : le champ reste un text ; on détecte
	// soit un type explicite, soit la présence du validateur url.
	const isUrl = $derived((config.validators ?? []).some((v) => v.type === 'url'));
	const urlDomain = $derived.by(() => {
		if (!isUrl) return null;
		const raw = String(field.value ?? '').trim();
		if (!raw) return null;
		try {
			const u = new URL(raw.includes('://') ? raw : `https://${raw}`);
			if (!u.hostname.includes('.')) return null;
			return u.hostname;
		} catch {
			return null;
		}
	});
	// Behavior clearable (api §9) : bouton × pour effacer la valeur.
	const clearable = $derived(hasBehavior(config, 'clearable'));
	const canClear = $derived(
		clearable && !field.isDisabled && !field.isReadonly && String(field.value ?? '') !== ''
	);
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	<div class="relative">
		<Input
			id={field.id}
			data-field={field.name}
			type={inputTypeFor(config.type)}
			value={field.value ?? ''}
			placeholder={config.placeholder ?? config.help}
			disabled={field.isDisabled}
			readonly={field.isReadonly}
			aria-invalid={!field.isValid}
			class={isEmail || canClear ? 'pr-9' : ''}
			oninput={(e) => {
				let v = (e.target as HTMLInputElement).value;
				if (isEmail) {
					v = v.trim().toLowerCase();
					(e.target as HTMLInputElement).value = v; // reflète la normalisation dans l'input
				}
				field.setValue(v || null);
				config.onInput?.(v || null);
			}}
			onblur={() => field.blur()}
			onfocus={() => field.focus()}
		/>
		{#if canClear}
			<button
				type="button"
				class="absolute right-2 top-1/2 -translate-y-1/2 text-sm text-muted-foreground hover:text-foreground"
				aria-label={t('field.clear')}
				onclick={() => {
					field.setValue(null);
					config.onInput?.(null);
				}}
			>
				×
			</button>
		{:else if isEmail && emailState !== null && !field.isDisabled && !field.isReadonly}
			<AppIcon
				name={emailState ? 'check' : 'alert'}
				size={14}
				class="pointer-events-none absolute right-3 top-1/2 -translate-y-1/2 {emailState
					? 'text-emerald-600 dark:text-emerald-400'
					: 'text-amber-600 dark:text-amber-400'}"
				aria-hidden="true"
			/>
		{/if}
	</div>
	{#if urlDomain && !field.isDisabled && !field.isReadonly}
		<div class="flex items-center gap-1.5 text-xs text-muted-foreground">
			<img
				src="https://icons.duckduckgo.com/ip3/{urlDomain}.ico"
				alt=""
				class="h-4 w-4 rounded-sm"
				onerror={(e) => ((e.currentTarget as HTMLImageElement).style.display = 'none')}
			/>
			<span class="text-sm">{urlDomain}</span>
		</div>
	{/if}
	<FieldMessages {config} {field} />
</div>



