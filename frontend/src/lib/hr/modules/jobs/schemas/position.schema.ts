import { z } from 'zod';


export const positionSchema = z.object({
  title: z.string().min(1, "L'intitulé du poste est requis").max(100, "L'intitulé ne doit pas dépasser 100 caractères"),
  familyName: z.string().min(1, "La famille de métier est requise").max(100, "La famille ne doit pas dépasser 100 caractères"),
  orgUnitId: z.string().min(1, "L'unité organisationnelle est requise"),
  seniority: z.enum(['TRAINEE', 'APPRENTICE', 'JUNIOR', 'INTERMEDIATE', 'SENIOR', 'LEAD', 'MANAGER', 'DIRECTOR', 'EXECUTIVE'], {
    message: "Le niveau de séniorité est requis"
  }),
  salaryRange: z.object({
    min: z.number().min(0, "Le salaire minimum doit être positif").optional(),
    max: z.number().min(0, "Le salaire maximum doit être positif").optional()
  }).refine((data) => {
    if (data.min !== undefined && data.max !== undefined) {
      return data.min <= data.max;
    }
    return true;
  }, {
    message: "Le salaire minimum doit être inférieur ou égal au maximum",
    path: ['min']
  }),
  requirements: z.array(z.string().min(1, "L'exigence ne peut pas être vide")).min(1, "Au moins une exigence est requise"),
  skills: z.array(
    z.object({
      name: z.string().min(1, "La compétence ne peut pas être vide"),
      level: z.number().min(1).max(5).optional()
    })
  ).min(1, "Au moins une compétence est requise")
});


export type PositionFormData = z.infer<typeof positionSchema>;

