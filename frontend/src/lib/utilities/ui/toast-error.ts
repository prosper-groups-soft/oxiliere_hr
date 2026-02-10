import {
    ForbiddenErrorToast,
    NetworkErrorToast,
    NotFoundErrorToast,
    ServerErrorToast,
    UnauthorizedErrorToast,
    UnknownErrorToast,
    ValidationErrorToast
} from '@/components/shared/errors/toast';
import { toast } from 'svelte-sonner';
import OxilereError from '../http/errors';


/**
 * Show the error toast based of type of OxiliereError error
 * @param error - Error to show
 * @param duration - Duration of showing toast in ms (default value : 5000)
 */
export function showErrorToast(error: OxilereError, duration: number = 5000) {
  const options = {
    duration,
    dismissible: true
  };

  if (error.isNetworkError()) {
    toast.error(NetworkErrorToast, {
      ...options,
      componentProps: { error }
    });
  } else if (error.isValidationError()) {
    toast.error(ValidationErrorToast, {
      ...options,
      componentProps: { error }
    });
  } else if (error.isNotFoundError()) {
    toast.error(NotFoundErrorToast, {
      ...options,
      componentProps: { error }
    });
  } else if (error.isForbiddenError()) {
    toast.error(ForbiddenErrorToast, {
      ...options,
      componentProps: { error }
    });
  } else if (error.isUnauthorizedError()) {
    toast.error(UnauthorizedErrorToast, {
      ...options,
      componentProps: { error }
    });
  } else if (error.code >= 500 && error.code < 600) {
    toast.error(ServerErrorToast, {
      ...options,
      componentProps: { error }
    });
  } else {
    toast.error(UnknownErrorToast, {
      ...options,
      componentProps: { error }
    });
  }
}


/**
 * Show the error toast as of whatever error
 * Automatically convert the error on OxiliereError if needed
 */
export function showError(error: any, duration: number = 5000) {
  let oxilereError: OxilereError;

  if (error instanceof OxilereError) {
    oxilereError = error;
  } else {
    oxilereError = OxilereError.parse(error);
  }

  showErrorToast(oxilereError, duration);
}

