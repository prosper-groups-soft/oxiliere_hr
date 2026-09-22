<script lang="ts">
	import type { ActionConfig, FieldConfig, FormInstance, LayoutConfig, FormHostConfig } from '../../core/types.js';
	import { untrack } from 'svelte';
	import { fieldKey } from '../../core/createForm.svelte.js';
	import { runAction, requiresConfirm, confirmMessage, matchesShortcut } from '../../actions/actions.js';
	import { t } from '../../validation/i18n.js';
	import { notification } from '@/hr/stores/notification.svelte';
	import FieldRenderer from '../renderers/FieldRenderer.svelte';
	import LayoutRenderer from '../layouts/LayoutRenderer.svelte';
	import FormHost from './FormHost.svelte';
import type { Snippet } from 'svelte';
import Button from '@/components/ui/button/button.svelte';
import AppIcon from '@/hr/components/layout/elements/AppIcon.svelte';
import AnimateSpin from '@/hr/components/layout/elements/AnimateSpin.svelte';

	let {
		form,
		fields,
		actions = [],
		submitLabel = 'Soumettre',
		submitIcon,
		resetIcon,
		showReset = true,
		showSubmit = true,
		layout,
		host,
		title,
		description,
		/** Entité métier réactive : à l'ouverture de l'hôte overlay, le form est
		 * hydraté avec entity (setValues, clés = fieldKey) ; à la fermeture il
		 * est réinitialisé (defaults). Sans entity : reset à la fermeture seule.
		 * (semantics §2 : l'hôte gère hydratation/réinitialisation à l'ouverture.)
		 * La config `entity` de createForm reste l'hydratation initiale à la
		 * création (avec parse du registre). */
		entity = undefined,
		/** État d'ouverture de l'hôte overlay (bindé vers FormHost) — closeOnSubmit. */
		open = $bindable(true)
	}: {
		form: FormInstance<any>;
		fields: FieldConfig[];
		actions?: ActionConfig[];
		submitLabel?: string;
		/** Icône (AppIcon) affichée avant le label du bouton submit. */
		submitIcon?: string;
		/** Icône (AppIcon) affichée avant le label du bouton Réinitialiser. */
		resetIcon?: string;
		showReset?: boolean;
		showSubmit?: boolean;
		layout?: LayoutConfig;
		host?: FormHostConfig;
		title?: string;
		description?: string;
		entity?: Record<string, any> | null;
		/** État d'ouverture de l'hôte overlay (bindé vers FormHost) — closeOnSubmit. */
		open?: boolean;
		extras?: Snippet;
	} = $props();

	// Choix 3 : layout/host lus depuis la config, prop explicite = override.
	const cfg = $derived(form.getConfig());
	const effLayout = $derived(layout ?? cfg.layout);
	const effHost = $derived(host ?? cfg.host);
	const effTitle = $derived(title ?? cfg.title);
	const effDescription = $derived(description ?? cfg.description);
	const effActions = $derived(actions.length ? actions : (cfg.actions ?? []));

	function collectKeys(node: LayoutConfig, acc = new Set<string>()): Set<string> {
		switch (node.type) {
			case 'row': for (const c of node.columns) for (const k of c.fields) acc.add(k); break;
			case 'column': case 'card':
				if (Array.isArray(node.fields)) for (const k of node.fields) acc.add(k);
				else collectKeys(node.fields, acc); break;
			case 'group': for (const g of node.groups) for (const k of g.fields) acc.add(k); break;
			case 'section': for (const s of node.sections) { if (Array.isArray(s.fields)) for (const k of s.fields) acc.add(k); else collectKeys(s.fields, acc); } break;
			case 'tabs': for (const t of node.tabs) { if (Array.isArray(t.fields)) for (const k of t.fields) acc.add(k); else collectKeys(t.fields, acc); } break;
			case 'stepper': for (const s of node.steps) { if (Array.isArray(s.fields)) for (const k of s.fields) acc.add(k); else collectKeys(s.fields, acc); } break;
			case 'accordion': for (const i of node.items) { if (Array.isArray(i.fields)) for (const k of i.fields) acc.add(k); else collectKeys(i.fields, acc); } break;
		}
		return acc;
	}

	// Choix 2 : champs hors-layout rendus à la fin (pas de perte).
	const leftover = $derived(
		effLayout ? fields.filter((f) => !collectKeys(effLayout!).has(fieldKey(f))) : []
	);

	function fieldOf(cfgF: FieldConfig) {
		const key = cfgF.name ?? cfgF.id;
		return form.getField(key);
	}

	async function onSubmit(e: SubmitEvent) {
		e.preventDefault();
		await doSubmit();
	}

	// closeOnSubmit (api §3, défaut true) : après un submit en succès (state
	// 'success'), ferme l'hôte overlay. Réutilise le canal open/onClose de FormHost.

	async function doSubmit(): Promise<void> {
		await form.submit();
		const shouldClose = isOverlay && (effHost as any)?.closeOnSubmit !== false;
		if (shouldClose && form.state.status === 'success') open = false;
	}

	// Hôtes overlay (sheet/drawer/dialog) : les actions partent dans le footer de l'hôte.
	const isOverlay = $derived(
		effHost?.type === 'sheet' ||
			effHost?.type === 'drawer' ||
			effHost?.type === 'dialog' ||
			effHost?.type === 'modal'
	);

	// ── Hydratation / réinitialisation pilotées par l'hôte (semantics §2) ──
	// À l'ouverture : hydratation depuis `entity` (clés = fieldKey, valeurs
	// telles quelles — l'hydratation initiale à la création via la config
	// `entity` applique elle-même le parse du registre). À la fermeture :
	// retour aux defaults (reset). Sans `entity` prop, comportement inchangé
	// pour les sheets qui gèrent leur propre cycle (ex: EmployeeAssignmentSheet).
	$effect(() => {
		if (entity === undefined) return; // opt-in
		if (open) {
			if (entity) {
				// untrack : setValues lit+écrit l'état interne du formulaire
				// (values/depState/errors) — tracker ces lectures ici créerait une
				// boucle effet (effect_update_depth_exceeded) : seuls open/entity
				// doivent déclencher l'hydratation.
				// hydrate() mappe les clés backend (`out`) → fieldKey + parse registre.
				untrack(() => form.hydrate(entity));
			}
		} else {
			untrack(() => form.reset());
		}
	});

	// ── Confirm (metamodel §10) : bloque runAction tant que non confirmé.
	// Passe par le ConfirmDialog global (notification.confirm) — pas de confirm() natif. ──
	/** Variante Button UI correspondant à l'action (danger → destructive). */
	function buttonVariant(a: ActionConfig): 'default' | 'secondary' | 'destructive' | 'ghost' | 'outline' {
		if (a.variant === 'primary') return 'default';
		if (a.variant === 'danger') return 'destructive';
		return a.variant ?? 'outline';
	}

	async function executeAction(a: ActionConfig) {
		if (typeof a.disabled === 'function' ? a.disabled(form) : a.disabled) return;
		if (requiresConfirm(a)) {
			const ok = await new Promise<boolean>((res) => {
				notification.confirm({
					title: a.label,
					message: confirmMessage(a, t('confirm.message')),
					type: a.type === 'delete' || a.variant === 'danger' ? 'danger' : 'info',
					yesText: t('action.confirm'),
					noText: t('action.cancel'),
					onYes: () => res(true),
					onNo: () => res(false)
				});
			});
			if (!ok) return;
		}
		await runAction(form, a);
	}

	// ── Shortcuts (metamodel §10) : keydown vérifié sur la fenêtre mais filtré
	// sur le <form> (pas de capture hors du formulaire). Escape → cancel seulement
	// si une action le déclare. ──
	function onKeyDown(e: KeyboardEvent) {
		const root = document.getElementById(form.id);
		if (!root || !(e.target instanceof Node) || !root.contains(e.target)) return;
		for (const a of effActions) {
			if (!a.shortcut) continue;
			if (!matchesShortcut(e, a.shortcut)) continue;
			const disabled = typeof a.disabled === 'function' ? a.disabled(form) : a.disabled;
			if (disabled) continue;
			e.preventDefault();
			void executeAction(a);
			return;
		}
	}
</script>

{#snippet actionsBar(stretch = false)}
	<div class="flex flex-1 flex-wrap items-center gap-2">
		{#if showSubmit}
		<Button
			type="button"
			onclick={() => doSubmit()}
			disabled={form.isSubmitting}
			class={stretch ? 'h-9 flex-1 rounded-md text-sm font-medium' : ''}
		>
			{#if form.isSubmitting}
				<AnimateSpin class="size-3 border-white" text="" />
			{:else if submitIcon}
				<AppIcon name={submitIcon} size={16} />
			{/if}
			{form.isSubmitting ? 'Envoi…' : submitLabel}
		</Button>
		{/if}
		{#if showReset}
			<Button
				type="button"
				variant="outline"
				onclick={() => form.reset()}
				class={stretch ? 'h-9 flex-1 rounded-md text-sm font-medium' : ''}
			>
				{#if resetIcon}<AppIcon name={resetIcon} size={16} />{/if}
				Réinitialiser
			</Button>
		{/if}
		{#each effActions as a (a.label)}
			<Button
				type="button"
				variant={buttonVariant(a)}
				disabled={typeof a.disabled === 'function' ? a.disabled(form) : a.disabled}
				onclick={() => executeAction(a)}
				class={stretch ? 'h-9 flex-1 rounded-md text-sm font-medium' : ''}
			>
				{#if a.icon}<AppIcon name={a.icon} size={16} />{/if}
				{a.label}
			</Button>
		{/each}
	</div>
{/snippet}

{#snippet footerBar()}
	{@render actionsBar(true)}
{/snippet}

<FormHost
	{form}
	bind:open
	host={effHost}
	title={effTitle}
	description={effDescription}
	footer={isOverlay ? footerBar : undefined}
>
	<form id={form.id} class="grid gap-4" onsubmit={onSubmit} novalidate>
		{#if form.errors['_form']}
			<p class="bg-destructive/10 text-destructive rounded-md px-3 py-2 text-sm" role="alert">{form.errors['_form']}</p>
		{/if}
		{#if effLayout}
			<LayoutRenderer {form} {fields} layout={effLayout} />
			{#each leftover as cfgF (cfgF.id)}
				{@const inst = fieldOf(cfgF)}
				{#if inst}<FieldRenderer config={cfgF} field={inst} form={form} />{/if}
			{/each}
		{:else}
			{#each fields as cfgF (cfgF.id)}
				{@const inst = fieldOf(cfgF)}
				{#if inst}<FieldRenderer config={cfgF} field={inst} form={form} />{/if}
			{/each}
		{/if}
		{#if extras}
			<div class="pt-2">
				{@render extras()}
			</div>
		{/if}
		{#if !isOverlay}
			<div class="flex flex-wrap items-center gap-2 pt-2">
				{@render actionsBar(false)}
			</div>
		{/if}
	</form>
</FormHost>

<svelte:window onkeydown={onKeyDown} />
