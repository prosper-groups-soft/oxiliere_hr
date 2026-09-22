import type { Document } from '../types/types';

class PreviewStore {
	isOpen = $state(false);
	activeDoc = $state<Document | null>(null);

	open(doc: Document) {
		this.activeDoc = doc;
		this.isOpen = true;
	}

	close() {
		this.isOpen = false;
		this.activeDoc = null;
	}
}

export const previewStore = new PreviewStore();
