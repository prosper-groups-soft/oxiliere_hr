import type { Currency } from '@/constants/finance';


export interface IPRBracket {
	id: string;
	min: number; // Seuil inférieur en USD
	max: number | null; // Seuil supérieur (null = illimité)
	rate: number; // Taux entre 0 et 1 (ex: 0.03 pour 3%)
	label: string;
	readOnly?: boolean; // Fixed by law (RDC Ordonnance 69-102)
}


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


export interface INPPRate {
	id?: string;
	rate: number;
	companySizeMin: number | null | undefined;
	companySizeMax: number | null | undefined;
}


export interface ONEMConfig {
	enabled: boolean;
	rate: number; // Généralement 0.2%
}


export interface TaxConfig {
	iprBrackets: IPRBracket[];
	iprConfig: IPRConfig;
	familyDeduction: FamilyDeduction;
	cnss: CNSSConfig;
	inss: INSSConfig;
	inpp: INPPRate[];
	onem: ONEMConfig;
	currency: Currency;
	// Additional payroll configuration from API
	workHoursPerMonth?: number;
	workHoursPerDay?: number;
	workDaysPerWeek?: number;
	housingAllowanceMinPercentage?: number;
	workHoursPerWeek: number | null;
	leaveDeductionDivisor?: number;
	exchangeRateUsdCdf?: number;
	exchangeRateSource?: 'MANUAL' | 'API';
	defaultPaymentMethod?: 'BANK_TRANSFER' | 'CASH' | 'MOBILE_MONEY' | 'CHECK';
	includeLeavesInPayroll?: boolean;
	useTheoreticalDaysFromAttendance?: boolean;
	fixedDeductionPerAbsentDay?: number | null;
}


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


/**
 * Legal Allowance - Statutory allowances required by local regulations (RDC)
 */
export interface LegalAllowance {
	id: string;
	allowance_type: 'HOUSING' | 'TRANSPORT' | 'OTHER';
	calculation_mode: 'FIXED' | 'PERCENTAGE' | 'FORMULA';
	base_amount: string | null; // API returns string (Decimal)
	formula_description: string | null;
	is_taxable: boolean;
	taxable_threshold_percentage: string | null; // API returns string (Decimal)
	is_active: boolean;
}


/**
 * Overtime Rule - Defines overtime calculation rules with different multipliers
 */
export interface OvertimeRule {
	id: string;
	rule_type: 'FIRST_TWO_HOURS' | 'SUBSEQUENT_HOURS' | 'HOLIDAY' | 'WEEKEND';
	multiplier: string; // API returns string (Decimal)
	description: string | null;
	is_active: boolean;
}

