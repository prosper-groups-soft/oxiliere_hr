import { z } from 'zod';


export const bankAccountSchema = z.object({
  employeeId: z.string({ message: "L'employé est requis" }).min(1, "L'employé est requis"),
  institutionId: z.string({ message: "La banque est requise" }).min(1, "La banque est requise"),
  accountNumber: z.string({ message: "Le numéro de compte est requis" }).min(1, "Le numéro de compte est requis").max(50, "Le numéro de compte ne doit pas dépasser 50 caractères"),
  accountName: z.string().optional(),
  branchCode: z.string().max(10, "Le code guichet ne doit pas dépasser 10 caractères").optional(),
  iban: z.string().max(34, "L'IBAN ne doit pas dépasser 34 caractères").optional(),
  currencies: z.array(z.string()).min(1, "Sélectionnez au moins une devise"),
  defaultCurrency: z.string().min(1, "La devise par défaut est requise"),
  type: z.enum(['checking', 'savings', 'salary', 'mobile_money'], {
    message: "Le type de compte est requis"
  }),
  isPrimary: z.boolean().optional(),
  notes: z.string().optional(),
});


export type BankAccountSchemaType = z.infer<typeof bankAccountSchema>;

