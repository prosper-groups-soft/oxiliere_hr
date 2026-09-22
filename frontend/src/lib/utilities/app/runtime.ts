import { goto } from '$app/navigation';
import { auth } from '$lib/features/auth/stores/auth.svelte';
import type { SessionUser } from '@/types/users';
import { AuthEndpoint, UserAccountEndpoints } from '@/hr/auth/api/auth.endpoints';
import BaseEndpoints from '@/api/endpoints';
import axios from 'axios';
import { toast } from 'svelte-sonner';
import { removeAuthCookie, setAuthCookie } from '../auth/auth-cookies';
import { get_logout_redirect_url } from '../http/urls';


export async function load_user(force = false) {
	let cu: SessionUser | null = auth.currentUser;

	if (!cu || force) {
		try {
			const data = await UserAccountEndpoints.session.retrieve();
			auth.currentUser = data;
			setAuthCookie();
		} catch (e: any) {
			if (axios.isAxiosError(e) && e.response?.status === 401) {
				// clean_user_auth();
				return;
			}
		}
	}
}

export function clean_user_auth() {
	auth.currentUser = null;
	auth.isLoggingOut = false;
	removeAuthCookie();
}

export async function logout() {
	const logout_redirect = get_logout_redirect_url();
	try {
		auth.isLoggingOut = true;
		await AuthEndpoint.logout.create();
		clean_user_auth();
		goto(logout_redirect);
	} catch (e) {
		if (axios.isAxiosError(e) && e.response?.status === 401) {
			clean_user_auth();
			goto(logout_redirect);
		} else {
			toast.error('Erreur de déconnexion', {
				description: 'Une erreur est survenue lors de la déconnexion'
			});
		}
	}
}

export async function init_csrf() {
	try {
		await BaseEndpoints.init_csrf.retrieve();
	} catch (error) {
		// pass
	}
}

