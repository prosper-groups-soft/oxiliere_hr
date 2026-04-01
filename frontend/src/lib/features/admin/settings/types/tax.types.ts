// Types Fiscalité IPR & Social - RDC

// Barème IPR Progressif (Impôt sur le Revenu des Personnes Physiques)
// Tranches selon la législation fiscale RDC

export interface IPRBracket {
	id: string;
	min: number; // Seuil inférieur en USD
	max: number | null; // Seuil supérieur (null = illimité)
	rate: number; // Taux entre 0 et 1 (ex: 0.03 pour 3%)
	label: string;
}

// Barème IPR officiel RDC
export const DEFAULT_IPR_BRACKETS: IPRBracket[] = [
	{
		id: 'bracket-1',
		min: 0,
		max: 300,
		rate: 0.03,
		label: 'Tranche 1 (0 - 300 USD)'
	},
	{
		id: 'bracket-2',
		min: 300,
		max: 500,
		rate: 0.15,
		label: 'Tranche 2 (300 - 500 USD)'
	},
	{
		id: 'bracket-3',
		min: 500,
		max: 1000,
		rate: 0.30,
		label: 'Tranche 3 (500 - 1000 USD)'
	},
	{
		id: 'bracket-4',
		min: 1000,
		max: null,
		rate: 0.40,
		label: 'Tranche 4 (> 1000 USD)'
	}
];

export interface FamilyDeduction {
	enabled: boolean;
	ratePerChild: number; // 0.02 pour 2%
	maxChildren: number; // 9 enfants maximum
}

export interface CNSSConfig {
	enabled: boolean;
	employerRate: number; // 0.15 pour 15%
	employeeRate: number; // 0.05 pour 5%
	salaryCap: number | null; // Plafond de salaire soumis (null = pas de plafond)
	includeInGross: boolean;
}

export interface INSSConfig {
	enabled: boolean;
	rate: number; // Généralement 3%
	salaryCap: number | null;
}

export interface IPRConfig {
	// Plafond légal: IPR ne peut excéder 30% du revenu net imposable
	globalCapRate: number; // 0.30 pour 30%
	
	// Abattement professionnel (si applicable)
	professionalAllowanceRate: number; // Généralement 20%
	
	// Base de calcul
	include13thMonth: boolean;
	includeBonuses: boolean;
}

export interface TaxConfig {
	iprBrackets: IPRBracket[];
	iprConfig: IPRConfig;
	familyDeduction: FamilyDeduction;
	cnss: CNSSConfig;
	inss: INSSConfig;
	currency: 'USD' | 'CDF';
}

// Configuration fiscale par défaut (RDC)
export const DEFAULT_TAX_CONFIG: TaxConfig = {
	iprBrackets: DEFAULT_IPR_BRACKETS,
	iprConfig: {
		globalCapRate: 0.30,
		professionalAllowanceRate: 0.20,
		include13thMonth: true,
		includeBonuses: true
	},
	familyDeduction: {
		enabled: true,
		ratePerChild: 0.02,
		maxChildren: 9
	},
	cnss: {
		enabled: true,
		employerRate: 0.15,
		employeeRate: 0.05,
		salaryCap: null,
		includeInGross: true
	},
	inss: {
		enabled: true,
		rate: 0.03,
		salaryCap: null
	},
	currency: 'USD'
};

// Types pour les calculs
export interface IPRCalculationResult {
	grossSalary: number;
	professionalAllowance: number;
	 taxableBase: number;
	brackets: {
		bracket: IPRBracket;
		amountInBracket: number;
		taxInBracket: number;
	}[];
	totalTaxBeforeDeductions: number;
	familyDeduction: number;
	finalTax: number;
	globalCapApplied: boolean;
	effectiveRate: number;
}

