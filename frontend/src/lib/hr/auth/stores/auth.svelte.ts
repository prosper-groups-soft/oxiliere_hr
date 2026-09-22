import type { Organization } from '@/types/organization';
import type { SessionUser } from '@/types/users';
import { browser } from '$app/environment';
import { OXILIERE_LABEL } from '@/constants/app/base';
import { authService } from '../services/auth.services';
import type { LoginCredentials } from '../types/auth';


/**
 * Authentication Store (Svelte 5 Runes)
 */
class AuthStore {
	// --- State ---
	currentUser = $state<SessionUser | null>(null);
	currentOrganization = $state<Organization | null>(null);
	authRequired = $state<boolean>(false);
	isLoggingOut = $state<boolean>(false);

	constructor() {
		if (browser) {
			this._loadFromStorage();
			this._setupPersistence();
			this._setupTabSync();
		}
	}

	// --- Derived ---
	get organizationName() {
		return this.currentOrganization?.name || OXILIERE_LABEL;
	}

	get isAuthenticated() {
		return this.currentUser !== null;
	}

	// --- Actions ---

	/**
	 * Performs login and updates state
	 */
	async login(credentials: LoginCredentials) {
		try {
			const response = await authService.login(credentials);
			await this.refreshSession();
			this.authRequired = false;
			return response;
		} catch (error) {
			console.error('Login failed:', error);
			throw error;
		}
	}

	/**
	 * Performs logout and clears state
	 */
	async logout() {
		this.isLoggingOut = true;
		try {
			await authService.logout();
		} finally {
			this.currentUser = null;
			this.currentOrganization = null;
			this.authRequired = true;
			this.isLoggingOut = false;
			this._clearStorage();
		}
	}

	/**
	 * Refreshes current session from server
	 */
	async refreshSession() {
		try {
			const session = await authService.getSession();
			this.currentUser = session;
			this.authRequired = false;
			return session;
		} catch (error) {
			this.currentUser = null;
			this.authRequired = true;
			throw error;
		}
	}

	// --- Internal Persistence ---

	private _loadFromStorage() {
		try {
			const storedUser = localStorage.getItem('current_user');
			if (storedUser) this.currentUser = JSON.parse(storedUser);

			const storedAuthRequired = localStorage.getItem('auth_required');
			if (storedAuthRequired) this.authRequired = JSON.parse(storedAuthRequired);
		} catch (e) {
			console.warn('AuthStore: Failed to load from storage', e);
		}
	}

	private _setupPersistence() {
		$effect.root(() => {
			$effect(() => {
				localStorage.setItem('current_user', JSON.stringify(this.currentUser));
			});
			$effect(() => {
				localStorage.setItem('auth_required', JSON.stringify(this.authRequired));
			});
		});
	}

	private _setupTabSync() {
		window.addEventListener('storage', (event) => {
			if (event.key === 'current_user' && event.newValue) {
				this.currentUser = JSON.parse(event.newValue);
			}
			if (event.key === 'auth_required' && event.newValue) {
				this.authRequired = JSON.parse(event.newValue);
			}
		});
	}

	private _clearStorage() {
		localStorage.removeItem('current_user');
		localStorage.setItem('auth_required', 'true');
	}
}


export const auth = new AuthStore();
