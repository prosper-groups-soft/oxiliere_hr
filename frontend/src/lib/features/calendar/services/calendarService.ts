import { notification } from '@/stores/notification.svelte';
import { getFriendlyErrorMessage } from '@/constants/errors';
import { calendarEndpoint } from '../api/calendar.endpoints';
import type { CalendarEventCreateIn, CalendarEventUpdateIn, CalendarEventOut } from '../api/calendar.endpoints';
import type { CalendarEvent, EventType, CalendarFilterParams } from '../types/types';
import { BACKEND_TO_FRONTEND_TYPE, FRONTEND_TO_BACKEND_TYPE } from '../types/types';


/**
 * Normalise un CalendarEventOut (backend) vers CalendarEvent (frontend)
 * snake_case → camelCase
 */
function mapBackendToFrontend(event: CalendarEventOut): CalendarEvent {
  return {
    id: event.id,
    title: event.name,
    defaultDate: event.start_date,
    endDate: event.end_date || undefined,
    type: mapEventType(event.event_type),
    scopeId: event.country_code || undefined,
    countryCode: event.country_code || undefined,
    isWorkable: event.is_workable,
    recurrent: event.recurrent !== 'NONE' ? event.recurrent : undefined,
    description: event.description || undefined,
    status: event.status,
    code: event.code || undefined,
    startTime: event.start_time || undefined,
    endTime: event.end_time || undefined,
    createdAt: event.created_at,
    updatedAt: event.updated_at,
  };
}

/**
 * Mappe le type d'événement backend → frontend
 */
function mapEventType(backendType: string): EventType {
  return BACKEND_TO_FRONTEND_TYPE[backendType] || 'training';
}

/**
 * Mappe le type d'événement frontend → backend
 */
function mapToBackendType(type: EventType): string {
  return FRONTEND_TO_BACKEND_TYPE[type] || 'OTHER';
}


/**
 * Service pour la gestion du calendrier
 * Utilise les endpoints dédiés dans le dossier api/
 */
class CalendarService {
  /**
   * Liste les événements selon les filtres
   * Pas de pagination : on charge tout selon les paramètres
   */
  async list(filters?: CalendarFilterParams): Promise<CalendarEvent[]> {
    try {
      // Map frontend filters to backend query params
      const params: Record<string, string | undefined> = {};
      if (filters?.start_date) params.start_date = filters.start_date;
      if (filters?.end_date) params.end_date = filters.end_date;
      if (filters?.event_type) params.event_type = filters.event_type;
      if (filters?.search) params.search = filters.search;
      if (filters?.country_code) params.country_code = filters.country_code;
      if (filters?.status) params.status = filters.status;
      if (filters?.recurrent) params.recurrent = filters.recurrent;
      if (filters?.is_workable !== undefined) params.is_workable = String(filters.is_workable);

      const response = await calendarEndpoint.listEvents(params);
      const events = response.map(mapBackendToFrontend);

      return events;
    } catch (error: any) {
      console.error('[CalendarService] list error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Récupère un événement par son ID
   */
  async get(eventId: string): Promise<CalendarEvent> {
    try {
      const event = await calendarEndpoint.getEvent(eventId);
      return mapBackendToFrontend(event);
    } catch (error: any) {
      console.error('[CalendarService] get error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Crée un nouvel événement
   */
  async create(data: {
    title: string;
    type: EventType;
    defaultDate: string;
    endDate?: string;
    startTime?: string;
    endTime?: string;
    description?: string;
    countryCode?: string;
    isWorkable?: boolean;
    recurrent?: string;
    status?: string;
  }): Promise<CalendarEvent> {
    try {
      const payload: CalendarEventCreateIn = {
        name: data.title,
        event_type: mapToBackendType(data.type),
        start_date: data.defaultDate,
        end_date: data.endDate || null,
        description: data.description || null,
        country_code: data.countryCode || null,
        start_time: data.startTime || null,
        end_time: data.endTime || null,
        is_workable: data.isWorkable ?? true,
        recurrent: data.recurrent || 'NONE',
        status: data.status || 'APPROVED',
      };

      const event = await calendarEndpoint.createEvent(payload);
      notification.toast.success('Événement créé avec succès');
      return mapBackendToFrontend(event);
    } catch (error: any) {
      console.error('[CalendarService] create error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Met à jour un événement existant
   */
  async update(
    eventId: string,
    data: {
      title?: string;
      type?: EventType;
      defaultDate?: string;
      endDate?: string;
      startTime?: string;
      endTime?: string;
      description?: string;
      isWorkable?: boolean;
      recurrent?: string;
      status?: string;
    }
  ): Promise<CalendarEvent> {
    try {
      const payload: CalendarEventUpdateIn = {};
      if (data.title !== undefined) payload.name = data.title;
      if (data.type !== undefined) payload.event_type = mapToBackendType(data.type);
      if (data.defaultDate !== undefined) payload.start_date = data.defaultDate;
      if (data.endDate !== undefined) payload.end_date = data.endDate || null;
      if (data.startTime !== undefined) payload.start_time = data.startTime || null;
      if (data.endTime !== undefined) payload.end_time = data.endTime || null;
      if (data.description !== undefined) payload.description = data.description || null;
      if (data.isWorkable !== undefined) payload.is_workable = data.isWorkable;
      if (data.recurrent !== undefined) payload.recurrent = data.recurrent;
      if (data.status !== undefined) payload.status = data.status;

      const event = await calendarEndpoint.partialUpdateEvent(eventId, payload);
      notification.toast.success('Événement mis à jour avec succès');
      return mapBackendToFrontend(event);
    } catch (error: any) {
      console.error('[CalendarService] update error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Supprime un événement
   */
  async delete(eventId: string): Promise<void> {
    try {
      await calendarEndpoint.deleteEvent(eventId);
      notification.toast.success('Événement supprimé');
    } catch (error: any) {
      console.error('[CalendarService] delete error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }

  /**
   * Réinitialise les jours fériés : supprime tous les PUBLIC_HOLIDAY
   * et les réimporte depuis le fixture du backend
   */
  async resetHolidays(): Promise<CalendarEvent[]> {
    try {
      const response = await calendarEndpoint.resetHolidays();
      const events = response.map(mapBackendToFrontend);
      notification.toast.success('Jours fériés réinitialisés avec succès');
      return events;
    } catch (error: any) {
      console.error('[CalendarService] resetHolidays error:', error);
      const message = getFriendlyErrorMessage(error);
      notification.toast.error(message);
      throw error;
    }
  }
}

export const calendarService = new CalendarService();
