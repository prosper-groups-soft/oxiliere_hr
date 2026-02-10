export interface ValidationErrorDetail {
  type: string;
  loc: (string | number)[];
  msg: string;
}

export interface UnprocessableEntityResponse {
  detail: ValidationErrorDetail[];
}

export interface FieldError {
  field: string;
  message: string;
}


export interface OxilereHttpError {
  detail: string;
  code: string;
  errors?: Record<string, any>;
}


class OxilereError extends Error {
  constructor(message: string, public code: number, public details?: FieldError[] | OxilereHttpError | null) {
    super(message);
    this.name = "OxilereError";
    this.code = code;
    this.details = details;
  }

  static parse(response: any): OxilereError {
    const statusCode = response?.code === 'ERR_NETWORK' ? 600 : response?.status ? response?.status : 601;
    let details: FieldError[] | OxilereHttpError | null = null;

    try {
      const data = response.data;

      if (statusCode === 422) {
        details = parse_unprocessable_entity(data);
      } else {
        details = parse_http_error(data);
      }
    } catch (e) {
      details = null;
    }

    return new OxilereError(this.get_message_from_code(statusCode), statusCode, details);
  }

  static get_message_from_code(code: number): string {
    switch (code) {
      case 400:
        return 'Requête invalide';
      case 401:
        return 'Non autorisé';
      case 403:
        return 'Accès refusé';
      case 404:
        return 'Ressource non trouvée';
      case 422:
        return 'Erreur de validation';
      case 500:
        return 'Erreur serveur';
      case 502:
        return 'Passerelle incorrecte';
      case 503:
        return 'Service indisponible';
      case 504:
        return 'Délai d\'attente dépassé';
      case 600:
        return 'Problème de connexion';
      default:
        return 'Une erreur est survenue';
    }
  }

  mappedErrors(maps: Record<string, string>): FieldError[] {
    if (!this.isValidationError() || !Array.isArray(this.details)) {
      return [];
    }
    return map_field_error(this.details, maps);
  }

  isValidationError() {
    return this.code === 422;
  }

  isForbiddenError() {
    return this.code === 403;
  }

  isNotFoundError() {
    return this.code === 404;
  }

  isUnauthorizedError() {
    return this.code === 401;
  }

  isNetworkError() {
    return this.code === 600;
  }

  isBadRequestError() {
    return this.code === 400;
  }
}


function parse_unprocessable_entity(data: unknown): FieldError[] {
  if (!data || typeof data !== 'object' || !('detail' in data)) {
    return [];
  }

  const response = data as UnprocessableEntityResponse;

  if (!Array.isArray(response.detail)) {
    return [];
  }

  return response.detail.map((error: ValidationErrorDetail): FieldError => ({
    field: String(error.loc?.slice(-1)[0] || ''),
    message: error.msg || ''
  }));
}

function parse_http_error(data: unknown): OxilereHttpError | null {
  if (!data || typeof data !== 'object') {
    return null;
  }

  const httpError = data as Partial<OxilereHttpError>;

  return {
    detail: httpError.detail || 'An error occurred',
    code: httpError.code || 'unknown_error',
    errors: httpError.errors
  };
}


function map_field_error(errors: FieldError[], maps: Record<string, string>) {
  return errors.map((error: FieldError): FieldError => ({
    field: maps[error.field] || error.field,
    message: error.message
  }));
}


export default OxilereError;

