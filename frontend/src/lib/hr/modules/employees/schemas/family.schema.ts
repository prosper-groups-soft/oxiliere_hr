import { z } from 'zod';


/**
 * Schema for a child dependent
 */
export const childSchema = z.object({
    last_name: z
        .string()
        .min(1, 'Le nom est requis')
        .max(75, 'Le nom ne doit pas dépasser 75 caractères'),
    first_name: z.string().optional().default(''),
    middle_name: z.string().optional().default(''),
    birthdate: z
        .string({ message: 'La date de naissance est requise' })
        .min(1, 'La date de naissance est requise')
        .refine((val) => !isNaN(Date.parse(val)), {
            message: 'Date de naissance invalide'
        })
        .refine((val) => new Date(val) <= new Date(), {
            message: 'La date de naissance ne peut pas être dans le futur'
        }),
    gender: z.enum(['MALE', 'FEMALE', 'NOT_SPECIFIED']).default('NOT_SPECIFIED'),
    is_dependent: z.boolean().default(true)
});


/**
 * Schema for an emergency contact
 */
export const emergencyContactSchema = z.object({
    last_name: z
        .string()
        .min(1, 'Le nom est requis')
        .max(100, 'Le nom ne doit pas dépasser 75 caractères'),
    first_name: z.string().optional().default(''),
    middle_name: z.string().optional().default(''),
    relation: z.string().min(1, 'La relation est requise'),
    phone: z.string().min(1, 'Le téléphone est requis'),
    is_primary: z.boolean().default(false)
});

export type ChildFormData = z.infer<typeof childSchema>;
export type EmergencyContactFormData = z.infer<typeof emergencyContactSchema>;
