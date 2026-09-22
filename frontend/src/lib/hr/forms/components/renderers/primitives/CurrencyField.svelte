<script lang="ts">
	// Champ montant en devise : sélecteur de devise + saisie formatée avec
	// séparateurs de milliers (fr-FR). Même pattern visuel que PhoneField :
	// groupe bordé h-9 [devise ⌄ | montant], états focus/erreur/disabled unifiés.
	// Valeur stockée dans le formulaire : { amount: number | null, currency: 'CDF' | 'USD' }.
	// Source des devises : constantes du projet (pas d'endpoint ni de store — principe standalone).
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import { CURRENCIES } from '@/hr/modules/admin/company/types/currency.types';
	import CountryFlag from '@/hr/components/shared/country/CountryFlag.svelte';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	let currency = $state(CURRENCIES.find((c) => c.isPrimary) ?? CURRENCIES[0]);
	let display = $state(''); // montant affiché, groupé par milliers
	let initialized = false;

	/** Affiche 1500000 → "1 500 000" (fr-FR : espace fine en séparateur). */
	const formatter = new Intl.NumberFormat('fr-FR', { maximumFractionDigits: 2 });

	/** Parse la saisie : digits + virgule décimale fr → number. */
	function parseDisplay(raw: string): number | null {
		const cleaned = raw.replace(/[^\d,]/g, '').replace(/,/g, '.');
		if (cleaned === '' || cleaned === '.') return null;
		const n = Number(cleaned);
		return Number.isNaN(n) ? null : n;
	}

	// ── Init : accepte { amount, currency }, un nombre nu, ou une chaîne numérique ──
	$effect(() => {
		if (initialized) return;
		initialized = true;
		const v = field.value as any;
		if (v == null || v === '') return;
		if (typeof v === 'object' && 'amount' in v) {
			if (v.currency) currency = CURRENCIES.find((c) => c.code === v.currency) ?? currency;
			display = v.amount != null ? formatter.format(v.amount) : '';
		} else {
			const n = Number(v);
			display = Number.isNaN(n) ? String(v) : formatter.format(n);
		}
	});

	function emit(amount: number | null) {
		field.setValue({ amount, currency: currency.code });
		config.onInput?.({ amount, currency: currency.code });
	}

	const handleInput = (e: Event) => {
		// Source de vérité = l'événement (pas le binding) : bind:value et oninput
		// écoutent le même évènement, l'ordre n'est pas garanti — relire `display`
		// ici lirait une valeur périmée et écraserait la saisie.
		const raw = (e.currentTarget as HTMLInputElement).value;
		const n = parseDisplay(raw);
		display = n == null ? '' : formatter.format(n);
		emit(n);
	};

	function onCurrencyChange(code: string | undefined) {
		const match = CURRENCIES.find((c) => c.code === code);
		if (!match) return;
		currency = match;
		// Le montant reste identique — seule la devise change
		emit(parseDisplay(display));
	}
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />

	<div
		class="flex h-9 w-full items-stretch overflow-hidden rounded-md border bg-transparent text-sm shadow-xs transition-colors
			{field.isValid ? 'border-input' : 'border-destructive'}
			{field.isDisabled || field.isReadonly ? 'opacity-50' : 'focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/50'}"
	>
		<Select.Root
			type="single"
			value={currency.code}
			onValueChange={onCurrencyChange}
			disabled={field.isDisabled || field.isReadonly}
		>
			<Select.Trigger
				id={field.id}
				class="h-auto w-fit shrink-0 gap-1.5 rounded-none border-0 bg-muted/50 px-3 shadow-none focus:ring-0 [&_svg]:size-3.5"
				aria-label="Devise"
			>
				<CountryFlag code={currency.country} size={20} />
				<span class="font-medium tabular-nums text-sm">{currency.code}</span>
				<span class="text-muted-foreground text-[0.82rem]">{currency.symbol}</span>
			</Select.Trigger>
			<Select.Content class="z-100 w-56">
				{#each CURRENCIES as c (c.code)}
					<Select.Item value={c.code} label={c.name}>
						<span class="flex items-center gap-2">
							<CountryFlag code={c.country} size={20} />
							<span class="flex-1 text-sm">{c.name}</span>
							<span class="text-muted-foreground text-[0.82rem]">{c.symbol}</span>
						</span>
					</Select.Item>
				{/each}
			</Select.Content>
		</Select.Root>

		<div class="my-1.5 w-px bg-border" role="separator"></div>

		<Input
			id={field.id + '-amount'}
			data-field={field.name}
			type="text"
			inputmode="decimal"
			class="min-w-0 flex-1 rounded-none border-0 text-right shadow-none focus-visible:ring-0 focus-visible:border-0 aria-invalid:border-0 aria-invalid:ring-0"
			value={display}
			placeholder={config.placeholder ?? '0'}
			disabled={field.isDisabled}
			readonly={field.isReadonly}
			aria-invalid={!field.isValid}
			oninput={handleInput}
			onblur={() => field.blur()}
			onfocus={() => field.focus()}
		/>
	</div>

	<FieldMessages {config} {field} />
</div>
