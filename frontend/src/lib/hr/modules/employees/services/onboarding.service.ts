import { onboardingEndpoint } from '../api/onboarding.endpoints';
import type {
	EmployeeCreate,
	EmployeeContractCreate,
	OnboardingSubmitData,
	OnboardingResult
} from '../types/types';
import { buildFullName } from "@/hr/utilities/common/employee.utils";
import { notification } from '@/hr/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/hr/constants/errors';
import type { QueryClient } from '@tanstack/svelte-query';


export const onboardingService = {
	/**
	 * Soumission complète de l'onboarding en 2 phases:
	 * Phase 1: Création employé (identity + account)
	 * Phase 2: Enrichissement (contract, photo, documents, family)
	 */
	async submitFullOnboarding(data: OnboardingSubmitData, queryClient?: QueryClient): Promise<OnboardingResult> {
		console.log('[OnboardingService] Starting full onboarding submission');
		
		// Mapping des relations françaises vers les valeurs de l'énumération backend
		const relationMapping: Record<string, string> = {
			'Parent': 'PARENT',
			'Enfant': 'CHILD',
			'Frère/Soeur': 'SIBLING',
			'Ami': 'FRIEND',
			'Conjoint': 'SPOUSE',
			'Partenaire': 'PARTNER',
			'Autre': 'OTHER'
		};
		
		// Variable pour tracker si l'employé a été créé (pour rollback)
		let createdEmployeeId: string | null = null;

		try {
			// ========== PHASE 1: Création de l'employé ==========
			const employeeCreateData: EmployeeCreate = {
				first_name: data.identity.first_name,
				middle_name: data.identity.middle_name,
				last_name: data.identity.last_name,
				email: data.identity.email,
				phone: data.identity.phone,
				gender: data.identity.gender || undefined,
				birthdate: data.identity.birthdate || undefined,
				nationality: data.identity.nationality || undefined,
				marital_status: data.identity.marital_status || undefined,
				work_site: data.identity.work_site,
				hire_date: data.contract.hire_date,
				create_account: data.account?.create_account || false,
				group_slug: data.account?.group_slug,
				initial_status: data.contract.initial_status || 'PROBATION'
			};

			console.log('[OnboardingService] Phase 1: Creating employee...');
			const employee = await onboardingEndpoint.createEmployee(employeeCreateData);
			createdEmployeeId = employee.id.toString();
			console.log('[OnboardingService] Employee created:', employee.matricule);

			// ========== PHASE 2: Enrichissement (HYBRIDE) ==========
			const employeeId = employee.id.toString();
			console.log('[OnboardingService] Phase 2: Starting hybrid enrichment...');

			// ÉTAPE 1: Opération critique séquentielle (contrat)
			const contractData: EmployeeContractCreate = {
				position_id: data.contract.position_id,
				seniority_level_id: data.contract.seniority_level_id,
				base_salary: data.contract.salary,
				contract_type: data.contract.contract_type,
				remuneration_type: data.contract.remuneration_type || "FIXED",
				salary_base_type: data.contract.salary_base_type || "BASE",
				start_date: data.contract.hire_date,
				end_date: data.contract.end_date || null,
				currency: data.contract.currency || "CDF",
				is_active: true,
				contractual_clauses: data.contract.contractual_clauses || ''
			};
			const contract = await onboardingEndpoint.createContract(employeeId, contractData);

			// ÉTAPE 2: Opérations indépendantes en parallèle
			console.log('[OnboardingService] Phase 2b: Starting parallel operations...');
			const parallelPromises: Promise<any>[] = [];

			// S10 — créer les éléments de paie sélectionnés pendant l'onboarding
			if (data.contract.contract_adjustments && data.contract.contract_adjustments.length > 0) {
				const payElementPromises = data.contract.contract_adjustments
					.filter((el: any) => el.adjustment_id || el.adjustment)
					.map((el: any) =>
						onboardingEndpoint.createContractPayElement(contract.id, {
							adjustment: el.adjustment_id || el.adjustment,
							custom_amount: el.custom_amount ?? null,
							custom_percentage: el.custom_percentage ?? null,
							start_period: el.start_period || data.contract.hire_date,
							end_period: el.end_period || null,
							is_active: el.is_active ?? true
						})
					);
				parallelPromises.push(Promise.all(payElementPromises));
			}

			// Photo de profil
			if (data.identity.profile_photo) {
				parallelPromises.push(
					onboardingEndpoint.uploadProfilePhoto(employeeId, data.identity.profile_photo)
						.then(() => console.log('[OnboardingService] Profile photo uploaded'))
				);
			}

			// Documents
			if (data.documents.length > 0) {
				const documentPromises = data.documents.map((doc) =>
					onboardingEndpoint.uploadDocument(employeeId, doc.file, {
						document_type: doc.document_type,
						document_number: doc.document_number,
						issue_date: doc.issue_date || undefined,
						expiry_date: doc.expiry_date || undefined
					})
				);
				parallelPromises.push(
					Promise.all(documentPromises)
						.then(() => console.log('[OnboardingService] All documents uploaded'))
				);
			}

			// Contacts d'urgence
			if (data.family.emergency_contacts.length > 0) {
				// Trier : contact primaire en premier, puis garder l'ordre d'ajout
				const sortedContacts = [...data.family.emergency_contacts].sort((a, b) => {
					if (a.primary && !b.primary) return -1;
					if (!a.primary && b.primary) return 1;
					return 0; // Garder l'ordre d'ajout sinon
				});
				
				const contactPromises = sortedContacts.map((contact, index) => {
					const priority = index + 1; // 1, 2, 3... selon l'ordre
					
					return onboardingEndpoint.addEmergencyContact(employeeId, {
						last_name: contact.name,
						phone: contact.phone,
						relation: relationMapping[contact.relation] || contact.relation,
						priority: priority,
						is_primary: contact.primary || (index === 0 && !sortedContacts.some(c => c.primary))
					});
				});
				parallelPromises.push(
					Promise.all(contactPromises)
						.then(() => console.log('[OnboardingService] All emergency contacts added'))
				);
			}

			// Enfants
			if (data.family.children.length > 0) {
				const childPromises = data.family.children.map((child) =>
					onboardingEndpoint.addChild(employeeId, {
						last_name: child.name,
						gender: child.gender,
						birthdate: child.birthDate,
						is_dependent: child.isDependent ?? true
					})
				);
				parallelPromises.push(
					Promise.all(childPromises)
						.then(() => console.log('[OnboardingService] All children added'))
				);
			}

			// Éducation
			if (data.education.educations.length > 0) {
				const educationPromises = data.education.educations.map((education) =>
					onboardingEndpoint.addEducation(employeeId, {
						degree: education.degree,
						institute: education.institute,
						major: education.major || undefined,
						location: education.location || undefined,
						start_year: education.start_year || undefined,
						end_year: education.end_year || undefined
					})
				);
				parallelPromises.push(
					Promise.all(educationPromises)
						.then(() => console.log('[OnboardingService] All educations added'))
				);
			}

			// Adresse
			if (data.identity.address && (
				data.identity.address.number ||
				data.identity.address.street ||
				data.identity.address.city
			)) {
				parallelPromises.push(
					onboardingEndpoint.addEmployeeAddress(employeeId, data.identity.address)
						.then(() => console.log('[OnboardingService] Address added'))
				);
			}

			// Exécuter toutes les opérations parallèles
			await Promise.all(parallelPromises);

			console.log('[OnboardingService] Onboarding completed successfully!');
			notification.toast.success(`Employé ${buildFullName(employee)} créé avec succès`);

			// Invalider le cache des employés pour refléter le nouvel employé
			if (queryClient) {
				queryClient.invalidateQueries({ queryKey: ['employees'] });
				queryClient.invalidateQueries({ queryKey: ['employee'] });
			}

			return {
				success: true,
				employee
			};
		} catch (error: any) {
			console.error('[OnboardingService] Onboarding failed:', error);
			
			// ========== ROLLBACK: Supprimer l'employé si créé ==========
			if (createdEmployeeId) {
				console.log('[OnboardingService] Rolling back: deleting employee', createdEmployeeId);
				try {
					await onboardingEndpoint.deleteEmployee(createdEmployeeId);
					console.log('[OnboardingService] Rollback successful: employee deleted');
				} catch (rollbackError) {
					console.error('[OnboardingService] Rollback failed:', rollbackError);
				}
			}
			
			// ========== Gestion des erreurs spécifiques ==========
			const errorData = error?.response?.data || error?.data;
			const errorMessage = errorData?.detail || '';
			
			// Détecter l'erreur d'email déjà existant (code 409)
			if (error?.status === 409 || error?.response?.status === 409) {
				if (errorData?.error === 'EMAIL_ALREADY_EXISTS') {
					const email = data.identity.email;
					notification.toast.error(
						`L'email "${email}" est déjà utilisé par un autre employé. Veuillez utiliser une autre adresse email.`,
						{ duration: 8000 }
					);
					return {
						success: false,
						errors: { 
							email: ['Cet email est déjà attribué à un employé.'],
							general: ['Email déjà existant']
						}
					};
				}
			}
			
			// Détecter l'erreur SMIG (salaire minimum)
			if (errorMessage.includes('cannot be lower than the active monthly SMIG') || 
			    errorMessage.includes('SMIG')) {
				notification.toast.error(
					`Le salaire de base doit être d'au moins 183 950,00 FC (SMIG mensuel en vigueur en RDC). Veuillez corriger le salaire.`,
					{ duration: 8000 }
				);
				return {
					success: false,
					errors: { 
						salary: ['Le salaire doit être d\'au moins 183 950,00 FC (SMIG).'],
						general: ['Salaire inférieur au SMIG']
					}
				};
			}
			
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(`Échec de l'onboarding: ${message}`);

			return {
				success: false,
				errors: { general: [message] }
			};
		}
	},

	/**
	 * Récupère la liste des positions pour le dropdown Contract
	 */
	async getPositions(): Promise<
		Array<{
			id: string;
			name: string;
			org_unit: {
				id: string;
				name: string;
				type: string;
			};
			job_family?: {
				id: string;
				name: string;
				description?: string;
			};
			description?: string;
			requirements?: string[];
			skills?: any[];
			seniority_levels?: any[];
		}>
	> {
		try {
			return await onboardingEndpoint.getPositions();
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(`Impossible de charger les postes: ${message}`);
			throw error;
		}
	},

	/**
	 * Récupère les niveaux de séniorité pour une position
	 */
	async getPositionSeniorityLevels(
		positionId: string
	): Promise<
		Array<{
			id: string;
			level: string;
			label: string;
			rank: number;
		}>
	> {
		try {
			return await onboardingEndpoint.getPositionSeniorityLevels(positionId);
		} catch (error: any) {
			const message = getFriendlyErrorMessage(error);
			notification.toast.error(`Impossible de charger les niveaux: ${message}`);
			throw error;
		}
	}
};
