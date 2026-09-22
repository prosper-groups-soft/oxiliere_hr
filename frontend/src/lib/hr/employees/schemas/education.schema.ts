import { z } from 'zod';


const VALID_DEGREES = [
  'TENASOSP', 'STATE_DIPLOMA', 'ASSOCIATE', 'BACHELOR',
  'MASTER', 'DOCTORATE', 'VOCATIONAL', 'NOT_SPECIFIED'
] as const;


const currentYear = new Date().getFullYear();


/**
 * Schema for an education record (academic qualification)
 */
export const educationSchema = z.object({
  degree: z.enum(VALID_DEGREES, {
    message: 'Le diplôme est requis'
  }),
  institute: z
    .string()
    .min(1, 'L\'institution est requise')
    .max(150, 'L\'institution ne doit pas dépasser 150 caractères'),
  major: z.string().optional().default(''),
  location: z.string().optional().default(''),
  start_year: z
    .union([z.number(), z.string()])
    .optional()
    .transform((val) => (val === '' || val === undefined ? undefined : Number(val)))
    .refine((val) => val === undefined || (!isNaN(val) && val >= 1950 && val <= 2099), {
      message: 'L\'année doit être entre 1950 et 2099'
    }),
  end_year: z
    .union([z.number(), z.string()])
    .optional()
    .transform((val) => (val === '' || val === undefined ? undefined : Number(val)))
    .refine((val) => val === undefined || (!isNaN(val) && val >= 1950 && val <= 2099), {
      message: 'L\'année doit être entre 1950 et 2099'
    }),
}).refine(
  (data) => {
    if (data.start_year && data.end_year) {
      return data.end_year >= data.start_year;
    }
    return true;
  },
  {
    message: 'L\'année de fin ne peut pas précéder l\'année de début',
    path: ['end_year']
  }
);


export type EducationFormData = z.infer<typeof educationSchema>;

