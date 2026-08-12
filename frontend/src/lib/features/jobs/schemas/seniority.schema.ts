import { z } from 'zod';
import type { SeniorityLevel } from '../types/types';


export const seniorityLevelSchema = z.object({
  level: z.string().min(1, 'Le niveau de séniorité est requis'),
  rank: z.number().int().positive('Le rang doit être un nombre positif'),
  requirements: z.array(z.string()).min(1, "Au moins une compétence/exigence est requise"),
  // Classe professionnelle RDC (1-7) — optionnelle (grille des catégories)
  classe: z.number().int().min(1, 'La classe doit être entre 1 et 7').max(7, 'La classe doit être entre 1 et 7').nullable().optional(),
});

export type SeniorityLevelFormData = z.infer<typeof seniorityLevelSchema>;

// Options pour le niveau de séniorité
export const SENIORITY_LEVEL_OPTIONS: { value: SeniorityLevel; label: string }[] = [
  { value: 'TRAINEE', label: 'Stagiaire' },
  { value: 'APPRENTICE', label: 'Apprenti' },
  { value: 'JUNIOR', label: 'Junior' },
  { value: 'INTERMEDIATE', label: 'Intermédiaire' },
  { value: 'SENIOR', label: 'Senior' },
  { value: 'LEAD', label: 'Lead' },
  { value: 'MANAGER', label: 'Manager' },
  { value: 'DIRECTOR', label: 'Directeur' },
  { value: 'EXECUTIVE', label: 'Exécutif' },
];
