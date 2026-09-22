// Helpers d'actions exacts api §10.
import type { ActionConfig, FormInstance } from '../core/types.js';

export function submit(label = 'Soumettre', config?: Partial<ActionConfig>): ActionConfig {
	return { type: 'submit', variant: 'primary', ...config, label: config?.label ?? label };
}

export function reset(label = 'Réinitialiser', config?: Partial<ActionConfig>): ActionConfig {
	return { type: 'reset', variant: 'secondary', ...config, label: config?.label ?? label };
}

export function cancel(label = 'Annuler', config?: Partial<ActionConfig>): ActionConfig {
	return { type: 'cancel', variant: 'ghost', ...config, label: config?.label ?? label };
}

/** Action `delete` (metamodel §10) : variante danger + confirmation obligatoire
 * (forcée à l'exécution par FormView, cf. `requiresConfirm`). */
export function remove(
	label = 'Supprimer',
	handler?: (form: FormInstance<any>) => void | Promise<void>,
	config?: Partial<ActionConfig>
): ActionConfig {
	return {
		type: 'delete',
		variant: 'danger',
		confirm: true,
		...config,
		label: config?.label ?? label,
		handler: config?.handler ?? handler
	};
}

export function action(type: ActionConfig['type'], config: Partial<ActionConfig>): ActionConfig {
	return { ...config, type } as ActionConfig;
}

/** Une action demande-t-elle une confirmation ? `delete` la force, même si
 * `confirm` est absent — metamodel §10 (« après confirmation »). */
export function requiresConfirm(a: ActionConfig): boolean {
	if (a.type === 'delete') return true;
	return typeof a.confirm === 'string' || a.confirm === true;
}

/** Message de confirmation : `confirm: string` sinon message par défaut i18n. */
export function confirmMessage(a: ActionConfig, fallback: string): string {
	return typeof a.confirm === 'string' ? a.confirm : fallback;
}

/** Exécute une action : submit/reset/cancel/delete/custom.
 * La confirmation éventuelle est gérée par l'appelant (FormView, ConfirmAction). */
export async function runAction(form: FormInstance, actionConfig: ActionConfig): Promise<void> {
	if (typeof actionConfig.disabled === 'function' ? actionConfig.disabled(form) : actionConfig.disabled)
		return;
	switch (actionConfig.type) {
		case 'submit':
			if (actionConfig.handler) await actionConfig.handler(form);
			else await form.submit();
			break;
		case 'reset':
			if (actionConfig.handler) await actionConfig.handler(form);
			else form.reset();
			break;
		case 'cancel':
			if (actionConfig.handler) await actionConfig.handler(form);
			else {
				// semantics §3 : l'annulation est émise et propagée à config.onCancel
				form.emitCancel();
				form.getConfig().onCancel?.();
			}
			break;
		case 'delete':
		case 'custom':
		default:
			if (actionConfig.handler) await actionConfig.handler(form);
	}
}

/** Parse un raccourci au format `"mod+s"`, `"mod+enter"`, `"escape"`.
 * Modificateurs : mod (Meta ou Ctrl), ctrl, meta, alt, shift. */
export function parseShortcut(
	shortcut: string
): { key: string; mod?: boolean; ctrl?: boolean; meta?: boolean; alt?: boolean; shift?: boolean } {
	const parts = shortcut.toLowerCase().split('+').map((p) => p.trim());
	const key = parts[parts.length - 1];
	const mods = parts.slice(0, -1);
	return {
		key,
		mod: mods.includes('mod'),
		ctrl: mods.includes('ctrl'),
		meta: mods.includes('meta') || mods.includes('cmd'),
		alt: mods.includes('alt'),
		shift: mods.includes('shift')
	};
}

/** Le KeyboardEvent correspond-il au raccourci ? */
export function matchesShortcut(
	e: KeyboardEvent,
	shortcut: string
): boolean {
	const s = parseShortcut(shortcut);
	let key = s.key;
	// Normalisations fréquentes : `esc` → escape, `return` → enter
	if (key === 'esc') key = 'escape';
	if (key === 'return') key = 'enter';
	if (e.key.toLowerCase() !== key) {
		// Tolère `+` saisi littéralement (mod++ impossible — mais '+' en clé)
		if (!(key === '+' && e.key === '+')) return false;
	}
	const hasCtrl = e.ctrlKey || e.metaKey;
	const wantCtrl = !!(s.mod || s.ctrl || s.meta);
	if (wantCtrl !== hasCtrl && (wantCtrl || hasCtrl)) return false;
	if (!!s.alt !== e.altKey) return false;
	if (!!s.shift !== e.shiftKey && !s.mod) return false;
	// mod+shift accepté si shift pressé et non requis ? Non : strict, sauf
	// `mod+enter` où certains navigateurs ne repportent pas shift — on reste strict.
	return true;
}
