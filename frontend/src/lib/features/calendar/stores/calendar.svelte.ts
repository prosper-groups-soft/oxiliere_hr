import type { CalendarEvent, EventType } from '../types/types';


class CalendarStore {
  events = $state<CalendarEvent[]>([]);
  selectedDate = $state<Date>(new Date());
  view = $state<'month' | 'year'>('month');
  
  constructor() {
    // Persistence du mode de vue
    const savedView = typeof localStorage !== 'undefined' ? localStorage.getItem('oxiliere_calendar_view') : null;
    if (savedView === 'month' || savedView === 'year') {
      this.view = savedView;
    }

    $effect.root(() => {
      $effect(() => {
        if (typeof localStorage !== 'undefined') {
          localStorage.setItem('oxiliere_calendar_view', this.view);
        }
      });
    });

    // Mock initial data
    const today = new Date();
    const currYear = today.getFullYear();
    const currMonth = String(today.getMonth() + 1).padStart(2, '0');

    this.events = [
      { 
        id: '1', 
        title: 'Lundi de Pâques', 
        defaultDate: `${currYear}-03-21`, 
        type: 'holiday' 
      },
      { 
        id: '2', 
        title: 'Fermeture Été', 
        defaultDate: `${currYear}-03-01`, 
        endDate: `${currYear}-03-16`, 
        type: 'closure' 
      },
      { 
        id: '3', 
        title: 'Formation Svelte 5', 
        defaultDate: `${currYear}-${currMonth}-15`, 
        type: 'training' 
      },
      { 
        id: '4', 
        title: 'Maintenance Système', 
        defaultDate: `${currYear}-${currMonth}-18`, 
        type: 'closure' 
      }
    ];
  }

  // Filters & Search
  searchQuery = $state('');
  typeFilters = $state<EventType[]>([]);
  
  // Derived state for filtered events
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

  addEvent(event: Omit<CalendarEvent, 'id'>) {
    const newEvent: CalendarEvent = {
      ...event,
      id: crypto.randomUUID()
    };
    this.events = [...this.events, newEvent];
    return newEvent;
  }

  updateEvent(id: string, updates: Partial<CalendarEvent>) {
    this.events = this.events.map(event => 
      event.id === id ? { ...event, ...updates } : event
    );
  }

  deleteEvent(id: string) {
    this.events = this.events.filter(event => event.id !== id);
  }

  setEvents(events: CalendarEvent[]) {
    this.events = events;
  }

  /**
   * Replicates events from one year to another
   * Useful for recurring holidays and closures
   */
  replicateYear(sourceYear: number, targetYear: number, types: EventType[]): number {
    const sourceEvents = this.events.filter(e => {
      const year = parseInt(e.defaultDate.split('-')[0]);
      return year === sourceYear && types.includes(e.type);
    });

    let count = 0;
    const newEvents: CalendarEvent[] = [];

    sourceEvents.forEach(e => {
      const newDefaultDate = e.defaultDate.replace(sourceYear.toString(), targetYear.toString());
      const newEndDate = e.endDate ? e.endDate.replace(sourceYear.toString(), targetYear.toString()) : undefined;

      // Check for duplicate (by title and date)
      const exists = this.events.some(existing => 
        existing.title === e.title && 
        existing.defaultDate === newDefaultDate
      );

      if (!exists) {
        newEvents.push({
          id: crypto.randomUUID(),
          title: e.title,
          type: e.type,
          defaultDate: newDefaultDate,
          endDate: newEndDate
        });
        count++;
      }
    });

    if (newEvents.length > 0) {
      this.events = [...this.events, ...newEvents];
    }

    return count;
  }

  /**
   * Detected conflicts between events
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

  /**
   * Mass delete events for a specific year
   */
  resetYear(year: number) {
    this.events = this.events.filter(e => {
      const eventYear = parseInt(e.defaultDate.split('-')[0]);
      return eventYear !== year;
    });
  }

  /**
   * Import official RDC holidays
   * In a real app, this would call a Django service/fixture
   */
  async importHolidays(year: number) {
    // Simulating API call
    const rdcHolidays: Omit<CalendarEvent, 'id'>[] = [
      { title: "Nouvel An", defaultDate: `${year}-01-01`, type: 'holiday' },
      { title: "Martyrs de l'Indépendance", defaultDate: `${year}-01-04`, type: 'holiday' },
      { title: "Laurent Désiré Kabila", defaultDate: `${year}-01-16`, type: 'holiday' },
      { title: "Patrice Emery Lumumba", defaultDate: `${year}-01-17`, type: 'holiday' },
      { title: "Fête du Travail", defaultDate: `${year}-05-01`, type: 'holiday' },
      { title: "Indépendance", defaultDate: `${year}-06-30`, type: 'holiday' },
      { title: "Fête des Parents", defaultDate: `${year}-08-01`, type: 'holiday' },
      { title: "Noël", defaultDate: `${year}-12-25`, type: 'holiday' }
    ];

    let importedCount = 0;
    rdcHolidays.forEach(h => {
      const exists = this.events.some(e => e.title === h.title && e.defaultDate === h.defaultDate);
      if (!exists) {
        this.addEvent(h);
        importedCount++;
      }
    });

    return importedCount;
  }

  /**
   * Derived stats for the current selected month
   */
  monthStats = $derived.by(() => {
    const year = this.selectedDate.getFullYear();
    const month = this.selectedDate.getMonth();
    const daysInMonth = new Date(year, month + 1, 0).getDate();
    
    let workingDays = 0;
    let holidaysCount = 0;
    let closuresCount = 0;

    for (let d = 1; d <= daysInMonth; d++) {
      const date = new Date(year, month, d);
      const isWeekend = date.getDay() === 0 || date.getDay() === 6;
      
      const events = this.getEventsForDate(date);
      const isHoliday = events.some(e => e.type === 'holiday');
      const isClosure = events.some(e => e.type === 'closure');

      if (!isWeekend && !isHoliday && !isClosure) {
        workingDays++;
      }
      
      if (isHoliday) holidaysCount++;
      if (isClosure) closuresCount++;
    }

    return {
      workingDays,
      holidaysCount,
      closuresCount,
      totalDays: daysInMonth
    };
  });

  /**
   * Helper to get events for a specific date
   * Handles both single day and multi-day events
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

  // Navigation
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
