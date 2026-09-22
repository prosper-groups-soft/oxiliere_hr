import { z } from 'zod';
import type { CandidateSource, CreateCandidateInput } from '../types/types';

export const createCandidateSchema = z.object({
	firstName: z.string().min(2, 'Le prénom doit contenir au moins 2 caractères'),
	lastName: z.string().min(2, 'Le nom doit contenir au moins 2 caractères'),
	email: z.string().email('Email invalide'),
	phone: z.string().min(10, 'Le numéro de téléphone doit contenir au moins 10 caractères'),
	source: z.enum(['LINKEDIN', 'CAREER_SITE', 'REFERRAL', 'DIRECT'] as const),
	positionId: z.string().optional(),
	resumeUrl: z.string().url('URL invalide').optional().or(z.literal('')),
	notes: z.string().max(1000, 'Les notes ne doivent pas dépasser 1000 caractères').optional()
});

export const updateCandidateSchema = z.object({
	firstName: z.string().min(2, 'Le prénom doit contenir au moins 2 caractères').optional(),
	lastName: z.string().min(2, 'Le nom doit contenir au moins 2 caractères').optional(),
	email: z.string().email('Email invalide').optional(),
	phone: z
		.string()
		.min(10, 'Le numéro de téléphone doit contenir au moins 10 caractères')
		.optional(),
	priority: z.enum(['LOW', 'MEDIUM', 'HIGH'] as const).optional(),
	notes: z.string().max(1000, 'Les notes ne doivent pas dépasser 1000 caractères').optional()
});

export const createInterviewSchema = z.object({
	candidateId: z.string().min(1, "L'ID du candidat est requis"),
	interviewerId: z.string().min(1, "L'ID de l'interviewer est requis"),
	type: z.enum(['PHONE', 'VIDEO', 'ONSITE'] as const),
	scheduledDate: z.string().min(1, 'La date est requise'),
	duration: z
		.number()
		.min(15, "La durée doit être d'au moins 15 minutes")
		.max(240, 'La durée ne doit pas dépasser 4 heures'),
	location: z.string().optional()
});

export const createJobOfferSchema = z
	.object({
		candidateId: z.string().min(1, "L'ID du candidat est requis"),
		positionId: z.string().min(1, "L'ID du poste est requis"),
		salaryMin: z.number().min(0, 'Le salaire minimum doit être positif'),
		salaryMax: z.number().min(0, 'Le salaire maximum doit être positif'),
		currency: z
			.string()
			.min(3, 'La devise doit contenir 3 caractères')
			.max(3, 'La devise doit contenir 3 caractères'),
		startDate: z.string().min(1, 'La date de début est requise')
	})
	.refine((data) => data.salaryMax >= data.salaryMin, {
		message: 'Le salaire maximum doit être supérieur ou égal au minimum',
		path: ['salaryMax']
	});

export type CreateCandidateForm = z.infer<typeof createCandidateSchema>;
export type UpdateCandidateForm = z.infer<typeof updateCandidateSchema>;
export type CreateInterviewForm = z.infer<typeof createInterviewSchema>;
export type CreateJobOfferForm = z.infer<typeof createJobOfferSchema>;
