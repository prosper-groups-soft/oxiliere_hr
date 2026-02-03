import { page } from "$app/state";
import axios, { type InternalAxiosRequestConfig, type AxiosError } from "axios";

export type AppMode = 'user' | 'organization';

/**
 * Détecte le mode de l'application basé sur le pathname
 * @param pathname - Le chemin de l'URL
 * @returns 'organization' si l'URL commence par /o/, sinon 'user'
 */
export function detectMode(pathname: string): AppMode {
    return pathname.startsWith('/o/') ? 'organization' : 'user';
}

/**
 * Extrait le slug de l'organisation depuis le pathname
 * @param pathname - Le chemin de l'URL
 * @returns Le slug de l'organisation ou null si pas en mode organisation
 */
export function extractOrgSlug(pathname: string): string | null {
    const orgMatch = pathname.match(/^\/o\/([^\/]+)/);
    return orgMatch ? orgMatch[1] : null;
}

/**
 * Classe pour gérer les états réactifs de l'application (Svelte 5)
 */
export class AppModeManager {
    /**
     * Mode de l'application détecté
     */
    appMode = $derived(detectMode(page.url.pathname));

    /**
     * Slug de l'organisation
     */
    orgSlug = $derived(extractOrgSlug(page.url.pathname));

    /**
     * Indique si on est en mode organisation
     */
    isOrganizationMode = $derived(detectMode(page.url.pathname) === 'organization');

    /**
     * Informations complètes du mode
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
 * Instance globale du gestionnaire de mode d'application
 */
export const appModeManager = new AppModeManager();



/**
 * Configure un intercepteur Axios pour ajouter le slug de l'organisation dans les headers
 * @returns L'ID de l'intercepteur pour pouvoir le supprimer plus tard
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
 * Supprime un intercepteur Axios par son ID
 * @param interceptorId L'ID de l'intercepteur à supprimer
 */
export function removeHeaderSlugInterceptor(interceptorId: number): void {
    axios.interceptors.request.eject(interceptorId);
}
