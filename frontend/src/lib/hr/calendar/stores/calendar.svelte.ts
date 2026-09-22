import type { CalendarEvent, EventType } from '../types/types';
import { calendarService } from '../services/calendarService';


class CalendarStore {
  events = $state<CalendarEvent[]>([]);
  loading = $state(false);
  error = $state<string | null>(null);
  selectedDate = $state<Date>(new Date());
  view = $state<'month' | 'year'>('month');
  /** Code pays par défaut pour filtrer les événements (RDC) */
  defaultCountryCode = $state('CD');

  constructor() {
    // --- Persistence du mode de vue ---
    const savedView = typeof localStorage !== 'undefined' ? localStorage.getItem('oxiliere_calendar_view') : null;
    if (savedView === 'month' || savedView === 'year') {
      this.view = savedView;
    }

    $effect.root(() => {
      // Sauvegarde du mode de vue
      $effect(() => {
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem('oxiliere_calendar_view', this.view);
        }
      });

      // Chargement automatique quand les filtres changent
      $effect(() => {
        const date = this.selectedDate;
        const year = date.getFullYear();
        const month = date.getMonth();
        const types = this.typeFilters;
        const query = this.searchQuery;
        const currentView = this.view;

        // Calcul de la plage de dates selon la vue
        let startDate: string | undefined;
        let endDate: string | undefined;

        if (query.trim()) {
          // Si recherche textuelle active, on recherche globalement
          startDate = undefined;
          endDate = undefined;
        } else if (currentView === 'year') {
          startDate = `${year}-01-01`;
          endDate = `${year}-12-31`;
        } else {
          const lastDay = new Date(year, month + 1, 0).getDate();
          startDate = `${year}-${String(month + 1).padStart(2, '0')}-01`;
          endDate = `${year}-${String(month + 1).padStart(2, '0')}-${String(lastDay).padStart(2, '0')}`;
        }

        this.#loadEvents(startDate, endDate, types.length === 1 ? types[0] : undefined, query);
      });
    });
  }

  /**
   * Charge les événements depuis le backend
   */
  async #loadEvents(startDate?: string, endDate?: string, eventType?: EventType, search?: string) {
    this.loading = true;
    this.error = null;

    try {
      const filters: Record<string, string | undefined> = {
        country_code: this.defaultCountryCode,
      };
      if (startDate) filters.start_date = startDate;
      if (endDate) filters.end_date = endDate;
      if (eventType) filters.event_type = this.#mapTypeToBackend(eventType);
      if (search) filters.search = search;

      const events = await calendarService.list(filters);
      this.events = events;
    } catch (err: any) {
      this.error = err?.message || 'Erreur lors du chargement des événements';
      console.error('[CalendarStore] load error:', err);
    } finally {
      this.loading = false;
    }
  }

  /**
   * Traduit un type frontend vers backend pour les filtres
   */
  #mapTypeToBackend(type: EventType): string {
    const map: Record<EventType, string> = {
      'holiday': 'PUBLIC_HOLIDAY',
      'closure': 'COMPANY_EVENT',
      'training': 'OTHER',
      'deadline': 'DEADLINE',
      'anniversary': 'ANNIVERSARY',
      'leave': 'LEAVE',
    };
    return map[type] || 'OTHER';
  }

  // ==========================================
  // CRUD — via le service
  // ==========================================

  async addEvent(data: {
    title: string;
    type: EventType;
    defaultDate: string;
    endDate?: string;
    startTime?: string;
    endTime?: string;
    description?: string;
    isWorkable?: boolean;
    recurrent?: string;
    status?: string;
  }) {
    try {
      const newEvent = await calendarService.create({
        title: data.title,
        type: data.type,
        defaultDate: data.defaultDate,
        endDate: data.endDate,
        startTime: data.startTime,
        endTime: data.endTime,
        description: data.description,
        isWorkable: data.isWorkable,
        recurrent: data.recurrent,
        status: data.status,
      });
      this.events = [...this.events, newEvent];
      return newEvent;
    } catch (err) {
      console.error('[CalendarStore] add error:', err);
      throw err;
    }
  }

  async updateEvent(id: string, updates: Partial<CalendarEvent>) {
    try {
      const updated = await calendarService.update(id, {
        title: updates.title,
        type: updates.type,
        defaultDate: updates.defaultDate,
        endDate: updates.endDate,
        startTime: updates.startTime,
        endTime: updates.endTime,
        description: updates.description,
        isWorkable: updates.isWorkable,
        recurrent: updates.recurrent,
        status: updates.status,
      });
      this.events = this.events.map(event =>
        event.id === id ? { ...event, ...updated } : event
      );
    } catch (err) {
      console.error('[CalendarStore] update error:', err);
      throw err;
    }
  }

  async deleteEvent(id: string) {
    try {
      await calendarService.delete(id);
      this.events = this.events.filter(event => event.id !== id);
    } catch (err) {
      console.error('[CalendarStore] delete error:', err);
      throw err;
    }
  }

  /**
   * Réinitialise les jours fériés : supprime tous les PUBLIC_HOLIDAY
   * et les réimporte depuis le fixture backend.
   * Les autres événements (formations, fermetures, échéances, etc.) sont préservés.
   */
  async resetHolidays(): Promise<number> {
    try {
      const imported = await calendarService.resetHolidays();
      if (imported.length > 0) {
        // Remplacer les événements existants par la version réimportée
        const importedIds = new Set(imported.map(e => e.id));
        // Garder les événements non-fériés + ajouter les fériés réimportés
        const nonHolidays = this.events.filter(e => e.type !== 'holiday');
        this.events = [...nonHolidays, ...imported];
      }
      return imported.length;
    } catch (err) {
      console.error('[CalendarStore] resetHolidays error:', err);
      throw err;
    }
  }

  // ==========================================
  // Filters & Search
  // ==========================================

  searchQuery = $state('');
  typeFilters = $state<EventType[]>([]);

  // Derived state for filtered events (client-side after API load)
  filteredEvents = $derived.by(() => {
    return this.events.filter(event => {
      // Filter by type
      if (this.typeFilters.length > 0 && !this.typeFilters.includes(event.type)) {
        return false;
      }

      // Filter by search query
      if (this.searchQuery.trim()) {
        const query = this.searchQuery.toLowerCase();
        return event.title.toLowerCase().includes(query);
      }

      return true;
    });
  });

  /**
   * Détection de conflits entre événements
   */
  conflicts = $derived.by(() => {
    const list: { eventId: string; type: 'overlap' | 'closure' | 'holiday'; message: string }[] = [];

    this.events.forEach(e1 => {
      this.events.forEach(e2 => {
        if (e1.id === e2.id) return;

        // Simple overlap check
        const start1 = new Date(e1.defaultDate);
        const end1 = new Date(e1.endDate || e1.defaultDate);
        const start2 = new Date(e2.defaultDate);
        const end2 = new Date(e2.endDate || e2.defaultDate);

        if (start1 <= end2 && end1 >= start2) {
          // Training on Holiday/Closure
          if (e1.type === 'training' && (e2.type === 'holiday' || e2.type === 'closure')) {
            list.push({
              eventId: e1.id,
              type: e2.type === 'holiday' ? 'holiday' : 'closure',
              message: `Chevauchement avec ${e2.title} (${e2.type === 'holiday' ? 'Férié' : 'Fermeture'})`
            });
          }
        }
      });
    });

    return list;
  });

  hasConflict(eventId: string) {
    return this.conflicts.some(c => c.eventId === eventId);
  }

  // ==========================================
  // Dérivés
  // ==========================================

  /**
   * Statistiques pour le mois sélectionné
   * - Chaque événement est compté une seule fois (même s'il s'étale sur plusieurs jours)
   * - workingDays compte les jours non-weekend, non-férié, non-fermeture
   */
  monthStats = $derived.by<{
    workingDays: number;
    holidaysCount: number;
    closuresCount: number;
    totalDays: number;
    typeCounts: Record<string, number>;
  }>(() => {
    const year = this.selectedDate.getFullYear();
    const month = this.selectedDate.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();

    // 1 — Compter les événements uniques du mois (par type)
    const typeCounts: Record<string, number> = {
      holiday: 0,
      closure: 0,
      training: 0,
      deadline: 0,
      anniversary: 0,
      leave: 0,
    };

    const monthStart = `${year}-${String(month + 1).padStart(2, '0')}-01`;
    const monthEnd = `${year}-${String(month + 1).padStart(2, '0')}-${String(daysInMonth).padStart(2, '0')}`;

    for (const event of this.events) {
      // L'événement touche-t-il ce mois-ci ?
      const evtStart = event.defaultDate;
      const evtEnd = event.endDate || event.defaultDate;
      if (evtEnd >= monthStart && evtStart <= monthEnd) {
        if (event.type in typeCounts) {
          typeCounts[event.type]++;
        }
      }
    }

    // 2 — Compter les jours ouvrés (en parcourant les jours)
    let workingDays = 0;

    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(year, month, d);
      const isWeekend = date.getDay() === 0 || date.getDay() === 6;

      const events = this.#getEventsForDateRaw(date);
      const isHoliday = events.some(e => e.type === 'holiday');
      const isClosure = events.some(e => e.type === 'closure');

      if (!isWeekend && !isHoliday && !isClosure) {
        workingDays++;
      }
    }

    return {
      workingDays,
      holidaysCount: typeCounts.holiday,
      closuresCount: typeCounts.closure,
      totalDays: daysInMonth,
      typeCounts,
    };
  });

  // ==========================================
  // Helpers
  // ==========================================

  /**
   * Récupère les événements pour une date donnée (utilise tous les événements, filtrés)
   */
  getEventsForDate(date: Date): CalendarEvent[] {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    const dStr = `${y}-${m}-${d}`;

    return this.filteredEvents.filter(event => {
      if (!event.endDate || event.endDate === event.defaultDate) {
        return event.defaultDate === dStr;
      }

      // Range check
      return dStr >= event.defaultDate && dStr <= event.endDate;
    });
  }

  /**
   * Récupère les événements pour une date donnée (utilise this.events brut,
   * ignoré les filtres typeFilters/searchQuery — utilisé par monthStats)
   */
  #getEventsForDateRaw(date: Date): CalendarEvent[] {
    const y = date.getFullYear();
    const m = String(date.getMonth() + 1).padStart(2, '0');
    const d = String(date.getDate()).padStart(2, '0');
    const dStr = `${y}-${m}-${d}`;

    return this.events.filter(event => {
      if (!event.endDate || event.endDate === event.defaultDate) {
        return event.defaultDate === dStr;
      }

      // Range check
      return dStr >= event.defaultDate && dStr <= event.endDate;
    });
  }

  // ==========================================
  // Navigation
  // ==========================================

  prevPeriod() {
    const d = new Date(this.selectedDate);
    if (this.view === 'month') d.setMonth(d.getMonth() - 1);
    else d.setFullYear(d.getFullYear() - 1);
    this.selectedDate = d;
  }

  nextPeriod() {
    const d = new Date(this.selectedDate);
    if (this.view === 'month') d.setMonth(d.getMonth() + 1);
    else d.setFullYear(d.getFullYear() + 1);
    this.selectedDate = d;
  }

  goToday() {
    this.selectedDate = new Date();
  }

  setView(v: 'month' | 'year') {
    this.view = v;
  }

  toggleTypeFilter(type: EventType) {
    if (this.typeFilters.includes(type)) {
      this.typeFilters = this.typeFilters.filter(t => t !== type);
    } else {
      this.typeFilters = [...this.typeFilters, type];
    }
  }

  resetFilters() {
    this.typeFilters = [];
    this.searchQuery = '';
  }
}


export const calendarStore = new CalendarStore();
