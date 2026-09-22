import type { EventType } from "../types/types";
import { EVENT_TYPE_LABELS } from "../types/types";

// ==========================================
// Months
// ==========================================

export const MONTHS = [
  "Janvier", "Février", "Mars", "Avril", "Mai", "Juin",
  "Juillet", "Août", "Septembre", "Octobre", "Novembre", "Décembre"
] as const;

export const SHORT_MONTHS = [
  "Jan", "Fév", "Mar", "Avr", "Mai", "Juin",
  "Juil", "Aoû", "Sep", "Oct", "Nov", "Déc"
] as const;

// ==========================================
// Status
// ==========================================

export const STATUS_LABELS: Record<string, string> = {
  PENDING: 'En attente',
  APPROVED: 'Approuvé',
  REJECTED: 'Rejeté',
  CANCELLED: 'Annulé',
  TAKEN: 'Archivé',
};

export const STATUS_COLORS: Record<string, string> = {
  PENDING: 'bg-amber-100 text-amber-700 border-amber-200',
  APPROVED: 'bg-emerald-100 text-emerald-700 border-emerald-200',
  REJECTED: 'bg-red-100 text-red-700 border-red-200',
  CANCELLED: 'bg-slate-100 text-slate-500 border-slate-200',
  TAKEN: 'bg-slate-100 text-slate-500 border-slate-200',
};

export const STATUS_PILL: Record<string, string> = {
  PENDING: 'bg-amber-100 text-amber-600',
  APPROVED: 'bg-emerald-100 text-emerald-600',
  REJECTED: 'bg-red-100 text-red-600',
  CANCELLED: 'bg-slate-100 text-slate-400',
  TAKEN: 'bg-slate-100 text-slate-400',
};

export const STATUS_OPTIONS = Object.entries(STATUS_LABELS)
  .filter(([key]) => key !== 'TAKEN')
  .map(([value, label]) => ({ value, label }));

// ==========================================
// Event Types
// ==========================================

export const TYPE_ICONS: Record<string, string> = {
  holiday: 'sun',
  closure: 'briefcase',
  training: 'graduation-cap',
  deadline: 'calendar-clock',
  anniversary: 'cake',
  leave: 'calendar-minus',
};

export const TIME_BADGE_COLORS: Record<string, string> = {
  holiday: 'bg-red-100 text-red-500',
  closure: 'bg-amber-100 text-amber-500',
  training: 'bg-indigo-100 text-indigo-500',
  deadline: 'bg-purple-100 text-purple-500',
  anniversary: 'bg-pink-100 text-pink-500',
  leave: 'bg-teal-100 text-teal-500',
};

export const TYPE_META: Record<EventType, { bg: string; text: string; border: string }> = {
  holiday: { bg: 'bg-red-50', text: 'text-red-600', border: 'border-red-100/50' },
  closure: { bg: 'bg-amber-50', text: 'text-amber-600', border: 'border-amber-100/50' },
  training: { bg: 'bg-indigo-50', text: 'text-indigo-600', border: 'border-indigo-100/50' },
  deadline: { bg: 'bg-purple-50', text: 'text-purple-600', border: 'border-purple-100/50' },
  anniversary: { bg: 'bg-pink-50', text: 'text-pink-600', border: 'border-pink-100/50' },
  leave: { bg: 'bg-teal-50', text: 'text-teal-600', border: 'border-teal-100/50' },
};

/** Type options with plural labels (for filters/actions) */
export const TYPE_OPTIONS: { value: EventType; label: string; icon: string }[] = [
  { value: 'holiday', label: 'Jours Fériés', icon: 'sun' },
  { value: 'closure', label: 'Fermetures', icon: 'briefcase' },
  { value: 'training', label: 'Formations', icon: 'graduation-cap' },
  { value: 'deadline', label: 'Échéances', icon: 'calendar-clock' },
  { value: 'anniversary', label: 'Anniversaires', icon: 'cake' },
  { value: 'leave', label: 'Congés / Absences', icon: 'calendar-minus' },
];

/** Type options with singular labels (for EventSheet form) — derives from EVENT_TYPE_LABELS */
export const TYPE_OPTIONS_SINGULAR: { value: EventType; label: string }[] = (
  Object.entries(EVENT_TYPE_LABELS) as [EventType, string][]
).map(([value, label]) => ({ value, label }));

// ==========================================
// Recurrence
// ==========================================

export const RECURRENCE_LABELS: Record<string, string> = {
  NONE: 'Non récurrent',
  YEARLY: 'Annuel',
  MONTHLY: 'Mensuel',
  WEEKLY: 'Hebdomadaire',
  DAILY: 'Quotidien',
};

export const RECURRENCE_OPTIONS: { value: string; label: string }[] = (
  Object.entries(RECURRENCE_LABELS) as [string, string][]
).map(([value, label]) => ({ value, label }));

// ==========================================
// Display
// ==========================================

/** Max visible events per day cell before "+X more" collapse */
export const MAX_VISIBLE_EVENTS = 3;
