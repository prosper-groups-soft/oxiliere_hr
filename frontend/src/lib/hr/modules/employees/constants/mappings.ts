/**
 * Constantes de mapping pour les champs d'identité
 * Utilisées pour convertir entre les valeurs du frontend et du backend
 */


// Mapping des valeurs du frontend vers les valeurs attendues par le backend
export const GENDER_MAPPING = {
  'Homme': 'MALE',
  'Femme': 'FEMALE',
  'Non spécifié': 'NOT_SPECIFIED'
} as const;


export const MARITAL_STATUS_MAPPING = {
  'Célibataire': 'SINGLE',
  'Marié(e)': 'MARRIED',
  'Divorcé(e)': 'DIVORCED',
  'Veuf(ve)': 'WIDOWED'
} as const;


// Mapping inverse pour trouver le label à partir du code du backend
export const REVERSE_GENDER_MAPPING = {
  'MALE': 'Homme',
  'FEMALE': 'Femme',
  'NOT_SPECIFIED': 'Non spécifié'
} as const;


export const REVERSE_MARITAL_STATUS_MAPPING = {
  'SINGLE': 'Célibataire',
  'MARRIED': 'Marié(e)',
  'DIVORCED': 'Divorcé(e)',
  'WIDOWED': 'Veuf(ve)'
} as const;


export const REVERSE_STATUS_MAPPING = {
  'ACTIVE': 'Actif',
  'PROBATION': 'Période d\'essai',
  'SUSPENDED': 'Suspendu',
  'MATERNITY_LEAVE': 'Congé maternité/paternité',
  'SICK_LEAVE': 'Congé maladie',
  'SABBATICAL': 'Congé sabbatique',
  'TERMINATED': 'Licencié',
  'RESIGNED': 'Démissionné',
  'RETIRED': 'Retraité'
} as const;


// Types pour les mappings
export type GenderMapping = typeof GENDER_MAPPING;
export type MaritalStatusMapping = typeof MARITAL_STATUS_MAPPING;
export type ReverseGenderMapping = typeof REVERSE_GENDER_MAPPING;
export type ReverseMaritalStatusMapping = typeof REVERSE_MARITAL_STATUS_MAPPING;


// Types des valeurs possibles
export type GenderValue = GenderMapping[keyof GenderMapping] | '';
export type MaritalStatusValue = MaritalStatusMapping[keyof MaritalStatusMapping] | '';
export type BackendGenderValue = 'MALE' | 'FEMALE' | 'NOT_SPECIFIED';
export type BackendMaritalStatusValue = 'SINGLE' | 'MARRIED' | 'DIVORCED' | 'WIDOWED';


// Relations (contacts d'urgence)
export const RELATION_TYPES = [
  { value: 'SPOUSE', label: 'Conjoint(e)' },
  { value: 'PARENT', label: 'Parent' },
  { value: 'CHILD', label: 'Enfant' },
  { value: 'SIBLING', label: 'Frère / Soeur' },
  { value: 'PARTNER', label: 'Partenaire' },
  { value: 'FRIEND', label: 'Ami(e)' },
  { value: 'OTHER', label: 'Autre' }
] as const;

export const REVERSE_RELATION_MAPPING: Record<string, string> = {
  'SPOUSE': 'Conjoint(e)',
  'PARENT': 'Parent',
  'CHILD': 'Enfant',
  'SIBLING': 'Frère / Soeur',
  'PARTNER': 'Partenaire',
  'FRIEND': 'Ami(e)',
  'OTHER': 'Autre'
};

