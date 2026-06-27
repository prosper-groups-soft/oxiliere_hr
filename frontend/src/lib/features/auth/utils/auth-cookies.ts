import { browser } from '$app/environment';

/**
 * Define the artificial cookie
 * To call after successful authentification
 */
export function setAuthCookie(): void {
	if (!browser) return;

	// Cookie valid for 7 days, access only on JS, secured HTTPS
	// Note: Escape HttpOnly to allow access via document.cookie
	const isSecure = window.location.protocol === 'https:';
	document.cookie = `is_authenticated=true; path=/; max-age=${7 * 24 * 60 * 60}; SameSite=Strict${
		isSecure ? '; Secure' : ''
	}`;
	localStorage.setItem('is_authenticated', 'true');
}

/**
 * Delete the artificial authentification cookie
 * To call after logout
 */
export function removeAuthCookie(): void {
	if (!browser) return;

	const isSecure = window.location.protocol === 'https:';
	document.cookie = `is_authenticated=; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT; SameSite=Strict${
		isSecure ? '; Secure' : ''
	}`;
	localStorage.removeItem('is_authenticated');
}

/**
 * Verify if the authentification cookie exists on client side
 * Use the hybrid approach : cookie + localStorage for HTTPS compatibility
 */
export function hasAuthCookie(): boolean {
	if (!browser) return false;

	// Verify the cookie first
	const cookieExists = document.cookie
		.split(';')
		.some((cookie) => cookie.trim().startsWith('is_authenticated=true'));

	// If the cookie is not found, verify the localStorage (fallback for HTTPS)
	if (!cookieExists) {
		return localStorage.getItem('is_authenticated') === 'true';
	}

	return cookieExists;
}

/**
 * Synchronize the store with the cookie (use when application start)
 */
export function syncAuthState(): boolean {
	return hasAuthCookie();
}
