import { auth } from '@/features/auth/stores/auth.svelte';
import { syncAuthState } from '@/utilities/auth/auth-cookies';
import { browser } from '$app/environment';
import type { ServerInit } from '@sveltejs/kit';


export const init: ServerInit = async () => {
	if (browser) {
		const isAuthenticated = syncAuthState();

		if (isAuthenticated && !auth.currentUser) {
			console.log('User cookie exists but store is empty - may need to reload user data');
			// Optionally trigger session refresh
			// try { await auth.refreshSession(); } catch(e) {}
		}
	}
};

