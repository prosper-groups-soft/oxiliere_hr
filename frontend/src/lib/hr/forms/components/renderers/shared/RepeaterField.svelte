<script lang="ts">
	// Behavior repeater (api §9, semantics §7) : le champ porte un tableau de
	// valeurs ; un item par élément, borné par min/max, réordonnable si sortable.
	// Chaque item est rendu par le dispatcher standard via un FieldInstance proxy
	// dont value/setValue écrivent l'index du tableau — les validateurs et le
	// payload restent gérés par le moteur (createForm).
	import type { BehaviorConfig, FieldConfig, FieldInstance, FormConfig, FormInstance, LayoutConfig, RepeaterConfig } from '../../../core/types.js';
	import FieldLabel from './FieldLabel.svelte';
	import FieldMessages from './FieldMessages.svelte';
	import FieldRenderer from '../FieldRenderer.svelte';
	import LayoutRenderer from '../../layouts/LayoutRenderer.svelte';
	import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
	import { repeaterBounds, repeaterSubFields, isRepeaterItemEmpty, withoutRepeaterBehavior } from '../field-helpers.js';
	import { repeaterConfigOf } from '../../../core/behaviors.js';
	import { t } from '../../../validation/i18n.js';
	import { slide } from 'svelte/transition';

	/** Durée (ms) de l'animation plier/déplier des items group. */
	const COLLAPSE_MS = 200;

	let {
		config,
		field,
		form
	}: { config: FieldConfig; field: FieldInstance; form?: FormInstance<any> } = $props();

	const items = $derived(Array.isArray(field.value) ? (field.value as any[]) : []);
	const bounds = $derived(repeaterBounds(config));
	const subFields = $derived(repeaterSubFields(config));
	const isGroup = $derived(subFields.length > 0);
	/** Layout optionnel du sous-formulaire d'item (`behaviors.repeater({ layout })`). */
	const itemLayout = $derived(repeaterConfigOf(config).layout);
	const atMin = $derived(items.length <= bounds.min);
	const atMax = $derived(items.length >= bounds.max);

	// ── Pliable : index → déplié ? Défaut : déplié ; un item ajouté est déplié. ──
	let expandedByIndex = $state<Record<number, boolean>>({});
	function isExpanded(i: number): boolean {
		return expandedByIndex[i] ?? true;
	}
	function toggleItem(i: number) {
		expandedByIndex = { ...expandedByIndex, [i]: !isExpanded(i) };
	}

	function setItems(next: any[]) {
		field.setValue(next);
		config.onChange?.(next);
	}

	/** Item vide conforme aux subFields (defaults) — pour « Ajouter » en mode group. */
	function emptyGroupItem(): Record<string, any> {
		return Object.fromEntries(
			subFields.map((sf) => [fieldKeyOf(sf), (sf as { defaultValue?: any }).defaultValue ?? null])
		);
	}

	function addItem() {
		if (atMax) return;
		setItems([...items, isGroup ? emptyGroupItem() : null]);
		expandedByIndex = { ...expandedByIndex, [items.length]: true }; // nouveau → déplié
	}

	function removeItem(i: number) {
		if (atMin) return;
		const next = [...items];
		next.splice(i, 1);
		setItems(next);
		// Compacte l'état pliable (les index se décalent)
		const shifted: Record<number, boolean> = {};
		for (const [k, v] of Object.entries(expandedByIndex)) {
			const ki = Number(k);
			if (ki < i) shifted[ki] = v;
			else if (ki > i) shifted[ki - 1] = v;
		}
		expandedByIndex = shifted;
	}

	function moveItem(i: number, dir: -1 | 1) {
		const j = i + dir;
		if (j < 0 || j >= items.length) return;
		const next = [...items];
		[next[i], next[j]] = [next[j], next[i]];
		setItems(next);
		// L'état pliable suit l'item déplacé
		const ei = expandedByIndex[i], ej = expandedByIndex[j];
		expandedByIndex = { ...expandedByIndex, [i]: ej ?? true, [j]: ei ?? true };
	}

	// fieldKey local (createForm n'est pas importé ici pour éviter un cycle)
	function fieldKeyOf(f: Pick<FieldConfig, 'id' | 'name'>): string {
		return (f as { name?: string }).name ?? f.id;
	}

	/** Résumé plié d'un item : « Label: valeur · Label: valeur » (valeurs vides → —). */
	function itemSummary(item: any): string {
		if (!isGroup) return item == null ? '' : String(item);
		return subFields
			.map((sf) => {
				const k = fieldKeyOf(sf);
				const v = item != null && typeof item === 'object' ? item[k] : undefined;
				const label = sf.label ?? k;
				return `${label}: ${v == null || v === '' ? '—' : String(v)}`;
			})
			.join(' · ');
	}

	/** FieldInstance proxy pour l'item i : value ↔ items[i] (scalaire) ou
	 * items[i][subKey] (group repeater). Error/isValid sont neutralisés — la
	 * remontée d'erreur est faite une fois au niveau du repeater. Pas de
	 * délégation focus/blur : field.focus() du moteur fait un querySelector sur
	 * data-field → retomberait sur le PREMIER item et volerait le focus. */
	function itemField(i: number, sub?: FieldConfig): FieldInstance {
		const key = sub ? (sub as { name?: string }).name ?? sub.id : undefined;
		const subConfig = sub ? withoutRepeaterBehavior(sub) : undefined;
		return {
			get id() {
				return sub ? `${field.id}-item-${i + 1}-${sub.id}` : `${field.id}-item-${i + 1}`;
			},
			get name() {
				return sub ? `${field.name}.${key}` : field.name;
			},
			get type() {
				return sub ? subConfig!.type : field.type;
			},
			get value() {
				const arr = field.value;
				if (!Array.isArray(arr)) return null;
				const item = arr[i];
				return key ? (item != null && typeof item === 'object' ? (item[key] ?? null) : null) : (item ?? null);
			},
			get initialValue() {
				const arr = field.initialValue;
				if (!Array.isArray(arr)) return null;
				const item = arr[i];
				return key ? (item != null && typeof item === 'object' ? (item[key] ?? null) : null) : (item ?? null);
			},
			get error() {
				return null;
			},
			get isValid() {
				return true;
			},
			get isDirty() {
				return field.isDirty;
			},
			get isTouched() {
				return field.isTouched;
			},
			get isLoading() {
				return field.isLoading;
			},
			get isFocused() {
				return field.isFocused;
			},
			get isDisabled() {
				return field.isDisabled;
			},
			get isReadonly() {
				return field.isReadonly;
			},
			get isVisible() {
				return field.isVisible;
			},
			get isRequired() {
				return sub ? subConfig!.required === true : field.isRequired;
			},
			setValue(v: any) {
				const arr = Array.isArray(field.value) ? [...(field.value as any[])] : [];
				if (key) {
					const item = arr[i] != null && typeof arr[i] === 'object' ? { ...arr[i] } : {};
					item[key] = v;
					arr[i] = item;
				} else {
					arr[i] = v;
				}
				setItems(arr);
			},
			setError() {},
			setDisabled() {},
			setReadonly() {},
			setVisible() {},
			// Pas de délégation : field.focus() du moteur fait un
			// querySelector('[data-field=…]') → retomberait sur le PREMIER item
			// (tous les items partagent le data-field du champ) et volerait le focus.
			focus() {},
			blur() {},
			reset() {},
			validate() {
				return Promise.resolve(true);
			},
			onChange() {
				return () => {};
			}
		} as unknown as FieldInstance;
	}

	/** Config d'item scalaire : sans label/help (rendus une fois au niveau
	 * repeater) et sans le behavior repeater (anti-récursion). Les autres
	 * behaviors (clearable, multiSelect…) restent actifs sur l'item. */
	function itemConfig(): FieldConfig {
		return { ...withoutRepeaterBehavior(config), label: undefined, help: undefined } as FieldConfig;
	}

	/** Proxys des subFields de l'item i, indexés par fieldKey — pour le layout. */
	function itemSubProxies(i: number): Record<string, FieldInstance> {
		const map: Record<string, FieldInstance> = {};
		for (const sf of subFields) map[fieldKeyOf(sf)] = itemField(i, sf);
		return map;
	}

	/** Shim `FormInstance` pour LayoutRenderer par item : getField → proxys,
	 * getConfig → config du formulaire réel (utilisé par les dépendances des
	 * subFields, ex: labels de cascade). Le reste n'est pas utilisé par les
	 * layouts simples (row/column/group/section/card). */
	function shimForm(proxies: Record<string, FieldInstance>): FormInstance<any> {
		return {
			getField: (k: string) => proxies[k],
			getConfig: () => (form ? form.getConfig() : { fields: [] }) as FormConfig<any>,
			values: {},
			fields: []
		} as unknown as FormInstance<any>;
	}
</script>

<div class="grid gap-1.5 text-sm" data-field-wrapper={field.name}>
	<FieldLabel {config} {field} />
	<div class="grid gap-2" role="list" aria-label={config.label ?? field.name}>
		{#each items as _, i (i)}
			{@const item = itemField(i)}
			{@const itemCfg = itemConfig()}
		{#if isGroup}
			<div
				class="rounded-md border bg-muted/30"
				role="listitem"
				aria-label={t('behavior.repeater.item', { index: i + 1, total: items.length })}
			>
				<div class="flex items-center gap-2 p-3">
					<button
						type="button"
						class="flex min-w-0 flex-1 items-center gap-2 text-left"
						onclick={() => toggleItem(i)}
						aria-expanded={isExpanded(i)}
					>
						<AppIcon
							name="chevron-down"
							size={14}
							class="shrink-0 text-muted-foreground transition-transform duration-200 {isExpanded(i) ? '' : '-rotate-90'}"
						/>
						<div class="min-w-0 flex-1">
							<span class="block text-xs font-medium text-muted-foreground">
								{t('behavior.repeater.item', { index: i + 1, total: items.length })}
							</span>
							{#if !isExpanded(i)}
								<span class="block truncate text-sm">{itemSummary(items[i])}</span>
							{/if}
						</div>
					</button>
					<div class="flex shrink-0 items-center gap-1">
						{#if bounds.sortable && items.length > 1}
							<button
								type="button"
								class="flex h-7 w-7 items-center justify-center rounded-md border text-muted-foreground hover:bg-accent hover:text-foreground disabled:opacity-40"
								aria-label={t('behavior.repeater.moveUp')}
								disabled={i === 0}
								onclick={(e) => { e.stopPropagation(); moveItem(i, -1); }}
							>
								<AppIcon name="arrow-up" size={14} />
							</button>
							<button
								type="button"
								class="flex h-7 w-7 items-center justify-center rounded-md border text-muted-foreground hover:bg-accent hover:text-foreground disabled:opacity-40"
								aria-label={t('behavior.repeater.moveDown')}
								disabled={i === items.length - 1}
								onclick={(e) => { e.stopPropagation(); moveItem(i, 1); }}
							>
								<AppIcon name="arrow-down" size={14} />
							</button>
						{/if}
						{#if !atMin}
							<button
								type="button"
								class="flex h-7 w-7 items-center justify-center rounded-md border text-muted-foreground hover:bg-accent hover:text-destructive"
								aria-label={t('behavior.repeater.remove')}
								onclick={(e) => { e.stopPropagation(); removeItem(i); }}
							>
								<AppIcon name="x" size={14} />
							</button>
						{/if}
					</div>
				</div>
				{#if isExpanded(i)}
					<div
						class="overflow-hidden"
						transition:slide={{ duration: COLLAPSE_MS }}
					>
						<div class="p-3 pt-0">
						{#if itemLayout}
							{@const proxies = itemSubProxies(i)}
							<LayoutRenderer form={shimForm(proxies)} fields={subFields} layout={itemLayout} />
						{:else}
							<div class="grid gap-3 sm:grid-cols-2">
								{#each subFields as sf (sf.id)}
									{@const subFieldProxy = itemField(i, sf)}
									{@const subCfg = withoutRepeaterBehavior(sf)}
									<FieldRenderer config={subCfg} field={subFieldProxy} {form} />
								{/each}
							</div>
						{/if}
						</div>
					</div>
				{/if}
			</div>
		{:else}
				<div
					class="flex items-center gap-2"
					role="listitem"
					aria-label={t('behavior.repeater.item', { index: i + 1, total: items.length })}
				>
					<span
						class="w-5 shrink-0 pt-2 text-right text-xs text-muted-foreground"
						aria-hidden="true"
					>
						{i + 1}
					</span>
					<div class="min-w-0 flex-1">
						<FieldRenderer config={itemCfg} field={item} {form} />
					</div>
					<div class="flex shrink-0 items-center gap-1 self-end">
						{#if bounds.sortable && items.length > 1}
							<button
								type="button"
								class="flex h-9 w-9 items-center justify-center rounded-md border text-muted-foreground hover:bg-accent hover:text-foreground disabled:opacity-40"
								aria-label={t('behavior.repeater.moveUp')}
								disabled={i === 0}
								onclick={() => moveItem(i, -1)}
							>
								<AppIcon name="arrow-up" size={14} />
							</button>
							<button
								type="button"
								class="flex h-9 w-9 items-center justify-center rounded-md border text-muted-foreground hover:bg-accent hover:text-foreground disabled:opacity-40"
								aria-label={t('behavior.repeater.moveDown')}
								disabled={i === items.length - 1}
								onclick={() => moveItem(i, 1)}
							>
								<AppIcon name="arrow-down" size={14} />
							</button>
						{/if}
						{#if !atMin}
							<button
								type="button"
								class="flex h-9 w-9 items-center justify-center rounded-md border text-muted-foreground hover:bg-accent hover:text-destructive"
								aria-label={t('behavior.repeater.remove')}
								onclick={() => removeItem(i)}
							>
								<AppIcon name="x" size={14} />
							</button>
						{/if}
					</div>
				</div>
			{/if}
		{/each}
	</div>
	{#if !atMax && !field.isDisabled && !field.isReadonly}
		<button
			type="button"
			class="group flex w-full items-center justify-center gap-2 rounded-md border border-dashed border-border py-1.5 text-xs font-medium text-muted-foreground transition-colors hover:border-primary/40 hover:bg-accent/50 hover:text-foreground"
			onclick={addItem}
		>
			<AppIcon
				name="plus"
				size={14}
				class="rounded-full border border-current p-0.5 text-current transition-transform"
			/>
			{config.behaviors?.find((b) => b.type === 'repeater')?.config?.addItemLabel ??
				t('behavior.repeater.add')}
		</button>
	{/if}
	<FieldMessages {config} {field} />
</div>
