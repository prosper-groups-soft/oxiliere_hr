import { z } from 'zod';
import { 
  CURRENCIES, 
  CONTRIBUTION_TYPES 
} from '@/constants/finance';


const customErrorMap: z.ZodErrorMap = (issue) => {
  if (issue.code === 'invalid_type') {
    if (issue.received === 'nan') {
      return 'Valeur numérique invalide';
    }
    if (issue.expected === 'number') {
      return 'Un nombre est requis';
    }
  }
  if (issue.code === 'too_small' && issue.type === 'string' && issue.minimum === 1) {
    return 'Ce champ est obligatoire';
  }
  return undefined;
};

z.config({ customError: customErrorMap });

    
// API Response types
export interface PayrollConfigResponse {
  id: string;
  currency: typeof CURRENCIES.USD | typeof CURRENCIES.CDF;
  work_hours_per_week?: number;
  work_hours_per_month?: number;
  work_hours_per_day?: number;
  work_days_per_week?: number;
  default_payment_method?: 'BANK_TRANSFER' | 'CASH' | 'CHECK' | 'MOBILE_MONEY';
  payment_method?: 'BANK_TRANSFER' | 'CASH' | 'CHECK' | 'MOBILE_MONEY';
  global_ipr_cap_rate?: number | string;
  professional_allowance_rate?: number | string;
  include_13th_month?: boolean;
  include_bonuses?: boolean;
  family_deduction_rate_per_child?: number | string;
  family_deduction_max_children?: number | string;
  housing_allowance_min_percentage?: number | string;
  include_leaves_in_payroll?: boolean;
  leave_deduction_divisor?: number | string;
  use_theoretical_days_from_attendance?: boolean;
  fixed_deduction_per_absent_day?: number | string | null;
  exchange_rate_usd_cdf?: number | string;
  exchange_rate_source?: 'MANUAL' | 'API';
}


export interface TaxBracketResponse {
  id: string;
  lower_limit: number | string;
  upper_limit: number | string | null;
  rate_percentage: number | string;
  label: string;
  min_tax_amount?: number | string | null;
  max_tax_percentage?: number | string | null;
  applies_to_taxable_base?: boolean;
  is_active?: boolean;
}


export interface SocialContributionResponse {
  id: string;
  contribution_type: typeof CONTRIBUTION_TYPES.CNSS | typeof CONTRIBUTION_TYPES.ONEM | typeof CONTRIBUTION_TYPES.INPP | typeof CONTRIBUTION_TYPES.AMO;
  // Backend fields (different names)
  rate_percentage: number | string;
  employee_portion: number | string;
  employer_portion: number | string;
  ceiling_amount: number | string | null;
  // Convenience getters mapping to frontend naming
  employer_rate?: number;
  employee_rate?: number;
  salary_cap?: number | null;
  is_active: boolean;
  effective_date?: string;
  company_size_min?: number | null;
  company_size_max?: number | null;
}


// API Update types - ONLY editable fields from TaxConfigPanel
// Backend expects uppercase values for enums
export interface PayrollConfigUpdate {
  
  // Payroll/Attendance settings (editable in TaxConfigPanel)
  work_hours_per_week?: number;
  leave_deduction_divisor?: number;
  include_leaves_in_payroll?: boolean;
  use_theoretical_days_from_attendance?: boolean;

  // Currency/Exchange settings (editable in TaxConfigPanel)
  exchange_rate_usd_cdf?: number;
  exchange_rate_source?: 'MANUAL' | 'API';
  default_payment_method?: 'BANK_TRANSFER' | 'CASH' | 'CHECK' | 'MOBILE_MONEY';
}


export interface TaxBracketCreate {
  lower_limit: number;
  upper_limit: number | null;
  rate_percentage: number;
  label: string;
  min_tax_amount?: number | null;
  max_tax_percentage?: number | null;
}

export interface TaxBracketUpdate {
  lower_limit?: number;
  upper_limit?: number | null;
  rate_percentage?: number;
  label?: string;
  min_tax_amount?: number | null;
  max_tax_percentage?: number | null;
}


export interface SocialContributionCreate {
  contribution_type: 'CNSS' | 'ONEM' | 'INPP';
  employer_rate: number;
  employee_rate: number;
  salary_cap?: number | null;
  is_active?: boolean;
}

export interface SocialContributionUpdate {
  employer_rate?: number;
  employee_rate?: number;
  salary_cap?: number | null;
  is_active?: boolean;
}


// Validation schemas
export const IPRBracketSchema = z.object({
  id: z.string(),
  lower_limit: z.number().min(0, 'Le minimum doit être positif'),
  upper_limit: z.number().nullable(),
  rate_percentage: z.number().min(0).max(100, 'Le taux doit être entre 0 et 100%'),
  label: z.string().min(1, 'Le libellé est requis'),
}).refine(
  (data) => data.upper_limit === null || data.upper_limit > data.lower_limit,
  {
    message: 'Le maximum doit être supérieur au minimum',
    path: ['upper_limit'],
  }
);


export const FamilyDeductionSchema = z.object({
  enabled: z.boolean(),
  ratePerChild: z.number().min(0).max(0.5, 'Le taux par enfant doit être ≤ 50%'),
  maxChildren: z.number().int().min(1).max(20, 'Maximum 20 enfants'),
});


export const CNSSConfigSchema = z.object({
  enabled: z.boolean(),
  employerRate: z.number().min(0).max(1, 'Taux patronal ≤ 100%'),
  employeeRate: z.number().min(0).max(1, 'Taux ouvrier ≤ 100%'),
  salaryCap: z.number().nullable(),
  includeInGross: z.boolean(),
}).refine(
  (data) => !data.enabled || (data.employerRate + data.employeeRate) <= 1,
  {
    message: 'La somme des taux CNSS ne peut excéder 100%',
    path: ['employerRate'],
  }
);


export const INSSConfigSchema = z.object({
  enabled: z.boolean(),
  rate: z.number().min(0).max(1, 'Taux ≤ 100%'),
  salaryCap: z.number().nullable(),
});


export const IPRConfigSchema = z.object({
  globalCapRate: z.number().min(0).max(1, 'Le plafond doit être ≤ 100%'),
  professionalAllowanceRate: z.number().min(0).max(1, 'L\'abattement doit être ≤ 100%'),
  include13thMonth: z.boolean(),
  includeBonuses: z.boolean(),
});


// ONEM schema
export const ONEMConfigSchema = z.object({
  enabled: z.boolean(),
  rate: z.number().min(0).max(1, 'Taux ONEM ≤ 100%'),
});


// INPP schema (read-only from API)
export const INPPRateSchema = z.object({
  id: z.string().optional(),
  rate: z.number(),
  companySizeMin: z.number().nullable(),
  companySizeMax: z.number().nullable(),
});


// General payroll configuration schema
export const PayrollGeneralConfigSchema = z.object({
  workHoursPerMonth: z.number().min(1).max(744).optional(),
  workHoursPerDay: z.number().min(1).max(24).optional(),
  workDaysPerWeek: z.number().min(1).max(7).optional(),
  housingAllowanceMinPercentage: z.number().min(0).max(1).optional(),
  leaveDeductionDivisor: z.number().min(1).optional(),
  exchangeRateUsdCdf: z.number().positive().optional(),
  exchangeRateSource: z.enum(['MANUAL', 'API']).optional(),
  defaultPaymentMethod: z.enum(['BANK_TRANSFER', 'CASH', 'CHECK', 'MOBILE_MONEY']).optional(),
  includeLeavesInPayroll: z.boolean().optional(),
  useTheoreticalDaysFromAttendance: z.boolean().optional(),
  fixedDeductionPerAbsentDay: z.number().nullable().optional(),
});


// Currency schema using constants
export const CurrencySchema = z.enum([CURRENCIES.USD, CURRENCIES.CDF]);


// Helper to validate number and reject NaN
const validNumber = () => z.number({
  message: 'Un nombre est requis',
}).refine((val) => !Number.isNaN(val) && Number.isFinite(val), {
  message: 'Valeur numérique invalide',
});


export const TaxConfigValidationSchema = z.object({
  // Payroll/Attendance settings (editable in TaxConfigPanel)
  // Note: workHoursPerMonth, housingAllowance are now managed
  // through LegalAllowances and OvertimeRules sections
  workHoursPerWeek: validNumber().min(1, 'Minimum 1 heure').max(168, 'Maximum 168 heures/semaine').optional(),
  leaveDeductionDivisor: validNumber().min(1, 'Le diviseur doit être ≥ 1').max(31, 'Maximum 31 jours').optional(),
  includeLeavesInPayroll: z.boolean().optional(),
  useTheoreticalDaysFromAttendance: z.boolean().optional(),
  // Currency/Exchange settings (editable in TaxConfigPanel)
  exchangeRateUsdCdf: validNumber().positive('Le taux doit être positif').optional(),
  exchangeRateSource: z.enum(['MANUAL', 'API']).optional(),
  defaultPaymentMethod: z.enum(['BANK_TRANSFER', 'CASH', 'CHECK', 'MOBILE_MONEY']).optional(),
});



export type TaxConfigValidation = z.infer<typeof TaxConfigValidationSchema>;
