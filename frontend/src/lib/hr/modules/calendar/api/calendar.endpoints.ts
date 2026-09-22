import APIEndPoint from '@/hr/utilities/http/rest';


// ==========================================
// Backend types (snake_case, aligned with CalendarEventOut schema)
// ==========================================

export interface CalendarEventOut {
  id: string;
  name: string;
  code: string | null;
  event_type: string;
  start_date: string;
  end_date: string | null;
  start_time: string | null;
  end_time: string | null;
  is_workable: boolean;
  recurrent: string;
  description: string | null;
  status: string;
  country_code: string | null;
  created_at: string;
  updated_at: string;
}

export interface CalendarEventCreateIn {
  name: string;
  event_type: string;
  start_date: string;
  end_date?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  is_workable?: boolean;
  recurrent?: string;
  description?: string | null;
  status?: string;
  country_code?: string | null;
}

export interface CalendarEventUpdateIn {
  name?: string;
  event_type?: string;
  start_date?: string;
  end_date?: string | null;
  start_time?: string | null;
  end_time?: string | null;
  is_workable?: boolean;
  recurrent?: string;
  description?: string | null;
  status?: string;
}


/**
 * Endpoints API pour la gestion du calendrier
 * Base path: /api/calendar
 *
 * Note: les URLs sont SANS slash final pour correspondre
 * au routage Django-Ninja (APPEND_SLASH ne retire pas les slashes).
 */
export const calendarEndpoint = {
  // ==========================================
  // EVENTS
  // ==========================================

  /**
   * GET /api/calendar/events
   * Liste tous les événements avec filtrage optionnel
   */
  listEvents: async (params?: {
    start_date?: string;
    end_date?: string;
    event_type?: string;
    search?: string;
    country_code?: string;
    status?: string;
    is_workable?: boolean;
    recurrent?: string;
  }): Promise<CalendarEventOut[]> => {
    const queryParams = new URLSearchParams();
    if (params?.start_date) queryParams.set('start_date', params.start_date);
    if (params?.end_date) queryParams.set('end_date', params.end_date);
    if (params?.event_type) queryParams.set('event_type', params.event_type);
    if (params?.search) queryParams.set('search', params.search);
    if (params?.country_code) queryParams.set('country_code', params.country_code);
    if (params?.status) queryParams.set('status', params.status);
    if (params?.is_workable !== undefined) queryParams.set('is_workable', params.is_workable.toString());
    if (params?.recurrent) queryParams.set('recurrent', params.recurrent);

    const queryString = queryParams.toString();
    const url = queryString ? `/api/calendar/events?${queryString}` : '/api/calendar/events';

    const endpoint = new APIEndPoint(url, url);
    return await endpoint.list();
  },

  /**
   * POST /api/calendar/events
   * Crée un nouvel événement
   */
  createEvent: async (data: CalendarEventCreateIn): Promise<CalendarEventOut> => {
    const endpoint = new APIEndPoint('/api/calendar/events', '/api/calendar/events');
    return await endpoint.create(data);
  },

  /**
   * GET /api/calendar/events/{event_id}
   * Récupère les détails d'un événement
   */
  getEvent: async (eventId: string): Promise<CalendarEventOut> => {
    const endpoint = new APIEndPoint(
      `/api/calendar/events/${eventId}`,
      `/api/calendar/events/${eventId}`
    );
    return await endpoint.retrieve();
  },

  /**
   * PUT /api/calendar/events/{event_id}
   * Met à jour un événement existant
   */
  updateEvent: async (eventId: string, data: CalendarEventUpdateIn): Promise<CalendarEventOut> => {
    const endpoint = new APIEndPoint(
      `/api/calendar/events/${eventId}`,
      `/api/calendar/events/${eventId}`
    );
    return await endpoint.update(data);
  },

  /**
   * PATCH /api/calendar/events/{event_id}
   * Met à jour partiellement un événement existant
   */
  partialUpdateEvent: async (eventId: string, data: CalendarEventUpdateIn): Promise<CalendarEventOut> => {
    const endpoint = new APIEndPoint(
      `/api/calendar/events/${eventId}`,
      `/api/calendar/events/${eventId}`
    );
    return await endpoint.partial_update(data);
  },

  /**
   * DELETE /api/calendar/events/{event_id}
   * Supprime un événement
   */
  deleteEvent: async (eventId: string): Promise<void> => {
    const endpoint = new APIEndPoint(
      `/api/calendar/events/${eventId}`,
      `/api/calendar/events/${eventId}`
    );
    return await endpoint.destroy();
  },

  // ==========================================
  // INIT (import default holidays)
  // ==========================================

  /**
   * GET /api/calendar/init-default-events
   * Initialise les événements par défaut (jours fériés officiels)
   */
  initDefaultEvents: async (): Promise<CalendarEventOut[]> => {
    const endpoint = new APIEndPoint(
      '/api/calendar/init-default-events',
      '/api/calendar/init-default-events'
    );
    return await endpoint.list();
  },

  /**
   * POST /api/calendar/reset-holidays
   * Supprime tous les PUBLIC_HOLIDAY et les réimporte depuis le fixture
   */
  resetHolidays: async (): Promise<CalendarEventOut[]> => {
    const endpoint = new APIEndPoint(
      '/api/calendar/reset-holidays',
      '/api/calendar/reset-holidays'
    );
    return await endpoint.create({});
  },
};
