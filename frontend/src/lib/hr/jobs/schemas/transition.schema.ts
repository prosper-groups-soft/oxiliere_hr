import { z } from 'zod';


export const transitionSchema = z.object({
  employee_id: z.string({ message: "L'employé est requis" }).min(1, "L'employé est requis"),
  transition_type: z.enum(['TRANSFER', 'PROMOTION', 'HIRE', 'OFFBOARD'], {
    message: "Le type de mouvement est requis"
  }),
  from_position_id: z.string().nullable().optional(),
  to_position_id: z.string().optional(),
  date: z.string().min(1, "La date d'effet est requise"),
  reason: z.string().min(10, "Le motif doit avoir au moins 10 caractères").optional()
}).refine(
  (data) => {
    // to_position_id is required for HIRE, PROMOTION, TRANSFER
    // but optional for OFFBOARD
    if (data.transition_type === 'OFFBOARD') {
      return true;
    }
    return data.to_position_id != null && data.to_position_id !== '';
  },
  {
    message: "Le nouveau poste est requis pour ce type de mouvement",
    path: ["to_position_id"]
  }
);


export type TransitionSchemaType = z.infer<typeof transitionSchema>;

