export type EventType = 'holiday' | 'closure' | 'training' | 'deadline' | 'anniversary' | 'leave';

export const EVENT_TYPE_LABELS: Record<EventType, string> = {
  'holiday': 'Jour Férié',
  'closure': 'Fermeture Entreprise',
  'training': 'Formation',
  'deadline': 'Échéance',
  'anniversary': 'Anniversaire',
  'leave': 'Congé / Absence',
};

export const EVENT_TYPE_COLORS: Record<EventType, { bg: string; text: string; border: string; dot: string }> = {
  'holiday': { bg: 'bg-red-50', text: 'text-red-700', border: 'border-red-200', dot: 'bg-red-500' },
  'closure': { bg: 'bg-amber-50', text: 'text-amber-700', border: 'border-amber-200', dot: 'bg-amber-500' },
  'training': { bg: 'bg-indigo-50', text: 'text-indigo-700', border: 'border-indigo-200', dot: 'bg-indigo-500' },
  'deadline': { bg: 'bg-purple-50', text: 'text-purple-700', border: 'border-purple-200', dot: 'bg-purple-500' },
  'anniversary': { bg: 'bg-pink-50', text: 'text-pink-700', border: 'border-pink-200', dot: 'bg-pink-500' },
  'leave': { bg: 'bg-teal-50', text: 'text-teal-700', border: 'border-teal-200', dot: 'bg-teal-500' },
};

/**
 * Backend → Frontend event type mapping
 */
export const BACKEND_TO_FRONTEND_TYPE: Record<string, EventType> = {
  'PUBLIC_HOLIDAY': 'holiday',
  'COMPANY_EVENT': 'closure',
  'DEADLINE': 'deadline',
  'ANNIVERSARY': 'anniversary',
  'LEAVE': 'leave',
  'OTHER': 'training',
};

/**
 * Frontend → Backend event type mapping
 */
export const FRONTEND_TO_BACKEND_TYPE: Record<EventType, string> = {
  'holiday': 'PUBLIC_HOLIDAY',
  'closure': 'COMPANY_EVENT',
  'training': 'OTHER',
  'deadline': 'DEADLINE',
  'anniversary': 'ANNIVERSARY',
  'leave': 'LEAVE',
};

export interface CalendarEvent {
  id: string;
  title: string;
  defaultDate: string; // ISO string YYYY-MM-DD
  endDate?: string;
  type: EventType;
  scopeId?: string;
  /** Backend-only: country code (e.g. "CD" for RDC) */
  countryCode?: string;
  /** Whether the day is workable */
  isWorkable?: boolean;
  /** Recurrence type (NONE, DAILY, WEEKLY, MONTHLY, YEARLY) */
  recurrent?: string;
  /** Optional description */
  description?: string;
  /** Event status (PENDING, APPROVED, REJECTED, CANCELLED, TAKEN) */
  status?: string;
  /** Internal code for the event */
  code?: string;
  /** Start time (HH:MM) */
  startTime?: string;
  /** End time (HH:MM) */
  endTime?: string;
  /** Timestamps */
  createdAt?: string;
  updatedAt?: string;
}

export interface DayClosure {
  date: string;
  reason: string;
  isHoliday: boolean;
}

/**
 * Filters passed to the backend list endpoint
 */
export interface CalendarFilterParams {
  start_date?: string;
  end_date?: string;
  event_type?: string;
  search?: string;
  country_code?: string;
  status?: string;
  is_workable?: boolean;
  recurrent?: string;
}
