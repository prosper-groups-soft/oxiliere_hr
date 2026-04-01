import { page } from '$app/state';
import { browser } from '$app/environment';

/**
 * Validates if a URL is safe for redirection
 * Prevents open redirect vulnerabilities by only allowing relative URLs and same-origin URLs
 */
function validate_url(url: string): boolean {
	if (!url || typeof url !== 'string') {
		return false;
	}

	// Remove leading/trailing whitespace
	url = url.trim();

	// Empty or just whitespace
	if (!url) {
		return false;
	}

	// Prevent javascript: and data: URLs
	if (url.toLowerCase().startsWith('javascript:') || url.toLowerCase().startsWith('data:')) {
		return false;
	}

	try {
		// If it starts with /, it's a relative URL - safe
		if (url.startsWith('/')) {
			return true;
		}

		// If it's a full URL, check if it's same origin
		if (url.startsWith('http://') || url.startsWith('https://')) {
			if (!browser)
				// Can't validate origin on server
				return false;

			const urlObj = new URL(url);
			const currentOrigin = window.location.origin;
			return urlObj.origin === currentOrigin;
		}

		// Relative URLs without leading slash are also safe
		if (!url.includes('://')) {
			return true;
		}

		return false;
	} catch {
		return false;
	}
}

/**
 * Gets the next URL from search parameters, with fallback to default
 */
export function get_next_url(defaultUrl: string = '/', url?: URL): string {
	if (!url && !browser) return defaultUrl;

	url = url || page.url;
	const next = page.url.searchParams.get('next_url');
	if (next && validate_url(next)) {
		return next;
	}

	return defaultUrl;
}

/**
 * Creates a URL with next_url parameter pointing to the current page
 */
export function create_url_with_next(targetPath: string, next_url?: string, url?: URL): string {
	if (!url && !browser) return targetPath;

	url = url || page.url;
	const urlToUse = next_url || url.pathname + url.search;
	const separator = targetPath.includes('?') ? '&' : '?';
	return `${targetPath}${separator}next_url=${encodeURIComponent(urlToUse)}`;
}

/**
 * Removes the next_url parameter from current URL
 */
export function remove_next_url_param(): string {
	if (!browser) return '/';

	const url = new URL(page.url);
	url.searchParams.delete('next_url');
	return url.pathname + url.search;
}

export function get_api_base_origin() {
	const url = import.meta.env.VITE_PUBLIC_API_BASE_URL;

	if (!url) throw Error('Please set the VITE_PUBLIC_API_BASE_URL environment variable');

	return url;
}

export function get_api_auth_origin() {
	const url = import.meta.env.VITE_PUBLIC_API_AUTH_URL;

	if (!url) throw Error('Please set the VITE_PUBLIC_API_AUTH_URL environment variable');

	return url;
}

export function get_auth_base_url() {
	const url = import.meta.env.VITE_PUBLIC_AUTH_BASE_URL;

	if (!url) throw Error('Please set the VITE_PUBLIC_AUTH_BASE_URL environment variable');

	return url;
}

export function get_logout_redirect_url() {
	const url = import.meta.env.VITE_PUBLIC_LOGOUT_REDIRECT_URL;

	if (!url) throw Error('Please set the VITE_PUBLIC_LOGOUT_REDIRECT_URL environment variable');

	return url;
}
