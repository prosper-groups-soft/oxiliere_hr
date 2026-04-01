/**
 * @author :  Edimedia Mutoke <https://github.com/edimedia>
 * @description : REST API Client
 * @version 1.0.0
 * @license MIT
 * @copyright Edimedia Mutoke 2024
 * @see {@link https://github.com/edimedia}
 **/
import { createEvent } from '@/events';
import axios, { AxiosError, type AxiosResponse, type InternalAxiosRequestConfig } from 'axios';
import * as rax from 'retry-axios';
import { AUTH_EVENT, AUTH_REQUIRED_EVENT, PERM_REQUIRED_EVENT } from '@/constants/app/events';
import { get_api_auth_origin, get_api_base_origin } from './urls';

const auth_event = createEvent<string>(AUTH_EVENT);
const ORIGIN = get_api_base_origin();

// Configure global Axios defaults
axios.defaults.baseURL = ORIGIN;
axios.defaults.withCredentials = true; // Crucial for sending cookies cross-origin
axios.defaults.xsrfCookieName = 'csrftoken'; // Default cookie name Django uses
axios.defaults.xsrfHeaderName = 'X-CSRFToken'; // Default header name Django expects

// Dev Authentication (BasicNoPasswordAuth)
axios.defaults.headers.common['Authorization'] = 'Basic ZGV2QG94aWxpZXJlLmNvbTo=';

axios.defaults.raxConfig = {
	retry: 2,
	noResponseRetries: 2,

	retryDelay: 100,
	httpMethodsToRetry: ['GET', 'POST', 'DELETE', 'PUT'],

	// Retry only when it's an authorized request (refresh token)
	statusCodesToRetry: [[401, 401]],

	backoffType: 'exponential',

	onRetryAttempt: (err) => {
		const cfg = rax.getConfig(err);
		const refresh_url = join_base_url('/auth/refresh', get_api_auth_origin());

		console.log(`Retry attempt #${cfg?.currentRetryAttempt}`);

		return new Promise<void>((resolve, reject) => {
			fetch(refresh_url, {
				method: 'POST',
				body: JSON.stringify({}),
				credentials: 'include',
				headers: {
					'Content-Type': 'application/json'
				}
			})
				.then((response) => {
					if (response.ok) {
						resolve();
					} else {
						if (response.status == 401 || response.status == 422) {
							auth_event.publish(AUTH_REQUIRED_EVENT);
						}

						reject();
					}
				})
				.catch((error) => {
					if (error.response.status == 401) {
						auth_event.publish(AUTH_REQUIRED_EVENT);
					}

					reject();
				});
		});
	},

	shouldRetry(error) {
		const url = error.config?.url || '';
		const cfg = rax.getConfig(error);

		if (error.response?.status == 403) {
			auth_event.publish(PERM_REQUIRED_EVENT);
			return false;
		}

		if (error.response?.status !== 401) {
			return false;
		}

		// @ts-ignore
		if (cfg?.currentRetryAttempt >= cfg?.retry) {
			auth_event.publish(PERM_REQUIRED_EVENT);
			return false;
		}

		return !url.includes('/auth/login');
	}
};

// Function to get a cookie by name
function getCookie(name: string): string | null {
	let cookieValue = null;
	if (document.cookie && document.cookie !== '') {
		const cookies = document.cookie.split(';');
		for (let i = 0; i < cookies.length; i++) {
			const cookie = cookies[i].trim();
			// Does this cookie string begin with the name we want?
			if (cookie.substring(0, name.length + 1) === name + '=') {
				cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
				break;
			}
		}
	}
	return cookieValue;
}

axios.interceptors.request.use(
	(config: InternalAxiosRequestConfig) => {
		const method = config.method?.toLowerCase();
		if (method && ['post', 'put', 'delete', 'patch'].includes(method)) {
			if (!config.headers['X-CSRFToken']) {
				const token = getCookie('csrftoken');
				if (token) {
					config.headers['X-CSRFToken'] = token;
				} else {
					console.warn(
						`CSRF token cookie not found. Request to ${config.url} might be rejected by the server.`
					);
				}
			}
		}
		return config;
	},
	(error) => {
		return Promise.reject(error);
	}
);

axios.interceptors.response.use(
	(response: AxiosResponse) => {
		return response.data;
	},
	(error: AxiosError<any>) => {
		return Promise.reject(error);
	}
);

rax.attach();

/**
 * Rest API Client must have validator, schema options,
 */

// Export axios instance configured si other modules needed it.
// If it import only 'axios', the global configuration should be applied.
export default axios;

/**
 * @param {string} url
 * @param {Function} process
 *
 */
export function request(url: string, process: (url: string, args: any[]) => any, origin?: string) {
	const tokens = url.split('/');
	const ORIGIN = origin ? origin : get_api_base_origin();
	return (...args: any[]) => {
		const mappedUrl =
			ORIGIN + tokens.map((token, i) => (token.startsWith(':') ? args.shift() : token)).join('/');
		return Promise.resolve(process(mappedUrl.replace(/\/$/, ''), args));
	};
}

export function GET(URL: string, origin?: string) {
	return request(
		URL,
		(url, args) => {
			const [params, cancelToken] = args;
			return axios.get(url, { params, cancelToken, withCredentials: true });
		},
		origin
	);
}

export function POST(URL: string, origin?: string) {
	return request(
		URL,
		(url, args) => {
			const [body, params, cancelToken] = args;
			return axios.post(url, body, { params, cancelToken, withCredentials: true });
		},
		origin
	);
}

export function DELETE(URL: string, origin?: string) {
	return request(
		URL,
		(url, args) => {
			const [params, cancelToken] = args;
			if (params && params['data']) {
				const body = params['data'];
				delete params['data'];
				return axios.delete(url, { data: body, params, cancelToken, withCredentials: true });
			} else {
				return axios.delete(url, { params, cancelToken, withCredentials: true });
			}
		},
		origin
	);
}

export function PUT(URL: string, origin?: string) {
	return request(
		URL,
		(url, args) => {
			const [body, params, cancelToken] = args;
			return axios.put(url, body, { params, cancelToken, withCredentials: true });
		},
		origin
	);
}

export function PATCH(URL: string, origin?: string) {
	return request(
		URL,
		(url, args) => {
			const [body, params, cancelToken] = args;
			return axios.patch(url, body, { params, cancelToken, withCredentials: true });
		},
		origin
	);
}

export function UPLOAD(
	URL: string,
	form: FormData,
	setProgressState: (progress: number) => void,
	origin?: string
) {
	const ORIGIN = origin ? origin : get_api_base_origin();

	return axios.post(join_base_url(URL, ORIGIN), form, {
		headers: {
			'Content-Type': 'multipart/form-data'
		},
		withCredentials: true,
		onUploadProgress: (progressEvent: any) => {
			const percentCompleted = Math.round(
				(progressEvent.loaded * 100) / (progressEvent.total || 1)
			);
			setProgressState(percentCompleted);
		}
	});
}

export const parseUrl = (url: string, args: any[], origin?: string) => {
	const tokens = url.split('/');
	const ORIGIN = origin ? origin : get_api_base_origin();
	return (
		ORIGIN + tokens.map((token, i) => (token.startsWith(':') ? args.shift() : token)).join('/')
	);
};

export function join_base_url(url: string, origin?: string) {
	if (!url) return origin || get_api_base_origin();

	if (url.startsWith('http://') || url.startsWith('https://')) {
		return url;
	}

	const ORIGIN = origin ? origin : get_api_base_origin();

	return join_url_path(ORIGIN, url);
}

export function join_url_path(url1: string, url2: string) {
	const cleanUrl1 = url1.replace(/\/+$/, '');
	const cleanUrl2 = url2.replace(/^\/+/, '');
	return `${cleanUrl1}/${cleanUrl2}`;
}
