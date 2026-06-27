import { toast } from '@/utilities/ui/toast';

export type AlertDialogVariant = 'info' | 'danger' | 'warning' | 'success';


export interface ConfirmRequest {
	title: string;
	message: string;
	type?: AlertDialogVariant;
	yesText?: string;
	noText?: string;
	onYes?: (() => void) | (() => Promise<any>);
	onNo?: () => void;
}


class NotificationStore {
	/** Ask for confirmation */
	confirmRequest = $state<ConfirmRequest | null>(null);

	// Toast

	readonly toast = {
		success: (message: string, options?: { duration?: number }) => toast.success(message, options),

		error: (message: string, options?: { duration?: number }) => toast.error(message, options),

		warning: (message: string, options?: { duration?: number }) => toast.warning(message, options),

		info: (message: string, options?: { duration?: number }) => toast.info(message, options),

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
		this.confirmRequest = request;
	}

	/** Called by ConfirmDialog: closes the modal */
	_close() {
		this.confirmRequest = null;
	}
}


export const notification = new NotificationStore();

