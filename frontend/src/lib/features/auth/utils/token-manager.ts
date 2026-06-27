/**
 * Gestion du token organization_token
 * - Décodage JWT
 * - Vérification expiration (DESACTIVE)
 * - Rafraîchissement automatique (DESACTIVE)
 */

import { browser } from '$app/environment';

interface JWTPayload {
	exp?: number;
	iat?: number;
	token_type?: string;
	tenant_id?: string;
	oxi_id?: string;
	schema_name?: string;
}

// Token refresh management - DESACTIVE
// let isRefreshing = false;
// let refreshPromise: Promise<boolean> | null = null;

/**
 * Récupère le token organization_token depuis les cookies
 */
function getOrganizationToken(): string | null {
	if (!browser) return null;
	
	const match = document.cookie.match(/organization_token=([^;]+)/);
	return match ? match[1] : null;
}

/**
 * Décode un JWT (sans vérification de signature)
 */
function decodeJWT(token: string): JWTPayload | null {
	try {
		const base64 = token.split('.')[1];
		const json = atob(base64.replace(/-/g, '+').replace(/_/g, '/'));
		return JSON.parse(json);
	} catch {
		return null;
	}
}

/**
 * Vérifie si le token va expirer dans les prochaines minutes
 * DESACTIVE - Retourne toujours false
 */
export function isTokenExpiringSoon(minutesBefore = 5): boolean {
	return false; // Token management disabled
}

/**
 * Vérifie si le token est déjà expiré
 * DESACTIVE - Retourne toujours false
 */
export function isTokenExpired(): boolean {
	return false; // Token management disabled
}

/**
 * Rafraîchit l'organization token
 * DESACTIVE - Retourne toujours true sans action
 */
async function performTokenRefresh(): Promise<boolean> {
	return true; // Token management disabled
}

/**
 * Rafraîchit le token avec gestion des requêtes concurrentes
 * DESACTIVE - Retourne toujours true sans action
 */
export async function refreshOrganizationToken(): Promise<boolean> {
	return true; // Token management disabled
}

/**
 * Vérifie et rafraîchit le token si nécessaire avant une requête
 * DESACTIVE - Retourne toujours true sans action
 */
export async function ensureValidToken(): Promise<boolean> {
	return true; // Token management disabled
}

/**
 * Parse le payload du token organization_token
 */
export function getTokenPayload(): JWTPayload | null {
	const token = getOrganizationToken();
	if (!token) return null;
	return decodeJWT(token);
}

/**
 * Affiche les infos de debug du token dans la console
 */
export function debugToken(): void {
	const payload = getTokenPayload();
	if (!payload) {
		console.log('[TokenManager] No organization_token found');
		return;
	}
	
	const now = Math.floor(Date.now() / 1000);
	const expiresIn = payload.exp ? payload.exp - now : 0;
	
	console.log('[TokenManager] Token info:', {
		token_type: payload.token_type,
		tenant_id: payload.tenant_id,
		oxi_id: payload.oxi_id,
		schema_name: payload.schema_name,
		expires_in: `${Math.floor(expiresIn / 60)}m ${expiresIn % 60}s`,
		is_expired: expiresIn < 0,
		is_expiring_soon: expiresIn < 300
	});
}

