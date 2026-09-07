/**
 * Constantes pour les types de contrat et rémunération
 * Alignées avec les modèles backend
 */


export const REMUNERATION_TYPES = [
  { value: 'FIXED', label: 'Salaire Fixe' },
  { value: 'HOURLY', label: 'Taux Horaire' }
] as const;


export const SALARY_BASE_TYPES = [
  { value: 'BASE', label: 'Salaire de base' },
  { value: 'NET', label: 'Net (brutage)' }
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


// PAYMENT_PERIODS supprimé — la périodicité appartient au run de paie,
// pas au contrat (métamodèle §7.1). Le pipeline calcule toujours au mois.
// WORK_REGIMES masqué — fonctionnalité « taux d'activité » à développer
// (métamodèle §7.2). La colonne DB est conservée, le champ API/UI est retiré.


// Types pour TypeScript
export type RemunerationType = typeof REMUNERATION_TYPES[number]['value'];
export type SalaryBaseType = typeof SALARY_BASE_TYPES[number]['value'];
export type Currency = typeof CURRENCIES[number]['value'];
export type ContractType = typeof CONTRACT_TYPES[number]['value'];

