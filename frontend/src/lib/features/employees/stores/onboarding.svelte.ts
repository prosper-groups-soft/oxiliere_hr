import type {
	Employee,
	EmergencyContact,
	Child,
	OnboardingSubmitData,
	OnboardingDocumentItem,
	OnboardingResult,
	OnboardingEducationItem,
	ContractPayElementItem
} from '../types/types';

import { onboardingService } from '../services/onboarding.service';
import { validateFullOnboarding, validateStep } from '../schemas/onboarding.schema';
import { notification } from '@/stores/notification.svelte';


export type OnboardingStep = 'identity' | 'account' | 'contract' | 'documents' | 'family' | 'education';


export function validateStepLocal(
	step: 'identity' | 'account' | 'contract' | 'family' | 'documents' | 'education',
	data: any
): { success: boolean; errors: string[] } {
	switch (step) {
		case 'family':
			// Family est optionnel, toujours valide
			return { success: true, errors: [] };
		case 'documents':
			// Documents est optionnel, toujours valide
			return { success: true, errors: [] };
		case 'education':
			// Education est optionnel, toujours valide
			return { success: true, errors: [] };
		default:
			return validateStep(step, data);
	}
}


export interface DocumentItem extends OnboardingDocumentItem {}


export interface OnboardingData {
	identity: {
		profile_photo?: File | null;
		first_name: string;
		middle_name: string;
		last_name: string;
		email: string;
		phone: string;
		birthdate: string;
		gender: 'MALE' | 'FEMALE' | 'NOT_SPECIFIED' | '';
		nationality: string;
		marital_status: 'SINGLE' | 'MARRIED' | 'DIVORCED' | 'WIDOWED' | '';
		work_site: string;
		address?: {
			number?: string;
			street?: string;
			municipality?: string;
			city?: string;
			province?: string;
			country_code?: string;
		};
	};
	account: {
		create_account: boolean;
		group_slug: string;
	};
	contract: {
		position_id: string;
		seniority_level_id: string;
		contract_type: 'CDI' | 'CDD' | 'INTERNSHIP' | 'PROBATION' | 'FREELANCE' | '';
		salary: number;
		hire_date: string;
		remuneration_type: 'FIXED' | 'HOURLY';
		salary_base_type: 'GROSS' | 'NET';
		currency: 'CDF' | 'USD' | 'EUR';
		end_date: string;
		is_active: boolean;
		initial_status: 'ACTIVE' | 'PROBATION' | 'PENDING';
		// Métamodèle (Règle 5)
		contractual_clauses: string;
		// S10 — éléments de paie sélectionnés pendant l'onboarding
		contract_adjustments: ContractPayElementItem[];
	};
	documents: DocumentItem[];
	family: {
		emergencyContacts: EmergencyContact[];
		children: Child[];
	};
	education: {
		educations: OnboardingEducationItem[];
	};
}


export class OnboardingStore {
	currentStep = $state<OnboardingStep>('identity');

	// Explicitly initialize all fields for better reactivity in Svelte 5
	data = $state<OnboardingData>({
		identity: {
			profile_photo: null,
			first_name: '',
			middle_name: '',
			last_name: '',
			email: '',
			phone: '',
			birthdate: '',
			gender: '',
			nationality: '',
			marital_status: '',
			work_site: '',
			address: {
				number: '',
				street: '',
				municipality: '',
				city: '',
				province: '',
				country_code: ''
			}
		},
		account: {
			create_account: false,
			group_slug: ''
		},
		contract: {
			position_id: '',
			seniority_level_id: '',
			contract_type: '',
			salary: 0,
			hire_date: '',
			remuneration_type: 'FIXED',
			salary_base_type: 'NET',
			currency: 'CDF',
			end_date: '',
			is_active: true,
			initial_status: 'PENDING',
			contractual_clauses: '',
			contract_adjustments: []
		},
		documents: [],
		family: {
			emergencyContacts: [],
			children: []
		},
		education: {
			educations: []
		}
	});

	steps: { id: OnboardingStep; label: string; icon: string }[] = [
		{ id: 'identity', label: 'Identité', icon: 'user' },
		{ id: 'account', label: 'Compte & Accès', icon: 'shield-check' },
		{ id: 'contract', label: 'Contrat', icon: 'file-text' },
		{ id: 'documents', label: 'Documents', icon: 'files' },
		{ id: 'family', label: 'Famille', icon: 'users' },
		{ id: 'education', label: 'Éducation', icon: 'graduation-cap' }
	];

	currentStepIndex = $derived(this.steps.findIndex((s) => s.id === this.currentStep));
	progress = $derived(((this.currentStepIndex + 1) / this.steps.length) * 100);

	// Compliance checklist - validation par étape
	compliance = $derived.by(() => {
		const issues: string[] = [];

		// Validation Identity (champs obligatoires uniquement)
		if (!this.data.identity.first_name) {
			issues.push('Identité: Le prénom est requis');
		}
		if (!this.data.identity.last_name) {
			issues.push('Identité: Le nom est requis');
		}
		if (!this.data.identity.email) {
			issues.push('Identité: L\'email est requis');
		} else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(this.data.identity.email)) {
			issues.push('Identité: Format d\'email invalide');
		}

		// Validation Contract (essentiel)
		if (!this.data.contract.position_id) {
			issues.push('Contrat: Le poste est requis');
		}
		if (!this.data.contract.seniority_level_id) {
			issues.push('Contrat: Le niveau de séniorité est requis');
		}
		if (!this.data.contract.contract_type) {
			issues.push('Contrat: Le type de contrat est requis');
		}
		if (!this.data.contract.salary || this.data.contract.salary <= 0) {
			issues.push('Contrat: Le salaire est requis');
		}
		if (!this.data.contract.hire_date) {
			issues.push('Contrat: La date de début est requise');
		} else if (isNaN(Date.parse(this.data.contract.hire_date))) {
			issues.push('Contrat: Date de début invalide');
		}

		return issues;
	});

	// Flag pour suivre la soumission en cours
	isSubmitting = $state(false);
	submitError = $state<string | null>(null);

	nextStep() {
		const index = this.currentStepIndex;
		if (index < this.steps.length - 1) {
			this.currentStep = this.steps[index + 1].id;
			this.triggerAutoSave();
		}
	}

	prevStep() {
		const index = this.currentStepIndex;
		if (index > 0) {
			this.currentStep = this.steps[index - 1].id;
			this.triggerAutoSave();
		}
	}

	setStep(step: OnboardingStep) {
		this.currentStep = step;
		this.triggerAutoSave();
	}

	/**
	 * Valide l'étape actuelle
	 */
	validateCurrentStep(): { success: boolean; errors: string[] } {
		const result = validateStepLocal(this.currentStep, this.data[this.currentStep]);
		if (result.success) {
			return { success: true, errors: [] };
		}
		return { success: false, errors: result.errors };
	}

	/**
	 * Prépare les données pour la soumission
	 */
	private prepareSubmitData(): OnboardingSubmitData {
		return {
			identity: {
				profile_photo: this.data.identity.profile_photo,
				first_name: this.data.identity.first_name,
				middle_name: this.data.identity.middle_name || undefined,
				last_name: this.data.identity.last_name,
				email: this.data.identity.email,
				phone: this.data.identity.phone || undefined,
				birthdate: this.data.identity.birthdate || undefined,
				gender: this.data.identity.gender || undefined,
				nationality: this.data.identity.nationality || undefined,
				marital_status: this.data.identity.marital_status || undefined,
				work_site: this.data.identity.work_site || undefined,
				address: this.data.identity.address
			},
			account: {
				create_account: this.data.account.create_account,
				group_slug: this.data.account.group_slug || undefined
			},
			contract: {
				position_id: this.data.contract.position_id,
				seniority_level_id: this.data.contract.seniority_level_id,
				contract_type: this.data.contract.contract_type as any,
				salary: this.data.contract.salary,
				hire_date: this.data.contract.hire_date,
				remuneration_type: this.data.contract.remuneration_type,
				salary_base_type: this.data.contract.salary_base_type,
				currency: this.data.contract.currency,
				end_date: this.data.contract.end_date || undefined,
				is_active: this.data.contract.is_active,
				contractual_clauses: this.data.contract.contractual_clauses,
				contract_adjustments: this.data.contract.contract_adjustments
			},
			documents: this.data.documents,
			family: {
				emergency_contacts: this.data.family.emergencyContacts,
				children: this.data.family.children
			},
			education: {
				educations: this.data.education.educations
			}
		};
	}

	/**
	 * Soumet l'onboarding complet au backend
	 */
	async submit(): Promise<OnboardingResult> {
		// Validation complète
		const validation = validateFullOnboarding(this.prepareSubmitData());
		if (!validation.success) {
			this.submitError = validation.errors.join(', ');
			notification.toast.error('Veuillez corriger les erreurs avant de soumettre');
			return { success: false, errors: { general: validation.errors } };
		}

		this.isSubmitting = true;
		this.submitError = null;

		try {
			const result = await onboardingService.submitFullOnboarding(validation.data);

			if (result.success) {
				// Clear le draft local après succès
				this.clearDraft();
				notification.toast.success(
					`Employé ${result.employee?.matricule} créé avec succès!`
				);
			} else {
				this.submitError = result.errors?.general?.[0] || 'Échec de la création';
			}

			return result;
		} catch (error: any) {
			const message = error.message || 'Erreur inattendue';
			this.submitError = message;
			notification.toast.error(`Erreur: ${message}`);
			return { success: false, errors: { general: [message] } };
		} finally {
			this.isSubmitting = false;
		}
	}

	updateIdentity(data: Partial<Employee>) {
		Object.assign(this.data.identity, data);
		this.triggerAutoSave();
	}

	updateContract(data: Partial<OnboardingData['contract']>) {
		Object.assign(this.data.contract, data);
		this.triggerAutoSave();
	}

	// Wrappers pour auto-save sur les champs individuels
	setIdentityField<K extends keyof OnboardingData['identity']>(
		field: K, 
		value: OnboardingData['identity'][K]
	) {
		this.data.identity[field] = value;
		this.triggerAutoSave();
	}

	setContractField<K extends keyof OnboardingData['contract']>(
		field: K, 
		value: OnboardingData['contract'][K]
	) {
		this.data.contract[field] = value;
		this.triggerAutoSave();
	}

	setAccountField<K extends keyof OnboardingData['account']>(
		field: K, 
		value: OnboardingData['account'][K]
	) {
		this.data.account[field] = value;
		this.triggerAutoSave();
	}

	setAddressField<K extends keyof NonNullable<OnboardingData['identity']['address']>>(
		field: K, 
		value: NonNullable<OnboardingData['identity']['address']>[K]
	) {
		if (!this.data.identity.address) {
			this.data.identity.address = {};
		}
		this.data.identity.address[field] = value;
		this.triggerAutoSave();
	}

	addEmergencyContact(contact: EmergencyContact) {
		this.data.family.emergencyContacts.push(contact);
		this.triggerAutoSave();
	}

	removeEmergencyContact(id: string) {
		this.data.family.emergencyContacts = this.data.family.emergencyContacts.filter(
			(c: EmergencyContact) => c.id !== id
		);
		this.triggerAutoSave();
	}

	updateEmergencyContact(id: string, updates: Partial<EmergencyContact>) {
		const index = this.data.family.emergencyContacts.findIndex((c: EmergencyContact) => c.id === id);
		if (index !== -1) {
			this.data.family.emergencyContacts[index] = {
				...this.data.family.emergencyContacts[index],
				...updates
			};
			this.triggerAutoSave();
		}
	}

	addChild(child: Child) {
		this.data.family.children.push(child);
		this.triggerAutoSave();
	}

	removeChild(id: string) {
		this.data.family.children = this.data.family.children.filter((c: Child) => c.id !== id);
		this.triggerAutoSave();
	}

	updateChild(id: string, updates: Partial<Child>) {
		const index = this.data.family.children.findIndex((c: Child) => c.id === id);
		if (index !== -1) {
			this.data.family.children[index] = { ...this.data.family.children[index], ...updates };
			this.triggerAutoSave();
		}
	}

	addDocument(doc: DocumentItem) {
		this.data.documents.push(doc);
		this.triggerAutoSave();
	}

	removeDocument(id: string) {
		this.data.documents = this.data.documents.filter((d) => d.id !== id);
		this.triggerAutoSave();
	}

	updateDocument(id: string, updates: Partial<DocumentItem>) {
		const index = this.data.documents.findIndex((d) => d.id === id);
		if (index !== -1) {
			this.data.documents[index] = { ...this.data.documents[index], ...updates };
			this.triggerAutoSave();
		}
	}

	addEducation(education: OnboardingEducationItem) {
		this.data.education.educations.push(education);
		this.triggerAutoSave();
	}

	removeEducation(index: number) {
		this.data.education.educations.splice(index, 1);
		this.triggerAutoSave();
	}

	updateEducation(index: number, updates: Partial<OnboardingEducationItem>) {
		if (index >= 0 && index < this.data.education.educations.length) {
			this.data.education.educations[index] = {
				...this.data.education.educations[index],
				...updates
			};
			this.triggerAutoSave();
		}
	}

	// --- Draft Management ---

	private STORAGE_KEY = 'oxiliere_onboarding_draft';
	private ARCHIVE_KEY = 'oxiliere_onboarding_archive';
	
	hasDraft = $state(false);
	lastSaved = $state<string | null>(null);
	isSyncing = $state(false);
	isAutoSaveEnabled = $state(false);
	isRestoring = $state(false); // Flag to prevent auto-save during load
	isRestoredDraft = $state(false); // Flag to indicate session was restored from draft
	archivedDrafts = $state<any[]>([]); // Reactive archive state
	private saveTimeout: any = null;

	// Métadonnées du brouillon
	draftMetadata = $state<{
		employeeName: string;
		createdAt: string;
		status: 'active' | 'submitted';
	} | null>(null);

	constructor() {
		this.checkDraft();
		this.loadArchivedDrafts(); // Load archive on init
		this.isAutoSaveEnabled = true;
	}

	/**
	 * Loads archived drafts from localStorage
	 */
	private loadArchivedDrafts() {
		if (typeof localStorage === 'undefined') {
			this.archivedDrafts = [];
			return;
		}
		try {
			const archive = localStorage.getItem(this.ARCHIVE_KEY);
			const drafts = archive ? JSON.parse(archive) : [];
			// Sort by archive date descending (most recent first)
			this.archivedDrafts = drafts.sort((a: any, b: any) => new Date(b.archivedAt).getTime() - new Date(a.archivedAt).getTime());
		} catch (e) {
			console.error('Failed to load archive', e);
			this.archivedDrafts = [];
		}
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
			
			// Créer ou mettre à jour les métadonnées
			const firstName = this.data.identity.first_name || '';
			const lastName = this.data.identity.last_name || '';
			const email = this.data.identity.email || '';
			const employeeName = `${firstName} ${lastName}`.trim() || email || 'Nouveau employé';
			
			if (!this.draftMetadata) {
				this.draftMetadata = {
					employeeName,
					createdAt: timestamp,
					status: 'active'
				};
			} else {
				this.draftMetadata.employeeName = employeeName;
			}
			
			localStorage.setItem(
				this.STORAGE_KEY,
				JSON.stringify({
					data: dataToSave,
					currentStep: this.currentStep,
					timestamp,
					metadata: this.draftMetadata
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
	 * Loads draft data into store.
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
					this.data.education.educations = parsed.data.education.educations || [];
				}

				this.currentStep = parsed.currentStep || 'identity';
				this.hasDraft = true;
				
				// Charger les métadonnées
				if (parsed.metadata) {
					this.draftMetadata = parsed.metadata;
				}
				
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
	 * Archives the draft instead of deleting it
	 */
	archiveDraft() {
		if (this.draftMetadata) {
			// Marquer comme soumis
			this.draftMetadata.status = 'submitted';
			
			// Sauvegarder dans l'archive
			const currentDraft = localStorage.getItem(this.STORAGE_KEY);
			if (currentDraft) {
				const parsed = JSON.parse(currentDraft);
				parsed.metadata = this.draftMetadata;
				
				// Récupérer l'archive existante
				const existingArchive = localStorage.getItem(this.ARCHIVE_KEY);
				const archive = existingArchive ? JSON.parse(existingArchive) : [];
				
				// Ajouter à l'archive
				archive.push({
					...parsed,
					archivedAt: new Date().toISOString()
				});
				
				// Garder seulement les 10 derniers brouillons
				if (archive.length > 10) {
					archive.splice(0, archive.length - 10);
				}
				
				localStorage.setItem(this.ARCHIVE_KEY, JSON.stringify(archive));
			}
		}
		
		// Nettoyer le brouillon actuel
		localStorage.removeItem(this.STORAGE_KEY);
		this.hasDraft = false;
		this.lastSaved = null;
		this.isRestoredDraft = false;
		this.draftMetadata = null;
		
		// Update reactive archive state
		this.loadArchivedDrafts();
	}

	/**
	 * Removes the draft from localStorage (suppression réelle)
	 */
	clearDraft() {
		// Supprimer le brouillon actuel sans l'archiver
		localStorage.removeItem(this.STORAGE_KEY);
		this.hasDraft = false;
		this.lastSaved = null;
		this.isRestoredDraft = false;
		this.draftMetadata = null;
	}

	/**
	 * Gets all archived drafts (returns reactive state)
	 */
	getArchivedDrafts() {
		return this.archivedDrafts;
	}

	/**
	 * Restores a draft from archive
	 */
	restoreFromArchive(archivedDraft: any) {
		try {
			// Désactiver l'auto-save pendant la restauration
			this.isRestoring = true;

			// Restaurer les données
			if (archivedDraft.data) {
				if (archivedDraft.data.identity) Object.assign(this.data.identity, archivedDraft.data.identity);
				if (archivedDraft.data.contract) Object.assign(this.data.contract, archivedDraft.data.contract);
				this.data.documents = archivedDraft.data.documents || [];
				this.data.family.emergencyContacts = archivedDraft.data.family.emergencyContacts || [];
				this.data.family.children = archivedDraft.data.family.children || [];
				this.data.education.educations = archivedDraft.data.education.educations || [];
			}

			this.currentStep = archivedDraft.currentStep || 'identity';
			
			// Restaurer les métadonnées
			this.draftMetadata = {
				employeeName: archivedDraft.metadata.employeeName,
				createdAt: archivedDraft.metadata.createdAt,
				status: 'active' // Remettre en actif
			};

			// Sauvegarder comme brouillon actuel
			this.saveDraft();

			this.isRestoring = false;
			this.isRestoredDraft = true;
			this.isAutoSaveEnabled = true;

			// Update reactive archive state
			this.loadArchivedDrafts();

			return true;
		} catch (e) {
			console.error('Failed to restore from archive', e);
			this.isRestoring = false;
			return false;
		}
	}

	/**
	 * Deletes a draft from archive
	 */
	deleteFromArchive(index: number) {
		try {
			const archive = [...this.archivedDrafts];
			archive.splice(index, 1);
			localStorage.setItem(this.ARCHIVE_KEY, JSON.stringify(archive));
			// Update reactive archive state
			this.loadArchivedDrafts();
			return true;
		} catch (e) {
			console.error('Failed to delete from archive', e);
			return false;
		}
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
		this.submitError = null;

		this.currentStep = 'identity';

		// Explicit property-by-property reset to maintain Proxy integrity
		this.data.identity.profile_photo = null;
		this.data.identity.first_name = '';
		this.data.identity.middle_name = '';
		this.data.identity.last_name = '';
		this.data.identity.email = '';
		this.data.identity.phone = '';
		this.data.identity.birthdate = '';
		this.data.identity.gender = '';
		this.data.identity.nationality = '';
		this.data.identity.marital_status = '';
		this.data.identity.work_site = '';
		this.data.identity.address = {
			number: '',
			street: '',
			municipality: '',
			city: '',
			province: '',
			country_code: ''
		};

		this.data.account.create_account = false;
		this.data.account.group_slug = '';

		this.data.contract.position_id = '';
		this.data.contract.seniority_level_id = '';
		this.data.contract.contract_type = '';
		this.data.contract.salary = 0;
		this.data.contract.hire_date = '';
		this.data.contract.remuneration_type = 'FIXED';
		this.data.contract.salary_base_type = 'NET';
		this.data.contract.currency = 'CDF';
		this.data.contract.end_date = '';
		this.data.contract.is_active = true;
		this.data.contract.initial_status = 'PENDING';
		this.data.contract.contractual_clauses = '';
		this.data.contract.contract_adjustments = [];

		this.data.documents = [];
		this.data.family.emergencyContacts = [];
		this.data.family.children = [];
		this.data.education.educations = [];

		// End restoration phase
		this.isRestoring = false;
	}
}


export const onboardingStore = new OnboardingStore();

