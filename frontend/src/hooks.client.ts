import { current_user_store } from '@/stores/auth';
import { syncAuthState } from '@/utilities/auth/auth-cookies';
import { browser } from '$app/environment';
import type { ServerInit } from '@sveltejs/kit';


export const init: ServerInit = async () => {
	if (browser) {
		const isAuthenticated = syncAuthState();

		if (isAuthenticated) {
			current_user_store.subscribe(user => {
				if (!user) {
					// Optional : trigger load_user() here if necessary
					console.log('User cookie exists but store is empty - may need to reload user data');
				}
			});
		}
	}
};

