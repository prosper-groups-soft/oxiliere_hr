import { z } from 'zod';

/**
 * Schémas de validation Zod pour les employés
 * Alignés avec les schémas backend EmployeeCreate et EmployeeUpdate
 */


// Schéma pour la création d'un employé (onboarding)
export const createEmployeeSchema = z.object({
  first_name: z
    .string()
    .min(2, 'Le prénom doit contenir au moins 2 caractères')
    .max(100, 'Le prénom ne peut pas dépasser 100 caractères'),
  
  middle_name: z
    .string()
    .max(100, 'Le deuxième prénom ne peut pas dépasser 100 caractères')
    .optional(),
  
  last_name: z
    .string()
    .min(2, 'Le nom doit contenir au moins 2 caractères')
    .max(100, 'Le nom ne peut pas dépasser 100 caractères'),
  
  email: z
    .email('Email invalide')
    .min(1, 'L\'email est requis'),
  
  phone: z
    .string()
    .regex(/^\+?[\d\s-]{8,20}$/, 'Numéro de téléphone invalide')
    .optional(),
  
  gender: z
    .enum(['M', 'F', 'OTHER'])
    .optional(),
  
  birthdate: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format de date invalide (YYYY-MM-DD)')
    .optional(),
  
  nationality: z
    .string()
    .max(100)
    .optional(),
  
  marital_status: z
    .enum(['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED', 'SEPARATED'])
    .optional(),
  
  hire_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format de date invalide (YYYY-MM-DD)')
    .optional(),
  
  description: z
    .string()
    .max(1000, 'La description ne peut pas dépasser 1000 caractères')
    .optional(),
  
  // Options pour la création de compte
  create_account: z
    .boolean()
    .default(false),
  
  group_slug: z
    .string()
    .optional(),
});


// Schéma pour la mise à jour des informations personnelles
export const updateEmployeeSchema = z.object({
  first_name: z
    .string()
    .min(2, 'Le prénom doit contenir au moins 2 caractères')
    .max(100, 'Le prénom ne peut pas dépasser 100 caractères')
    .optional(),
  
  middle_name: z
    .string()
    .max(100, 'Le deuxième prénom ne peut pas dépasser 100 caractères')
    .optional(),
  
  last_name: z
    .string()
    .min(2, 'Le nom doit contenir au moins 2 caractères')
    .max(100, 'Le nom ne peut pas dépasser 100 caractères')
    .optional(),
  
  email: z
    .email('Email invalide')
    .optional(),
  
  phone: z
    .string()
    .regex(/^\+?[\d\s-]{8,20}$/, 'Numéro de téléphone invalide')
    .optional(),
  
  gender: z
    .enum(['M', 'F', 'OTHER'])
    .optional(),
  
  birthdate: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format de date invalide (YYYY-MM-DD)')
    .optional(),
  
  nationality: z
    .string()
    .max(100)
    .optional(),
  
  marital_status: z
    .enum(['SINGLE', 'MARRIED', 'DIVORCED', 'WIDOWED', 'SEPARATED'])
    .optional(),
  
  description: z
    .string()
    .max(1000, 'La description ne peut pas dépasser 1000 caractères')
    .optional(),
});


// Schéma pour l'adresse employé
export const employeeAddressSchema = z.object({
  number: z.string().optional(),
  street: z.string().min(1, 'La rue est requise'),
  municipality: z.string().optional(),
  city: z.string().min(1, 'La ville est requise'),
  province: z.string().optional(),
  country: z.string().min(1, 'Le pays est requis'),
  country_code: z.string().length(2, 'Le code pays doit être sur 2 caractères').optional(),
  move_in_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format de date invalide')
    .optional(),
});


// Schéma pour les contacts d'urgence
export const emergencyContactSchema = z.object({
  first_name: z
    .string()
    .min(2, 'Le prénom doit contenir au moins 2 caractères'),
  
  middle_name: z.string().optional(),
  
  last_name: z
    .string()
    .min(2, 'Le nom doit contenir au moins 2 caractères'),
  
  phone: z
    .string()
    .regex(/^\+?[\d\s-]{8,20}$/, 'Numéro de téléphone invalide'),
  
  relation: z
    .string()
    .min(1, 'La relation est requise'),
  
  priority: z
    .number()
    .int()
    .min(1, 'La priorité doit être >= 1')
    .default(1),
});


// Schéma pour les enfants
export const employeeChildSchema = z.object({
  first_name: z
    .string()
    .min(2, 'Le prénom doit contenir au moins 2 caractères'),
  
  middle_name: z.string().optional(),
  
  last_name: z
    .string()
    .min(2, 'Le nom doit contenir au moins 2 caractères'),
  
  gender: z
    .enum(['M', 'F', 'OTHER'])
    .optional(),
  
  birthdate: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format de date invalide (YYYY-MM-DD)'),
  
  is_dependent: z
    .boolean()
    .default(true),
});


// Schéma pour l'éducation
export const employeeEducationSchema = z.object({
  institute: z
    .string()
    .min(2, 'L\'institut doit contenir au moins 2 caractères'),
  
  degree: z
    .string()
    .min(1, 'Le diplôme est requis'),
  
  major: z.string().optional(),
  
  start_year: z
    .number()
    .int()
    .min(1900)
    .max(new Date().getFullYear())
    .optional(),
  
  end_year: z
    .number()
    .int()
    .min(1900)
    .max(new Date().getFullYear() + 10)
    .optional(),
  
  location: z.string().optional(),
});


// Types inférés des schémas
export type CreateEmployeeForm = z.infer<typeof createEmployeeSchema>;
export type UpdateEmployeeForm = z.infer<typeof updateEmployeeSchema>;
export type EmployeeAddressForm = z.infer<typeof employeeAddressSchema>;
export type EmergencyContactForm = z.infer<typeof emergencyContactSchema>;
export type EmployeeChildForm = z.infer<typeof employeeChildSchema>;
export type EmployeeEducationForm = z.infer<typeof employeeEducationSchema>;


// Schémas pour le cycle de vie de l'employé
export const suspendEmployeeSchema = z.object({
  reason: z.string().min(2, 'Le motif de suspension est requis'),
  effective_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format de date invalide (YYYY-MM-DD)')
    .optional(),
});


export const reactivateEmployeeSchema = z.object({
  effective_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format de date invalide (YYYY-MM-DD)')
    .optional(),
  reason: z.string().optional(),
  is_active: z.boolean().default(true),
  can_connect: z.boolean().optional(),
});


export const offboardEmployeeSchema = z.object({
  end_date: z
    .string()
    .regex(/^\d{4}-\d{2}-\d{2}$/, 'Format de date invalide (YYYY-MM-DD)'),
  departure_type: z
    .enum(['TERMINATED', 'RESIGNED', 'RETIRED'])
    .default('TERMINATED'),
  reason: z.string().min(2, 'Le motif de départ est requis'),
});


export type SuspendEmployeeForm = z.infer<typeof suspendEmployeeSchema>;
export type ReactivateEmployeeForm = z.infer<typeof reactivateEmployeeSchema>;
export type OffboardEmployeeForm = z.infer<typeof offboardEmployeeSchema>;
