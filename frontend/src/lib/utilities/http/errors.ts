export interface ValidationErrorDetail {
	readonly type: string;
	readonly loc: ReadonlyArray<string | number>;
	readonly msg: string;
}

export interface UnprocessableEntityResponse {
	readonly detail: ValidationErrorDetail[];
}

export interface FieldError {
	readonly field: string;
	readonly message: string;
}

export interface OxilereHttpError {
	readonly detail: string;
	readonly code: string;
	readonly errors?: Readonly<Record<string, unknown>>;
}

interface ErrorResponse {
	readonly data?: unknown;
	readonly status?: number;
	readonly code?: string;
}

// === Constants ===
const HTTP_STATUS = {
	BAD_REQUEST: 400,
	UNAUTHORIZED: 401,
	FORBIDDEN: 403,
	NOT_FOUND: 404,
	UNPROCESSABLE_ENTITY: 422,
	SERVER_ERROR: 500,
	BAD_GATEWAY: 502,
	SERVICE_UNAVAILABLE: 503,
	GATEWAY_TIMEOUT: 504,
} as const;

const NETWORK_STATUS = {
	NETWORK_ERROR: 600,
	CONNECTION_REFUSED: 601,
	TIMEOUT: 602,
	UNKNOWN_ERROR: 603,
} as const;

// Mapping des erreurs techniques Django vers des messages conviviaux
const ERROR_MESSAGE_MAP: Readonly<Record<string, string>> = {
	'matching query does not exist': 'Utilisateur introuvable',
	'unique constraint failed': 'Cette valeur existe déjà',
	'cannot delete': 'Suppression impossible - des données sont liées',
	'invalid password': 'Mot de passe incorrect',
	'user not found': 'Utilisateur introuvable',
	'permission denied': 'Action non autorisée',
	'integrity error': 'Données en conflit avec des entrées existantes',
	'connection refused': 'Connexion au serveur refusée',
	'timeout': 'Délai de connexion dépassé'
};

/**
 * Custom error class for Oxilere HTTP errors.
 * Provides structured error handling with user-friendly messages.
 */
class OxilereError extends Error {
	readonly code: number;
	readonly details?: FieldError[] | OxilereHttpError | null;

	private constructor(
		message: string,
		code: number,
		details?: FieldError[] | OxilereHttpError | null
	) {
		super(message);
		this.name = 'OxilereError';
		this.code = code;
		this.details = details;
	}

	/**
	 * Parses an error response into an OxilereError instance.
	 * @param response - The error response from an HTTP request
	 * @returns A new OxilereError instance
	 */
	static parse(response: ErrorResponse | undefined): OxilereError {
		const statusCode = resolveStatusCode(response);
		const details = parseErrorDetails(response?.data, statusCode);

		return new OxilereError(
			this.getMessageFromCode(statusCode),
			statusCode,
			details
		);
	}

	/**
	 * Maps a technical error detail to a user-friendly message.
	 * @param detail - The technical error message
	 * @returns A user-friendly error message
	 */
	static mapTechnicalError(detail: string): string {
		const lowerDetail = detail.toLowerCase();
		
		for (const [technical, friendly] of Object.entries(ERROR_MESSAGE_MAP)) {
			if (lowerDetail.includes(technical.toLowerCase())) {
				return friendly;
			}
		}
		
		return detail;
	}

	/**
	 * Gets a user-friendly message for an HTTP status code.
	 * @param code - The HTTP status code
	 * @returns A localized error message
	 */
	static getMessageFromCode(code: number): string {
		const messages: Record<number, string> = {
			[HTTP_STATUS.BAD_REQUEST]: 'Requête invalide',
			[HTTP_STATUS.UNAUTHORIZED]: 'Non autorisé',
			[HTTP_STATUS.FORBIDDEN]: 'Accès refusé',
			[HTTP_STATUS.NOT_FOUND]: 'Ressource non trouvée',
			[HTTP_STATUS.UNPROCESSABLE_ENTITY]: 'Erreur de validation',
			[HTTP_STATUS.SERVER_ERROR]: 'Erreur serveur',
			[HTTP_STATUS.BAD_GATEWAY]: 'Passerelle incorrecte',
			[HTTP_STATUS.SERVICE_UNAVAILABLE]: 'Service indisponible',
			[HTTP_STATUS.GATEWAY_TIMEOUT]: "Délai d'attente dépassé",
			[NETWORK_STATUS.NETWORK_ERROR]: 'Problème de connexion réseau',
			[NETWORK_STATUS.CONNECTION_REFUSED]: 'Connexion au serveur refusée',
			[NETWORK_STATUS.TIMEOUT]: 'Délai de connexion dépassé',
			[NETWORK_STATUS.UNKNOWN_ERROR]: 'Erreur de communication inconnue',
		};

		return messages[code] ?? 'Une erreur est survenue';
	}

	/**
	 * Maps field errors using the provided field name mappings.
	 * @param maps - Record mapping technical field names to display names
	 * @returns Array of field errors with mapped field names
	 */
	mappedErrors(maps: Readonly<Record<string, string>>): FieldError[] {
		if (!this.isValidationError() || !Array.isArray(this.details)) {
			return [];
		}
		return mapFieldErrors(this.details, maps);
	}

	isValidationError(): boolean {
		return this.code === HTTP_STATUS.UNPROCESSABLE_ENTITY;
	}

	isForbiddenError(): boolean {
		return this.code === HTTP_STATUS.FORBIDDEN;
	}

	isNotFoundError(): boolean {
		return this.code === HTTP_STATUS.NOT_FOUND;
	}

	isUnauthorizedError(): boolean {
		return this.code === HTTP_STATUS.UNAUTHORIZED;
	}

	isNetworkError(): boolean {
		return this.code >= NETWORK_STATUS.NETWORK_ERROR && this.code <= NETWORK_STATUS.UNKNOWN_ERROR;
	}

	isBadRequestError(): boolean {
		return this.code === HTTP_STATUS.BAD_REQUEST;
	}
}

// === Type Guards ===
function isUnprocessableEntityResponse(data: unknown): data is UnprocessableEntityResponse {
	return (
		data !== null &&
		typeof data === 'object' &&
		'detail' in data &&
		Array.isArray((data as UnprocessableEntityResponse).detail)
	);
}

function isOxilereHttpError(data: unknown): data is OxilereHttpError {
	return (
		data !== null &&
		typeof data === 'object' &&
		'detail' in data &&
		typeof (data as OxilereHttpError).detail === 'string'
	);
}

// === Helper Functions ===
function resolveStatusCode(response: ErrorResponse | undefined): number {
	if (!response) {
		return NETWORK_STATUS.UNKNOWN_ERROR;
	}

	const networkCodes: Readonly<Record<string, number>> = {
		'ERR_NETWORK': NETWORK_STATUS.NETWORK_ERROR,
		'ECONNABORTED': NETWORK_STATUS.NETWORK_ERROR,
		'ECONNREFUSED': NETWORK_STATUS.CONNECTION_REFUSED,
		'ERR_CONNECTION_REFUSED': NETWORK_STATUS.CONNECTION_REFUSED,
		'ETIMEDOUT': NETWORK_STATUS.TIMEOUT,
		'ERR_TIMEOUT': NETWORK_STATUS.TIMEOUT,
	};

	if (response.code && response.code in networkCodes) {
		return networkCodes[response.code];
	}

	if (response.status) {
		return response.status;
	}

	return NETWORK_STATUS.UNKNOWN_ERROR;
}

function parseErrorDetails(
	data: unknown,
	statusCode: number
): FieldError[] | OxilereHttpError | null {
	try {
		if (statusCode === HTTP_STATUS.UNPROCESSABLE_ENTITY) {
			return parseUnprocessableEntity(data);
		}

		const httpError = parseHttpError(data);
		if (httpError) {
			return {
				...httpError,
				detail: OxilereError.mapTechnicalError(httpError.detail)
			};
		}

		return null;
	} catch {
		return null;
	}
}

function parseUnprocessableEntity(data: unknown): FieldError[] {
	if (!isUnprocessableEntityResponse(data)) {
		return [];
	}

	return data.detail.map((error): FieldError => ({
		field: String(error.loc?.slice(-1)[0] ?? ''),
		message: error.msg ?? ''
	}));
}

function parseHttpError(data: unknown): OxilereHttpError | null {
	if (!isOxilereHttpError(data)) {
		return null;
	}

	return {
		detail: data.detail,
		code: data.code ?? 'unknown_error',
		errors: data.errors
	};
}

function mapFieldErrors(
	errors: ReadonlyArray<FieldError>,
	maps: Readonly<Record<string, string>>
): FieldError[] {
	return errors.map((error): FieldError => ({
		field: maps[error.field] ?? error.field,
		message: error.message
	}));
}

export default OxilereError;

