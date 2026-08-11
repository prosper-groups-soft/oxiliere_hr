/**
 * Constantes pour les types de contrat et rémunération
 * Alignées avec les modèles backend
 */


export const REMUNERATION_TYPES = [
  { value: 'FIXED', label: 'Salaire Fixe' },
  { value: 'HOURLY', label: 'Taux Horaire' },
  { value: 'GROSS_UP', label: 'Brutage (Net à Brut)' }
] as const;


export const PAYMENT_PERIODS = [
  { value: 'MONTHLY', label: 'Mensuel' },
  { value: 'BIWEEKLY', label: 'Quinzaine / Bi-mensuel' },
  { value: 'WEEKLY', label: 'Hebdomadaire' },
  { value: 'DAILY', label: 'Journalier' },
  { value: 'PER_TASK', label: 'À la tâche / Forfaitaire' }
] as const;


export const SALARY_BASE_TYPES = [
  { value: 'NET', label: 'Net' },
  { value: 'GROSS', label: 'Brut' }
] as const;


export const CURRENCIES = [
  { value: 'CDF', label: 'CDF (Franc Congolais)' },
  { value: 'USD', label: 'USD (Dollar Américain)' },
  { value: 'EUR', label: 'EUR (Euro)' }
] as const;


export const CONTRACT_TYPES = [
  { value: 'CDI', label: 'CDI (Indéterminé)' },
  { value: 'CDD', label: 'CDD (Durée Déterminée)' },
  { value: 'INTERNSHIP', label: 'Stage Professionnel' },
  { value: 'FREELANCE', label: 'Consultance / Freelance' },
  { value: 'PROBATION', label: 'Période d\'Essai' },
  { value: 'TEMPORARY', label: 'Journalier / Temporaire' }
] as const;


/** Régimes de travail — alignés sur l'enum backend WorkRegime (enums.py L44-54) */
export const WORK_REGIMES = [
  { value: 'FULL_TIME', label: 'Temps plein' },
  { value: 'PART_TIME', label: 'Temps partiel' },
  { value: 'REDUCED_TIME', label: 'Temps réduit' },
  { value: 'INTERMITTENT', label: 'Travail intermittent' },
  { value: 'SEASONAL', label: 'Travail saisonnier' },
  { value: 'SHIFT', label: 'Travail posté' },
  { value: 'NIGHT', label: 'Travail de nuit' },
  { value: 'HOME', label: 'Travail à domicile' },
  { value: 'REMOTE', label: 'Télétravail' }
] as const;


// Types pour TypeScript
export type RemunerationType = typeof REMUNERATION_TYPES[number]['value'];
export type PaymentPeriod = typeof PAYMENT_PERIODS[number]['value'];
export type SalaryBaseType = typeof SALARY_BASE_TYPES[number]['value'];
export type Currency = typeof CURRENCIES[number]['value'];
export type ContractType = typeof CONTRACT_TYPES[number]['value'];
export type WorkRegime = typeof WORK_REGIMES[number]['value'];

