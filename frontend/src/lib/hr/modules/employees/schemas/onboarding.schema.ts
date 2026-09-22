import { z } from 'zod';
import { educationSchema } from './education.schema';
import type { OnboardingEducationItem } from '../types/types';


// ============================================
// IDENTITY SCHEMA (Step 1)
// ============================================
export const identitySchema = z.object({
    first_name: z
        .string()
        .min(1, 'Le prénom est requis')
        .max(75, 'Le prénom ne doit pas dépasser 75 caractères'),
    middle_name: z
        .string()
        .max(75, 'Le deuxième prénom ne doit pas dépasser 75 caractères')
        .optional(),
    last_name: z
        .string()
        .min(1, 'Le nom est requis')
        .max(75, 'Le nom ne doit pas dépasser 75 caractères'),
    email: z
        .email('Format d\'email invalide'),
    phone: z
        .string()
        .optional()
        .refine((val) => !val || /^[\d\s\+\-\(\)]{10,20}$/.test(val), {
            message: 'Format de téléphone invalide'
        }),
    birthdate: z
        .string()
        .optional()
        .refine((val) => !val || !isNaN(Date.parse(val)), {
            message: 'Date de naissance invalide'
        }),
    gender: z
        .enum(['MALE', 'FEMALE', 'NOT_SPECIFIED'])
        .optional(),
    nationality: z
        .string()
        .optional(),
    marital_status: z
        .enum(['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED'])
        .optional(),
    work_site: z
        .string()
        .min(1, 'Le site de travail est requis'),
    address: z.object({
        number: z.string().max(5, 'Le numéro ne doit pas dépasser 5 caractères').optional(),
        street: z.string().max(75, 'La rue ne doit pas dépasser 75 caractères').optional(),
        municipality: z.string().max(75, 'La commune ne doit pas dépasser 75 caractères').optional(),
        city: z.string().max(75, 'La ville ne doit pas dépasser 75 caractères').optional(),
        province: z.string().max(75, 'La province ne doit pas dépasser 75 caractères').optional(),
        country_code: z.string().max(2, 'Le code pays ne doit pas dépasser 2 caractères').optional()
    }).optional()
});

// ============================================
// ACCOUNT SCHEMA (Step 2)
// ============================================
export const accountSchema = z.object({
    create_account: z.boolean(),
    group_slug: z
        .string()
        .optional()
        .refine((val) => !val || val.length > 0, {
            message: 'Le groupe est requis si un compte est créé'
        })
});

// ============================================
// CONTRACT SCHEMA (Step 3)
// ============================================
export const contractSchema = z.object({
    position_id: z.string().min(1, 'Le poste est requis'),
    seniority_level_id: z.string().min(1, 'Le niveau de séniorité est requis'),
    contract_type: z.enum(
        ['CDI', 'CDD', 'INTERNSHIP', 'PROBATION', 'FREELANCE'],
        { message: 'Le type de contrat est requis' }
    ),
    remuneration_type: z.enum(
        ['FIXED', 'HOURLY'],
        { message: 'Le type de rémunération est requis' }
    ),
    salary: z
        .number()
        .min(0, 'Le salaire doit être positif')
        .refine((val: number) => val > 0, {
            message: 'Le salaire est requis'
        }),
    salary_base_type: z.enum(
        ['BASE', 'NET'],
        { message: 'La base de calcul est requise' }
    ),
    currency: z.enum(
        ['CDF', 'USD', 'EUR'],
        { message: 'La devise est requise' }
    ),
    hire_date: z
        .string()
        .min(1, 'La date de début est requise')
        .refine((val) => !isNaN(Date.parse(val)), {
            message: 'Date de début invalide'
        }),
    end_date: z
        .string()
        .optional()
        .refine((val) => {
            if (!val) return true;
            return !isNaN(Date.parse(val));
        }, {
            message: 'Date de fin invalide'
        }),
    // Métamodèle (Règle 5)
    contractual_clauses: z.string().optional(),
    // S10 — éléments de paie sélectionnés pendant l'onboarding
    contract_adjustments: z.array(z.any()).optional()
});

// ============================================
// DOCUMENT SCHEMA (Step 4)
// ============================================
export const documentSchema = z.object({
    id: z.string(),
    file: z.instanceof(File, { message: 'Un fichier est requis' }),
    document_type: z.enum(
        ["NATIONAL_ID", "VOTER_CARD", "PASSPORT", "DRIVING_LICENSE", "DIPLOMA", "RESIDENCE_PERMIT", "PHOTO", "CRIMINAL_RECORD", "OTHER"],
        { message: 'Le type de document est requis' }
    ),
    document_number: z.string().optional(),
    issue_date: z.string().optional(),
    expiry_date: z.string().optional()
});

// ============================================
// FAMILY SCHEMA (Step 5)
// ============================================
export const emergencyContactSchema = z.object({
    id: z.union([z.string(), z.number()]),
    name: z.string().min(1, 'Le nom est requis'),
    relation: z.string().min(1, 'La relation est requise'),
    phone: z.string().min(1, 'Le téléphone est requis'),
    primary: z.boolean()
});

export const childSchema = z.object({
    id: z.union([z.string(), z.number()]),
    name: z.string().min(1, 'Le nom est requis'),
    birthDate: z.string().min(1, 'La date de naissance est requise'),
    gender: z.enum(['MALE', 'FEMALE', 'NOT_SPECIFIED']).optional(),
    isDependent: z.boolean().optional()
});

export const familySchema = z.object({
    emergency_contacts: z.array(emergencyContactSchema),
    children: z.array(childSchema)
});

// ============================================
// EDUCATION SCHEMA (Step 6)
// ============================================
export const educationSchemaWrapper = z.object({
    educations: z.array(educationSchema)
});

// ============================================
// FULL ONBOARDING SCHEMA
// ============================================
export const fullOnboardingSchema = z.object({
    identity: identitySchema,
    account: accountSchema.optional(),
    contract: contractSchema,
    documents: z.array(documentSchema),
    family: familySchema,
    education: educationSchemaWrapper
});

// ============================================
// TYPES INFÉRÉS
// ============================================
export type IdentityFormData = z.infer<typeof identitySchema>;
export type AccountFormData = z.infer<typeof accountSchema>;
export type ContractFormData = z.infer<typeof contractSchema>;
export type DocumentFormData = z.infer<typeof documentSchema>;
export type FamilyFormData = z.infer<typeof familySchema>;
export type EducationFormData = z.infer<typeof educationSchemaWrapper>;
export type FullOnboardingFormData = z.infer<typeof fullOnboardingSchema>;

// ============================================
// HELPERS DE VALIDATION
// ============================================

/**
 * Valide une étape spécifique de l'onboarding
 */
export function validateStep(
    step: 'identity' | 'account' | 'contract' | 'family' | 'documents' | 'education',
    data: unknown
): { success: boolean; errors: string[] } {
    
    // On définit le schéma dynamiquement
    let schema: z.ZodSchema;

    switch (step) {
        case 'identity':
            schema = identitySchema;
            break;
        case 'account':
            schema = accountSchema;
            break;
        case 'contract':
            schema = contractSchema;
            break;
        case 'family':
            return { success: true, errors: [] };
        case 'documents':
            return { success: true, errors: [] };
        case 'education':
            return { success: true, errors: [] };
        default:
            return { success: false, errors: ['Étape inconnue'] };
    }

    const result = schema.safeParse(data);

    if (!result.success) {
        // Utilisation de .issues qui est la propriété officielle de ZodError
        const errors = result.error.issues.map((issue) => issue.message);
        return { success: false, errors };
    }

    return { success: true, errors: [] };
}

/**
 * Valide l'onboarding complet avant soumission
 */
export function validateFullOnboarding(
    data: unknown
): { success: true; data: FullOnboardingFormData } | { success: false; errors: string[] } {
    const result = fullOnboardingSchema.safeParse(data);

    if (!result.success) {
        const errors = result.error.issues.map((issue) => 
            `${issue.path.join('.')}: ${issue.message}`
        );
        return { success: false, errors };
    }

    return { success: true, data: result.data };
}

