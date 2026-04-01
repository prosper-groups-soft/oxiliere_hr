import axios from 'axios';
import { AVATAR_PALETTES } from '@/constants/ui/colors';

/**
 * Example of API response when user needs to verify email:
 * {
    "status": 401,
    "data": {
        "flows": [
            {
                "id": "login"
            },
            {
                "id": "verify_email",
                "is_pending": true
            }
        ]
    },
    "meta": {
        "is_authenticated": false
    }
}
 */

/**
 * Checks if an error response indicates that the user must verify their email
 * @param err The error object from an API request
 * @returns boolean True if the error indicates email verification is required
 */
export function is_must_verify_email_error(err: any): boolean {
	if (!err) return false;

	if (err.status !== 401) return false;

	const data = err.data;
	if (!data || !data.flows || !Array.isArray(data.flows)) return false;

	return data.flows.some((flow: any) => flow.id === 'verify_email' && flow.is_pending === true);
}

export function is_axios_error(error: any) {
	return axios.isAxiosError(error);
}

export function is_call_to_login(err: any) {
	if (!err) return false;

	if (err.status !== 401) return false;

	const data = err.data;
	if (!data || !data.flows || !Array.isArray(data.flows)) return false;

	return data.flows[0].id === 'login';
}

export function isPromise(value: any): value is Promise<any> {
	return value !== null && value !== undefined && typeof value.then === 'function';
}

export function is_nan(value: string) {
	const val = parseInt(value);
	return Number.isNaN(val);
}

export function format_currency(currency: any, value: string, show_null = false) {
	if (!show_null && is_nan(value)) return '';
	return currency(value).format();
}

export function to_deep_string(val: any): string[] {
	if (Array.isArray(val)) {
		return val.map((v) => String(v));
	} else if (val && typeof val === 'object') {
		return Object.entries(val).map((k, val) => `${k}: ${val}`);
	} else {
		return [String(val)];
	}
}

export function getAvatarPalette(name: string) {
	if (!name) return AVATAR_PALETTES[0];

	// We calculate a "hash" based on the character codes of the name
	let hash = 0;
	for (let i = 0; i < name.length; i++) {
		hash = name.charCodeAt(i) + ((hash << 5) - hash);
	}

	// We use the modulo to stay within the limits of the palette array
	const index = Math.abs(hash) % AVATAR_PALETTES.length;

	return AVATAR_PALETTES[index];
}
