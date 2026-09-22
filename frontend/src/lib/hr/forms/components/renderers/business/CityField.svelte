<script lang="ts">
	// Champ ville dédié (Lot D) : cascade sur le(s) champ(s) parent(s) (pays…),
	// tri alphabétique français et état vide explicite « Sélectionnez d'abord : … »
	// tant que le parent est vide. Logique de source/cascade partagée via
	// business-options.svelte.ts. La valeur reste l'identifiant métier de la ville.
	import type { FieldConfig, FieldInstance, FormInstance } from '../../../core/types.js';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import SelectPicker from '../shared/SelectPicker.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';
	import { multiSelectLabel } from '../field-helpers.js';
	import { createBusinessOptions } from './business-options.svelte.js';

	let { config, field, form }: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	// Props stables par instance (config/field ne sont jamais remplacés) : la capture
	// de la valeur initiale est voulue — le helper ne doit s'initialiser qu'une fois.
	// svelte-ignore state_referenced_locally
	const biz = createBusinessOptions(config, field, form);

	const isMultiple = $derived(biz.isMultiple);
	const allOpts = $derived(biz.allOpts);
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const multiVals = $derived(
		Array.isArray(field.value) ? field.value.map((v) => String(v)) : []
	);
	const multiLabel = $derived(multiSelectLabel(multiVals, allOpts));
	const typeaheadItems = $derived(
		allOpts.map((o) => ({ value: String(o.value), label: o.label }))
	);

	// Tri alphabétique français (les sources remote ne garantissent pas l'ordre)
	const sortedOpts = $derived(
		[...allOpts].sort((a, b) => a.label.localeCompare(b.label, 'fr'))
	);

	// État vide explicite quand le champ parent (pays…) n'est pas encore choisi
	const emptyText = $derived(
		sortedOpts.length === 0 && biz.depSourceKeys.length > 0
			? `Sélectionnez d'abord : ${biz.sourceLabels}`
			: 'Aucun résultat'
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
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	<SelectPicker
		id={field.id}
		name={field.name}
		multiple={isMultiple}
		options={sortedOpts}
		singleValue={singleVal}
		multiValues={multiVals}
		{multiLabel}
		placeholder={config.placeholder ?? 'Sélectionner…'}
		searchable
		onSearch={biz.isRemote ? biz.onSearchInput : undefined}
		onOpenChange={(open) => { if (open) biz.ensureLoaded(); else field.blur(); }}
		hasMore={biz.hasMore}
		onLoadMore={biz.loadMore}
		manualLoadText={biz.needsManualLoad ? 'Rechercher' : undefined}
		onManualLoad={biz.manualLoad}
		emptyText={emptyText}
		disabled={field.isDisabled || biz.loading}
		{typeaheadItems}
		allowDeselect={!config.required}
		onSingle={handleSingle}
		onMulti={handleMulti}
		loading={biz.loading}
	/>
	<FieldMessages {config} {field} />
</div>

