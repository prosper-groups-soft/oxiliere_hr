/**
 * Messages d'erreur pour l'application
 * Centralise tous les messages pour faciliter la maintenance et la traduction
 */


export const ERROR_MESSAGES = {
	// HTTP Status Codes
	HTTP: {
		400: "Requête invalide. Veuillez vérifier les données saisies.",
		401: "Votre session a expiré. Veuillez vous reconnecter.",
		403: "Vous n'avez pas les droits nécessaires pour effectuer cette action. Contactez un administrateur.",
		404: "La ressource demandée n'existe pas ou a été supprimée.",
		409: "Conflit détecté. La ressource existe déjà ou est en cours de modification.",
		422: "Données invalides. Veuillez corriger les erreurs et réessayer.",
		429: "Trop de requêtes. Veuillez patienter quelques instants.",
		500: "Une erreur serveur s'est produite. Veuillez réessayer plus tard.",
		502: "Service temporairement indisponible. Veuillez réessayer plus tard.",
		503: "Service en maintenance. Veuillez réessayer dans quelques minutes.",
		504: "Le serveur met trop de temps à répondre. Veuillez réessayer.",
	},

	// Network / API
	NETWORK: {
		OFFLINE: "Vous semblez hors ligne. Veuillez vérifier votre connexion.",
		TIMEOUT: "La requête a pris trop de temps. Veuillez réessayer.",
		ABORTED: "La connexion a été interrompue. Veuillez réessayer.",
		UNKNOWN: "Une erreur inattendue s'est produite. Veuillez réessayer.",
	},
} as const;


/**
 * Récupère le message d'erreur correspondant à un code HTTP
 */
export function getHttpErrorMessage(statusCode: number): string {
	return ERROR_MESSAGES.HTTP[statusCode as keyof typeof ERROR_MESSAGES.HTTP] 
		|| ERROR_MESSAGES.NETWORK.UNKNOWN;
}


/**
 * Traduit les messages d'erreur anglais du backend Django en français
 */
const FRENCH_ERROR_MAP: Record<string, string> = {
	'You have already applied for this offer.': 'Vous avez déjà postulé à cette offre.',
	'This request overlaps with an already submitted leave.': 'Cette période chevauche une demande de congé déjà soumise.',
	'Field required': 'Veuillez remplir tous les champs obligatoires.',
	'field required': 'Veuillez remplir tous les champs obligatoires.',
	'This field is required.': 'Ce champ est obligatoire.',
	'The maximum number of applications for this position has been reached.': 'Le nombre maximum de candidatures pour ce poste a été atteint.',
	'Unable to create shift policy': 'Impossible de créer le modèle de travail. Vérifiez les données saisies.',
};

/**
 * Extrait le premier message d'une ValidationError Django sérialisée en chaîne.
 * Ex. "{'__all__': ['Base salary ... .']}" → "Base salary ... ."
 */
function unwrapDjangoValidationMessage(raw: string): string | null {
	const m = raw.match(/\[\s*['"]([^'"]+)['"]/);
	return m ? m[1] : null;
}

/** Formate un montant décimal en français (ex. "500000.0" → "500 000"). */
function formatAmount(value: string): string {
	const n = Number(value);
	if (!Number.isFinite(n)) return value;
	return Math.round(n).toLocaleString('fr-FR');
}

/**
 * Traduit un message d'erreur backend en français, en gérant :
 *  - les ValidationError Django sérialisées en chaîne ({'__all__': [...]}),
 *  - le cas SMIG (salaire < SMIG mensuel) avec reformulation claire.
 */
export function frenchBackendError(message: string): string {
	const inner = unwrapDjangoValidationMessage(message) ?? message;

	// Cas SMIG : « Base salary (500000.0 FC) cannot be lower than the active
	// monthly SMIG (559000.00 FC). »
	const smig = inner.match(
		/Base salary \(([0-9.]+) ([A-Za-z]+)\) cannot be lower than the active monthly SMIG \(([0-9.]+) ([A-Za-z]+)\)/
	);
	if (smig) {
		return (
			`Le salaire de base (${formatAmount(smig[1])} ${smig[2]}) est inférieur au ` +
			`SMIG mensuel en vigueur (${formatAmount(smig[3])} ${smig[4]}). ` +
			`Saisissez un salaire au moins égal au SMIG.`
		);
	}

	for (const [english, french] of Object.entries(FRENCH_ERROR_MAP)) {
		if (inner.includes(english)) {
			return french;
		}
	}
	return inner;
}


/**
 * Récupère un message d'erreur utilisateur friendly
 * Gère plusieurs formats d'erreur (Axios, Fetch, string, etc.)
 * Priorité : messages français basés sur le code HTTP
 */
export function getFriendlyErrorMessage(error: any): string {
	// Vérifier si c'est une erreur "Field required" (Pydantic/Django Ninja)
	const errorStr = typeof error === 'string' ? error : JSON.stringify(error);
	if (errorStr.includes('Field required') || errorStr.includes('field required') || error?.message?.includes('Field required')) {
		return "Veuillez remplir tous les champs obligatoires.";
	}

	// PRIORITÉ 1: Code HTTP connu → message français
	const status = error?.response?.status || error?.status || error?.statusCode;
	if (status) {
		// Pour les erreurs 400 et 422, on essaie d'abord le message du backend
		if (status === 400 || status === 422) {
			const detail = error?.response?.data?.detail;
			if (typeof detail === 'string') {
				return frenchBackendError(detail);
			}
			if (Array.isArray(detail) && detail.length > 0) {
				const firstError = detail[0];
				if (typeof firstError === 'string') {
					return frenchBackendError(firstError);
				}
				if (firstError?.msg) {
					return frenchBackendError(firstError.msg);
				}
				if (firstError?.type === 'missing' || firstError?.type === 'value_error.missing') {
					return "Veuillez remplir tous les champs obligatoires.";
				}
			}
			if (typeof detail === 'object' && detail !== null) {
				// Erreur de champ spécifique (format Django Ninja)
				const values = Object.values(detail);
				if (values.length > 0) {
					const firstVal = values[0];
					if (Array.isArray(firstVal) && firstVal.length > 0 && typeof firstVal[0] === 'string') {
						return frenchBackendError(firstVal[0]);
					}
				}
			}
		}
		// Pour tous les autres codes, message français standard
		return getHttpErrorMessage(status);
	}

	// Fallback: ancienne logique pour compatibilité
	if (error?.response?.data?.detail) {
		const detail = error.response.data.detail;
		if (typeof detail === 'string') return frenchBackendError(detail);
		if (Array.isArray(detail) && detail.length > 0) {
			const firstError = detail[0];
			if (typeof firstError === 'string') return frenchBackendError(firstError);
			if (firstError?.msg) return frenchBackendError(firstError.msg);
		}
		if (typeof detail === 'object') return JSON.stringify(detail);
		return String(detail);
	}
	if (error?.response?.data?.message) {
		return error.response.data.message;
	}
	
	// Si c'est une erreur avec status direct (autres libs)
	if (error?.status) {
		return getHttpErrorMessage(error.status);
	}
	
	// Si c'est une erreur avec statusCode
	if (error?.statusCode) {
		return getHttpErrorMessage(error.statusCode);
	}
	
	// Si c'est une string avec "403" ou autre code HTTP
	if (typeof error === 'string') {
		// Détecter si c'est une erreur réseau
		if (error === 'Network Error' || 
		    error.includes('Failed to fetch') ||
		    error.includes('ECONNREFUSED') ||
		    error.includes('net::ERR_CONNECTION_REFUSED')) {
			return ERROR_MESSAGES.NETWORK.OFFLINE;
		}
		// Détecter si c'est une erreur de connexion interrompue
		if (error.includes('ABORTED') ||
		    error.includes('abort') ||
		    error.includes('AbortError')) {
			return ERROR_MESSAGES.NETWORK.ABORTED;
		}
		
		const statusMatch = error.match(/\b(400|401|403|404|409|422|429|500|502|503|504)\b/);
		if (statusMatch) {
			return getHttpErrorMessage(parseInt(statusMatch[1]));
		}
		return error;
	}
	
	// Si c'est un Error object avec message
	if (error instanceof Error) {
		// Détecter si le serveur n'est pas accessible (Network Error)
		if (error.message === 'Network Error' || 
		    error.message.includes('Failed to fetch') ||
		    error.message.includes('ECONNREFUSED') ||
		    error.message.includes('net::ERR_CONNECTION_REFUSED')) {
			return ERROR_MESSAGES.NETWORK.OFFLINE;
		}
		// Détecter si c'est une erreur de connexion interrompue
		if (error.message.includes('ABORTED') ||
		    error.message.includes('abort') ||
		    error.name === 'AbortError') {
			return ERROR_MESSAGES.NETWORK.ABORTED;
		}
		
		// Essayer d'extraire un code HTTP du message
		const statusMatch = error.message.match(/\b(400|401|403|404|409|422|429|500|502|503|504)\b/);
		if (statusMatch) {
			return getHttpErrorMessage(parseInt(statusMatch[1]));
		}
		return error.message;
	}
	
	// Si c'est une erreur avec message (objet générique)
	if (error?.message) {
		// Détecter si le serveur n'est pas accessible
		if (error.message === 'Network Error' || 
		    error.message.includes('Failed to fetch') ||
		    error.message.includes('ECONNREFUSED') ||
		    error.message.includes('net::ERR_CONNECTION_REFUSED')) {
			return ERROR_MESSAGES.NETWORK.OFFLINE;
		}
		// Détecter si c'est une erreur de connexion interrompue
		if (error.message.includes('ABORTED') ||
		    error.message.includes('abort') ||
		    error.name === 'AbortError') {
			return ERROR_MESSAGES.NETWORK.ABORTED;
		}
		
		const statusMatch = error.message.match(/\b(400|401|403|404|409|422|429|500|502|503|504)\b/);
		if (statusMatch) {
			return getHttpErrorMessage(parseInt(statusMatch[1]));
		}
		return error.message;
	}
	
	// Fallback
	return ERROR_MESSAGES.NETWORK.UNKNOWN;
}

