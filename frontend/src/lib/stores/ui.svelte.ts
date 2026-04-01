import { settings } from './settings.svelte';
import { type Snippet, untrack } from 'svelte';


interface RegisteredAction {
	id: string;
	snippet: Snippet;
}


class UiStore {
	selectedMenuItem = $state<string | null>('home');
	initialLoading = $state(true);

	// Use a private state for the stack
	private _actionsStack = $state<RegisteredAction[]>([]);

	/**
	 * Getter: Returns snippets.
	 * Svelte 5 will only re-run effects using this when _actionsStack actually changes.
	 */
	get pageActions() {
		return this._actionsStack.map((a) => a.snippet);
	}

	/**
	 * Adds an action without triggering a reactive dependency loop
	 */
	addActions(id: string, snippet: Snippet) {
		untrack(() => {
			if (!this._actionsStack.find((a) => a.id === id)) {
				this._actionsStack.push({ id, snippet });
			}
		});
	}

	/**
	 * Removes an action without triggering a reactive dependency loop
	 */
	removeActions(id: string) {
		untrack(() => {
			this._actionsStack = this._actionsStack.filter((a) => a.id !== id);
		});
	}

	// --- PERSISTENT STATES ---
	get isExpanded() {
		return settings.current.sidebarExpanded;
	}
	setExpanded(val: boolean) {
		settings.update('sidebarExpanded', val);
	}
}


export const ui = new UiStore();

