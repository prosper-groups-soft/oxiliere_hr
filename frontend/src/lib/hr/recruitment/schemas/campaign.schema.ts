import { z } from 'zod';


export const campaignSchema = z.object({
  title: z.string().min(1, 'Le titre est obligatoire'),
  jobIds: z.array(z.string()).min(1, 'Au moins un poste est obligatoire'),
  jobNames: z.array(z.string()).min(1, 'Au moins un poste est obligatoire'),
  location: z.string().optional(),
  status: z.enum(['DRAFT', 'OPEN', 'PAUSED', 'CLOSED']),
  targetHires: z.number().min(1, 'Le nombre de postes doit être au moins 1'),
  description: z.string().optional(),
  requirements: z.array(z.string()).optional(),
  salaryRange: z.string().optional(),
  closeDate: z.string().optional(),
  vacancyIds: z.array(z.string()).optional(),
  maxApplications: z.number().optional(),
  recruiterId: z.string().optional()
});


export type CampaignFormData = z.infer<typeof campaignSchema>;

