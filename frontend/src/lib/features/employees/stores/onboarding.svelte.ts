import type { Employee, EmergencyContact, Child } from '../types/types';

export type OnboardingStep = 'identity' | 'account' | 'contract' | 'documents' | 'family';

export interface DocumentItem {
	id: string;
	label: string;
	type: string;
	file: File | null;
}

export interface OnboardingData {
	identity: Partial<Employee>;
	account: {
		createAccount: boolean;
		groupSlug: string;
	};
	contract: {
		jobTitle: string;
		department: string;
		departmentId: string;
		positionId: string;
		location: string;
		contractType: string;
		salary: number;
		startDate: string;
	};
	documents: DocumentItem[];
	family: {
		emergencyContacts: EmergencyContact[];
		children: Child[];
	};
}

export class OnboardingStore {
	currentStep = $state<OnboardingStep>('identity');

	// Explicitly initialize all fields for better reactivity in Svelte 5
	data = $state<OnboardingData>({
		identity: {
			name: '',
			email: '',
			phone: '',
			birthDate: ''
		},
		account: {
			createAccount: false,
			groupSlug: ''
		},
		contract: {
			jobTitle: '',
			department: '',
			departmentId: '',
			positionId: '',
			location: '',
			contractType: '',
			salary: 0,
			startDate: ''
		},
		documents: [],
		family: {
			emergencyContacts: [],
			children: []
		}
	});

	steps: { id: OnboardingStep; label: string; icon: string }[] = [
		{ id: 'identity', label: 'Identité', icon: 'user' },
		{ id: 'account', label: 'Compte & Accès', icon: 'shield-check' },
		{ id: 'contract', label: 'Contrat', icon: 'file-text' },
		{ id: 'documents', label: 'Documents', icon: 'files' },
		{ id: 'family', label: 'Famille', icon: 'users' }
	];

	currentStepIndex = $derived(this.steps.findIndex((s) => s.id === this.currentStep));
	progress = $derived(((this.currentStepIndex + 1) / this.steps.length) * 100);

	// Compliance checklist
	compliance = $derived.by(() => {
		const issues: string[] = [];
		if (!this.data.identity.name) issues.push('Nom manquant');
		if (!this.data.identity.email) issues.push('Email manquant');
		if (!this.data.contract.jobTitle) issues.push('Poste non renseigné');
		if (!this.data.contract.startDate) issues.push('Date de début manquante');
		return issues;
	});

	nextStep() {
		const index = this.currentStepIndex;
		if (index < this.steps.length - 1) {
			this.currentStep = this.steps[index + 1].id;
		}
	}

	prevStep() {
		const index = this.currentStepIndex;
		if (index > 0) {
			this.currentStep = this.steps[index - 1].id;
		}
	}

	setStep(step: OnboardingStep) {
		this.currentStep = step;
	}

	updateIdentity(data: Partial<Employee>) {
		Object.assign(this.data.identity, data);
	}

	updateContract(data: Partial<OnboardingData['contract']>) {
		Object.assign(this.data.contract, data);
	}

	addEmergencyContact(contact: EmergencyContact) {
		this.data.family.emergencyContacts.push(contact);
	}

	removeEmergencyContact(id: string) {
		this.data.family.emergencyContacts = this.data.family.emergencyContacts.filter(
			(c) => c.id !== id
		);
	}

	updateEmergencyContact(id: string, updates: Partial<EmergencyContact>) {
		const index = this.data.family.emergencyContacts.findIndex((c) => c.id === id);
		if (index !== -1) {
			this.data.family.emergencyContacts[index] = {
				...this.data.family.emergencyContacts[index],
				...updates
			};
		}
	}

	addChild(child: Child) {
		this.data.family.children.push(child);
	}

	removeChild(id: string) {
		this.data.family.children = this.data.family.children.filter((c) => c.id !== id);
	}

	updateChild(id: string, updates: Partial<Child>) {
		const index = this.data.family.children.findIndex((c) => c.id === id);
		if (index !== -1) {
			this.data.family.children[index] = { ...this.data.family.children[index], ...updates };
		}
	}

	addDocument(doc: DocumentItem) {
		this.data.documents.push(doc);
	}

	removeDocument(id: string) {
		this.data.documents = this.data.documents.filter((d) => d.id !== id);
	}

	updateDocument(id: string, updates: Partial<DocumentItem>) {
		const index = this.data.documents.findIndex((d) => d.id === id);
		if (index !== -1) {
			this.data.documents[index] = { ...this.data.documents[index], ...updates };
		}
	}

	// --- Draft Management ---

	private STORAGE_KEY = 'oxiliere_onboarding_draft';
	hasDraft = $state(false);
	lastSaved = $state<string | null>(null);
	isSyncing = $state(false);
	isAutoSaveEnabled = $state(false);
	isRestoring = $state(false); // Flag to prevent auto-save during load
	isRestoredDraft = $state(false); // Flag to indicate session was restored from draft
	private saveTimeout: any = null;

	constructor() {
		this.checkDraft();
	}

	/**
	 * Checks if a draft exists in localStorage and retrieves the timestamp
	 */
	checkDraft() {
		if (typeof localStorage !== 'undefined') {
			const saved = localStorage.getItem(this.STORAGE_KEY);
			this.hasDraft = saved !== null;
			if (saved) {
				try {
					const parsed = JSON.parse(saved);
					if (parsed.timestamp) {
						const date = new Date(parsed.timestamp);
						this.lastSaved = date.toLocaleTimeString('fr-FR', {
							hour: '2-digit',
							minute: '2-digit'
						});
					}
				} catch (e) {
					// Keep as silent or standard error
				}
			}
		}
	}

	/**
	 * Triggers a debounced auto-save
	 */
	triggerAutoSave() {
		if (this.isRestoring) return; // Never auto-save while restoring

		if (this.saveTimeout) clearTimeout(this.saveTimeout);
		this.isSyncing = true;
		this.saveTimeout = setTimeout(() => {
			this.saveDraft();
		}, 1500);
	}

	/**
	 * Persists current state to localStorage
	 */
	saveDraft() {
		if (this.isRestoring) return false;

		try {
			const timestamp = new Date().toISOString();
			const dataToSave = JSON.parse(JSON.stringify(this.data));
			localStorage.setItem(
				this.STORAGE_KEY,
				JSON.stringify({
					data: dataToSave,
					currentStep: this.currentStep,
					timestamp
				})
			);
			this.hasDraft = true;
			this.lastSaved = new Date(timestamp).toLocaleTimeString('fr-FR', {
				hour: '2-digit',
				minute: '2-digit'
			});
			this.isSyncing = false;
			return true;
		} catch (e) {
			console.error('Failed to save draft', e);
			this.isSyncing = false;
			return false;
		}
	}

	/**
	 * Loads draft data into the store.
	 * Atomic operation to prevent race conditions with UI effects.
	 */
	loadDraft() {
		try {
			const saved = localStorage.getItem(this.STORAGE_KEY);
			if (saved) {
				const parsed = JSON.parse(saved);

				// Use a restoration guard to prevent any side-effects during state swapping
				this.isRestoring = true;

				if (parsed.data) {
					// Deep assignment to ensure reactivity triggers correctly
					if (parsed.data.identity) Object.assign(this.data.identity, parsed.data.identity);
					if (parsed.data.contract) Object.assign(this.data.contract, parsed.data.contract);
					this.data.documents = parsed.data.documents || [];
					this.data.family.emergencyContacts = parsed.data.family.emergencyContacts || [];
					this.data.family.children = parsed.data.family.children || [];
				}

				this.currentStep = parsed.currentStep || 'identity';
				this.hasDraft = true;
				this.checkDraft();

				this.isAutoSaveEnabled = true;
				this.isRestoring = false;
				this.isRestoredDraft = true;

				return true;
			}
		} catch (e) {
			console.error('Failed to load draft', e);
			this.isRestoring = false;
		}
		return false;
	}

	/**
	 * Removes the draft from localStorage
	 */
	clearDraft() {
		localStorage.removeItem(this.STORAGE_KEY);
		this.hasDraft = false;
		this.lastSaved = null;
		this.isRestoredDraft = false;
	}

	/**
	 * Resets the store to its default initial state.
	 * Synchronous operation to prevent accidental auto-save triggers.
	 */
	reset() {
		// Disable auto-save and set restoration guard BEFORE mutating data
		this.isAutoSaveEnabled = false;
		this.isRestoring = true;
		this.isRestoredDraft = false;

		this.currentStep = 'identity';

		// Explicit property-by-property reset to maintain Proxy integrity
		this.data.identity.name = '';
		this.data.identity.email = '';
		this.data.identity.phone = '';
		this.data.identity.birthDate = '';

		this.data.account.createAccount = false;
		this.data.account.groupSlug = '';

		this.data.contract.jobTitle = '';
		this.data.contract.department = '';
		this.data.contract.departmentId = '';
		this.data.contract.positionId = '';
		this.data.contract.location = '';
		this.data.contract.contractType = '';
		this.data.contract.salary = 0;
		this.data.contract.startDate = '';

		this.data.documents = [];
		this.data.family.emergencyContacts = [];
		this.data.family.children = [];

		// End restoration phase
		this.isRestoring = false;
	}
}

export const onboardingStore = new OnboardingStore();
