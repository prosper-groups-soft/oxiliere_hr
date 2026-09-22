<script lang="ts">
	// Champ téléphone dédié : sélecteur d'indicatif international (drapeau flagcdn + code)
	// + saisie nationale formatée selon le pays. La valeur stockée dans le formulaire
	// est le numéro complet E.164 sans espaces (ex: "+243812345678").
	// Source des préfixes : constantes du projet (pas d'endpoint ni de store — principe standalone).
	import type { FieldConfig, FieldInstance } from '../../../core/types.js';
	import * as Select from '@/components/ui/select/index.js';
	import Input from '@/components/ui/input/input.svelte';
	import CountryFlag from '@/hr/components/shared/country/CountryFlag.svelte';
	import { DEFAULT_PREFIX, PHONE_PREFIXES, formatPhoneNumber } from '@/hr/modules/employees/constants/phone-prefixes';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';

	let { config, field }: { config: FieldConfig; field: FieldInstance } = $props();

	let prefix = $state(DEFAULT_PREFIX);
	let national = $state(''); // numéro national affiché (formaté avec espaces)
	let query = $state(''); // recherche dans le menu déroulant
	let initialized = false;

	/** Tri par indicatif décroissant : le parse "+1…" vs "+24…" doit tester les plus longs d'abord. */
	const sortedPrefixes = [...PHONE_PREFIXES].sort((a, b) => b.code.length - a.code.length);

	const filteredPrefixes = $derived(
		query.trim()
			? sortedPrefixes.filter(
					(p) =>
						p.name.toLowerCase().includes(query.trim().toLowerCase()) ||
						p.code.includes(query.trim())
				)
			: sortedPrefixes
	);

	// ── Init : parse la valeur existante ("+243812345678" → préfixe + national) ──
	$effect(() => {
		if (initialized) return;
		initialized = true;
		const v = String(field.value ?? '');
		if (!v) return;
		if (v.startsWith('+')) {
			const match = sortedPrefixes.find((p) => v.startsWith(p.code));
			if (match) {
				prefix = match;
				national = formatPhoneNumber(v.slice(match.code.length), match);
				return;
			}
		}
		// Valeur sans indicatif : formatée avec le préfixe par défaut
		national = formatPhoneNumber(v, prefix);
	});

	function emit(cleaned: string) {
		// Valeur du formulaire : "+243812345678" ou '' si vide
		field.setValue(cleaned ? prefix.code + cleaned : '');
		config.onInput?.(cleaned ? prefix.code + cleaned : '');
	}

	const handleInput = (e: Event) => {
		// Source de vérité = l'événement (pas le binding) : bind:value et oninput
		// écoutent le même évènement, l'ordre n'est pas garanti — relire `national`
		// ici lirait une valeur périmée et écraserait la saisie.
		const raw = (e.currentTarget as HTMLInputElement).value;
		const cleaned = raw.replace(/\D/g, '').slice(0, prefix.maxLength);
		national = formatPhoneNumber(cleaned, prefix);
		emit(cleaned);
	};

	function onPrefixChange(code: string | undefined) {
		const match = PHONE_PREFIXES.find((p) => p.code === code);
		if (!match) return;
		prefix = match;
		query = '';
		// Reformate les chiffres existants avec le nouveau pays, tronque si plus court
		const cleaned = national.replace(/\D/g, '').slice(0, match.maxLength);
		national = formatPhoneNumber(cleaned, match);
		emit(cleaned);
	}
</script>

<div class="grid gap-1.5" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />

	<!-- Groupe visuel unique : [drapeau + indicatif] | [numéro] -->
	<div
		class="flex h-9 w-full items-stretch overflow-hidden rounded-md border bg-transparent text-sm shadow-xs transition-colors
			{field.isValid ? 'border-input' : 'border-destructive'}
			{field.isDisabled || field.isReadonly ? 'opacity-50' : 'focus-within:border-ring focus-within:ring-[3px] focus-within:ring-ring/50'}"
	>
		<Select.Root
			type="single"
			value={prefix.code}
			onValueChange={onPrefixChange}
			disabled={field.isDisabled || field.isReadonly}
		>
			<Select.Trigger
				id={field.id}
				class="h-auto w-fit shrink-0 gap-1.5 rounded-none border-0 bg-muted/50 px-3 shadow-none focus:ring-0 [&_svg]:size-3.5"
				aria-label="Indicatif international"
			>
				<CountryFlag code={prefix.iso} size={20} />
				<span class="tabular-nums text-[0.82rem]">{prefix.code}</span>
			</Select.Trigger>
			<Select.Content class="z-100 max-h-72 w-72 *:data-[slot=select-scroll-up-button]:hidden">
				<!-- Recherche : filtre par nom de pays ou indicatif — collée en haut du menu (sticky),
					le bouton scroll-up est masqué pour ne pas la recouvrir. -->
				<div
					class="sticky top-0 z-10 -mx-1 -mt-1 mb-1 border-b bg-popover p-1.5"
				>
					<Input
						type="text"
						bind:value={query}
						placeholder="Rechercher un pays…"
						class="h-8"
						onkeydown={(e: KeyboardEvent) => e.stopPropagation()}
					/>
				</div>
				{#each filteredPrefixes as p (p.code)}
					<Select.Item value={p.code} label={p.name}>
						<span class="flex items-center gap-2">
							<CountryFlag code={p.iso} size={20} />
							<span class="flex-1 text-sm">{p.name}</span>
							<span class="text-muted-foreground tabular-nums text-[0.82rem]">{p.code}</span>
						</span>
					</Select.Item>
				{:else}
					<p class="px-3 py-4 text-center text-sm text-muted-foreground">Aucun pays trouvé</p>
				{/each}
			</Select.Content>
		</Select.Root>

		<div class="my-1.5 w-px bg-border" role="separator"></div>

		<Input
			id={field.id + '-national'}
			data-field={field.name}
			type="tel"
			inputmode="tel"
			autocomplete="tel-national"
			class="min-w-0 flex-1 rounded-none border-0 shadow-none focus-visible:ring-0 focus-visible:border-0 aria-invalid:border-0 aria-invalid:ring-0"
			value={national}
			placeholder={config.placeholder ?? 'Ex. 812 345 678'}
			maxlength={prefix.maxLength + 4}
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
