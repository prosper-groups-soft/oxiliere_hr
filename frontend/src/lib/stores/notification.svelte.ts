import { toast } from '@/utilities/ui/toast';

export type AlertDialogVariant = 'info' | 'danger' | 'warning' | 'success';

type ToastOpts = { duration?: number; id?: string | number };

/** ponytail: dedup window 2.5s — augmente si toasts légitimes identiques trop proches */
const DEDUP_WINDOW_MS = 2500;
const _lastToast = new Map<string, number>();

function shouldShow(variant: string, message: string, id?: string | number): boolean {
	if (id != null) return true; // caller-managed dedup via id
	const key = `${variant}:${message}`;
	const now = Date.now();
	const prev = _lastToast.get(key);
	if (prev != null && now - prev < DEDUP_WINDOW_MS) return false;
	_lastToast.set(key, now);
	// prune old entries
	for (const [k, t] of _lastToast) if (now - t > DEDUP_WINDOW_MS) _lastToast.delete(k);
	return true;
}


export interface ConfirmRequest {
	title: string;
	message: string;
	type?: AlertDialogVariant;
	yesText?: string;
	noText?: string;
	onYes?: ((value?: string) => void) | ((value?: string) => Promise<any>);
	onNo?: () => void;
	/** Si renseigné, affiche un textarea dans le dialog */
	inputLabel?: string;
	/** Valeur saisie dans le textarea (bindée) */
	inputValue?: string;
}


class NotificationStore {
	/** Ask for confirmation */
	confirmRequest = $state<ConfirmRequest | null>(null);

	// Toast — dedup identical variant+message within DEDUP_WINDOW_MS

	readonly toast = {
		success: (message: string, options?: ToastOpts) => {
			if (!shouldShow('success', message, options?.id)) return;
			toast.success(message, options);
		},
		error: (message: string, options?: ToastOpts) => {
			if (!shouldShow('error', message, options?.id)) return;
			toast.error(message, options);
		},
		warning: (message: string, options?: ToastOpts) => {
			if (!shouldShow('warning', message, options?.id)) return;
			toast.warning(message, options);
		},
		info: (message: string, options?: ToastOpts) => {
			if (!shouldShow('info', message, options?.id)) return;
			toast.info(message, options);
		},
		dismiss: (id?: string | number) => toast.dismiss(id)
	};

	// Confirmation

	/**
	 * Opens the global AlertDialog.
	 *
	 * @example
	 * notification.confirm({
	 *   title: 'Delete?',
	 *   message: 'This action is irreversible.',
	 *   type: 'danger',
	 *   yesText: 'Delete',
	 *   onYes: () => store.delete(id),
	 * });
	 */
	confirm(request: ConfirmRequest) {
		// Reset inputValue in case it was used before
		if (!request.inputValue) request.inputValue = '';
		this.confirmRequest = request;
	}

	/** Called by ConfirmDialog: closes the modal */
	_close() {
		this.confirmRequest = null;
	}
}


export const notification = new NotificationStore();

