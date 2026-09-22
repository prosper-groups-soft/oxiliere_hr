import { z } from 'zod';


export const vacancySchema = z.object({
	position_id: z.string({ message: "Le poste est requis" }).min(1, "Le poste est requis"),
	priority: z.enum(['HIGH', 'MEDIUM', 'LOW'], {
		message: "La priorité est requise"
	}),
	status: z.enum(['OPEN', 'IN_PROGRESS', 'RECRUITMENT', 'CANCELLED', 'FILLED'], {
		message: "Le statut est requis"
	}),
	opened_date: z.string().min(1, "La date d'ouverture est requise"),
	target_date: z.string().nullable().optional(),
	reason: z.preprocess(
		(val) => val === '' ? undefined : val,
		z.string().min(10, "Le motif doit avoir au moins 10 caractères").optional()
	)
});


export type VacancySchemaType = z.infer<typeof vacancySchema>;

