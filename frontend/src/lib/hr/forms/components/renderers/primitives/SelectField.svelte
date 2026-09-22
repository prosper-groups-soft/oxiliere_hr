<script lang="ts">
	import type { FieldConfig, FieldInstance, FormInstance } from '../../../core/types.js';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import SelectPicker from '../shared/SelectPicker.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';
	import { multiSelectLabel } from '../field-helpers.js';
	import { hasBehavior, getBehaviorConfig } from '../../../core/behaviors.js';
	import { t } from '../../../validation/i18n.js';
	import { createBusinessOptions } from '../business/business-options.svelte.js';

	let { config, field, form }: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	// ── Picker select/combobox/autocomplete : static + function/api/store ──
	// Logique de source (chargement remote, debounce, cascade) déléguée au helper
	// partagé — un select peut porter n'importe quelle DataSource, pas seulement static.
	// svelte-ignore state_referenced_locally
	const biz = createBusinessOptions(config, field, form);

	// Options créées à la volée (behavior creatable) fusionnées dans la liste —
	// doublons exclus (l'item créé est remonté par la liste remote après reload).
	let createdOptions = $state<Array<{ label: string; value: unknown }>>([]);
	const opts = $derived([
		...biz.allOpts,
		...createdOptions.filter((o) => !biz.allOpts.some((r) => String(r.value) === String(o.value)))
	]);
	const isMultiple = $derived(biz.isMultiple);
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const multiVals = $derived(Array.isArray(field.value) ? field.value.map((v) => String(v)) : []);
	const multiLabel = $derived(multiSelectLabel(multiVals, opts));
	// items pour le typeahead natif bits-ui (single uniquement)
	const typeaheadItems = $derived(opts.map((o) => ({ value: String(o.value), label: o.label })));
	// Recherche : demandée via config, naturelle pour combobox/autocomplete, automatique
	// au-delà de 10 options, et toujours active sur source distante (filtre serveur).
	const searchable = $derived(
		(config as any).searchable === true ||
			config.type === 'combobox' ||
			config.type === 'autocomplete' ||
			biz.isRemote ||
			opts.length > 10
	);

	function handleSingle(v: string | undefined) {
		const next = v ?? '';
		field.setValue(next || null);
		config.onChange?.(next || null);
	}

	function handleMulti(v: string[] | undefined) {
		const next = v ?? [];
		field.setValue(next);
		config.onChange?.(next);
	}

	// Behaviors (api §9) rendus par le picker partagé
	const clearable = $derived(hasBehavior(config, 'clearable'));
	const sortable = $derived(hasBehavior(config, 'sortable'));
	// Behavior creatable : options ajoutées à la volée, gardées localement et
	// fusionnées dans la liste. onCreate du behavior (si fourni) peut renvoyer la
	// valeur à stocker (ex: id renvoyé par l'API) — sinon la valeur = le label.
	const creatable = $derived(hasBehavior(config, 'creatable'));
	const creatableCfg = $derived(getBehaviorConfig<{ onCreate?: (v: string) => any; label?: string }>(config, 'creatable'));
	// Échec de onCreate (ex: API indisponible) → message visible, pas de valeur locale.
	let createError = $state('');
	const virtual = $derived(
		hasBehavior(config, 'virtualized') ? (getBehaviorConfig(config, 'virtualized') ?? {}) : undefined
	);
	function handleClear() {
		const empty = isMultiple ? [] : null;
		field.setValue(empty);
		config.onChange?.(empty);
	}

	/** Creatable : ajoute l'option (ou sélectionne l'existante) puis la sélectionne. */
	async function handleCreate(label: string) {
		createError = '';
		const name = label.trim();
		if (!name) return;
		const existing = opts.find((o) => o.label.trim().toLowerCase() === name.toLowerCase());
		if (existing) {
			selectValue(existing.value);
			return;
		}
		if (!creatableCfg?.onCreate) {
			// Pas d' onCreate → valeur locale = le label (création purement cliente).
			createdOptions = [...createdOptions, { label: name, value: name }];
			selectValue(name);
			return;
		}
		try {
			const returned = await creatableCfg.onCreate(name);
			const value = returned != null ? returned : name;
			createdOptions = [...createdOptions, { label: name, value }];
			selectValue(value);
		} catch {
			createError = t('behavior.creatable.error');
		}
	}

	function selectValue(v: unknown) {
		if (isMultiple) {
			const arr = Array.isArray(field.value) ? [...field.value] : [];
			if (!arr.some((x) => String(x) === String(v))) arr.push(v);
			field.setValue(arr);
			config.onChange?.(arr);
		} else {
			field.setValue(v);
			config.onChange?.(v);
		}
	}
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	<SelectPicker
		id={field.id}
		name={field.name}
		multiple={isMultiple}
		options={opts}
		singleValue={singleVal}
		multiValues={multiVals}
		{multiLabel}
		placeholder={config.placeholder ?? 'Sélectionner…'}
		{searchable}
		onSearch={biz.isRemote ? biz.onSearchInput : undefined}
		onOpenChange={(open) => { if (open) biz.ensureLoaded(); else field.blur(); }}
		hasMore={biz.hasMore}
		onLoadMore={biz.loadMore}
		manualLoadText={biz.needsManualLoad ? 'Rechercher' : undefined}
		onManualLoad={biz.manualLoad}
		{clearable}
		onClear={handleClear}
		{sortable}
		creatable={creatable}
		onCreate={creatable ? handleCreate : undefined}
		{virtual}
		disabled={field.isDisabled || biz.loading}
		{typeaheadItems}
		allowDeselect={!config.required}
		onSingle={handleSingle}
		onMulti={handleMulti}
		loading={biz.loading}
	/>
	<FieldMessages {config} {field} />
		{#if createError}
			<p class="text-xs text-destructive">{createError}</p>
		{/if}
	</div>
