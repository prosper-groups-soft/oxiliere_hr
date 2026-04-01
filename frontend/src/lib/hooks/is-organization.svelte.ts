import { page } from '$app/state';
import axios, { type InternalAxiosRequestConfig, type AxiosError } from 'axios';

export type AppMode = 'user' | 'organization';

/**
 * Detects the application mode based on the pathname
 * @param pathname - The URL path
 * @returns 'organization' if the URL starts with /o/, otherwise 'user'
 */
export function detectMode(pathname: string): AppMode {
	return pathname.startsWith('/o/') ? 'organization' : 'user';
}

/**
 * Extracts the organization slug from the pathname
 * @param pathname - The URL path
 * @returns The organization slug or null if not in organization mode
 */
export function extractOrgSlug(pathname: string): string | null {
	const orgMatch = pathname.match(/^\/o\/([^\/]+)/);
	return orgMatch ? orgMatch[1] : null;
}

/**
 * Class to manage application reactive states (Svelte 5)
 */
export class AppModeManager {
	/**
	 * Detected application mode
	 */
	appMode = $derived(detectMode(page.url.pathname));

	/**
	 * Organization slug
	 */
	orgSlug = $derived(extractOrgSlug(page.url.pathname));

	/**
	 * Indicates if we are in organization mode
	 */
	isOrganizationMode = $derived(detectMode(page.url.pathname) === 'organization');

	/**
	 * Complete mode information
	 */
	modeInfo = $derived.by(() => {
		const pathname = page.url.pathname;
		const mode = detectMode(pathname);
		const orgSlug = mode === 'organization' ? extractOrgSlug(pathname) : null;

		return {
			mode,
			isOrganization: mode === 'organization',
			isUser: mode === 'user',
			orgSlug,
			pathname
		};
	});
}

/**
 * Global instance of the application mode manager
 */
export const appModeManager = new AppModeManager();

/**
 * Configures an Axios interceptor to add the organization slug to headers
 * @returns The interceptor ID to be able to remove it later
 */
export function setHeaderSlugInterceptor(): number {
	return axios.interceptors.request.use(
		(config: InternalAxiosRequestConfig) => {
			const orgSlug = appModeManager.orgSlug;
			if (orgSlug) {
				config.headers['X-Organization-ID'] = orgSlug;
			}
			return config;
		},
		(error: AxiosError) => {
			return Promise.reject(error);
		}
	);
}

/**
 * Removes an Axios interceptor by its ID
 * @param interceptorId The ID of the interceptor to remove
 */
export function removeHeaderSlugInterceptor(interceptorId: number): void {
	axios.interceptors.request.eject(interceptorId);
}
