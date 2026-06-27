/**
 * Constantes pour le module Recruitment
 */


// Options de filtre pour le statut des campagnes
export const CAMPAIGN_STATUS_OPTIONS = [
  { value: 'OPEN', label: 'Ouvert' },
  { value: 'PAUSED', label: 'En pause' },
  { value: 'DRAFT', label: 'Brouillon' },
  { value: 'CLOSED', label: 'Fermé' }
];


// Options de filtre pour le type de contrat
export const CAMPAIGN_TYPE_OPTIONS = [
  { value: 'CDI', label: 'CDI (Indéterminé)' },
  { value: 'CDD', label: 'CDD (Durée Déterminée)' },
  { value: 'INTERNSHIP', label: 'Stage Professionnel' },
  { value: 'FREELANCE', label: 'Consultance / Freelance' },
  { value: 'PROBATION', label: 'Période d\'Essai' },
  { value: 'TEMPORARY', label: 'Journalier / Temporaire' }
];


// Labels pour les filtres
export const CAMPAIGN_STATUS_LABELS: Record<string, string> = {
  'OPEN': 'Ouvert',
  'PAUSED': 'En pause',
  'DRAFT': 'Brouillon',
  'CLOSED': 'Fermé'
};


// Labels pour les types de contrat
export const CAMPAIGN_TYPE_LABELS: Record<string, string> = {
  'CDI': 'CDI (Indéterminé)',
  'CDD': 'CDD (Durée Déterminée)',
  'INTERNSHIP': 'Stage Professionnel',
  'FREELANCE': 'Consultance / Freelance',
  'PROBATION': "Période d'Essai",
  'TEMPORARY': 'Journalier / Temporaire'
};


// Labels de tri
export const CAMPAIGN_SORT_LABELS: Record<string, string> = {
  title: "Titre (A-Z)",
  jobName: "Poste",
  status: "Statut",
  openDate: "Date d'ouverture"
};


export const STATUS_CONFIG: Record<string, { label: string, color: string, bg: string, border: string, dot: string }> = {
  'OPEN':   { label: CAMPAIGN_STATUS_LABELS.OPEN, color: 'text-blue-700', bg: 'bg-blue-50', border: 'border-blue-100', dot: 'bg-blue-500' },
  'PAUSED': { label: CAMPAIGN_STATUS_LABELS.PAUSED, color: 'text-amber-700', bg: 'bg-amber-50', border: 'border-amber-100', dot: 'bg-amber-500' },
  'DRAFT':  { label: CAMPAIGN_STATUS_LABELS.DRAFT, color: 'text-slate-600', bg: 'bg-slate-50', border: 'border-slate-200', dot: 'bg-slate-400' },
  'CLOSED': { label: CAMPAIGN_STATUS_LABELS.CLOSED, color: 'text-emerald-700', bg: 'bg-emerald-50', border: 'border-emerald-100', dot: 'bg-emerald-500' }
};


// ---------------------------------------------------------------------------
// Mapping des statuts Application backend (ApplicationStatus) → CandidateStage frontend
// ---------------------------------------------------------------------------
export const APPLICATION_STATUS_MAP: Record<string, string> = {
  PENDING: 'SCREENING',
  REVIEW: 'SHORTLIST',
  INTERVIEW: 'INTERVIEW',
  OFFER: 'OFFER',
  ACCEPTED: 'ACCEPTED',
  REJECTED: 'REJECTED',
  WITHDRAWN: 'REJECTED',
};


export function mapApplicationStatusToCandidateStage(status: string): string {
  return APPLICATION_STATUS_MAP[status] || 'SCREENING';
}

// ---------------------------------------------------------------------------
// Options de filtre pour les candidats
// ---------------------------------------------------------------------------

// Étapes de candidature
export const CANDIDATE_STAGE_OPTIONS = [
  { value: 'SCREENING' as const, label: 'Tri', icon: 'filter' },
  { value: 'SHORTLIST' as const, label: 'Shortlist', icon: 'star' },
  { value: 'INTERVIEW' as const, label: 'Entretien', icon: 'users' },
  { value: 'OFFER' as const, label: 'Offre', icon: 'send' },
  { value: 'ACCEPTED' as const, label: 'Acceptée', icon: 'check' },
  { value: 'REJECTED' as const, label: 'Rejeté', icon: 'x' }
];


export const CANDIDATE_STAGE_LABELS: Record<string, string> = {
  'SCREENING': 'Tri',
  'SHORTLIST': 'Shortlist',
  'INTERVIEW': 'Entretien',
  'OFFER': 'Offre',
  'ACCEPTED': 'Acceptée',
  'REJECTED': 'Rejeté'
};


// Priorités
export const CANDIDATE_PRIORITY_OPTIONS = [
  { value: 'HIGH' as const, label: 'Urgente', color: 'text-red-500' },
  { value: 'MEDIUM' as const, label: 'Normale', color: 'text-amber-500' },
  { value: 'LOW' as const, label: 'Faible', color: 'text-emerald-500' }
];


export const CANDIDATE_PRIORITY_LABELS: Record<string, string> = {
  'HIGH': 'Urgente',
  'MEDIUM': 'Normale',
  'LOW': 'Faible'
};


export const CANDIDATE_SOURCE_OPTIONS = [
  { value: 'LINKEDIN' as const, label: 'LinkedIn', icon: 'linkedin' },
  { value: 'CAREER_SITE' as const, label: 'Site Carrière', icon: 'globe' },
  { value: 'REFERRAL' as const, label: 'Cooptation', icon: 'users' },
  { value: 'DIRECT' as const, label: 'Direct', icon: 'mail' }
] as const;


export const CANDIDATE_SOURCE_LABELS: Record<string, string> = {
  'LINKEDIN': 'LinkedIn',
  'CAREER_SITE': 'Site Carrière',
  'REFERRAL': 'Cooptation',
  'DIRECT': 'Direct'
};


// Options de sexe/genre
export const CANDIDATE_GENDER_OPTIONS = [
  { value: 'MALE' as const, label: 'Masculin', icon: 'male' },
  { value: 'FEMALE' as const, label: 'Féminin', icon: 'female' },
  { value: 'NOT_SPECIFIED' as const, label: 'Non spécifié', icon: 'help-circle' }
] as const;


export const CANDIDATE_GENDER_LABELS: Record<string, string> = {
  'MALE': 'Masculin',
  'FEMALE': 'Féminin',
  'NOT_SPECIFIED': 'Non spécifié'
};


// Configuration des étapes de candidature
export const STAGE_CONFIG: Record<
	string,
	{
		label: string;
		color: string;
		bgColor: string;
		borderColor: string;
		icon: string;
	}
> = {
	SCREENING: { 
    label: 'Tri', color: 'bg-blue-50 text-blue-700 border-blue-100',
    bgColor: 'bg-blue-50', borderColor: 'border-blue-200', icon: 'filter'
	},
	SHORTLIST: {
		label: 'Shortlist', color: 'bg-amber-50 text-amber-700 border-amber-100',
		bgColor: 'bg-amber-50', borderColor: 'border-amber-200', icon: 'star'
	},
	INTERVIEW: {
		label: 'Entretien', color: 'bg-purple-50 text-purple-700 border-purple-100',
		bgColor: 'bg-purple-50', borderColor: 'border-purple-200', icon: 'users'
	},
	OFFER: {
		label: 'Offre', color: 'bg-emerald-50 text-emerald-700 border-emerald-100',
		bgColor: 'bg-emerald-50', borderColor: 'border-emerald-200', icon: 'send'
	},
	ACCEPTED: {
		label: 'Acceptée', color: 'bg-green-50 text-green-700 border-green-100',
		bgColor: 'bg-green-50', borderColor: 'border-green-200', icon: 'check'
	},
	REJECTED: {
		label: 'Rejeté', color: 'bg-red-50 text-red-700 border-red-100',
		bgColor: 'bg-red-50', borderColor: 'border-red-200', icon: 'x'
	}
};


// Configuration des badges pour le pipeline (couleurs par étape)
export const PIPELINE_BADGE_CONFIG: Record<string, { color: string, bgColor: string, borderColor: string }> = {
	SCREENING:  { color: 'text-blue-700', bgColor: 'bg-blue-100', borderColor: 'border-blue-200' },
	SHORTLIST:  { color: 'text-amber-700', bgColor: 'bg-amber-100', borderColor: 'border-amber-200' },
	INTERVIEW:  { color: 'text-purple-700', bgColor: 'bg-purple-100', borderColor: 'border-purple-200' },
	OFFER:      { color: 'text-emerald-700', bgColor: 'bg-emerald-100', borderColor: 'border-emerald-200' },
	ACCEPTED:   { color: 'text-green-700', bgColor: 'bg-green-100', borderColor: 'border-green-200' },
	REJECTED:   { color: 'text-red-700', bgColor: 'bg-red-100', borderColor: 'border-red-200' }
};


// Configuration des priorités (avec classes complètes)
export const CANDIDATE_PRIORITY_CONFIG: Record<string, { label: string, color: string }> = {
	'HIGH':   { label: 'Urgente', color: 'bg-red-50 text-red-600 border-red-100' },
	'MEDIUM': { label: 'Normale', color: 'bg-amber-50 text-amber-600 border-amber-100' },
	'LOW':    { label: 'Faible',  color: 'bg-emerald-50 text-emerald-600 border-emerald-100' }
};


// Configuration des sources
// FIXME-v2: Compléter les icônes liées aux vraies sources
export const CANDIDATE_SOURCE_CONFIG: Record<string, { label: string, icon: string }> = {
	'LINKEDIN':     { label: 'LinkedIn',     icon: 'briefcase' },
	'CAREER_SITE':  { label: 'Site Carrière', icon: 'globe' },
	'REFERRAL':     { label: 'Cooptation',   icon: 'users' },
	'DIRECT':       { label: 'Direct',       icon: 'mail' }
};


// Configuration des statuts d'entretien
export const INTERVIEW_STATUS_CONFIG: Record<string, { label: string, color: string, icon: string }> = {
	'SCHEDULED':  { label: 'Planifié',    color: 'bg-blue-50 text-blue-600 border-blue-100', icon: 'calendar' },
	'COMPLETED':  { label: 'Terminé',    color: 'bg-green-50 text-green-600 border-green-100', icon: 'check' },
	'CANCELLED':  { label: 'Annulé',     color: 'bg-red-50 text-red-600 border-red-100', icon: 'x' },
	'NO_SHOW':    { label: 'Absent',     color: 'bg-amber-50 text-amber-600 border-amber-100', icon: 'alert' }
};


// Configuration des types d'entretien
export const INTERVIEW_TYPE_CONFIG: Record<string, { label: string, icon: string, color: string }> = {
	'PHONE':      { label: 'Téléphonique', icon: 'phone', color: 'text-blue-500' },
	'VIDEO':      { label: 'Visioconférence', icon: 'video', color: 'text-purple-500' },
	'ONSITE':     { label: 'Présentiel', icon: 'map-pin', color: 'text-emerald-500' },
	'TECHNICAL':  { label: 'Technique', icon: 'code', color: 'text-amber-500' },
	'BEHAVIORAL': { label: 'Comportemental', icon: 'users', color: 'text-indigo-500' }
};

