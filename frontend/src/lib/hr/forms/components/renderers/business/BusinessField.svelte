<script lang="ts">
	import type { FieldConfig, FieldInstance, FormInstance } from '../../../core/types.js';
	import FieldLabel from '../shared/FieldLabel.svelte';
	import SelectPicker from '../shared/SelectPicker.svelte';
	import FieldMessages from '../shared/FieldMessages.svelte';
	import { hasBehavior, getBehaviorConfig } from '../../../core/behaviors.js';
	import { multiSelectLabel } from '../field-helpers.js';
	import { t } from '../../../validation/i18n.js';
	import { createBusinessOptions } from './business-options.svelte';

	let { config, field, form }: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	// Rendu + spécificités orgUnit ; source/cascade déléguées à business-options.svelte.ts.
	// svelte-ignore state_referenced_locally
	const biz = createBusinessOptions(config, field, form);

	const isMultiple = $derived(biz.isMultiple);
	const allOpts = $derived(biz.allOpts);
	// Options « créées à la volée » (behavior creatable) — déclaré tôt car
	// fusionné dans tous les dérivés d'affichage ci-dessous.
	let createdOptions = $state<Array<{ label: string; value: unknown }>>([]);
	// Après reload, l'item créé vient du serveur avec le même id — on exclut les
	// doublons pour éviter des clés dupliquées dans les each.
	const extraOpts = $derived(
		createdOptions.filter((o) => !allOpts.some((r) => String(r.value) === String(o.value)))
	);
	const singleVal = $derived(field.value == null ? '' : String(field.value));
	const multiVals = $derived(
		Array.isArray(field.value) ? field.value.map((v) => String(v)) : []
	);
	const multiLabel = $derived(multiSelectLabel(multiVals, allOpts));
	const typeaheadItems = $derived(
		[...allOpts, ...extraOpts].map((o) => ({ value: String(o.value), label: o.label }))
	);

	// `orgUnit` : groupement par type (suffixe « (TYPE) » des labels — OrgUnitType backend)
	const orgGroups = $derived.by(() => {
		if (config.type !== 'orgUnit' || isMultiple) return undefined;
		const groups: Array<{ label: string; options: Array<{ label: string; value: unknown }> }> = [];
		const byType = new Map<string, Array<{ label: string; value: unknown }>>();
		for (const o of [...allOpts, ...extraOpts]) {
			const m = String(o.label).match(/^(.*) \(([A-Z_]+)\)$/);
			const key = m ? m[2] : '';
			const label = m ? m[1] : String(o.label);
			const entry = { label, value: o.value };
			if (!key) continue; // option sans type → liste plate
			if (!byType.has(key)) {
				const g = { label: key.charAt(0) + key.slice(1).toLowerCase(), options: [] };
				byType.set(key, g.options);
				groups.push(g);
			}
			byType.get(key)!.push(entry);
		}
		return groups.length > 0 ? groups : undefined;
	});
	// En mode groupé, le label affiché dans le menu est le nom sans le suffixe « (TYPE) »
	const pickerOptions = $derived(
		orgGroups
			? orgGroups.flatMap((g) => g.options)
			: [...allOpts, ...extraOpts]
	);

	// Behavior creatable (api §9) : options ajoutées à la volée, gardées
	// localement et fusionnées dans la liste. onCreate du behavior (si fourni)
	// peut renvoyer la valeur à stocker (ex: id renvoyé par l'API) — sinon la
	// valeur = le label.
	const creatable = $derived(hasBehavior(config, 'creatable'));
	const creatableCfg = $derived(
		getBehaviorConfig<{ onCreate?: (v: string) => any; label?: string }>(config, 'creatable')
	);
	// Échec de onCreate/onUpdate/onDelete (ex: API indisponible) → message visible.
	let createError = $state('');

	// Behavior manageable : renommage/suppression inline des options (branché sur
	// le CRUD du binding via callbacks — api §9).
	const manageable = $derived(hasBehavior(config, 'manageable'));
	const manageCfg = $derived(
		getBehaviorConfig<{ update?: (id: string, label: string) => Promise<any>; remove?: (id: string) => Promise<any> }>(
			config,
			'manageable'
		)
	);

	/** Renomme l'option : API + rafraîchissement de la liste + label local. */
	async function handleUpdate(id: string, label: string) {
		try {
			await manageCfg?.update?.(id, label);
			createdOptions = createdOptions.map((o) =>
				String(o.value) === id ? { ...o, label } : o
			);
			biz.reload();
		} catch {
			createError = t('behavior.manageable.error');
			throw new Error('update failed');
		}
	}

	/** Supprime l'option : API + rafraîchissement + désélection si nécessaire. */
	async function handleDelete(id: string) {
		try {
			await manageCfg?.remove?.(id);
			createdOptions = createdOptions.filter((o) => String(o.value) !== id);
			if (isMultiple) {
				if (multiVals.includes(id)) handleMulti(multiVals.filter((v) => v !== id));
			} else if (singleVal === id) {
				field.setValue(null);
				config.onChange?.(null);
			}
			biz.reload();
		} catch {
			createError = t('behavior.manageable.error');
			throw new Error('delete failed');
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

	/** Creatable : ajoute l'option (ou sélectionne l'existante) puis la sélectionne. */
	async function handleCreate(label: string) {
		createError = '';
		const name = label.trim();
		if (!name) return;
		const existing = [...biz.allOpts, ...extraOpts].find(
			(o) => o.label.trim().toLowerCase() === name.toLowerCase()
		);
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
		options={pickerOptions}
		groups={orgGroups}
		singleValue={singleVal}
		multiValues={multiVals}
		{multiLabel}
		placeholder={config.placeholder ?? 'Sélectionner…'}
		searchable={config.searchable !== false}
		onSearch={biz.isRemote ? biz.onSearchInput : undefined}
		onOpenChange={(open) => { if (open) biz.ensureLoaded(); else field.blur(); }}
		hasMore={biz.hasMore}
		onLoadMore={biz.loadMore}
		manualLoadText={biz.needsManualLoad ? 'Rechercher' : undefined}
		onManualLoad={biz.manualLoad}
		disabled={field.isDisabled || biz.loading}
		{typeaheadItems}
		allowDeselect={!config.required}
		{creatable}
		onCreate={creatable ? handleCreate : undefined}
		{manageable}
		onUpdate={manageable && manageCfg?.update ? handleUpdate : undefined}
		onDelete={manageable && manageCfg?.remove ? handleDelete : undefined}
		onSingle={handleSingle}
		onMulti={handleMulti}
		loading={biz.loading}
	/>
	<FieldMessages {config} {field} />
		{#if createError}
			<p class="text-xs text-destructive">{createError}</p>
		{/if}
	</div>
