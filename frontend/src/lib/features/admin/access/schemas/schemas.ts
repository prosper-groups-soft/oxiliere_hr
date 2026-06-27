import { z } from 'zod';


export const groupSchema = z.object({
  name: z.string().min(2, 'Le nom doit contenir au moins 2 caractères').max(100, 'Le nom ne doit pas dépasser 100 caractères'),
  slug: z.string()
    .min(2, 'L\'identifiant doit contenir au moins 2 caractères')
    .max(50, 'L\'identifiant ne doit pas dépasser 50 caractères')
    .regex(/^[a-z0-9_]+$/, 'L\'identifiant ne peut contenir que des lettres minuscules, chiffres et underscores'),
  roles: z.array(z.string()).min(1, 'Sélectionnez au moins un rôle'),
});


export const groupUpdateSchema = z.object({
  name: z.string().min(2, 'Le nom doit contenir au moins 2 caractères').max(100, 'Le nom ne doit pas dépasser 100 caractères'),
  roles: z.array(z.string()).min(1, 'Sélectionnez au moins un rôle'),
});


export type GroupForm = z.infer<typeof groupSchema>;
export type GroupUpdateForm = z.infer<typeof groupUpdateSchema>;


export function validateGroup(data: { name: string; slug: string; roles: string[] }): { valid: boolean; errors: string[] } {
  const result = groupSchema.safeParse(data);
  if (result.success) {
    return { valid: true, errors: [] };
  }
  return { 
    valid: false, 
    errors: result.error.issues.map(e => e.message) 
  };
}


export function validateGroupUpdate(data: { name: string; roles: string[] }): { valid: boolean; errors: string[] } {
  const result = groupUpdateSchema.safeParse(data);
  if (result.success) {
    return { valid: true, errors: [] };
  }
  return { 
    valid: false, 
    errors: result.error.issues.map(e => e.message) 
  };
}

