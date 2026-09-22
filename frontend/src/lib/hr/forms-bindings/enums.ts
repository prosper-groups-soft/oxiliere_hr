// Enums statiques du catalogue (lot P1) — options figées, pas de backend.
// Règle « ne pas inventer de valeurs » : les options sont dérivées des
// constantes/unions existantes du code (mappings, constants/contract,
// onboarding). Les écarts vs catalogue.md sont notés dans avancement.md §3.1.
import { registerType } from '@/hr/forms/index.js';
import {
	REMUNERATION_TYPES,
	SALARY_BASE_TYPES,
	CONTRACT_TYPES
} from '@/hr/modules/employees/constants/contract.js';
import {
	REVERSE_GENDER_MAPPING,
	REVERSE_MARITAL_STATUS_MAPPING
} from '@/hr/modules/employees/constants/mappings.js';

let registered = false;

/** Enregistre les 8 types énumérés statiques du catalogue (idempotent). */
export function registerEnumTypes(): void {
	if (registered) return;
	registered = true;

	const enumOf = (name: string, options: readonly { value: string; label: string }[]) =>
		registerType(name, {
			valueType: 'string',
			defaultRenderer: 'business',
			defaultDataSource: { type: 'static', values: [...options] }
		});

	// Gender : labels dérivés de REVERSE_GENDER_MAPPING (Homme/Femme/Non spécifié)
	enumOf(
		'gender',
		Object.entries(REVERSE_GENDER_MAPPING).map(([value, label]) => ({ value, label }))
	);

	// MaritalStatus : labels dérivés de REVERSE_MARITAL_STATUS_MAPPING
	enumOf(
		'maritalStatus',
		Object.entries(REVERSE_MARITAL_STATUS_MAPPING).map(([value, label]) => ({ value, label }))
	);

	// ContractType : 6 valeurs réelles (inclut TEMPORARY, absent du catalogue)
	enumOf('contractType', CONTRACT_TYPES);

	// RemunerationType : FIXED/HOURLY (GROSS_UP du catalogue n'existe pas côté code)
	enumOf('remunerationType', REMUNERATION_TYPES);

	// SalaryBaseType : BASE/NET (le catalogue dit GROSS/NET — arbitrage §3.1)
	enumOf('salaryBaseType', SALARY_BASE_TYPES);

	// PaymentPeriod : PAYMENT_PERIODS a été supprimé du contrat (méta-modèle §7.1,
	// pipeline toujours mensuel) → option unique MONTHLY, champ gardé pour compat.
	enumOf('paymentPeriod', [{ value: 'MONTHLY', label: 'Mensuel' }]);

	// InitialStatus : union onboarding (ACTIVE | PROBATION | PENDING)
	enumOf('initialStatus', [
		{ value: 'ACTIVE', label: 'Actif' },
		{ value: 'PROBATION', label: 'En période d’essai' },
		{ value: 'PENDING', label: 'En attente' }
	]);

	// DocumentType : union OnboardingDocumentItem (9 valeurs)
	enumOf('documentType', [
		{ value: 'NATIONAL_ID', label: 'Carte d’identité' },
		{ value: 'VOTER_CARD', label: 'Carte d’électeur' },
		{ value: 'PASSPORT', label: 'Passeport' },
		{ value: 'DRIVING_LICENSE', label: 'Permis de conduire' },
		{ value: 'DIPLOMA', label: 'Diplôme' },
		{ value: 'RESIDENCE_PERMIT', label: 'Permis de séjour' },
		{ value: 'PHOTO', label: 'Photo d’identité' },
		{ value: 'CRIMINAL_RECORD', label: 'Casier judiciaire' },
		{ value: 'OTHER', label: 'Autre' }
	]);

	// Contract (lot P6) : le catalogue distinguait « contract » (API types de
	// contrat) de « contractType » (statique). Aucune API de types de contrat
	// n'existe — le contrat est créé avec un contract_type parmi CONTRACT_TYPES.
	// Même source que contractType, type gardé pour compat catalogue.
	enumOf('contract', CONTRACT_TYPES);
}
