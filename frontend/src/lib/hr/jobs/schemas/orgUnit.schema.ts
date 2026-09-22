import { z } from 'zod';


export const orgUnitSchema = z.object({
  name: z.string().min(1, 'Le nom est requis'),
  type: z.enum(['DEPARTMENT', 'DIVISION', 'TEAM', 'FUNCTION', 'BRANCH', 'PROJECT']),
  parentId: z.string().nullable().optional(),
  managerId: z.string().nullable().refine((val) => val !== null && val !== '', {
    message: 'Un responsable est requis'
  }),
  affointId: z.string().nullable().optional(),
  authorizedHeadcount: z.number().min(1, 'L\'effectif autorisé doit être au moins de 1'),
});


export type OrgUnitFormData = z.infer<typeof orgUnitSchema>;
